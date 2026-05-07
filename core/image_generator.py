import io
import os
import requests
from datetime import datetime
from PIL import Image
import config

HF_API_URL = f"https://api-inference.huggingface.co/models/{config.HF_IMAGE_MODEL}"

def generate_image(prompt: str, output_filename: str = "design.png") -> str | None:
    """Generate an interior design image using HuggingFace Inference API (free tier)."""
    if not config.HF_TOKEN:
        print("[image_generator] HF_TOKEN not set.")
        return None

    headers = {"Authorization": f"Bearer {config.HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"num_inference_steps": 30, "guidance_scale": 7.5}
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        image = Image.open(io.BytesIO(response.content))
        output_path = os.path.join(config.OUTPUTS_PATH, output_filename)
        image.save(output_path)
        return output_path

    except requests.exceptions.HTTPError as e:
        print(f"[image_generator] HTTP error: {e} — {response.text}")
        return None
    except Exception as e:
        print(f"[image_generator] Unexpected error: {e}")
        return None

class ImageGenerator:
    """Wrapper class for backward compatibility."""
    def __init__(self):
        pass
    
    def generate(self, optimized_prompt: str, negative_prompt: str = None) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"room_design_{timestamp}.png"
        result = generate_image(optimized_prompt, filename)
        if result:
            return result
        return "https://placehold.co/1024x768/e8d5b7/8B4513?text=Room+Design+Preview"