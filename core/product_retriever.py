import chromadb
from chromadb.config import Settings
import json
import os
import config
from core.clip_embedder import CLIPEmbedder


FALLBACK_PRODUCTS = {
    "sofa": [
        {"id": "fb_001", "name": "Comfy 3-Seater Sofa", "category": "sofa", "style": "Modern", "price": 35000, "brand": "Nilkamal", "material": "Fabric", "color": "Grey", "purchase_url": "https://example.com"},
        {"id": "fb_002", "name": "Classic 2-Seater", "category": "sofa", "style": "Modern", "price": 25000, "brand": "Nilkamal", "material": "Fabric", "color": "Beige", "purchase_url": "https://example.com"},
        {"id": "fb_003", "name": "Executive Sofa", "category": "sofa", "style": "Modern", "price": 55000, "brand": "Nilkamal", "material": "Leather", "color": "Brown", "purchase_url": "https://example.com"}
    ],
    "bed": [
        {"id": "fb_004", "name": "Queen Size Platform Bed", "category": "bed", "style": "Modern", "price": 28000, "brand": "Nilkamal", "material": "Engineered Wood", "color": "Walnut", "purchase_url": "https://example.com"},
        {"id": "fb_005", "name": "Standard Double Bed", "category": "bed", "style": "Modern", "price": 22000, "brand": "Nilkamal", "material": "Engineered Wood", "color": "White", "purchase_url": "https://example.com"},
        {"id": "fb_006", "name": "Premium King Bed", "category": "bed", "style": "Luxury", "price": 65000, "brand": "Godrej Interio", "material": "Wood", "color": "Brown", "purchase_url": "https://example.com"}
    ],
    "dining_table": [
        {"id": "fb_007", "name": "4-Seater Dining Table", "category": "dining_table", "style": "Modern", "price": 25000, "brand": "Nilkamal", "material": "MDF", "color": "Oak", "purchase_url": "https://example.com"},
        {"id": "fb_008", "name": "Extendable Dining Set", "category": "dining_table", "style": "Modern", "price": 35000, "brand": "Nilkamal", "material": "Wood", "color": "White", "purchase_url": "https://example.com"},
        {"id": "fb_009", "name": "Luxury Dining Table", "category": "dining_table", "style": "Luxury", "price": 85000, "brand": "HomeTown", "material": "Wood", "color": "Walnut", "purchase_url": "https://example.com"}
    ],
    "wardrobe": [
        {"id": "fb_010", "name": "2-Door Wardrobe", "category": "wardrobe", "style": "Modern", "price": 22000, "brand": "Nilkamal", "material": "Engineered Wood", "color": "White", "purchase_url": "https://example.com"},
        {"id": "fb_011", "name": "Sliding Wardrobe", "category": "wardrobe", "style": "Modern", "price": 32000, "brand": "Nilkamal", "material": "MDF", "color": "Grey", "purchase_url": "https://example.com"},
        {"id": "fb_012", "name": "Premium Wardrobe", "category": "wardrobe", "style": "Luxury", "price": 85000, "brand": "Godrej Interio", "material": "Wood", "color": "Walnut", "purchase_url": "https://example.com"}
    ],
    "coffee_table": [
        {"id": "fb_013", "name": "Modern Coffee Table", "category": "coffee_table", "style": "Modern", "price": 5500, "brand": "Nilkamal", "material": "MDF", "color": "Black", "purchase_url": "https://example.com"},
        {"id": "fb_014", "name": "Wooden Coffee Table", "category": "coffee_table", "style": "Modern", "price": 8500, "brand": "Nilkamal", "material": "Wood", "color": "Oak", "purchase_url": "https://example.com"},
        {"id": "fb_015", "name": "Marble Top Table", "category": "coffee_table", "style": "Luxury", "price": 25000, "brand": "HomeTown", "material": "Marble", "color": "White", "purchase_url": "https://example.com"}
    ],
    "bookshelf": [
        {"id": "fb_016", "name": "5-Tier Bookshelf", "category": "bookshelf", "style": "Modern", "price": 8500, "brand": "Nilkamal", "material": "Engineered Wood", "color": "White", "purchase_url": "https://example.com"},
        {"id": "fb_017", "name": "Open Display Unit", "category": "bookshelf", "style": "Modern", "price": 12000, "brand": "Nilkamal", "material": "Wood", "color": "Walnut", "purchase_url": "https://example.com"},
        {"id": "fb_018", "name": "Classic Library Shelf", "category": "bookshelf", "style": "Luxury", "price": 45000, "brand": "HomeTown", "material": "Teak", "color": "Brown", "purchase_url": "https://example.com"}
    ],
    "tv_unit": [
        {"id": "fb_019", "name": "Wall-Mounted TV Unit", "category": "tv_unit", "style": "Modern", "price": 8500, "brand": "Nilkamal", "material": "MDF", "color": "White", "purchase_url": "https://example.com"},
        {"id": "fb_020", "name": "TV Cabinet", "category": "tv_unit", "style": "Modern", "price": 15000, "brand": "Nilkamal", "material": "Wood", "color": "Walnut", "purchase_url": "https://example.com"},
        {"id": "fb_021", "name": "Luxury Media Console", "category": "tv_unit", "style": "Luxury", "price": 55000, "brand": "HomeTown", "material": "Wood", "color": "Brown", "purchase_url": "https://example.com"}
    ],
    "study_desk": [
        {"id": "fb_022", "name": "Compact Study Desk", "category": "study_desk", "style": "Modern", "price": 8000, "brand": "Nilkamal", "material": "Engineered Wood", "color": "White", "purchase_url": "https://example.com"},
        {"id": "fb_023", "name": "Wooden Work Desk", "category": "study_desk", "style": "Modern", "price": 15000, "brand": "Nilkamal", "material": "Wood", "color": "Oak", "purchase_url": "https://example.com"},
        {"id": "fb_024", "name": "Executive Desk", "category": "study_desk", "style": "Luxury", "price": 55000, "brand": "Godrej Interio", "material": "Teak", "color": "Brown", "purchase_url": "https://example.com"}
    ],
    "accent_chair": [
        {"id": "fb_025", "name": "Modern Accent Chair", "category": "accent_chair", "style": "Modern", "price": 8000, "brand": "Nilkamal", "material": "Fabric", "color": "Grey", "purchase_url": "https://example.com"},
        {"id": "fb_026", "name": "Comfy Armchair", "category": "accent_chair", "style": "Modern", "price": 12000, "brand": "Nilkamal", "material": "Fabric", "color": "Blue", "purchase_url": "https://example.com"},
        {"id": "fb_027", "name": "Premium Lounge Chair", "category": "accent_chair", "style": "Luxury", "price": 35000, "brand": "HomeTown", "material": "Leather", "color": "Brown", "purchase_url": "https://example.com"}
    ],
    "lighting": [
        {"id": "fb_028", "name": "Modern Floor Lamp", "category": "lighting", "style": "Modern", "price": 2500, "brand": "Nilkamal", "material": "Metal", "color": "White", "purchase_url": "https://example.com"},
        {"id": "fb_029", "name": "Pendant Light", "category": "lighting", "style": "Modern", "price": 1800, "brand": "Nilkamal", "material": "Glass", "color": "White", "purchase_url": "https://example.com"},
        {"id": "fb_030", "name": "Crystal Chandelier", "category": "lighting", "style": "Luxury", "price": 65000, "brand": "HomeTown", "material": "Crystal", "color": "Clear", "purchase_url": "https://example.com"}
    ]
}


