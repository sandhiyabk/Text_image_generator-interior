from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    designs = relationship("Design", back_populates="user")


class Design(Base):
    __tablename__ = "designs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    optimized_prompt = Column(Text)
    style = Column(String(100))
    room_type = Column(String(100))
    budget = Column(Integer)
    image_path = Column(String(500))
    total_cost = Column(Integer)
    design_explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="designs")
    cart_items = relationship("CartItem", back_populates="design", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True)
    design_id = Column(Integer, ForeignKey("designs.id"), nullable=False)
    product_id = Column(String(50))
    product_name = Column(String(255))
    category = Column(String(100))
    price = Column(Integer)
    allocated_budget = Column(Integer)
    image_search_query = Column(String(255))
    purchase_url = Column(String(500))
    
    design = relationship("Design", back_populates="cart_items")