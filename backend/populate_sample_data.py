#!/usr/bin/env python3
"""
Populate the database with sample data for demonstration
"""

import sys
import os
from datetime import datetime
from decimal import Decimal
import uuid

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, Product, Price, Vendor, Category

def create_sample_data():
    """Create sample data for demonstration"""
    db = SessionLocal()
    
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        
        # Create categories
        categories = [
            Category(id=str(uuid.uuid4()), name='laptops', display_name='Laptops'),
            Category(id=str(uuid.uuid4()), name='headphones', display_name='Headphones'),
            Category(id=str(uuid.uuid4()), name='speakers', display_name='Speakers')
        ]
        
        for category in categories:
            existing = db.query(Category).filter(Category.name == category.name).first()
            if not existing:
                db.add(category)
        
        db.commit()
        
        # Get categories for reference
        laptops_cat = db.query(Category).filter(Category.name == 'laptops').first()
        headphones_cat = db.query(Category).filter(Category.name == 'headphones').first()
        speakers_cat = db.query(Category).filter(Category.name == 'speakers').first()
        
        # Create vendors
        vendors = [
            Vendor(id=str(uuid.uuid4()), name='amazon', display_name='Amazon', base_url='https://www.amazon.com'),
            Vendor(id=str(uuid.uuid4()), name='bestbuy', display_name='Best Buy', base_url='https://www.bestbuy.com'),
            Vendor(id=str(uuid.uuid4()), name='walmart', display_name='Walmart', base_url='https://www.walmart.com'),
            Vendor(id=str(uuid.uuid4()), name='brand', display_name='Brand Website', base_url='')
        ]
        
        for vendor in vendors:
            existing = db.query(Vendor).filter(Vendor.name == vendor.name).first()
            if not existing:
                db.add(vendor)
        
        db.commit()
        
        # Get vendors for reference
        amazon = db.query(Vendor).filter(Vendor.name == 'amazon').first()
        bestbuy = db.query(Vendor).filter(Vendor.name == 'bestbuy').first()
        walmart = db.query(Vendor).filter(Vendor.name == 'walmart').first()
        brand = db.query(Vendor).filter(Vendor.name == 'brand').first()
        
        # Create sample products
        products = [
            # Laptops
            Product(
                id=str(uuid.uuid4()),
                name='MacBook Pro 14" M3 Chip',
                brand='Apple',
                category_id=laptops_cat.id,
                description='Professional laptop with M3 chip, perfect for developers and creators.',
                image_url='https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-spacegray-select-202310?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1697311054290',
                popularity_score=95
            ),
            Product(
                id=str(uuid.uuid4()),
                name='Dell XPS 13 Plus',
                brand='Dell',
                category_id=laptops_cat.id,
                description='Ultra-thin laptop with stunning InfinityEdge display.',
                image_url='https://via.placeholder.com/400x300/f8f9fa/6c757d?text=Dell+XPS+13+Plus',
                popularity_score=88
            ),
            # Headphones
            Product(
                id=str(uuid.uuid4()),
                name='Sony WH-1000XM4 Wireless Noise Canceling Headphones',
                brand='Sony',
                category_id=headphones_cat.id,
                description='Industry-leading noise canceling headphones with 30-hour battery life.',
                image_url='https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6408/6408356_sd.jpg',
                popularity_score=92
            ),
            Product(
                id=str(uuid.uuid4()),
                name='Apple AirPods Pro (2nd Generation)',
                brand='Apple',
                category_id=headphones_cat.id,
                description='Active Noise Cancellation, Transparency mode, Spatial audio.',
                image_url='https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MQD83?wid=1144&hei=1144&fmt=jpeg&qlt=90&.v=1660803972361',
                popularity_score=96
            ),
            # Speakers
            Product(
                id=str(uuid.uuid4()),
                name='JBL Charge 5 Portable Bluetooth Speaker',
                brand='JBL',
                category_id=speakers_cat.id,
                description='Portable Bluetooth speaker with powerful sound and 20-hour playtime.',
                image_url='https://www.jbl.com/dw/image/v2/BFND_PRD/on/demandware.static/-/Sites-masterCatalog_Harman/default/dw7c9e3c8e/JBL_Charge5_Hero_Blue_0117_x1.png',
                popularity_score=85
            ),
            Product(
                id=str(uuid.uuid4()),
                name='Bose SoundLink Revolve+ II',
                brand='Bose',
                category_id=speakers_cat.id,
                description='360-degree Bluetooth speaker with deep, loud sound.',
                image_url='https://assets.bose.com/content/dam/Bose_DAM/Web/consumer_electronics/global/products/speakers/soundlink_revolve_plus_ii/product_silo_images/SLR_PlusII_Silver_EC_01.psd/_jcr_content/renditions/cq5dam.web.320.320.png',
                popularity_score=82
            )
        ]
        
        for product in products:
            existing = db.query(Product).filter(Product.name == product.name).first()
            if not existing:
                db.add(product)
        
        db.commit()
        
        # Create sample prices
        all_products = db.query(Product).all()
        
        sample_prices = [
            # MacBook Pro 14" M3 - ALL 4 VENDORS
            (all_products[0].id, amazon.id, Decimal('1899.00'), Decimal('1999.00'), 5.0, 'in_stock', 'https://amazon.com/macbook-pro'),
            (all_products[0].id, bestbuy.id, Decimal('1949.99'), Decimal('1999.00'), 2.5, 'in_stock', 'https://bestbuy.com/macbook-pro'),
            (all_products[0].id, walmart.id, Decimal('1929.00'), None, None, 'in_stock', 'https://walmart.com/macbook-pro'),
            (all_products[0].id, brand.id, Decimal('1999.00'), None, None, 'in_stock', 'https://apple.com/macbook-pro'),
            
            # Dell XPS 13 Plus - ALL 4 VENDORS (Walmart out of stock)
            (all_products[1].id, amazon.id, Decimal('1299.99'), Decimal('1399.99'), 7.1, 'in_stock', 'https://amazon.com/dell-xps'),
            (all_products[1].id, bestbuy.id, Decimal('1349.99'), None, None, 'in_stock', 'https://bestbuy.com/dell-xps'),
            (all_products[1].id, walmart.id, Decimal('1329.00'), Decimal('1399.99'), 5.1, 'out_of_stock', 'https://walmart.com/dell-xps'),
            (all_products[1].id, brand.id, Decimal('1399.99'), None, None, 'in_stock', 'https://dell.com/xps-13-plus'),
            
            # Sony WH-1000XM4 - ALL 4 VENDORS (Brand discontinued)
            (all_products[2].id, amazon.id, Decimal('248.00'), Decimal('349.99'), 29.1, 'in_stock', 'https://amazon.com/sony-wh1000xm4'),
            (all_products[2].id, bestbuy.id, Decimal('279.99'), Decimal('349.99'), 20.0, 'in_stock', 'https://bestbuy.com/sony-wh1000xm4'),
            (all_products[2].id, walmart.id, Decimal('268.88'), Decimal('349.99'), 23.2, 'in_stock', 'https://walmart.com/sony-wh1000xm4'),
            (all_products[2].id, brand.id, Decimal('349.99'), None, None, 'discontinued', 'https://sony.com/wh-1000xm4'),
            
            # AirPods Pro (2nd Gen) - ALL 4 VENDORS (Walmart limited stock)
            (all_products[3].id, amazon.id, Decimal('199.99'), Decimal('249.00'), 19.7, 'in_stock', 'https://amazon.com/airpods-pro'),
            (all_products[3].id, bestbuy.id, Decimal('229.99'), Decimal('249.00'), 7.6, 'in_stock', 'https://bestbuy.com/airpods-pro'),
            (all_products[3].id, walmart.id, Decimal('219.00'), Decimal('249.00'), 12.0, 'limited_stock', 'https://walmart.com/airpods-pro'),
            (all_products[3].id, brand.id, Decimal('249.00'), None, None, 'in_stock', 'https://apple.com/airpods-pro'),
            
            # JBL Charge 5 - ALL 4 VENDORS (Best Buy unavailable)
            (all_products[4].id, amazon.id, Decimal('119.95'), Decimal('149.95'), 20.0, 'in_stock', 'https://amazon.com/jbl-charge5'),
            (all_products[4].id, bestbuy.id, Decimal('139.99'), Decimal('149.95'), 6.6, 'unavailable', 'https://bestbuy.com/jbl-charge5'),
            (all_products[4].id, walmart.id, Decimal('129.00'), Decimal('149.95'), 13.9, 'in_stock', 'https://walmart.com/jbl-charge5'),
            (all_products[4].id, brand.id, Decimal('149.95'), None, None, 'in_stock', 'https://jbl.com/charge-5'),
            
            # Bose SoundLink Revolve+ II - ALL 4 VENDORS (Amazon out of stock)
            (all_products[5].id, amazon.id, Decimal('229.00'), Decimal('299.00'), 23.4, 'out_of_stock', 'https://amazon.com/bose-revolve'),
            (all_products[5].id, bestbuy.id, Decimal('249.99'), Decimal('299.00'), 16.4, 'in_stock', 'https://bestbuy.com/bose-revolve'),
            (all_products[5].id, walmart.id, Decimal('259.00'), Decimal('299.00'), 13.4, 'in_stock', 'https://walmart.com/bose-revolve'),
            (all_products[5].id, brand.id, Decimal('299.00'), None, None, 'in_stock', 'https://bose.com/soundlink-revolve-plus-ii'),
        ]
        
        for product_id, vendor_id, price, original_price, discount, stock, url in sample_prices:
            existing = db.query(Price).filter(
                Price.product_id == product_id,
                Price.vendor_id == vendor_id
            ).first()
            
            if not existing:
                price_record = Price(
                    id=str(uuid.uuid4()),
                    product_id=product_id,
                    vendor_id=vendor_id,
                    price=price,
                    original_price=original_price,
                    discount_percentage=discount,
                    stock_status=stock,
                    product_url=url,
                    last_updated_at=datetime.utcnow()
                )
                db.add(price_record)
        
        db.commit()
        print("✅ Sample data created successfully!")
        print(f"Created {len(categories)} categories")
        print(f"Created {len(vendors)} vendors (Amazon, Best Buy, Walmart, Brand Websites)")
        print(f"Created {len(products)} products")
        print(f"Created {len(sample_prices)} price records (4 vendors per product)")
        print("📊 Every product now has all 4 vendor price comparisons!")
        print("🎯 Includes realistic stock statuses: in_stock, out_of_stock, limited_stock, unavailable, discontinued")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()