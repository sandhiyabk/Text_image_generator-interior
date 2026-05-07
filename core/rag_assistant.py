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
            print("[rag_assistant] FAISS index or knowledge file not found. Run seed_products.py first.")

def get_design_advice(query: str, room_type: str, style: str) -> str:
    """Retrieve relevant design principles and generate advice using Groq."""
    if not config.GROQ_API_KEY:
        return "GROQ_API_KEY not configured."

    try:
        _load_resources()
        context = ""
        if _index is not None and _knowledge:
            query_vec = _embedder.encode([query], normalize_embeddings=True).astype("float32")
            _, indices = _index.search(query_vec, k=3)
            relevant = [_knowledge[i]["principle"] for i in indices[0] if i < len(_knowledge)]
            context = "\n".join(relevant)

        system = (
            "You are an expert interior designer. Use the design principles below to give "
            "practical, specific advice for the user's room. Be concise and actionable.\n\n"
            f"Design Principles:\n{context}"
        )
        user_msg = f"Room: {room_type}, Style: {style}\nQuestion: {query}"

        client = Groq(api_key=config.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=400,
            temperature=0.6,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[rag_assistant] Error: {e}")
        return "Could not generate design advice at this time."