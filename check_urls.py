#!/usr/bin/env python3
"""
Check the URLs stored in the database
"""

import sys
import os
sys.path.append('backend')

from backend.app.database import SessionLocal
from backend.app.models import Product, Price, Vendor

def check_urls():
    db = SessionLocal()
    
    try:
        # Get a few products with their prices
        products = db.query(Product).limit(3).all()
        
        for product in products:
            print(f"\n📦 Product: {product.name[:60]}...")
            print(f"   Brand: {product.brand}")
            
            prices = db.query(Price).filter(Price.product_id == product.id).all()
            
            for price in prices:
                vendor = db.query(Vendor).filter(Vendor.id == price.vendor_id).first()
                print(f"\n   💰 {vendor.display_name}: ${price.price}")
                print(f"   🔗 URL: {price.product_url}")
                
                # Check if URL looks valid
                if not price.product_url or price.product_url == "":
                    print("   ❌ Empty URL!")
                elif "sspa/click" in price.product_url:
                    print("   ❌ Sponsored/click URL - not a direct product link!")
                elif "/dp/" not in price.product_url and "/gp/product/" not in price.product_url:
                    print("   ❌ Not a valid Amazon product URL!")
                else:
                    print("   ✅ URL format looks correct")
                    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_urls()