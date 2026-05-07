import anthropic
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
        if config.ANTHROPIC_API_KEY and config.ANTHROPIC_API_KEY != "your_anthropic_api_key_here":
            self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def optimize(self, user_prompt: str, room_type: str, style: str, color_palette: str = None) -> str:
        """Convert user prompt to detailed SDXL image generation prompt."""
        if not self.client:
            return self._fallback_optimize(user_prompt, room_type, style)
        
        style_keywords = STYLE_KEYWORDS.get(style, "")
        
        system_prompt = """You are an expert in interior design and AI image generation. Your task is to convert 
user's vague room descriptions into detailed, high-quality prompts for Stable Diffusion XL (SDXL) image generation.

The optimized prompt should:
- Be photorealistic and architectural rendering style
- Include interior photography lighting and composition
- Reference specific furniture, materials, and architectural details
- Include the room type and detected style keywords
- Be detailed enough for SDXL to generate high-quality images
- Keep to one paragraph, under 200 words
- Output ONLY the optimized prompt, no explanation or meta-commentary"""

        color_info = f" with {color_palette} color palette" if color_palette else ""
        
        user_message = f"""Room description: {user_prompt}
Room type: {room_type}
Style: {style}
{color_info}

Style keywords to incorporate: {style_keywords}

Generate a detailed SDXL prompt for generating this interior design image."""

        try:
            response = self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=300,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            return self._fallback_optimize(user_prompt, room_type, style)
    
    def _fallback_optimize(self, user_prompt: str, room_type: str, style: str) -> str:
        """Fallback prompt optimization without API."""
        style_keywords = STYLE_KEYWORDS.get(style, "")
        return f"Photorealistic interior photography of a {style.lower()} {room_type.lower()}, {user_prompt}. {style_keywords}. Natural lighting from windows, professional architectural photography, high detail, 8k quality, interior design magazine style."
    
    def detect_style(self, user_prompt: str) -> str:
        """Detect which style best matches the user prompt."""
        if not self.client:
            return "Modern"
        
        system_prompt = """You are an interior design style classifier. Analyze the user's description and select the most appropriate style from this list:
- Modern: Contemporary, sleek, minimal
- Scandinavian: Clean, white, natural wood, functional, bright
- Bohemian: Eclectic, colorful, layered, artistic
- Industrial: Raw, urban, exposed materials, edgy
- Japandi: Japanese + Scandinavian, zen, natural
- Luxury: Elegant, premium, sophisticated
- Minimalist: Simple, uncluttered, essential
- Rustic: Country, warm, natural wood, farmhouse

Respond with just the style name, no explanation."""

        try:
            response = self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=50,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            detected = response.content[0].text.strip()
            if detected in config.STYLES:
                return detected
            return "Modern"
        except Exception:
            return "Modern"