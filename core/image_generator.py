import os
import requests
import replicate
from datetime import datetime
from PIL import Image
import config


class ImageGenerator:
    def __init__(self):
        self.client = None
        if config.REPLICATE_API_TOKEN and config.REPLICATE_API_TOKEN != "your_replicate_api_token_here":
            replicate.api.token = config.REPLICATE_API_TOKEN
            self.client = replicate
    
    def generate(self, optimized_prompt: str, negative_prompt: str = None) -> str:
        """Generate room design image using Replicate SDXL."""
        if not self.client:
            return self._fallback_generate(optimized_prompt)
        
        default_negative = "blurry, low quality, cartoon, anime, distorted, watermark, text, ugly, deformed, bad anatomy"
        
        try:
            output = self.client.run(
                config.SDXL_MODEL,
                input={
                    "prompt": optimized_prompt,
                    "negative_prompt": negative_prompt or default_negative,
                    "width": 1024,
                    "height": 768,
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5,
                    "num_outputs": 1
                }
            )
            
            if output and len(output) > 0:
                image_url = output[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"room_design_{timestamp}.png"
                return self.save_image(image_url, filename)
            
            return self._fallback_generate(optimized_prompt)
            
        except Exception as e:
            return self._fallback_generate(optimized_prompt)
    
    def _fallback_generate(self, optimized_prompt: str) -> str:
        """Return placeholder image when API not available."""
        return "https://placehold.co/1024x768/e8d5b7/8B4513?text=Room+Design+Preview"
    
    def save_image(self, image_url: str, filename: str) -> str:
        """Download image from URL and save to outputs folder."""
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                os.makedirs(config.OUTPUTS_PATH, exist_ok=True)
                filepath = os.path.join(config.OUTPUTS_PATH, filename)
                
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                return filepath
        except Exception:
            pass
        
        return image_url