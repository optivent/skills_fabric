"""
CodeWiki Robust Extractor - Deterministic, Zero AI
Handles edge cases, filters anomalies, preserves GitHub links
"""
import asyncio
import re
import shutil
from pathlib import Path
from dataclasses import dataclass
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# Output directory
OUTPUT_DIR = Path("./loguru_docs_output")

# Test with single repo
REPOS = [
    "Delgan/loguru",
]

# Anomaly filters
SKIP_PATTERNS = [
    r'<!--',           # HTML comments (template files)
    r'-->',
    r'^\s*$',          # Empty names
    r'^Sections?$',    # Generic headers
    r'^Table of Contents$',
    r'^Index$',
    r'PULL_REQUEST',   # PR templates
    r'ISSUE_TEMPLATE',
    r'Checklist',      # Contribution templates
]

MIN_CONTENT_LENGTH = 500    # Minimum characters
MIN_LINK_COUNT = 2          # Minimum GitHub links


@dataclass
class Section:
    name: str
    content: str
    github_links: list

    @property
    def is_valid(self) -> bool:
        """Check if section passes quality filters"""
        # Check name patterns
        for pattern in SKIP_PATTERNS:
            if re.search(pattern, self.name, re.IGNORECASE):
                return False

        # Check content length
        if len(self.content) < MIN_CONTENT_LENGTH:
            return False

        # Check link count
        if len(self.github_links) < MIN_LINK_COUNT:
            return False

        return True

    @property
    def safe_dirname(self) -> str:
        """Generate safe directory name"""
        # Remove problematic characters
        clean = re.sub(r'[<>:"/\\|?*]', '', self.name)
        clean = re.sub(r'\s+', '_', clean.strip())
        clean = re.sub(r'_+', '_', clean)  # Collapse multiple underscores
        clean = re.sub(r'^_|_$', '', clean)  # Strip leading/trailing underscores

        # Truncate but don't break words
        if len(clean) > 50:
            clean = clean[:50].rsplit('_', 1)[0]

        return clean or "unnamed_section"


def extract_github_links(text: str) -> list[dict]:
    """Extract GitHub source links with deduplication"""
    pattern = r'\[`?([^]`]+)`?\]\((https://github\.com/[^)]+)\)'
    matches = re.findall(pattern, text)

    seen = set()
    links = []
    for name, url in matches:
        key = (name.strip(), url.strip())
        if key not in seen:
            seen.add(key)
            links.append({"name": name.strip(), "url": url.strip()})

    return links


def parse_sections(markdown: str) -> list[Section]:
    """Parse markdown into validated sections"""

    # Match ## headers (main sections in CodeWiki)
    section_pattern = r'^## (.+)$'
    matches = list(re.finditer(section_pattern, markdown, re.MULTILINE))

    sections = []

    for i, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)

        content = markdown[start:end].strip()
        github_links = extract_github_links(content)

        section = Section(
            name=name,
            content=content,
            github_links=github_links
        )

        if section.is_valid:
            sections.append(section)
        else:
            print(f"    ⚠ Filtered: '{name[:40]}...' (len={len(content)}, links={len(github_links)})")

    return sections


def format_skill_markdown(section: Section) -> str:
    """Format as clean skill-style markdown"""

    # Clean content
    lines = []
    for line in section.content.split('\n'):
        # Skip navigation artifacts
        if line.strip() in ['link', 'zoom_in', 'content_copyCopy', '|']:
            continue
        lines.append(line)

    cleaned_content = '\n'.join(lines)

    # Build markdown
    md = f"""# {section.name}

{cleaned_content}

---

## Source References

"""

    for link in section.github_links:
        md += f"- [`{link['name']}`]({link['url']})\n"

    return md


async def process_repo(repo: str, crawler: AsyncWebCrawler) -> dict:
    """Process a single repository"""

    url = f"https://codewiki.google/github.com/{repo}"
    repo_dirname = repo.replace('/', '_')
    repo_dir = OUTPUT_DIR / repo_dirname

    print(f"\n{'─' * 60}")
    print(f"  {repo}")
    print(f"{'─' * 60}")

    config = CrawlerRunConfig(
        wait_until="networkidle",
        delay_before_return_html=2.0,
    )

    try:
        result = await crawler.arun(url, config)
    except Exception as e:
        print(f"    ❌ Crawl error: {e}")
        return {"repo": repo, "error": str(e), "status": "crawl_error"}

    if not result.success:
        print(f"    ❌ Crawl failed (no content)")
        return {"repo": repo, "error": "No content", "status": "no_content"}

    if not result.markdown or len(result.markdown) < 100:
        print(f"    ⚠ No CodeWiki available")
        return {"repo": repo, "error": "No CodeWiki", "status": "no_codewiki"}

    # Parse sections
    sections = parse_sections(result.markdown)

    if not sections:
        print(f"    ⚠ No valid sections found")
        return {"repo": repo, "error": "No sections", "status": "no_sections"}

    # Create output
    repo_dir.mkdir(parents=True, exist_ok=True)

    total_links = 0
    index_content = f"""# {repo} - CodeWiki

> Auto-extracted from [CodeWiki]({url})

## Sections

"""

    for section in sections:
        section_dir = repo_dir / section.safe_dirname
        section_dir.mkdir(parents=True, exist_ok=True)

        # Filename: codewiki_SectionName.md
        filename = f"codewiki_{section.safe_dirname}.md"
        content_file = section_dir / filename
        content_file.write_text(format_skill_markdown(section), encoding='utf-8')

        index_content += f"- [{section.name}](./{section.safe_dirname}/{filename}) ({len(section.github_links)} refs)\n"
        total_links += len(section.github_links)

        print(f"    ✓ {section.safe_dirname}/{filename} ({len(section.github_links)} links)")

    # Write index
    (repo_dir / "README.md").write_text(index_content, encoding='utf-8')

    print(f"\n    📁 {len(sections)} sections, {total_links} links")

    return {
        "repo": repo,
        "sections": len(sections),
        "links": total_links,
        "path": str(repo_dir),
        "status": "success"
    }


async def main():
    print("=" * 70)
    print("CODEWIKI ROBUST EXTRACTOR")
    print("20 Major AI Libraries - Zero AI Tokens")
    print("=" * 70)

    # Clean output
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    results = []

    # Use single crawler instance for efficiency
    async with AsyncWebCrawler() as crawler:
        for repo in REPOS:
            try:
                result = await process_repo(repo, crawler)
                results.append(result)
            except Exception as e:
                print(f"    ❌ Unexpected error: {e}")
                results.append({"repo": repo, "error": str(e), "status": "error"})

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    success = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") != "success"]

    total_sections = sum(r.get("sections", 0) for r in success)
    total_links = sum(r.get("links", 0) for r in success)

    print(f"\n✅ Successful: {len(success)}/{len(REPOS)}")
    for r in success:
        print(f"   {r['repo']}: {r['sections']} sections, {r['links']} links")

    if failed:
        print(f"\n⚠ Failed/Unavailable: {len(failed)}")
        for r in failed:
            print(f"   {r['repo']}: {r.get('error', 'Unknown')}")

    print(f"\n{'─' * 70}")
    print(f"📊 Total: {total_sections} sections, {total_links} GitHub links")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"🔧 Filters applied: min {MIN_CONTENT_LENGTH} chars, min {MIN_LINK_COUNT} links")
    print(f"✅ Zero AI tokens used!")


if __name__ == "__main__":
    asyncio.run(main())
