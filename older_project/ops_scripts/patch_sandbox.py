import os

SANDBOX_PATH = os.path.expanduser("~/lab/new_crawl4AI/ultrathink_v7/sandbox.py")

# Mockable decorator
MOCK_TRACEABLE = """
def traceable(func=None, **kwargs):
    if func:
        return func
    def wrapper(f):
        return f
    return wrapper
"""

def main():
    try:
        with open(SANDBOX_PATH, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"File not found: {SANDBOX_PATH}")
        return

    # Replacing the import
    if "from langsmith import traceable" in content:
        print("Found langsmith import. Patching...")
        new_content = content.replace("from langsmith import traceable", 
                                    "try:\n    from langsmith import traceable\nexcept ImportError:\n" + 
                                    "\n".join(["    " + line for line in MOCK_TRACEABLE.splitlines() if line]))
        
        with open(SANDBOX_PATH, 'w') as f:
            f.write(new_content)
        print("Success: sandbox.py patched.")
    else:
        print("Langsmith import not found or already patched.")

if __name__ == "__main__":
    main()
