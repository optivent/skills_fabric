import os

SANDBOX_PATH = os.path.expanduser("~/lab/new_crawl4AI/ultrathink_v7/sandbox.py")

OLD_CODE = 'cmd.extend(["--ro-bind", venv_str, venv_str])'
NEW_CODE = """
        if Path(venv_str).exists():
            cmd.extend(["--ro-bind", venv_str, venv_str])
"""

def main():
    try:
        with open(SANDBOX_PATH, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"File not found: {SANDBOX_PATH}")
        return

    if OLD_CODE in content:
        print("Found blind venv bind. Patching...")
        new_content = content.replace(OLD_CODE, NEW_CODE)
        
        with open(SANDBOX_PATH, 'w') as f:
            f.write(new_content)
        print("Success: sandbox.py bwrap patched.")
    else:
        print("Bind pattern not found or already patched.")

if __name__ == "__main__":
    main()
