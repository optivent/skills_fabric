import asyncio
import re
import os
import shutil
import argparse
from typing import List, Tuple
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# --- CONFIGURATION ---
MAX_CHARS = 24000
MAX_LINES = 500
OUTPUT_DIR = "ingest_output"

# --- PART 1: CRAWL ---
async def crawl_url(url: str) -> str:
    print(f"[*] Crawling: {url} ...")
    browser_conf = BrowserConfig(headless=True)
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=10,
        wait_until="networkidle",
        delay_before_return_html=30.0, # High delay for Gemini dynamic renders
        js_code="window.scrollTo(0, document.body.scrollHeight);"
    )
    
    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(url=url, config=run_conf)
        
        if not result.success:
            print(f"[!] Crawl Failed: {result.error_message}")
            return ""
        
        print(f"[+] Crawl Success: {len(result.markdown)} chars captured.")
        return result.markdown

# --- PART 2: CLEAN ---
def clean_markdown(raw_md: str) -> str:
    print("[*] Cleaning Markdown...")
    cleaned = raw_md
    
    # 1. Remove UI Artifacts (Copy code, zoom, etc.)
    cleaned = re.sub(r'copy code', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'zoom_in', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'fullscreen', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'filter_center_focus', '', cleaned, flags=re.IGNORECASE)
    
    # 2. Normalize whitespace (3+ newlines -> 2)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # 3. Preserve Links (Sanity Check - No action needed, regex above is safe)
    
    print(f"[+] Cleaning Complete. Size: {len(cleaned)} chars.")
    return cleaned

# --- PART 3: SEGMENT ---
def clean_filename(title: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9]', '_', title)
    return clean.strip('_').lower()

def save_chunk(content: str, base_name: str, output_path: str, part_num: int = None):
    if not content.strip():
        return
    
    filename = f"{base_name}_part_{part_num}.md" if part_num else f"{base_name}.md"
    full_path = os.path.join(output_path, filename)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  -> Saved: {filename} ({len(content)} chars)")

def process_h3_split(h2_title: str, h2_content: str, output_path: str):
    parts = re.split(r'(^### .*)', h2_content, flags=re.MULTILINE)
    base_name = clean_filename(h2_title)
    
    current_chunk = ""
    current_part = 1
    
    # Preamble
    if parts[0].strip():
        current_chunk += parts[0]
    
    it = iter(parts[1:])
    for header in it:
        try:
            content = next(it)
        except StopIteration:
            content = ""
        
        full_section = header + content
        
        if len(current_chunk) + len(full_section) > MAX_CHARS:
            if current_chunk:
                save_chunk(current_chunk, base_name, output_path, current_part)
                current_part += 1
                current_chunk = ""

            # Check if the single H3 section ITSELF is too big
            h3_lines = len(full_section.splitlines())
            if len(full_section) > MAX_CHARS or h3_lines > MAX_LINES:
                print(f"[!] Deep Splitting H3 Section: '{header.strip()[:50]}...'")
                # Split by Paragraphs
                paragraphs = re.split(r'(\n{2,})', full_section)
                sub_chunk = ""
                for para in paragraphs:
                    if len(sub_chunk) + len(para) > MAX_CHARS or len((sub_chunk + para).splitlines()) > MAX_LINES:
                        if sub_chunk:
                            save_chunk(sub_chunk, base_name, output_path, current_part)
                            current_part += 1
                            sub_chunk = para
                        else:
                            # Edge Code: Paragraph IS the limit? Force save.
                            save_chunk(para, base_name, output_path, current_part)
                            current_part += 1
                            sub_chunk = ""
                    else:
                        sub_chunk += para
                
                if sub_chunk:
                    save_chunk(sub_chunk, base_name, output_path, current_part)
                    current_part += 1
            else:
                # Normal case: H3 section fits in a new chunk
                current_chunk = full_section
        else:
            current_chunk += full_section
            
    if current_chunk:
        save_chunk(current_chunk, base_name, output_path, current_part)

def segment_markdown(clean_md: str, output_path: str):
    print("[*] Segmenting Documentation...")
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)
    
    parts = re.split(r'(^## .*)', clean_md, flags=re.MULTILINE)
    
    if parts[0].strip():
        save_chunk(parts[0], "00_introduction", output_path)
        
    it = iter(parts[1:])
    for header in it:
        try:
            content = next(it)
        except StopIteration:
            content = ""
            
        full_h2_block = header + content
        title = header.strip().lstrip('#').strip()
        line_count = len(full_h2_block.splitlines())
        
        if len(full_h2_block) <= MAX_CHARS and line_count <= MAX_LINES:
            save_chunk(full_h2_block, clean_filename(title), output_path)
        else:
            print(f"[!] Splitting Section: '{title}' (Chars: {len(full_h2_block)}, Lines: {line_count})")
            process_h3_split(title, full_h2_block, output_path)

# --- MAIN ---
async def main():
    parser = argparse.ArgumentParser(description="Sovereign Ingestion Pipeline")
    parser.add_argument("url", help="CodeWiki URL to ingest")
    parser.add_argument("--output", default="ingest_output", help="Output directory")
    args = parser.parse_args()
    
    # 1. URL Normalization (GitHub -> CodeWiki)
    target_url = args.url
    if "github.com" in target_url and "codewiki.google" not in target_url:
        # Strip protocol if present to avoid double https://
        clean_target = target_url.replace("https://", "").replace("http://", "")
        target_url = f"https://codewiki.google/{clean_target}"
        print(f"[*] Detected GitHub URL. Target converted to: {target_url}")

    # 2. Crawl
    raw_md = await crawl_url(target_url)
    if not raw_md:
        return
        
    # 2. Clean
    clean_md = clean_markdown(raw_md)
    
    # 3. Segment
    segment_markdown(clean_md, args.output)
    print("\n[+] Ingestion Complete.")

if __name__ == "__main__":
    asyncio.run(main())
