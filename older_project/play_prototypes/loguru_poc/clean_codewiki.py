import sys
import re

def clean_markdown(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into lines
    lines = content.split("\n")
    cleaned_lines = []
    
    # UI Artifacts to strip from within lines
    ui_tokens = [
        r"link",
        r"zoom_in",
        r"content_copyCopy",
        r"content_copy",
        r"refresh",
        r"send",
        r"Share",
        r"Copy code",
        r"View on GitHub"
    ]
    
    # Patterns to skip entire lines
    skip_patterns = [
        r"^\[!\[Code Wiki logo\]",
        r"^dark_mode",
        r"^sharespark Chat",
        r"^Toggle theme",
        r"^Feedback",
        r"^\[ Terms \]",
        r"^\[ Privacy \]",
        r"^\[FAQ\]",
        r"^Toggle theme",
        r"^Copy code",
        r"^View on GitHub",
        r"^--- START ---",
        r"^--- END ---"
    ]

    for line in lines:
        line = line.strip()
        
        # Skip empty lines but keep one for spacing (later)
        if not line:
            cleaned_lines.append("")
            continue
            
        # Check if line should be skipped entirely
        should_skip = False
        for pattern in skip_patterns:
            if re.search(pattern, line):
                should_skip = True
                break
        if should_skip:
            continue
            
        # Clean specific tokens within the line
        for token in ui_tokens:
            line = re.sub(rf"\b{token}\b", "", line)
            
        # Clean up any leftover hanging spaces from token removal
        line = line.strip()
        
        if line:
            cleaned_lines.append(line)

    # Rejoin and collapse excessive newlines
    final_output = "\n".join(cleaned_lines)
    final_output = re.sub(r"\n{3,}", "\n\n", final_output)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_output)
    
    return len(final_output)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 clean_codewiki.py input.md output.md")
        sys.exit(1)
        
    chars = clean_markdown(sys.argv[1], sys.argv[2])
    print(f"Cleaning complete. Wrote {chars} characters to {sys.argv[2]}")
