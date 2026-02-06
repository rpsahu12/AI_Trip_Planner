import os
import requests
import time

class TripVisualizer:
    def __init__(self):
        # We use the API instead of loading the model locally
        # 1. This URL is CORRECT (router.huggingface.co)
        self.api_url = "https://router.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        self.api_key = os.getenv("HF_TOKEN") 
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

        # Retry logic
        for attempt in range(3):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload)
                
                # CASE 1: Success (Image binary data)
                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    return filepath

                # CASE 2: Handle Errors safely
                # We try to parse JSON, but if it fails (because it's raw text), we catch it.
                try:
                    error_data = response.json()
                except:
                    # If response isn't JSON, it's a raw error string (e.g., 503 Service Unavailable)
                    print(f"❌ HF API Raw Error ({response.status_code}): {response.text}")
                    break 

                # CASE 3: Model Loading (Wait and Retry)
                if "estimated_time" in error_data:
                    wait_time = error_data["estimated_time"]
                    print(f"⏳ Model loading... waiting {wait_time:.1f}s")
                    time.sleep(wait_time)
                    continue # Try loop again

                # CASE 4: Actual API Error (Invalid Key, etc.)
                if "error" in error_data:
                    print(f"❌ HF API Error: {error_data['error']}")
                    break

            except Exception as e:
                print(f"⚠️ Connection Exception: {e}")
                break
                
        # If we failed 3 times or broke out of loop, return None instead of Crashing
        print(f"⚠️ Failed to generate image for {location_name}")
        return None