import json
import os
import shutil
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path(os.path.expanduser("~/.config/opencode/oh-my-opencode.json"))

# New Model Mappings
# Heavy Lifters: High Context, High Reasoning
HEAVY_LIFTER_MODEL = "google/gemini-3-pro-high"

# Specialists: High Speed, Low Latency
SPECIALIST_MODEL = "google/gemini-3-flash"

AGENT_MAPPING = {
    # Core Orchestration & Research
    "Sisyphus": HEAVY_LIFTER_MODEL,
    "librarian": HEAVY_LIFTER_MODEL,
    "explore": HEAVY_LIFTER_MODEL,
    "oracle": HEAVY_LIFTER_MODEL,
    
    # Task Specialists
    "frontend-ui-ux-engineer": SPECIALIST_MODEL,
    "document-writer": SPECIALIST_MODEL,
    "multimodal-looker": SPECIALIST_MODEL
}

def main():
    if not CONFIG_PATH.exists():
        print(f"Config file not found at {CONFIG_PATH}")
        return

    # 1. Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = CONFIG_PATH.with_suffix(f".backup_{timestamp}.json")
    shutil.copy2(CONFIG_PATH, backup_path)
    print(f"Backed up config to {backup_path}")

    try:
        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return

    # 2. Update Agents
    if "agents" not in data:
        data["agents"] = {}

    print("\nUpdating Agents:")
    for agent, new_model in AGENT_MAPPING.items():
        old_model = data["agents"].get(agent, {}).get("model", "unknown")
        
        # Create agent entry if missing
        if agent not in data["agents"]:
            data["agents"][agent] = {}
            
        data["agents"][agent]["model"] = new_model
        print(f"  {agent}: {old_model} -> {new_model}")

    # 3. Write back
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nSuccessfully updated {CONFIG_PATH}")

if __name__ == "__main__":
    main()
