import config
from core.product_retriever import ProductRetriever


ROOM_CATEGORIES = {
    "Living Room": ["sofa", "coffee_table", "tv_unit", "accent_chair", "lighting"],
    "Bedroom": ["bed", "wardrobe", "study_desk", "lighting"],
    "Kitchen": ["dining_table", "accent_chair", "lighting"],
    "Dining Room": ["dining_table", "accent_chair", "lighting"],
    "Home Office": ["study_desk", "bookshelf", "accent_chair", "lighting"],
    "Bathroom": ["lighting", "accent_chair"]
}


class BudgetOptimizer:
    def __init__(self):
        self.retriever = ProductRetriever()
    
    def allocate(self, total_budget: int, room_type: str, _: str, detected_categories: list = None) -> dict:
        room_alloc = config.BUDGET_ALLOCATION.get(room_type, {})
        
        relevant_cats = detected_categories or self.get_room_categories(room_type)
        relevant_cats = [c for c in relevant_cats if c in room_alloc]
        
        if not relevant_cats:
            relevant_cats = list(room_alloc.keys())[:3]
        
        total_ratio = sum(room_alloc.get(cat, 0.1) for cat in relevant_cats)
        
        allocation = {}
        for cat in relevant_cats:
            ratio = room_alloc.get(cat, 0.1)
            normalized = ratio / total_ratio if total_ratio > 0 else 1.0 / len(relevant_cats)
            allocation[cat] = int(total_budget * normalized)
        
        return allocation
    
    def build_cart(self, total_budget: int, room_type: str, style: str, image_path: str = None) -> dict:
        categories = self.get_room_categories(room_type)
        
        if not categories:
            return {"items": [], "total_cost": 0, "total_budget": total_budget, "savings": total_budget, "over_budget": False, "alternatives": {}}
        
        allocation = self.allocate(total_budget, room_type, style, categories)
        
        items = []
        alternatives = {}
        total_cost = 0
        
        for category in categories:
            category_budget = allocation.get(category, 0)
            
            if image_path:
                products = self.retriever.retrieve_by_image(image_path, category=category, max_price=category_budget, n_results=3)
            else:
                products = self.retriever.retrieve_by_style(style=style, category=category, max_price=category_budget, n_results=3)
            
            selected = None
            if products:
                for p in products:
                    if p.get("price", 0) <= category_budget:
                        selected = p
                        break
                if not selected:
                    selected = products[0]
            
            item = {"category": category, "product": selected, "allocated_budget": category_budget, "selected": selected is not None}
            
            if selected:
                total_cost += selected.get("price", 0)
            
            items.append(item)
        
        savings = total_budget - total_cost
        over_budget = total_cost > total_budget
        
        return {
            "items": items,
            "total_cost": total_cost,
            "total_budget": total_budget,
            "savings": savings if not over_budget else 0,
            "over_budget": over_budget,
            "alternatives": alternatives
        }
    
    def get_room_categories(self, room_type: str) -> list:
        return ROOM_CATEGORIES.get(room_type, [])