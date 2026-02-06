import os
import requests
import time

class TripVisualizer:
    def __init__(self):
        # We use the API instead of loading the model locally
        self.api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        self.api_key = os.getenv("HF_TOKEN") # <--- You need to set this in .env
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def generate_image(self, location_name, output_dir="static/images"):
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Clean filename
        safe_name = "".join([c for c in location_name if c.isalnum() or c in (' ', '_')]).strip()
        filename = f"{safe_name.replace(' ', '_')}.png"
        filepath = os.path.join(output_dir, filename)

        # Skip if exists (Cache)
        if os.path.exists(filepath):
            return filepath

        payload = {
            "inputs": f"cyberpunk style travel photography of {location_name}, highly detailed, 8k, cinematic lighting",
            "parameters": {"negative_prompt": "blurry, text, low quality"}
        }

        # Retry logic (The API sometimes needs to "wake up")
        for _ in range(3):
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                return filepath
            
            elif "estimated_time" in response.json():
                # If model is loading, wait and try again
                wait_time = response.json()["estimated_time"]
                print(f"⏳ Model loading... waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                print(f"❌ API Error: {response.text}")
                break
                
        raise Exception("Failed to generate image via API")