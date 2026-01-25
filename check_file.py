import os

print(f"Current working directory: {os.getcwd()}")

if os.path.exists("config.yaml"):
    print("✅ SUCCESS: Found config.yaml in the main folder!")
elif os.path.exists("config/config.yaml"):
    print("⚠️ FOUND: config.yaml is inside 'config/' folder (Move it out!)")
else:
    print("❌ ERROR: Cannot find config.yaml anywhere.")