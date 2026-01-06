#!/usr/bin/env python3
"""Crawl CodeWiki using Brightdata Web Unlocker API.

This works in Claude Code web sandbox because it uses simple HTTP requests,
while Brightdata handles the JavaScript rendering on their servers.

Usage:
    export BRIGHTDATA_API_KEY="your_api_key"
    export BRIGHTDATA_ZONE="web_unlocker1"  # or your zone name
    python scripts/crawl_codewiki_brightdata.py https://codewiki.google/github.com/docling-project/docling
"""
import os
import re
import sys
import json
import requests
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
import html2text


# Configuration
BRIGHTDATA_API_URL = "https://api.brightdata.com/request"
DEFAULT_ZONE = "web_unlocker1"


@dataclass
class CodeWikiLink:
    """A GitHub link extracted from CodeWiki."""
    concept: str
    repo: str
    file_path: str
    line: int
    commit: str
    context: str = ""

    def __str__(self):
        return f"{self.concept} → {self.file_path}:{self.line}"


@dataclass
class CodeWikiSection:
    """A section extracted from CodeWiki."""
    title: str
    content: str
    level: int
    links: List[CodeWikiLink] = field(default_factory=list)


def get_api_credentials() -> Tuple[str, str]:
    """Get Brightdata API credentials from environment."""
    api_key = os.environ.get("BRIGHTDATA_API_KEY")
    zone = os.environ.get("BRIGHTDATA_ZONE", DEFAULT_ZONE)

    if not api_key:
        print("ERROR: BRIGHTDATA_API_KEY environment variable not set")
        print("Please set it: export BRIGHTDATA_API_KEY='your_api_key'")
        sys.exit(1)

    return api_key, zone


