import json
import os
import sys
import pickle
import numpy as np
import chromadb
from chromadb.config import Settings
import faiss

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from core.clip_embedder import CLIPEmbedder
from sentence_transformers import SentenceTransformer


def seed_products():
    """Seed furniture products into ChromaDB vector database."""
    print("Loading products from JSON...")
    
    try:
        with open("data/products.json", "r") as f:
            products = json.load(f)
    except Exception as e:
        print(f"Error loading products.json: {e}")
        return
    
    print(f"Loaded {len(products)} products")
    
    print("Initializing ChromaDB...")
    os.makedirs(config.CHROMA_PATH, exist_ok=True)
    
    try:
        client = chromadb.Client(Settings(persist_directory=config.CHROMA_PATH))
        
        try:
            collection = client.get_collection("furniture_products")
            client.delete_collection("furniture_products")
        except:
            pass
        
        collection = client.create_collection(
            "furniture_products",
            metadata={"description": "Furniture product catalog for interior design"}
        )
    except Exception as e:
        print(f"Error initializing ChromaDB: {e}")
        return
    
    print("Initializing CLIP embedder...")
    try:
        clip_embedder = CLIPEmbedder()
    except Exception as e:
        print(f"Error initializing CLIP: {e}")
        print("Falling back to text-only embeddings")
        clip_embedder = None
    
    print("Embedding and indexing products...")
    for i, product in enumerate(products):
        product_id = product.get("id", f"prod_{i+1:03d}")
        
        rich_text = f"{product['name']}, {product['style']} style, {product['material']}, {product['color']}, {product['description']}"
        
        metadata = {
            "name": product["name"],
            "category": product["category"],
            "style": product["style"],
            "price": product["price"],
            "material": product["material"],
            "color": product["color"],
            "brand": product["brand"],
            "image_search_query": product["image_search_query"],
            "purchase_url": product["purchase_url"]
        }
        
        if clip_embedder:
            try:
                embedding = clip_embedder.embed_product_description(product)
                embedding = [float(x) for x in embedding]
            except Exception as e:
                print(f"Error embedding product {product_id}: {e}")
                embedding = None
        else:
            embedding = None
        
        try:
            collection.add(
                ids=[product_id],
                embeddings=[embedding] if embedding else None,
                documents=[rich_text],
                metadatas=[metadata]
            )
        except Exception as e:
            print(f"Error adding product {product_id}: {e}")
        
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{len(products)} products indexed")
    
    print(f"Seeding complete. {len(products)} products indexed.")


def seed_knowledge():
    """Build FAISS index for design knowledge base."""
    print("Loading design knowledge...")
    
    try:
        with open("data/design_knowledge.json", "r") as f:
            knowledge = json.load(f)
    except Exception as e:
        print(f"Error loading design_knowledge.json: {e}")
        return
    
    print(f"Loaded {len(knowledge)} design principles")
    
    print("Building FAISS index...")
    
    try:
        text_model = SentenceTransformer(config.TEXT_EMBED_MODEL)
    except Exception as e:
        print(f"Error loading sentence transformer: {e}")
        return
    
    contents = [item["content"] for item in knowledge]
    
    try:
        embeddings = text_model.encode(contents)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    except Exception as e:
        print(f"Error encoding knowledge: {e}")
        return
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype('float32'))
    
    print("Saving FAISS index...")
    os.makedirs(config.FAISS_INDEX_PATH, exist_ok=True)
    
    try:
        faiss.write_index(index, os.path.join(config.FAISS_INDEX_PATH, "index.faiss"))
        with open(os.path.join(config.FAISS_INDEX_PATH, "knowledge.pkl"), "wb") as f:
            pickle.dump(knowledge, f)
    except Exception as e:
        print(f"Error saving FAISS index: {e}")
        return
    
    print(f"Knowledge base ready. {len(knowledge)} principles indexed.")


if __name__ == "__main__":
    print("=" * 50)
    print("Seeding Product Catalog and Knowledge Base")
    print("=" * 50)
    print()
    
    seed_products()
    print()
    
    seed_knowledge()
    print()
    
    print("=" * 50)
    print("Seeding Complete!")
    print("=" * 50)