import json
import os
import numpy as np
import faiss
import config
from groq import Groq
from sentence_transformers import SentenceTransformer

_embedder = None
_index = None
_knowledge = []

def _load_resources():
    global _embedder, _index, _knowledge
    if _embedder is None:
        _embedder = SentenceTransformer(config.TEXT_EMBED_MODEL)
    knowledge_path = "data/design_knowledge.json"
    index_path = os.path.join(config.FAISS_INDEX_PATH, "knowledge.index")
    if _index is None:
        if os.path.exists(index_path) and os.path.exists(knowledge_path):
            _index = faiss.read_index(index_path)
            with open(knowledge_path, "r") as f:
                _knowledge = json.load(f)
        else:
            _knowledge = []

def get_design_advice(query: str, room_type: str, style: str) -> str:
    if not config.GROQ_API_KEY:
        return "GROQ_API_KEY not configured."
    try:
        _load_resources()
        client = Groq(api_key=config.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert interior designer."},
                {"role": "user", "content": f"Room: {room_type}, Style: {style}\nQuery: {query}"}
            ],
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate advice: {e}"

class RAGAssistant:
    """Wrapper class for backward compatibility."""
    def __init__(self):
        pass
    
    def explain_design(self, user_prompt: str, style: str, room_type: str, products: list) -> str:
        return get_design_advice("Explain this design", room_type, style)
    
    def chat(self, message: str, history: list, design_context: dict) -> str:
        return get_design_advice(message, design_context.get("room_type", "Living Room"), design_context.get("style", "Modern"))