def fetch_with_brightdata(url: str, api_key: str, zone: str) -> Optional[str]:
    """Fetch a URL using Brightdata Web Unlocker with JS rendering."""
    print(f"  Fetching via Brightdata Web Unlocker...")
    print(f"  URL: {url}")
    print(f"  Zone: {zone}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "zone": zone,
        "url": url,
        "format": "raw",  # Get raw HTML
        "render_js": True,  # Enable JavaScript rendering
        "wait_for_selector": "main",  # Wait for main content
        "timeout": 60000  # 60 second timeout
    }

    try:
        response = requests.post(
            BRIGHTDATA_API_URL,
            headers=headers,
            json=payload,
            timeout=90
        )

        if response.status_code == 200:
            print(f"  Success! Got {len(response.text)} chars")
            return response.text
        else:
            print(f"  Error: HTTP {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return None

    except requests.exceptions.Timeout:
        print("  Error: Request timed out")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def html_to_markdown(html_content: str) -> str:
    """Convert HTML to markdown."""
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Try to find main content area
    main_content = None
    for selector in ['main', 'article', '[role="main"]', '.content', '#content', '.markdown-body']:
        main_content = soup.select_one(selector)
        if main_content:
            break

    if not main_content:
        main_content = soup.body or soup

    # Convert to markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0
    h.unicode_snob = True

    markdown = h.handle(str(main_content))
    return markdown


def clean_codewiki_content(raw_md: str) -> str:
    """Remove non-relevant UI artifacts from CodeWiki."""
    cleaned = raw_md

    # Remove UI patterns
    ui_patterns = [
        r'copy code', r'zoom_in', r'fullscreen', r'filter_center_focus',
        r'\[edit\]', r'\[source\]', r'Skip to content', r'Table of contents',
        r'search', r'menu', r'close', r'arrow_back', r'arrow_forward',
        r'expand_more', r'expand_less', r'dark_mode', r'light_mode',
        r'Code Search', r'Sign in', r'Google.*Account', r'Privacy Policy',
        r'Terms of Service', r'send_feedback', r'content_copy',
    ]

    for pattern in ui_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Clean up whitespace
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = re.sub(r'\[\s*\]\([^)]*\)', '', cleaned)

    return cleaned.strip()


def extract_github_links(markdown: str) -> List[CodeWikiLink]:
    """Extract all GitHub links from markdown."""
    pattern = r"\[`?([^`\]]+)`?\]\(https://github\.com/([^/]+/[^/]+)/blob/([^/]+)/([^#\)]+)(?:#L(\d+))?\)"

    links = []
    for match in re.finditer(pattern, markdown):
        links.append(CodeWikiLink(
            concept=match.group(1),
            repo=match.group(2),
            file_path=match.group(4),
            line=int(match.group(5)) if match.group(5) else 0,
            commit=match.group(3)
        ))

    return links


def split_by_headings(markdown: str) -> List[CodeWikiSection]:
    """Split markdown into sections by headings."""
    sections = []
    pattern = r'^(#{1,4})\s+(.+)$'

    current_section = None
    current_content = []

    for line in markdown.split('\n'):
        match = re.match(pattern, line)
        if match:
            if current_section:
                content = '\n'.join(current_content).strip()
                current_section.content = content
                current_section.links = extract_github_links(content)
                sections.append(current_section)

            level = len(match.group(1))
            title = match.group(2).strip()
            current_section = CodeWikiSection(title=title, content="", level=level)
            current_content = [line]
        else:
            current_content.append(line)

    if current_section:
        content = '\n'.join(current_content).strip()
        current_section.content = content
        current_section.links = extract_github_links(content)
        sections.append(current_section)
    elif current_content:
        content = '\n'.join(current_content).strip()
        if content:
            sections.insert(0, CodeWikiSection(
                title="Introduction",
                content=content,
                level=0,
                links=extract_github_links(content)
            ))

    return sections


def save_sections(sections: List[CodeWikiSection], output_dir: Path, library: str):
    """Save sections as individual files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, section in enumerate(sections):
        safe_title = re.sub(r'[^\w\s-]', '', section.title)
        safe_title = re.sub(r'\s+', '_', safe_title)[:50]
        filename = f"{i:02d}_{safe_title}.md"

        content = f"# {section.title}\n\n{section.content}"

        if section.links:
            content += "\n\n---\n\n## Source References\n\n"
            for link in section.links:
                url = f"https://github.com/{link.repo}/blob/{link.commit}/{link.file_path}"
                if link.line > 0:
                    url += f"#L{link.line}"
                content += f"- [`{link.concept}`]({url})\n"

        (output_dir / filename).write_text(content)

    print(f"  Saved {len(sections)} section files")


def generate_link_catalog(sections: List[CodeWikiSection], output_path: Path) -> List[CodeWikiLink]:
    """Generate catalog of all GitHub links."""
    all_links = []
    for section in sections:
        for link in section.links:
            link.context = section.title
            all_links.append(link)

    # Deduplicate
    seen = set()
    unique_links = []
    for link in all_links:
        key = (link.concept, link.file_path, link.line)
        if key not in seen:
            seen.add(key)
            unique_links.append(link)

    # Generate catalog
    content = f"# CodeWiki Link Catalog\n\n"
    content += f"Generated: {datetime.now().isoformat()}\n"
    content += f"Source: Brightdata Web Unlocker\n\n"
    content += f"Total unique links: {len(unique_links)}\n\n"

    # Group by file
    by_file = {}
    for link in unique_links:
        if link.file_path not in by_file:
            by_file[link.file_path] = []
        by_file[link.file_path].append(link)

    content += f"## By File ({len(by_file)} files)\n\n"
    for file_path in sorted(by_file.keys()):
        links = by_file[file_path]
        content += f"### `{file_path}`\n\n"
        for link in sorted(links, key=lambda l: l.line):
            content += f"- Line {link.line}: `{link.concept}` (from: {link.context})\n"
        content += "\n"

    output_path.write_text(content)
    print(f"  Saved link catalog ({len(unique_links)} unique links)")

    return unique_links


def extract_library_name(url: str) -> str:
    """Extract library name from CodeWiki URL."""
    # https://codewiki.google/github.com/owner/repo -> repo
    match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
    if match:
        return match.group(2)
    return "unknown"


def main():
    """Main crawl pipeline using Brightdata."""
    if len(sys.argv) < 2:
        print("Usage: python crawl_codewiki_brightdata.py <codewiki_url>")
        print("Example: python crawl_codewiki_brightdata.py https://codewiki.google/github.com/docling-project/docling")
        print("\nMake sure to set environment variables:")
        print("  export BRIGHTDATA_API_KEY='your_api_key'")
        print("  export BRIGHTDATA_ZONE='web_unlocker1'  # optional")
        sys.exit(1)

    url = sys.argv[1]
    library = extract_library_name(url)

    print("=" * 70)
    print("  CODEWIKI CRAWLER (Brightdata Web Unlocker)")
    print("=" * 70)
    print(f"\n  URL: {url}")
    print(f"  Library: {library}")

    # Setup
    api_key, zone = get_api_credentials()
    output_base = Path(__file__).parent.parent / "crawl_output" / library
    output_base.mkdir(parents=True, exist_ok=True)

    # Step 1: Fetch with Brightdata
    print("\n[1/4] Fetching with Brightdata Web Unlocker...")
    html_content = fetch_with_brightdata(url, api_key, zone)

    if not html_content:
        print("Failed to fetch content. Exiting.")
        sys.exit(1)

    # Save raw HTML
    (output_base / "raw_html.html").write_text(html_content)
    print(f"  Saved raw HTML ({len(html_content)} chars)")

    # Step 2: Convert to markdown
    print("\n[2/4] Converting to markdown...")
    markdown = html_to_markdown(html_content)
    cleaned = clean_codewiki_content(markdown)
    (output_base / "codewiki_content.md").write_text(cleaned)
    print(f"  Converted: {len(html_content)} HTML → {len(cleaned)} markdown")

    # Step 3: Split by headings
    print("\n[3/4] Splitting by headings...")
    sections = split_by_headings(cleaned)
    sections_dir = output_base / "sections"
    save_sections(sections, sections_dir, library)

    # Step 4: Extract links
    print("\n[4/4] Extracting GitHub links...")
    links = generate_link_catalog(sections, output_base / "link_catalog.md")

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Sections: {len(sections)}")
    print(f"  Unique GitHub links: {len(links)}")
    print(f"  Output: {output_base}")

    if links:
        by_file = {}
        for link in links:
            if link.file_path not in by_file:
                by_file[link.file_path] = 0
            by_file[link.file_path] += 1

        print(f"\n  Most referenced files:")
        for fp, cnt in sorted(by_file.items(), key=lambda x: -x[1])[:10]:
            print(f"    {cnt:3d}× {fp}")

    print("\n" + "=" * 70)
    print("  SUCCESS!")
    print("=" * 70)
    print(f"  CodeWiki content saved to: {output_base}/codewiki_content.md")
    print(f"  Link catalog saved to: {output_base}/link_catalog.md")


if __name__ == "__main__":
    main()
