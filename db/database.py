import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from db.models import Base, Design, CartItem, User


DB_PATH = "interior_copilot.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Initialize database and create all tables."""
    Base.metadata.create_all(engine)


@contextmanager
def get_db():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def save_design(design_data: dict, cart_items: list[dict]) -> Design:
    """Save a design with its cart items to the database."""
    with get_db() as session:
        design = Design(
            user_id=design_data.get("user_id"),
            prompt=design_data["prompt"],
            optimized_prompt=design_data.get("optimized_prompt"),
            style=design_data.get("style"),
            room_type=design_data.get("room_type"),
            budget=design_data.get("budget"),
            image_path=design_data.get("image_path"),
            total_cost=design_data.get("total_cost"),
            design_explanation=design_data.get("design_explanation")
        )
        session.add(design)
        session.flush()
        
        for item in cart_items:
            cart_item = CartItem(
                design_id=design.id,
                product_id=item.get("product_id"),
                product_name=item.get("product_name"),
                category=item.get("category"),
                price=item.get("price"),
                allocated_budget=item.get("allocated_budget"),
                image_search_query=item.get("image_search_query"),
                purchase_url=item.get("purchase_url")
            )
            session.add(cart_item)
        
        session.commit()
        return design


def get_all_designs() -> list:
    """Retrieve all designs with their cart items."""
    with get_db() as session:
        designs = session.query(Design).order_by(Design.created_at.desc()).all()
        result = []
        for design in designs:
            cart_items = session.query(CartItem).filter(CartItem.design_id == design.id).all()
            result.append({
                "id": design.id,
                "prompt": design.prompt,
                "optimized_prompt": design.optimized_prompt,
                "style": design.style,
                "room_type": design.room_type,
                "budget": design.budget,
                "image_path": design.image_path,
                "total_cost": design.total_cost,
                "design_explanation": design.design_explanation,
                "created_at": design.created_at,
                "cart_items": [
                    {
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "category": item.category,
                        "price": item.price,
                        "allocated_budget": item.allocated_budget,
                        "image_search_query": item.image_search_query,
                        "purchase_url": item.purchase_url
                    }
                    for item in cart_items
                ]
            })
        return result


def get_design_by_id(design_id: int) -> dict:
    """Retrieve a specific design by ID."""
    with get_db() as session:
        design = session.query(Design).filter(Design.id == design_id).first()
        if not design:
            return None
        
        cart_items = session.query(CartItem).filter(CartItem.design_id == design.id).all()
        
        return {
            "id": design.id,
            "prompt": design.prompt,
            "optimized_prompt": design.optimized_prompt,
            "style": design.style,
            "room_type": design.room_type,
            "budget": design.budget,
            "image_path": design.image_path,
            "total_cost": design.total_cost,
            "design_explanation": design.design_explanation,
            "created_at": design.created_at,
            "cart_items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "category": item.category,
                    "price": item.price,
                    "allocated_budget": item.allocated_budget,
                    "image_search_query": item.image_search_query,
                    "purchase_url": item.purchase_url
                }
                for item in cart_items
            ]
        }


def delete_design(design_id: int) -> bool:
    """Delete a design and its cart items."""
    with get_db() as session:
        design = session.query(Design).filter(Design.id == design_id).first()
        if not design:
            return False
        
        session.delete(design)
        session.commit()
        return True