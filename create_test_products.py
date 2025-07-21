#!/usr/bin/env python3
"""
Create test products with prices from multiple vendors for testing
"""

import sys
import os
from decimal import Decimal
from datetime import datetime
import uuid

# Add paths
sys.path.append('backend')

from backend.app.database import SessionLocal, engine
from backend.app.models import Base, Product, Price, Vendor, Category

def create_test_products():
    """Create test products with prices from all vendors"""
    
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Ensure vendors exist
        vendors_data = [
            {'name': 'amazon', 'display_name': 'Amazon', 'base_url': 'https://www.amazon.com'},
            {'name': 'bestbuy', 'display_name': 'Best Buy', 'base_url': 'https://www.bestbuy.com'},
            {'name': 'walmart', 'display_name': 'Walmart', 'base_url': 'https://www.walmart.com'},
            {'name': 'brand', 'display_name': 'Brand Websites', 'base_url': ''}
        ]
        
        for vendor_data in vendors_data:
            existing = db.query(Vendor).filter(Vendor.name == vendor_data['name']).first()
            if not existing:
                vendor = Vendor(
                    id=str(uuid.uuid4()),
                    **vendor_data
                )
                db.add(vendor)
        
        # Ensure categories exist
        categories_data = [
            {'name': 'laptops', 'display_name': 'Laptops'},
            {'name': 'headphones', 'display_name': 'Headphones'},
            {'name': 'speakers', 'display_name': 'Speakers'}
        ]
        
        for category_data in categories_data:
            existing = db.query(Category).filter(Category.name == category_data['name']).first()
            if not existing:
                category = Category(
                    id=str(uuid.uuid4()),
                    **category_data
                )
                db.add(category)
        
        db.commit()
        
        # Get vendors and category
        amazon = db.query(Vendor).filter(Vendor.name == 'amazon').first()
        bestbuy = db.query(Vendor).filter(Vendor.name == 'bestbuy').first()
        walmart = db.query(Vendor).filter(Vendor.name == 'walmart').first()
        brand = db.query(Vendor).filter(Vendor.name == 'brand').first()
        laptops_category = db.query(Category).filter(Category.name == 'laptops').first()
        
        # Create a test MacBook product
        test_product = Product(
            id=str(uuid.uuid4()),
            name="Apple MacBook Pro 14-inch M3 Pro",
            brand="Apple",
            category_id=laptops_category.id,
            image_url="https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-spacegray-select-202310.jpeg",
            popularity_score=100
        )
        
        db.add(test_product)
        db.commit()
        db.refresh(test_product)
        
        print(f"Created test product: {test_product.name}")
        print(f"Product ID: {test_product.id}")
        
        # Create prices from all 4 vendors
        prices_data = [
            {
                'vendor': amazon,
                'price': Decimal('1999.99'),
                'original_price': Decimal('2199.99'),
                'discount_percentage': 9.09,
                'stock_status': 'in_stock',
                'product_url': 'https://www.amazon.com/dp/test-macbook-pro'
            },
            {
                'vendor': bestbuy,
                'price': Decimal('2099.99'),
                'original_price': None,
                'discount_percentage': None,
                'stock_status': 'in_stock',
                'product_url': 'https://www.bestbuy.com/site/apple-macbook-pro/test'
            },
            {
                'vendor': walmart,
                'price': Decimal('1949.99'),  # Best price
                'original_price': Decimal('2199.99'),
                'discount_percentage': 11.36,
                'stock_status': 'in_stock',
                'product_url': 'https://www.walmart.com/ip/apple-macbook-pro/test'
            },
            {
                'vendor': brand,
                'price': Decimal('2199.99'),  # Full price from Apple
                'original_price': None,
                'discount_percentage': None,
                'stock_status': 'in_stock',
                'product_url': 'https://www.apple.com/macbook-pro-14-and-16/test'
            }
        ]
        
        for price_data in prices_data:
            # Check if price already exists
            existing_price = db.query(Price).filter(
                Price.product_id == test_product.id,
                Price.vendor_id == price_data['vendor'].id
            ).first()
            
            if existing_price:
                # Update existing price
                existing_price.price = price_data['price']
                existing_price.original_price = price_data['original_price']
                existing_price.discount_percentage = price_data['discount_percentage']
                existing_price.stock_status = price_data['stock_status']
                existing_price.product_url = price_data['product_url']
                existing_price.last_updated_at = datetime.utcnow()
                print(f"Updated price for {price_data['vendor'].display_name}: ${price_data['price']}")
            else:
                # Create new price
                new_price = Price(
                    id=str(uuid.uuid4()),
                    product_id=test_product.id,
                    vendor_id=price_data['vendor'].id,
                    price=price_data['price'],
                    original_price=price_data['original_price'],
                    discount_percentage=price_data['discount_percentage'],
                    stock_status=price_data['stock_status'],
                    product_url=price_data['product_url'],
                    last_updated_at=datetime.utcnow()
                )
                db.add(new_price)
                print(f"Created price for {price_data['vendor'].display_name}: ${price_data['price']}")
        
        db.commit()
        
        # Verify the data
        print(f"\nVerification - Prices for {test_product.name}:")
        prices = db.query(Price, Vendor).join(Vendor).filter(Price.product_id == test_product.id).all()
        for price, vendor in prices:
            discount_text = f" (was ${price.original_price}, {price.discount_percentage}% off)" if price.original_price else ""
            print(f"  - {vendor.display_name}: ${price.price}{discount_text}")
        
        print(f"\nTest product created successfully!")
        print(f"You can now search for 'MacBook Pro' in the frontend to see all 4 vendor prices.")
        
    except Exception as e:
        print(f"Error creating test products: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_products()