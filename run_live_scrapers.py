#!/usr/bin/env python3
"""
Live Scraper Runner - Scrapes real data and populates database
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict
import uuid
from decimal import Decimal

# Add paths
sys.path.append('backend')
sys.path.append('scrapers')

from backend.app.database import SessionLocal, engine
from backend.app.models import Base, Product, Price, Vendor, Category, ScraperRun
from scrapers.amazon_scraper import AmazonScraper
from scrapers.bestbuy_scraper import BestBuyScraper
from scrapers.walmart_scraper import WalmartScraper
from fuzzywuzzy import fuzz

class LiveScraperRunner:
    def __init__(self):
        self.db = SessionLocal()
        self.ensure_vendors_exist()
        
    def ensure_vendors_exist(self):
        """Ensure all vendors exist in database"""
        vendors_data = [
            {'name': 'amazon', 'display_name': 'Amazon', 'base_url': 'https://www.amazon.com'},
            {'name': 'bestbuy', 'display_name': 'Best Buy', 'base_url': 'https://www.bestbuy.com'},
            {'name': 'walmart', 'display_name': 'Walmart', 'base_url': 'https://www.walmart.com'},
            {'name': 'brand', 'display_name': 'Brand Website', 'base_url': ''}
        ]
        
        for vendor_data in vendors_data:
            existing = self.db.query(Vendor).filter(Vendor.name == vendor_data['name']).first()
            if not existing:
                vendor = Vendor(id=str(uuid.uuid4()), **vendor_data)
                self.db.add(vendor)
        
        # Ensure categories exist
        categories_data = [
            {'name': 'laptops', 'display_name': 'Laptops'},
            {'name': 'headphones', 'display_name': 'Headphones'},
            {'name': 'speakers', 'display_name': 'Speakers'}
        ]
        
        for category_data in categories_data:
            existing = self.db.query(Category).filter(Category.name == category_data['name']).first()
            if not existing:
                category = Category(id=str(uuid.uuid4()), **category_data)
                self.db.add(category)
        
        self.db.commit()
    
    def find_or_create_product(self, scraped_name: str, brand: str = None, category_name: str = 'laptops') -> Product:
        """Find existing product or create new one"""
        # Try to find existing product with fuzzy matching
        existing_products = self.db.query(Product).all()
        
        best_match = None
        best_score = 0
        
        for product in existing_products:
            score = fuzz.ratio(scraped_name.lower(), product.name.lower())
            if score > best_score and score >= 80:  # 80% similarity threshold
                best_score = score
                best_match = product
        
        if best_match:
            print(f"  📎 Matched to existing product: {best_match.name} (score: {best_score})")
            return best_match
        
        # Create new product
        category = self.db.query(Category).filter(Category.name == category_name).first()
        
        new_product = Product(
            id=str(uuid.uuid4()),
            name=scraped_name,
            brand=brand or self._extract_brand(scraped_name),
            category_id=category.id if category else None,
            popularity_score=1
        )
        
        self.db.add(new_product)
        self.db.commit()
        self.db.refresh(new_product)
        
        print(f"  ✨ Created new product: {new_product.name}")
        return new_product
    
    def _extract_brand(self, product_name: str) -> str:
        """Extract brand from product name"""
        common_brands = [
            'Apple', 'Samsung', 'Sony', 'Bose', 'Dell', 'HP', 'Lenovo', 
            'ASUS', 'Acer', 'Microsoft', 'Google', 'Amazon', 'JBL', 'Beats',
            'MacBook', 'iPad', 'iPhone', 'AirPods'
        ]
        
        name_words = product_name.split()
        for word in name_words:
            for brand in common_brands:
                if word.lower() == brand.lower() or brand.lower() in word.lower():
                    return brand
        
        return name_words[0] if name_words else "Unknown"
    
    def update_product_price(self, product: Product, vendor_name: str, scraped_data: dict):
        """Update or create price record for product"""
        vendor = self.db.query(Vendor).filter(Vendor.name == vendor_name).first()
        if not vendor:
            return
        
        # Find existing price record
        existing_price = self.db.query(Price).filter(
            Price.product_id == product.id,
            Price.vendor_id == vendor.id
        ).first()
        
        # Calculate discount percentage
        discount_percentage = None
        if scraped_data.get('original_price') and scraped_data.get('price'):
            original = float(scraped_data['original_price'])
            current = float(scraped_data['price'])
            if original > current:
                discount_percentage = round(((original - current) / original) * 100, 2)
        
        if existing_price:
            # Update existing price
            existing_price.price = Decimal(str(scraped_data['price']))
            existing_price.original_price = Decimal(str(scraped_data['original_price'])) if scraped_data.get('original_price') else None
            existing_price.discount_percentage = Decimal(str(discount_percentage)) if discount_percentage else None
            existing_price.stock_status = scraped_data.get('stock_status', 'in_stock')
            existing_price.product_url = scraped_data.get('product_url', '')
            existing_price.last_updated_at = datetime.utcnow()
            print(f"    🔄 Updated {vendor.display_name} price: ${scraped_data['price']}")
        else:
            # Create new price record
            new_price = Price(
                id=str(uuid.uuid4()),
                product_id=product.id,
                vendor_id=vendor.id,
                price=Decimal(str(scraped_data['price'])),
                original_price=Decimal(str(scraped_data['original_price'])) if scraped_data.get('original_price') else None,
                discount_percentage=Decimal(str(discount_percentage)) if discount_percentage else None,
                stock_status=scraped_data.get('stock_status', 'in_stock'),
                product_url=scraped_data.get('product_url', ''),
                last_updated_at=datetime.utcnow()
            )
            self.db.add(new_price)
            print(f"    ✨ Added {vendor.display_name} price: ${scraped_data['price']}")
        
        # Update product image if we have one and product doesn't
        if scraped_data.get('image_url') and not product.image_url:
            product.image_url = scraped_data['image_url']
            print(f"    🖼️  Added product image")
        
        self.db.commit()
    
    async def scrape_vendor(self, vendor_name: str, search_queries: List[str]):
        """Scrape a specific vendor"""
        print(f"\\n🔍 Scraping {vendor_name.upper()}...")
        
        # Initialize scraper
        if vendor_name == 'amazon':
            scraper = AmazonScraper({'headless': True})
        elif vendor_name == 'bestbuy':
            scraper = BestBuyScraper({'headless': True})
        elif vendor_name == 'walmart':
            scraper = WalmartScraper({'headless': True})
        else:
            print(f"  ❌ No scraper available for {vendor_name}")
            return
        
        vendor = self.db.query(Vendor).filter(Vendor.name == vendor_name).first()
        
        # Create scraper run record
        scraper_run = ScraperRun(
            id=str(uuid.uuid4()),
            vendor_id=vendor.id,
            status='running',
            started_at=datetime.utcnow()
        )
        self.db.add(scraper_run)
        self.db.commit()
        
        products_scraped = 0
        errors = 0
        
        try:
            for query in search_queries:
                print(f"  🔎 Searching for: {query}")
                
                try:
                    results = await scraper.search_product(query)
                    print(f"    Found {len(results)} products")
                    
                    for result in results[:3]:  # Limit to first 3 results per query
                        try:
                            # Find or create product
                            product = self.find_or_create_product(
                                result.name, 
                                result.brand,
                                self._determine_category(query)
                            )
                            
                            # Update price data
                            scraped_data = {
                                'price': result.price,
                                'original_price': result.original_price,
                                'stock_status': result.stock_status,
                                'product_url': result.product_url,
                                'image_url': result.image_url
                            }
                            
                            self.update_product_price(product, vendor_name, scraped_data)
                            products_scraped += 1
                            
                        except Exception as e:
                            print(f"    ❌ Error processing product: {e}")
                            errors += 1
                    
                    # Small delay between queries
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"    ❌ Error searching for {query}: {e}")
                    errors += 1
            
            # Complete scraper run
            scraper_run.status = 'completed'
            scraper_run.products_scraped = products_scraped
            scraper_run.errors_count = errors
            scraper_run.completed_at = datetime.utcnow()
            
        except Exception as e:
            print(f"  ❌ Scraper failed: {e}")
            scraper_run.status = 'failed'
            scraper_run.error_details = {'error': str(e)}
            scraper_run.completed_at = datetime.utcnow()
            
        finally:
            self.db.commit()
            if hasattr(scraper, 'quit'):
                scraper.quit()
            
            print(f"  📊 Results: {products_scraped} products, {errors} errors")
    
    def _determine_category(self, query: str) -> str:
        """Determine category based on search query"""
        query_lower = query.lower()
        if any(word in query_lower for word in ['laptop', 'macbook', 'notebook']):
            return 'laptops'
        elif any(word in query_lower for word in ['headphone', 'earphone', 'airpods']):
            return 'headphones'
        elif any(word in query_lower for word in ['speaker', 'soundbar']):
            return 'speakers'
        return 'laptops'  # default
    
    async def run_all_scrapers(self):
        """Run all scrapers with realistic search queries"""
        search_queries = [
            "MacBook Pro 14",
            "Dell XPS 13", 
            "Sony WH-1000XM4",
            "AirPods Pro",
            "JBL Charge 5",
            "Bose SoundLink"
        ]
        
        print("🚀 Starting Live Scraper Run")
        print("=" * 50)
        
        # Scrape each vendor
        for vendor in ['amazon']:  # Start with Amazon only for testing
            await self.scrape_vendor(vendor, search_queries)
        
        print("\\n🎉 Live scraping completed!")
        print("\\nNext steps:")
        print("1. Check your frontend at http://localhost:3001")
        print("2. Search for the products that were just scraped")
        print("3. View live price data and real product images")
    
    def cleanup(self):
        """Clean up database connection"""
        self.db.close()

async def main():
    """Main function"""
    Base.metadata.create_all(bind=engine)
    
    runner = LiveScraperRunner()
    try:
        await runner.run_all_scrapers()
    finally:
        runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())