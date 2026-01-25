import yaml
import os

def load_config():
    # 1. Define possible locations for the config file
    possible_paths = [
        "config.yaml",              # Root directory (where you moved it)
        "config/config.yaml",       # Old location
        "../config.yaml",           # One level up
        "AI_Trip_Planner/config.yaml" # Full path check
    ]
    
    # 2. Search for the file
    found_path = None
    for path in possible_paths:
        if os.path.exists(path):
            found_path = path
            print(f"✅ ConfigLoader found file at: {os.path.abspath(path)}")
            break
            
    # 3. If not found, print a loud warning and return None
    if found_path is None:
        print("❌ CRITICAL ERROR: ConfigLoader could not find 'config.yaml'.")
        print(f"   Checked locations: {possible_paths}")
        print(f"   Current Working Directory: {os.getcwd()}")
        return None

    # 4. Load the YAML
    try:
        with open(found_path, "r") as file:
            config = yaml.safe_load(file)
            if not config:
                print("❌ ERROR: config.yaml is empty!")
                return None
            return config
    except Exception as e:
        print(f"❌ ERROR: Could not parse config.yaml: {e}")
        return None