import re
import os
import shutil

INPUT_FILE = "/home/aig/play/skills_factory/loguru_poc/loguru_docs_clean.md"
OUTPUT_DIR = "/home/aig/play/skills_factory/loguru_poc/doc_structure"
MAX_CHARS = 24000

def clean_filename(title):
    # Keep only alphanumeric and replace spaces/symbols with underscore
    clean = re.sub(r'[^a-zA-Z0-9]', '_', title)
    return clean.strip('_').lower()

def save_chunk(content, base_name, part_num=None):
    if not content.strip():
        return
    
    if part_num is not None:
        filename = f"{base_name}_part_{part_num}.md"
    else:
        filename = f"{base_name}.md"
        
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {filename} ({len(content)} chars)")

def process_h3_split(h2_title, h2_content):
    # Split by Heading 3, keeping delimiters
    # Pattern looks for start of line ###
    parts = re.split(r'(^### .*)', h2_content, flags=re.MULTILINE)
    
    # parts[0] is preamble (text before first ###)
    # parts[1] is first ### header
    # parts[2] is first ### content
    # etc...
    
    base_name = clean_filename(h2_title)
    
    current_chunk = ""
    current_part = 1
    
    # Add preamble if exists
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
            # Current chunk is full, save it
            if current_chunk:
                save_chunk(current_chunk, base_name, current_part)
                current_part += 1
                current_chunk = full_section
            else:
                # Determines if a single section is massive (edge case)
                # Just save it anyway to avoid losing data
                save_chunk(full_section, base_name, current_part)
                current_part += 1
                current_chunk = ""
        else:
            current_chunk += full_section
            
    # Save remainder
    if current_chunk:
        save_chunk(current_chunk, base_name, current_part)

def main():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # Split by Heading 2
    # Logic: Find all starts of ## 
    # re.split includes the capture group, so we get Title, Content
    parts = re.split(r'(^## .*)', raw_text, flags=re.MULTILINE)
    
    # parts[0] is intro (before first ##)
    if parts[0].strip():
        save_chunk(parts[0], "00_introduction")

    # Iterate pairs (Header, Content)
    it = iter(parts[1:])
    for header in it:
        try:
            content = next(it)
        except StopIteration:
            content = ""
            
        full_h2_block = header + content
        title = header.strip().lstrip('#').strip()
        
        line_count = len(full_h2_block.splitlines())
        
        if len(full_h2_block) <= MAX_CHARS and line_count <= 500:
            save_chunk(full_h2_block, clean_filename(title))
        else:
            print(f"Section '{title}' (Chars: {len(full_h2_block)}, Lines: {line_count}) exceeds limits (24k chars or 500 lines). Splitting by H3...")
            process_h3_split(title, full_h2_block)

if __name__ == "__main__":
    main()
