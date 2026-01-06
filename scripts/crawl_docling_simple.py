#!/usr/bin/env python3
"""Simple CodeWiki crawler using requests + BeautifulSoup.

Alternative to crawl4ai when browser automation isn't available.
"""
import re
import requests
from pathlib import Path
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import html2text


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


def clean_markdown(raw_md: str) -> str:
    """Clean markdown from UI artifacts."""
    cleaned = raw_md

    # Remove common UI patterns
    patterns = [
        r'copy code', r'zoom_in', r'fullscreen', r'filter_center_focus',
        r'\[edit\]', r'\[source\]', r'Skip to content', r'Table of contents',
        r'search', r'menu', r'close', r'arrow_back', r'arrow_forward',
        r'expand_more', r'expand_less', r'dark_mode', r'light_mode',
        r'Code Search', r'Sign in', r'Google.*Account', r'Privacy Policy',
        r'Terms of Service', r'send_feedback',
    ]

    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Clean up whitespace
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = re.sub(r'\[\s*\]\([^)]*\)', '', cleaned)

    return cleaned.strip()


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
        safe_title = re.sub(r'\s+', '_', safe_title)
        filename = f"{i:02d}_{safe_title[:50]}.md"

        content = f"# {section.title}\n\n{section.content}"

        if section.links:
            content += "\n\n---\n\n## Source References\n\n"
            for link in section.links:
                url = f"https://github.com/{link.repo}/blob/{link.commit}/{link.file_path}"
                if link.line > 0:
                    url += f"#L{link.line}"
                content += f"- [`{link.concept}`]({url})\n"

        (output_dir / filename).write_text(content)

    print(f"Saved {len(sections)} sections to {output_dir}")


def generate_link_catalog(sections: List[CodeWikiSection], output_path: Path) -> List[CodeWikiLink]:
    """Generate catalog of all GitHub links."""
    all_links = []
    for section in sections:
        for link in section.links:
            link.context = section.title
            all_links.append(link)

    seen = set()
    unique_links = []
    for link in all_links:
        key = (link.concept, link.file_path, link.line)
        if key not in seen:
            seen.add(key)
            unique_links.append(link)

    content = f"# GitHub Link Catalog\n\nGenerated: {datetime.now().isoformat()}\n\n"
    content += f"Total unique links: {len(unique_links)}\n\n"

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
    print(f"Saved link catalog to {output_path}")

    return unique_links


def crawl_codewiki_simple(url: str) -> str:
    """Crawl CodeWiki using requests + html2text."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    print(f"  Fetching {url}...")
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    print(f"  Got {len(response.text)} chars of HTML")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Try to find main content area
    # CodeWiki usually has the content in a specific container
    main_content = None

    # Try different selectors
    for selector in ['main', 'article', '[role="main"]', '.content', '#content']:
        main_content = soup.select_one(selector)
        if main_content:
            break

    if not main_content:
        main_content = soup.body or soup

    # Convert to markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0  # Don't wrap

    markdown = h.handle(str(main_content))
    print(f"  Converted to {len(markdown)} chars of markdown")

    return markdown


def main():
    """Main pipeline for docling CodeWiki crawl."""
    print("=" * 70)
    print("  CRAWLING CODEWIKI: docling-project/docling (Simple Method)")
    print("=" * 70)

    output_base = Path(__file__).parent.parent / "crawl_output" / "docling"
    output_base.mkdir(parents=True, exist_ok=True)

    raw_output = output_base / "raw_crawl.md"
    clean_output = output_base / "clean_content.md"
    sections_dir = output_base / "sections"
    catalog_path = output_base / "link_catalog.md"

    # Step 1: Crawl
    print("\n[1/4] Crawling CodeWiki...")
    url = "https://codewiki.google/github.com/docling-project/docling"

    try:
        content = crawl_codewiki_simple(url)
        raw_output.write_text(content)
        print(f"  Saved raw crawl")
    except Exception as e:
        print(f"  Failed: {e}")
        if raw_output.exists():
            print("  Using cached data...")
            content = raw_output.read_text()
        else:
            print("  No cached data. Exiting.")
            return

    # Step 2: Clean
    print("\n[2/4] Cleaning content...")
    cleaned = clean_markdown(content)
    clean_output.write_text(cleaned)
    print(f"  Cleaned: {len(content)} → {len(cleaned)} chars")

    # Step 3: Split
    print("\n[3/4] Splitting by headings...")
    sections = split_by_headings(cleaned)
    save_sections(sections, sections_dir, "docling")

    # Step 4: Extract links
    print("\n[4/4] Extracting GitHub links...")
    links = generate_link_catalog(sections, catalog_path)

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Sections: {len(sections)}")
    print(f"  Unique links: {len(links)}")
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


if __name__ == "__main__":
    main()
