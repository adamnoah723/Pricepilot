from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class CategoryResponse(BaseModel):
    id: str
    name: str
    display_name: str
    
    class Config:
        from_attributes = True


class VendorResponse(BaseModel):
    id: str
    name: str
    display_name: str
    base_url: Optional[str] = None
    logo_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: str
    name: str
    brand: Optional[str] = None
    category_id: Optional[str] = None
    image_url: Optional[str] = None
    best_price: Decimal
    best_vendor_id: str
    popularity_score: int = 0
    match_score: Optional[int] = None
    
    class Config:
        from_attributes = True


class PriceComparisonResponse(BaseModel):
    vendor_id: str
    vendor_name: str
    vendor_logo_url: Optional[str] = None
    price: Decimal
    original_price: Optional[Decimal] = None
    discount_percentage: Optional[float] = None
    stock_status: str
    product_url: str
    is_best_deal: bool
    last_updated: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProductDetailResponse(BaseModel):
    id: str
    name: str
    brand: Optional[str] = None
    category_id: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    price_comparison: List[PriceComparisonResponse]
    best_price: Decimal
    best_vendor_id: str
    popularity_score: int = 0
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    limit: int
    offset: int
    
    class Config:
        from_attributes = True


class ScraperStatusResponse(BaseModel):
    vendor_id: str
    vendor_name: str
    status: str
    last_run_at: Optional[datetime] = None
    products_scraped: int = 0
    errors_count: int = 0
    duration_seconds: Optional[int] = None
    
    class Config:
        from_attributes = True


class AutocompleteResponse(BaseModel):
    suggestions: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True