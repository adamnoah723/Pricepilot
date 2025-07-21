from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.types import Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime
from .database import Base


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship("Product", back_populates="category")


class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    logo_url = Column(String(500))
    base_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    scraper_config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prices = relationship("Price", back_populates="vendor")
    scraper_runs = relationship("ScraperRun", back_populates="vendor")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    brand = Column(String(100))
    model = Column(String(100))
    category_id = Column(String, ForeignKey("categories.id"))
    description = Column(Text)
    image_url = Column(String(500))
    specifications = Column(JSON)
    popularity_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    prices = relationship("Price", back_populates="product", cascade="all, delete-orphan")


class Price(Base):
    __tablename__ = "prices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"))
    vendor_id = Column(String, ForeignKey("vendors.id"))
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2))
    discount_percentage = Column(Numeric(5, 2))
    stock_status = Column(String(20), default="in_stock")
    product_url = Column(String(500), nullable=False)
    variation_details = Column(JSON)
    last_updated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="prices")
    vendor = relationship("Vendor", back_populates="prices")


class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    price_id = Column(String, ForeignKey("prices.id", ondelete="CASCADE"))
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"))
    vendor_id = Column(String, ForeignKey("vendors.id"))
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2))
    discount_percentage = Column(Numeric(5, 2))
    stock_status = Column(String(20))
    product_url = Column(String(500))
    variation_details = Column(JSON)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    price_record = relationship("Price")
    product = relationship("Product")
    vendor = relationship("Vendor")


class ScraperRun(Base):
    __tablename__ = "scraper_runs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    vendor_id = Column(String, ForeignKey("vendors.id"))
    status = Column(String(20), nullable=False)
    products_scraped = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    duration_seconds = Column(Integer)
    error_details = Column(JSON)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    vendor = relationship("Vendor", back_populates="scraper_runs")