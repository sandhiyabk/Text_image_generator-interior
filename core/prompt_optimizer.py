import streamlit as st
from groq import Groq
import config


STYLE_KEYWORDS = {
    "Modern": "clean lines, contemporary, sleek, minimalist furniture, modern architecture",
    "Scandinavian": "clean lines, white walls, natural wood, hygge, functional simplicity, bright airy space",
    "Bohemian": "layered textures, eclectic, plants, warm earth tones, global influences, artistic, cozy",
    "Industrial": "exposed brick, metal beams, raw materials, urban, edgy, concrete, vintage touches",
    "Japandi": "wabi-sabi, natural materials, muted earth tones, organic textures, zen, simple, minimalist Japanese influence",
    "Luxury": "elegant, premium materials, rich colors, sophisticated, opulent, statement pieces, refined",
    "Minimalist": "simple, uncluttered, neutral colors, functional, essential only, clean spaces",
    "Rustic": "natural wood, warm, cozy, country, farmhouse, earthy, weathered, authentic"
}


class PromptOptimizer:
    def __init__(self):
        self.client = None
        if config.GROQ_API_KEY:
            self.client = Groq(api_key=config.GROQ_API_KEY)
    
    def optimize(self, user_prompt: str, room_type: str, style: str, color_palette: str = None) -> str:
        if not self.client:
            return self._fallback_optimize(user_prompt, room_type, style)
        
        style_keywords = STYLE_KEYWORDS.get(style, "")
        
        system_prompt = """You are an expert in interior design and AI image generation. Convert vague room descriptions into detailed SDXL prompts.

The optimized prompt should:
- Be photorealistic and architectural rendering style
- Include interior photography lighting and composition
- Be detailed enough for SDXL to generate high-quality images
- Keep to one paragraph, under 200 words
- Output ONLY the optimized prompt, no explanation"""

        color_info = f" with {color_palette} color palette" if color_palette else ""
        
        user_message = f"""Room description: {user_prompt}
Room type: {room_type}
Style: {style}
{color_info}

Style keywords: {style_keywords}

Generate a detailed SDXL prompt."""

        try:
            response = self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error: {e}")
            return self._fallback_optimize(user_prompt, room_type, style)
    
    def _fallback_optimize(self, user_prompt: str, room_type: str, style: str) -> str:
        style_keywords = STYLE_KEYWORDS.get(style, "")
        return f"Photorealistic interior of a {style.lower()} {room_type.lower()}, {user_prompt}. {style_keywords}. Natural lighting, 8k quality."
    
    def detect_style(self, user_prompt: str) -> str:
        if not self.client:
            return "Modern"
        
        try:
            response = self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "Select ONE style: Modern, Scandinavian, Bohemian, Industrial, Japandi, Luxury, Minimalist, Rustic"},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=50
            )
            detected = response.choices[0].message.content.strip()
            if detected in config.STYLES:
                return detected
            return "Modern"
        except Exception:
            return "Modern"