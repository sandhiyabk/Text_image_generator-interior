import config
from core.product_retriever import ProductRetriever


ROOM_CATEGORIES = {
    "Living Room": ["sofa", "coffee_table", "tv_unit", "bookshelf", "lighting", "accent_chair"],
    "Bedroom": ["bed", "wardrobe", "study_desk", "lighting"],
    "Kitchen": ["dining_table", "lighting"],
    "Dining Room": ["dining_table", "accent_chair", "lighting"],
    "Home Office": ["study_desk", "bookshelf", "accent_chair", "lighting"],
    "Bathroom": []
}


class BudgetOptimizer:
    def __init__(self):
        self.retriever = ProductRetriever()
    
    def allocate(self, total_budget: int, room_type: str, style: str, detected_categories: list[str]) -> dict:
        """Allocate budget across relevant furniture categories."""
        relevant_cats = detected_categories or self.get_room_categories(room_type)
        
        relevant_cats = [c for c in relevant_cats if c in config.BUDGET_ALLOCATION]
        
        if not relevant_cats:
            relevant_cats = list(config.BUDGET_ALLOCATION.keys())[:3]
        
        total_ratio = sum(config.BUDGET_ALLOCATION.get(cat, 0.1) for cat in relevant_cats)
        
        allocation = {}
        for cat in relevant_cats:
            ratio = config.BUDGET_ALLOCATION.get(cat, 0.1)
            normalized_ratio = ratio / total_ratio if total_ratio > 0 else 1.0 / len(relevant_cats)
            allocation[cat] = int(total_budget * normalized_ratio)
        
        return allocation
    
    def build_cart(self, total_budget: int, room_type: str, style: str, image_path: str = None) -> dict:
        """Build shopping cart with recommended products within budget."""
        categories = self.get_room_categories(room_type)
        
        if not categories:
            return self._empty_cart(total_budget)
        
        allocation = self.allocate(total_budget, room_type, style, categories)
        
        items = []
        alternatives = {}
        total_cost = 0
        
        for category in categories:
            category_budget = allocation.get(category, 0)
            
            if image_path:
                products = self.retriever.retrieve_by_image(
                    image_path,
                    category=category,
                    max_price=category_budget,
                    n_results=3
                )
            else:
                products = self.retriever.retrieve_by_style(
                    style=style,
                    category=category,
                    max_price=category_budget,
                    n_results=3
                )
            
            selected_product = None
            if products:
                for p in products:
                    if p.get("price", 0) <= category_budget:
                        selected_product = p
                        break
                
                if not selected_product and products:
                    selected_product = products[0]
            
            item = {
                "product": selected_product,
                "allocated_budget": category_budget,
                "selected": selected_product is not None
            }
            
            if selected_product:
                if selected_product.get("price", 0) > category_budget:
                    cheaper = self.retriever.get_cheaper_alternative(selected_product, category_budget)
                    if cheaper:
                        alternatives[category] = cheaper[0] if cheaper else None
                
                total_cost += selected_product.get("price", 0)
            
            items.append(item)
        
        savings = total_budget - total_cost
        over_budget = total_cost > total_budget
        
        if over_budget and items:
            items, total_cost, alternatives = self._adjust_for_budget(
                items, total_budget, total_cost, alternatives
            )
        
        return {
            "items": items,
            "total_cost": total_cost,
            "total_budget": total_budget,
            "savings": savings if not over_budget else 0,
            "over_budget": over_budget,
            "alternatives": alternatives
        }
    
    def _adjust_for_budget(self, items: list, budget: int, total_cost: int, alternatives: dict) -> tuple:
        """Adjust cart to fit within budget by finding cheaper alternatives."""
        excess = total_cost - budget
        new_items = []
        new_cost = total_cost
        
        for item in items:
            product = item.get("product")
            category_budget = item.get("allocated_budget")
            
            if product and product.get("price", 0) > category_budget:
                alt = alternatives.get(item.get("category"))
                if alt and alt.get("price", 0) < product.get("price", 0):
                    new_cost -= product.get("price", 0)
                    new_cost += alt.get("price", 0)
                    item = item.copy()
                    item["product"] = alt
                    
                    if new_cost <= budget:
                        break
            
            new_items.append(item)
        
        return new_items, new_cost, alternatives
    
    def _empty_cart(self, budget: int) -> dict:
        """Return empty cart structure."""
        return {
            "items": [],
            "total_cost": 0,
            "total_budget": budget,
            "savings": budget,
            "over_budget": False,
            "alternatives": {}
        }
    
    def get_room_categories(self, room_type: str) -> list[str]:
        """Get relevant furniture categories for room type."""
        return ROOM_CATEGORIES.get(room_type, [])