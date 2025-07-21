from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

from .database import SessionLocal, engine
from .models import Base, Product, Price, Vendor, Category, ScraperRun
from .schemas import (
    ProductResponse, ProductDetailResponse, CategoryResponse, 
    VendorResponse, SearchResponse, PriceComparisonResponse,
    ScraperStatusResponse
)
from .price_service import get_price_service, PriceService
from fuzzywuzzy import fuzz
from sqlalchemy import func, desc, asc

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PricePilot API",
    description="Price comparison API for high-ticket tech items",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3002", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "PricePilot API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "PricePilot API"}

@app.get("/api/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all product categories"""
    categories = db.query(Category).all()
    return categories

@app.get("/api/vendors", response_model=List[VendorResponse])
async def get_vendors(db: Session = Depends(get_db)):
    """Get all vendors"""
    vendors = db.query(Vendor).all()
    return vendors

@app.get("/api/search", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., description="Search query"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """Search products with fuzzy matching and autocomplete"""
    query = db.query(Product).join(Price)
    
    # Filter by category if provided
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    # Get all products for fuzzy matching
    all_products = query.all()
    
    # Perform fuzzy matching
    scored_products = []
    for product in all_products:
        score = fuzz.partial_ratio(q.lower(), product.name.lower())
        if score >= 60:  # Minimum similarity threshold
            scored_products.append((product, score))
    
    # Sort by score (descending) and popularity
    scored_products.sort(key=lambda x: (x[1], x[0].popularity_score), reverse=True)
    
    # Apply pagination
    total = len(scored_products)
    paginated_products = scored_products[offset:offset + limit]
    
    # Convert to response format
    products = []
    for product, score in paginated_products:
        # Get best price for this product
        best_price = db.query(Price).filter(
            Price.product_id == product.id
        ).order_by(Price.price.asc()).first()
        
        if best_price:
            products.append(ProductResponse(
                id=product.id,
                name=product.name,
                brand=product.brand,
                category_id=product.category_id,
                image_url=product.image_url,
                best_price=best_price.price,
                best_vendor_id=best_price.vendor_id,
                popularity_score=product.popularity_score,
                match_score=score
            ))
    
    return SearchResponse(
        products=products,
        total=total,
        limit=limit,
        offset=offset
    )

@app.get("/api/products", response_model=SearchResponse)
async def get_products(
    category_id: Optional[str] = Query(None, description="Filter by category"),
    sort_by: str = Query("popularity", description="Sort by: popularity, price_low, price_high, name"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """Get products with filtering and sorting"""
    query = db.query(Product).join(Price)
    
    # Filter by category if provided
    if category_id:
        # Check if category_id is a name (like "laptops") or an actual ID
        category = db.query(Category).filter(
            (Category.id == category_id) | (Category.name == category_id)
        ).first()
        if category:
            query = query.filter(Product.category_id == category.id)
    
    # Apply sorting
    if sort_by == "popularity":
        query = query.order_by(desc(Product.popularity_score))
    elif sort_by == "price_low":
        # Get minimum price for each product
        subquery = db.query(
            Price.product_id,
            func.min(Price.price).label('min_price')
        ).group_by(Price.product_id).subquery()
        
        query = query.join(subquery, Product.id == subquery.c.product_id)\
                    .order_by(asc(subquery.c.min_price))
    elif sort_by == "price_high":
        # Get minimum price for each product (but sort descending)
        subquery = db.query(
            Price.product_id,
            func.min(Price.price).label('min_price')
        ).group_by(Price.product_id).subquery()
        
        query = query.join(subquery, Product.id == subquery.c.product_id)\
                    .order_by(desc(subquery.c.min_price))
    elif sort_by == "name":
        query = query.order_by(asc(Product.name))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    products = query.offset(offset).limit(limit).all()
    
    # Convert to response format
    product_responses = []
    for product in products:
        # Get best price for this product
        best_price = db.query(Price).filter(
            Price.product_id == product.id
        ).order_by(Price.price.asc()).first()
        
        if best_price:
            product_responses.append(ProductResponse(
                id=product.id,
                name=product.name,
                brand=product.brand,
                category_id=product.category_id,
                image_url=product.image_url,
                best_price=best_price.price,
                best_vendor_id=best_price.vendor_id,
                popularity_score=product.popularity_score
            ))
    
    return SearchResponse(
        products=product_responses,
        total=total,
        limit=limit,
        offset=offset
    )

@app.get("/api/products/{product_id}", response_model=ProductDetailResponse)
async def get_product_detail(product_id: str, db: Session = Depends(get_db)):
    """Get detailed product information with price comparison"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get all prices for this product
    prices = db.query(Price).filter(Price.product_id == product_id).all()
    
    if not prices:
        raise HTTPException(status_code=404, detail="No prices found for this product")
    
    # Get vendors for price comparison
    vendor_ids = [price.vendor_id for price in prices]
    vendors = db.query(Vendor).filter(Vendor.id.in_(vendor_ids)).all()
    vendor_map = {vendor.id: vendor for vendor in vendors}
    
    # Build price comparison data
    price_comparison = []
    best_price = min(prices, key=lambda p: p.price)
    
    for price in prices:
        vendor = vendor_map.get(price.vendor_id)
        if vendor:
            price_comparison.append(PriceComparisonResponse(
                vendor_id=vendor.id,
                vendor_name=vendor.display_name,
                vendor_logo_url=vendor.logo_url,
                price=price.price,
                original_price=price.original_price,
                discount_percentage=price.discount_percentage,
                stock_status=price.stock_status,
                product_url=price.product_url,
                is_best_deal=price.id == best_price.id,
                last_updated=price.last_updated_at
            ))
    
    # Sort by price (best deals first)
    price_comparison.sort(key=lambda x: x.price)
    
    return ProductDetailResponse(
        id=product.id,
        name=product.name,
        brand=product.brand,
        category_id=product.category_id,
        image_url=product.image_url,
        description=product.description,
        specifications=product.specifications,
        price_comparison=price_comparison,
        best_price=best_price.price,
        best_vendor_id=best_price.vendor_id,
        popularity_score=product.popularity_score
    )

@app.get("/api/products/{product_id}/similar", response_model=List[ProductResponse])
async def get_similar_products(
    product_id: str, 
    limit: int = Query(4, ge=1, le=10, description="Number of similar products"),
    db: Session = Depends(get_db)
):
    """Get similar products based on category and brand"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Find similar products in the same category
    query = db.query(Product).filter(
        Product.id != product_id,
        Product.category_id == product.category_id
    )
    
    # Prefer same brand
    if product.brand:
        same_brand_products = query.filter(Product.brand == product.brand).limit(limit//2).all()
        other_products = query.filter(Product.brand != product.brand)\
                             .order_by(desc(Product.popularity_score))\
                             .limit(limit - len(same_brand_products)).all()
        similar_products = same_brand_products + other_products
    else:
        similar_products = query.order_by(desc(Product.popularity_score)).limit(limit).all()
    
    # Convert to response format
    product_responses = []
    for similar_product in similar_products:
        # Get best price for this product
        best_price = db.query(Price).filter(
            Price.product_id == similar_product.id
        ).order_by(Price.price.asc()).first()
        
        if best_price:
            product_responses.append(ProductResponse(
                id=similar_product.id,
                name=similar_product.name,
                brand=similar_product.brand,
                category_id=similar_product.category_id,
                image_url=similar_product.image_url,
                best_price=best_price.price,
                best_vendor_id=best_price.vendor_id,
                popularity_score=similar_product.popularity_score
            ))
    
    return product_responses

@app.get("/api/scraper-status", response_model=List[ScraperStatusResponse])
async def get_scraper_status(db: Session = Depends(get_db)):
    """Get status of recent scraper runs"""
    # Get the most recent scraper run for each vendor
    recent_runs = db.query(ScraperRun)\
                   .order_by(desc(ScraperRun.started_at))\
                   .limit(10)\
                   .all()
    
    # Get vendor information
    vendor_ids = [run.vendor_id for run in recent_runs]
    vendors = db.query(Vendor).filter(Vendor.id.in_(vendor_ids)).all()
    vendor_map = {vendor.id: vendor for vendor in vendors}
    
    status_responses = []
    for run in recent_runs:
        vendor = vendor_map.get(run.vendor_id)
        if vendor:
            status_responses.append(ScraperStatusResponse(
                vendor_id=vendor.id,
                vendor_name=vendor.display_name,
                status=run.status,
                last_run_at=run.started_at,
                products_scraped=run.products_scraped or 0,
                errors_count=run.errors_count or 0,
                duration_seconds=run.duration_seconds
            ))
    
    return status_responses

@app.get("/api/autocomplete")
async def autocomplete_search(
    q: str = Query(..., min_length=2, description="Search query for autocomplete"),
    limit: int = Query(10, ge=1, le=20, description="Number of suggestions"),
    db: Session = Depends(get_db)
):
    """Get autocomplete suggestions for search"""
    # Search in product names and brands
    products = db.query(Product).filter(
        Product.name.ilike(f"%{q}%")
    ).order_by(desc(Product.popularity_score)).limit(limit).all()
    
    suggestions = []
    for product in products:
        suggestions.append({
            "id": product.id,
            "text": product.name,
            "type": "product",
            "brand": product.brand
        })
    
    # Also search brands
    brands = db.query(Product.brand).filter(
        Product.brand.ilike(f"%{q}%"),
        Product.brand.isnot(None)
    ).distinct().limit(5).all()
    
    for brand_tuple in brands:
        brand = brand_tuple[0]
        if brand and brand not in [s["text"] for s in suggestions]:
            suggestions.append({
                "text": brand,
                "type": "brand"
            })
    
    return {"suggestions": suggestions[:limit]}

@app.get("/api/data-freshness")
async def get_data_freshness(
    product_id: Optional[str] = Query(None, description="Get freshness for specific product"),
    db: Session = Depends(get_db)
):
    """Get data freshness information showing how current the price data is"""
    price_service = get_price_service(db)
    freshness_info = price_service.get_data_freshness_info(product_id)
    return freshness_info

@app.get("/api/scraper/last-run")
async def get_last_scraper_run(db: Session = Depends(get_db)):
    """Get information about the most recent scraper runs"""
    # Get the most recent run for each vendor
    vendors = db.query(Vendor).filter(Vendor.is_active == True).all()
    
    last_runs = []
    for vendor in vendors:
        last_run = db.query(ScraperRun).filter(
            ScraperRun.vendor_id == vendor.id
        ).order_by(desc(ScraperRun.started_at)).first()
        
        if last_run:
            # Calculate time since last run
            time_since = datetime.utcnow() - last_run.started_at
            hours_since = time_since.total_seconds() / 3600
            
            last_runs.append({
                "vendor_id": vendor.id,
                "vendor_name": vendor.display_name,
                "last_run_at": last_run.started_at.isoformat(),
                "status": last_run.status,
                "hours_since_last_run": round(hours_since, 1),
                "products_scraped": last_run.products_scraped or 0,
                "errors_count": last_run.errors_count or 0,
                "duration_seconds": last_run.duration_seconds,
                "completed_at": last_run.completed_at.isoformat() if last_run.completed_at else None
            })
        else:
            last_runs.append({
                "vendor_id": vendor.id,
                "vendor_name": vendor.display_name,
                "last_run_at": None,
                "status": "never_run",
                "hours_since_last_run": None,
                "products_scraped": 0,
                "errors_count": 0,
                "duration_seconds": None,
                "completed_at": None
            })
    
    return {"last_runs": last_runs}

@app.get("/api/best-deals")
async def get_best_deals(
    category_id: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Number of deals to return"),
    db: Session = Depends(get_db)
):
    """Get products with the best current deals (highest discount percentages)"""
    price_service = get_price_service(db)
    deals = price_service.get_best_deals(category_id, limit)
    return {"deals": deals}

@app.get("/api/price-alerts")
async def get_price_alerts(
    target_discount: float = Query(20.0, ge=5.0, le=90.0, description="Minimum discount percentage for alerts"),
    db: Session = Depends(get_db)
):
    """Get products that have reached a target discount threshold in the last 24 hours"""
    price_service = get_price_service(db)
    alerts = price_service.get_price_alerts(target_discount)
    return {"alerts": alerts}

@app.get("/api/products/{product_id}/price-history")
async def get_product_price_history(
    product_id: str,
    vendor_id: Optional[str] = Query(None, description="Filter by specific vendor"),
    days_back: int = Query(30, ge=1, le=365, description="Number of days of history"),
    db: Session = Depends(get_db)
):
    """Get price history for a product"""
    price_service = get_price_service(db)
    
    if vendor_id:
        # Get history for specific vendor
        history = price_service.get_price_history(product_id, vendor_id, days_back)
        return {
            "product_id": product_id,
            "vendor_id": vendor_id,
            "history": [
                {
                    "price": float(h.price),
                    "original_price": float(h.original_price) if h.original_price else None,
                    "discount_percentage": float(h.discount_percentage) if h.discount_percentage else None,
                    "stock_status": h.stock_status,
                    "recorded_at": h.recorded_at.isoformat()
                }
                for h in history
            ]
        }
    else:
        # Get trends across all vendors
        trends = price_service.get_price_trends(product_id, days_back)
        return {
            "product_id": product_id,
            "trends": trends
        }