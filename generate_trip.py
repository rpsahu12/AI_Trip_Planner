import torch
from diffusers import StableDiffusionPipeline

# 1. SETUP: Load the model
# We use "runwayml/stable-diffusion-v1-5" (Standard, reliable version)
# float16: Cuts memory usage by 50% without losing much quality
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id, 
    torch_dtype=torch.float16
)

# 2. OPTIMIZATION (The "Cisco/Deep Learning" part)
# enable_model_cpu_offload(): The "Secret Weapon" for 4GB cards.
# It automatically moves the Text Encoder, U-Net, and VAE to the GPU 
# *only* when they are being used, then sends them back to CPU RAM.
pipe.enable_model_cpu_offload()

# enable_attention_slicing(): Slices the computation to save more memory
# at the cost of a tiny bit of speed.
pipe.enable_attention_slicing()

# 3. GENERATION FUNCTION
def generate_location_image(location_name):
    # Prompt Engineering: We add keywords to ensure high quality
    # We use "cyberpunk" style since you likely enjoy that aesthetic
    prompt = f"cyberpunk style travel photography of {location_name}, highly detailed, 8k resolution, cinematic lighting"
    
    # Negative Prompt: What we DON'T want
    negative_prompt = "blurry, low quality, distorted, ugly, text, watermark"

    print(f"Generating image for: {location_name}...")
    
    # Run the diffusion process
    # num_inference_steps=30: Balance between speed and quality (Default is 50)
    image = pipe(
        prompt, 
        negative_prompt=negative_prompt, 
        num_inference_steps=30
    ).images[0]
    
    return image

# 4. RUN IT
if __name__ == "__main__":
    # Test with a location from your Trip Planner
    location = "Kyoto, Japan"
    img = generate_location_image(location)
    
    # Save the result
    file_name = "kyoto_trip_card.png"
    img.save(file_name)
    print(f"Success! Image saved as {file_name}")