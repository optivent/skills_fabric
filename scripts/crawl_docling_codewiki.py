#!/usr/bin/env python3
"""Crawl CodeWiki for docling project.

This script:
1. Crawls the CodeWiki page for docling
2. Cleans non-relevant content
3. Splits by headings into files
4. Extracts and catalogs GitHub links
"""
import asyncio
import re
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple
from datetime import datetime

# Try to import crawl4ai
try:
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("crawl4ai not available - will use cached data if exists")


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
    level: int  # 1 for H1, 2 for H2, etc.
    links: List[CodeWikiLink] = field(default_factory=list)


def clean_codewiki_content(raw_md: str) -> str:
    """Remove non-relevant UI artifacts from CodeWiki crawl."""
    cleaned = raw_md

    # Remove common UI artifacts
    ui_patterns = [
        r'copy code',
        r'zoom_in',
        r'fullscreen',
        r'filter_center_focus',
        r'\[edit\]',
        r'\[source\]',
        r'Skip to content',
        r'Table of contents',
        r'search',
        r'menu',
        r'close',
        r'arrow_back',
        r'arrow_forward',
        r'expand_more',
        r'expand_less',
        r'dark_mode',
        r'light_mode',
        # CodeWiki specific
        r'Code Search',
        r'Sign in',
        r'Google.*Account',
        r'Privacy Policy',
        r'Terms of Service',
    ]

    for pattern in ui_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Remove empty links
    cleaned = re.sub(r'\[\s*\]\([^)]*\)', '', cleaned)

    # Remove multiple consecutive blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    # Remove lines that are just whitespace or special characters
    lines = cleaned.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that are just punctuation or very short
        if stripped and (len(stripped) > 2 or stripped.startswith('#')):
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines).strip()


def extract_github_links(markdown: str) -> List[CodeWikiLink]:
    """Extract all GitHub links from markdown."""
    # Pattern for GitHub links: [text](https://github.com/owner/repo/blob/commit/path#L123)
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

    # Split by any heading (# through ####)
    pattern = r'^(#{1,4})\s+(.+)$'

    current_section = None
    current_content = []

    for line in markdown.split('\n'):
        match = re.match(pattern, line)
        if match:
            # Save previous section
            if current_section:
                content = '\n'.join(current_content).strip()
                current_section.content = content
                current_section.links = extract_github_links(content)
                sections.append(current_section)

            # Start new section
            level = len(match.group(1))
            title = match.group(2).strip()
            current_section = CodeWikiSection(
                title=title,
                content="",
                level=level
            )
            current_content = [line]
        else:
            current_content.append(line)

    # Save last section
    if current_section:
        content = '\n'.join(current_content).strip()
        current_section.content = content
        current_section.links = extract_github_links(content)
        sections.append(current_section)
    elif current_content:
        # Content before first heading
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
    """Save sections as individual markdown files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, section in enumerate(sections):
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', section.title)
        safe_title = re.sub(r'\s+', '_', safe_title)
        filename = f"{i:02d}_{safe_title[:50]}.md"

        filepath = output_dir / filename

        content = f"# {section.title}\n\n"
        content += section.content

        if section.links:
            content += "\n\n---\n\n## Source References\n\n"
            for link in section.links:
                content += f"- [`{link.concept}`](https://github.com/{link.repo}/blob/{link.commit}/{link.file_path}"
                if link.line > 0:
                    content += f"#L{link.line}"
                content += ")\n"

        filepath.write_text(content)

    print(f"Saved {len(sections)} sections to {output_dir}")


def generate_link_catalog(sections: List[CodeWikiSection], output_path: Path):
    """Generate a catalog of all GitHub links."""
    all_links = []
    for section in sections:
        for link in section.links:
            link.context = section.title
            all_links.append(link)

    # Deduplicate by concept+file+line
    seen = set()
    unique_links = []
    for link in all_links:
        key = (link.concept, link.file_path, link.line)
        if key not in seen:
            seen.add(key)
            unique_links.append(link)

    # Generate catalog
    content = f"# GitHub Link Catalog\n\n"
    content += f"Generated: {datetime.now().isoformat()}\n\n"
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
    print(f"Saved link catalog to {output_path}")

    return unique_links


async def crawl_codewiki(url: str) -> Tuple[bool, str]:
    """Crawl a CodeWiki URL."""
    if not CRAWL4AI_AVAILABLE:
        return False, "crawl4ai not installed"

    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=10,
        wait_until="networkidle",
        delay_before_return_html=5.0,
        js_code="window.scrollTo(0, document.body.scrollHeight);"
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)

        if result.success:
            return True, result.markdown
        else:
            return False, result.error_message


async def main():
    """Main crawl pipeline for docling."""
    print("=" * 70)
    print("  CRAWLING CODEWIKI: docling-project/docling")
    print("=" * 70)

    # Setup paths
    output_base = Path(__file__).parent.parent / "crawl_output" / "docling"
    output_base.mkdir(parents=True, exist_ok=True)

    raw_output = output_base / "raw_crawl.md"
    clean_output = output_base / "clean_content.md"
    sections_dir = output_base / "sections"
    catalog_path = output_base / "link_catalog.md"

    # Step 1: Crawl
    print("\n[1/4] Crawling CodeWiki...")
    url = "https://codewiki.google/github.com/docling-project/docling"

    success, content = await crawl_codewiki(url)

    if not success:
        print(f"  Failed to crawl: {content}")
        # Try to use cached data
        if raw_output.exists():
            print("  Using cached raw data...")
            content = raw_output.read_text()
        else:
            print("  No cached data available. Exiting.")
            return
    else:
        # Save raw
        raw_output.write_text(content)
        print(f"  Saved raw crawl ({len(content)} chars)")

    # Step 2: Clean
    print("\n[2/4] Cleaning content...")
    cleaned = clean_codewiki_content(content)
    clean_output.write_text(cleaned)
    print(f"  Cleaned: {len(content)} → {len(cleaned)} chars")

    # Step 3: Split by headings
    print("\n[3/4] Splitting by headings...")
    sections = split_by_headings(cleaned)
    save_sections(sections, sections_dir, "docling")
    print(f"  Created {len(sections)} section files")

    # Step 4: Extract and catalog links
    print("\n[4/4] Extracting GitHub links...")
    links = generate_link_catalog(sections, catalog_path)

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Sections extracted: {len(sections)}")
    print(f"  Unique GitHub links: {len(links)}")
    print(f"  Output directory: {output_base}")

    # Show top linked files
    by_file = {}
    for link in links:
        if link.file_path not in by_file:
            by_file[link.file_path] = 0
        by_file[link.file_path] += 1

    print(f"\n  Most referenced files:")
    for file_path, count in sorted(by_file.items(), key=lambda x: -x[1])[:10]:
        print(f"    {count:3d}× {file_path}")

    print("\n" + "=" * 70)
    print("  NEXT STEPS")
    print("=" * 70)
    print("  1. Clone docling repo: git clone https://github.com/docling-project/docling")
    print("  2. Validate links against cloned repo")
    print("  3. Build proof-based understanding from verified links")


if __name__ == "__main__":
    asyncio.run(main())
