import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import config


class CLIPEmbedder:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained(config.CLIP_MODEL_NAME)
        self.processor = CLIPProcessor.from_pretrained(config.CLIP_MODEL_NAME)
        self.model.to(self.device)
        self.model.eval()
    
    def embed_text(self, text: str) -> list[float]:
        """Generate CLIP text embedding."""
        inputs = self.processor(text=[text], return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy().tolist()[0]
    
    def embed_image(self, image_path: str) -> list[float]:
        """Generate CLIP image embedding."""
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy().tolist()[0]
    
    def embed_product_description(self, product: dict) -> list[float]:
        """Generate rich text embedding for product."""
        rich_text = f"{product['name']}, {product['style']} style, {product['material']}, {product['color']}, {product['description']}"
        return self.embed_text(rich_text)