class ProductRetriever:
    def __init__(self):
        self.collection = None
        self.clip_embedder = CLIPEmbedder()
        self._init_chroma()
    
    def _init_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            os.makedirs(config.CHROMA_PATH, exist_ok=True)
            client = chromadb.Client(Settings(persist_directory=config.CHROMA_PATH))
            
            try:
                self.collection = client.get_collection("furniture_products")
            except:
                self.collection = client.create_collection("furniture_products", metadata={"description": "Furniture product catalog"})
            
            if self.collection.count() == 0:
                self.collection = None
        except Exception:
            self.collection = None
    
    def retrieve_by_image(self, image_path: str, category: str = None, max_price: int = None, n_results: int = 5) -> list[dict]:
        """Find products visually similar to generated room image."""
        if self.collection is None:
            return self._get_fallbacks(category, n_results)
        
        try:
            image_embedding = self.clip_embedder.embed_image(image_path)
            
            where_filter = {}
            if category:
                where_filter["category"] = category
            if max_price:
                where_filter["$and"] = [{"price": {"$lte": max_price}}]
            
            results = self.collection.query(
                query_embeddings=[image_embedding],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            return self._format_chroma_results(results)
            
        except Exception:
            return self._get_fallbacks(category, n_results)
    
    def retrieve_by_style(self, style: str, category: str, max_price: int, n_results: int = 3) -> list[dict]:
        """Find products by style and category."""
        if self.collection is None:
            return self._get_fallbacks(category, n_results)
        
        try:
            query_text = f"{style} {category} furniture"
            text_embedding = self.clip_embedder.embed_text(query_text)
            
            where_filter = {"category": category} if category else {}
            if max_price:
                where_filter["price"] = {"$lte": max_price}
            
            results = self.collection.query(
                query_embeddings=[text_embedding],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            return self._format_chroma_results(results)
            
        except Exception:
            return self._get_fallbacks(category, n_results)
    
    def get_cheaper_alternative(self, product: dict, budget: int) -> dict | None:
        """Find visually similar but cheaper product in same category."""
        if self.collection is None:
            return None
        
        category = product.get("category")
        if not category:
            return None
        
        return self.retrieve_by_style(
            style=product.get("style", "Modern"),
            category=category,
            max_price=budget,
            n_results=1
        )
    
    def _format_chroma_results(self, results: dict) -> list[dict]:
        """Format ChromaDB results into product dicts."""
        products = []
        
        if not results or not results.get("ids") or not results["ids"][0]:
            return []
        
        ids = results["ids"][0]
        documents = results["documents"][0] if results.get("documents") else [""]
        metadatas = results["metadatas"][0] if results.get("metadatas") else [{}]
        distances = results["distances"][0] if results.get("distances") else [1.0]
        
        for i, doc_id in enumerate(ids):
            product = metadatas[i].copy() if i < len(metadatas) else {}
            product["id"] = doc_id
            product["description"] = documents[i] if i < len(documents) else ""
            product["similarity"] = 1 - distances[i] if i < len(distances) else 0.0
            products.append(product)
        
        return products
    
    def _get_fallbacks(self, category: str, n_results: int) -> list[dict]:
        """Return fallback products when ChromaDB is unavailable."""
        if category and category in FALLBACK_PRODUCTS:
            return FALLBACK_PRODUCTS[category][:n_results]
        
        all_products = []
        for cat_products in FALLBACK_PRODUCTS.values():
            all_products.extend(cat_products)
        return all_products[:n_results]