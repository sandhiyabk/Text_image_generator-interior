import pickle
import os
import numpy as np
import faiss
import json
import anthropic
from sentence_transformers import SentenceTransformer
import config


FALLBACK_EXPLANATION = """
Based on your {room_type} design in {style} style, here's an overview:

**Why This Style Works for Your Space:**
The {style} aesthetic brings timeless appeal to any room. It emphasizes clean lines and thoughtful curation, creating a space that feels both functional and visually appealing.

**Product Recommendations:**
Your recommended furniture pieces have been selected to match this style. Each piece complements the overall aesthetic while staying within your budget.

**Actionable Tips:**
1. Focus on lighting - the right ambient lighting can transform the space
2. Add textiles ( throws, cushions) to soften hard surfaces
3. Keep surfaces relatively clear to maintain the clean aesthetic
"""


class RAGAssistant:
    def __init__(self):
        self.faiss_index = None
        self.knowledge_list = []
        self.text_model = None
        self.client = None
        self._init_faiss()
        self._init_claude()
    
    def _init_faiss(self):
        """Initialize FAISS index for design knowledge."""
        index_path = os.path.join(config.FAISS_INDEX_PATH, "index.faiss")
        meta_path = os.path.join(config.FAISS_INDEX_PATH, "knowledge.pkl")
        
        try:
            if os.path.exists(index_path) and os.path.exists(meta_path):
                self.faiss_index = faiss.read_index(index_path)
                with open(meta_path, "rb") as f:
                    self.knowledge_list = pickle.load(f)
        except Exception:
            pass
        
        if not self.knowledge_list:
            self._load_json_knowledge()
    
    def _load_json_knowledge(self):
        """Load design knowledge from JSON if FAISS not available."""
        try:
            with open("data/design_knowledge.json", "r") as f:
                self.knowledge_list = json.load(f)
        except Exception:
            self.knowledge_list = []
    
    def _init_claude(self):
        """Initialize Anthropic client."""
        if config.ANTHROPIC_API_KEY and config.ANTHROPIC_API_KEY != "your_anthropic_api_key_here":
            self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def retrieve_principles(self, query: str, k: int = 3) -> list[dict]:
        """Find design principles relevant to the query."""
        if not self.knowledge_list:
            return []
        
        if self.faiss_index is not None and self.text_model is not None:
            try:
                query_embedding = self.text_model.encode([query])
                query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
                
                distances, indices = self.faiss_index.search(query_embedding.astype('float32'), k)
                
                results = []
                for idx in indices[0]:
                    if 0 <= idx < len(self.knowledge_list):
                        results.append(self.knowledge_list[idx])
                return results
            except Exception:
                pass
        
        query_lower = query.lower()
        scored = []
        for item in self.knowledge_list:
            score = 0
            tags = item.get("tags", [])
            principle = item.get("principle", "").lower()
            content = item.get("content", "").lower()
            
            for tag in tags:
                if tag.lower() in query_lower:
                    score += 2
            
            if any(word in principle for word in query_lower.split()):
                score += 3
            if any(word in content for word in query_lower.split()):
                score += 1
            
            scored.append((score, item))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:k]]
    
    def explain_design(self, user_prompt: str, style: str, room_type: str, products: list[dict]) -> str:
        """Generate design explanation using RAG and Claude."""
        query = f"{style} {room_type}"
        principles = self.retrieve_principles(query, k=3)
        
        if not self.client:
            return self._fallback_explanation(style, room_type, products)
        
        principles_text = "\n\n".join([
            f"- **{p['principle']}**: {p['content']}" for p in principles
        ]) if principles else "No design principles found."
        
        products_text = "\n\n".join([
            f"- {p.get('name', 'Unnamed')} by {p.get('brand', 'Unknown')} - ₹{p.get('price', 0):,}" +
            f" ({p.get('style', 'N/A')} style)"
            for p in products if p
        ]) if products else "No products selected."
        
        system_prompt = """You are an expert interior designer. Explain design decisions clearly and warmly.
Help the user understand why certain choices were made and how they work together.
Reference specific design principles where relevant. Keep explanations practical and actionable."""

        user_message = f"""Design Request:
- Room: {room_type}
- Style: {style}
- User's description: {user_prompt}

Recommended Products:
{products_text}

Design Principles Reference:
{principles_text}

Please explain:
1. Why this {style} style works well for a {room_type}
2. How the selected products complement each other
3. 1-2 actionable tips to enhance the space
4. Reference the design principles naturally in your response

Keep it warm, conversational, and practical (2-3 paragraphs)."""

        try:
            response = self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=600,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text
        except Exception:
            return self._fallback_explanation(style, room_type, products)
    
    def _fallback_explanation(self, style: str, room_type: str, products: list[dict]) -> str:
        """Fallback explanation without API."""
        return FALLBACK_EXPLANATION.format(
            style=style,
            room_type=room_type,
            products_count=len([p for p in products if p])
        )
    
    def chat(self, message: str, history: list, design_context: dict) -> str:
        """Handle conversational redesign chat."""
        if not self.client:
            return "Please add your Anthropic API key to .env to enable AI chat features."
        
        history_messages = []
        for msg in history[-5:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_messages.append({"role": role, "content": content})
        
        system_prompt = f"""You are an interior design expert helping refine a room design.
The current design has:
- Style: {design_context.get('style', 'Modern')}
- Room Type: {design_context.get('room_type', 'Living Room')}
- Budget: ₹{design_context.get('budget', 50000):,}

Be helpful, conversational, and practical. When asked to make changes, explain what you're adjusting and why."""

        history_messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=400,
                system=system_prompt,
                messages=history_messages
            )
            return response.content[0].text
        except Exception:
            return "I'm here to help refine your design. What would you like to change?"