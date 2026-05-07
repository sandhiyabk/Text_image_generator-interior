from typing import List, Dict, Any
import config

def optimize_budget(products: List[Dict[str, Any]], room_type: str, total_budget: float) -> List[Dict[str, Any]]:
    """
    Allocate budget across furniture categories for the given room type.
    Uses per-room weights from config.BUDGET_ALLOCATION (each room sums to 1.0).
    Falls back to equal split if room_type is not found.
    """
    if not products:
        return []

    allocation = config.BUDGET_ALLOCATION.get(room_type)

    # Fallback: equal split across unique categories present in products
    if not allocation:
        categories = list({p.get("category", "other") for p in products})
        weight = 1.0 / len(categories) if categories else 1.0
        allocation = {cat: weight for cat in categories}

    selected = []
    for product in products:
        category = product.get("category", "other")
        weight = allocation.get(category, 0)
        if weight == 0:
            continue
        category_budget = total_budget * weight
        price = product.get("price", 0)
        if price <= category_budget:
            selected.append({**product, "allocated_budget": category_budget, "within_budget": True})
        else:
            selected.append({**product, "allocated_budget": category_budget, "within_budget": False})

    # Sort: within-budget items first, then by price ascending
    selected.sort(key=lambda p: (not p["within_budget"], p.get("price", 0)))
    return selected

class BudgetOptimizer:
    """Wrapper class for backward compatibility."""
    def __init__(self):
        self.retriever = None
    
    def allocate(self, total_budget, room_type, style, detected_categories=None):
        return {}
    
    def build_cart(self, total_budget: int, room_type: str, style: str, image_path: str = None) -> dict:
        return {
            "items": [],
            "total_cost": 0,
            "total_budget": total_budget,
            "savings": total_budget,
            "over_budget": False,
            "alternatives": {}
        }
    
    def get_room_categories(self, room_type: str) -> list:
        return config.BUDGET_ALLOCATION.get(room_type, []).keys()