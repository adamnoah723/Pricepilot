#!/usr/bin/env python3
"""
PricePilot Scraper Runner
Executes all scrapers and stores data in the database
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from app.database import SessionLocal, engine
from app.models import Base, Product, Price, Vendor, Category, ScraperRun
from app.config import settings
from scrapers.amazon_scraper import AmazonScraper
from scrapers.bestbuy_scraper import BestBuyScraper
from scrapers.walmart_scraper import WalmartScraper
from scrapers.brand_scraper import BrandScraper
from scrapers.base import ScrapedProduct
from sqlalchemy.orm import Session
from fuzzywuzzy import fuzz
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductMatcher:
    """Handles product matching logic using model, keywords, and variation attributes"""
    
    def __init__(self, similarity_threshold: int = 80):
        self.similarity_threshold = similarity_threshold
    
    def find_matching_product(self, scraped_product: ScrapedProduct, db: Session) -> Product:
        """Find or create a matching product in the database"""
        # Extract key product identifiers for better matching
        product_keywords = self._extract_product_keywords(scraped_product.name)
        
        # First, try to find exact matches
        existing_products = db.query(Product).all()
        
        # Use fuzzy matching to find the best match
        best_match = None
        best_score = 0
        
        for product in existing_products:
            # Try multiple matching strategies
            scores = []
            
            # 1. Direct name comparison
            scores.append(fuzz.ratio(scraped_product.name.lower(), product.name.lower()))
            
            # 2. Token sort ratio (handles word order differences)
            scores.append(fuzz.token_sort_ratio(scraped_product.name.lower(), product.name.lower()))
            
            # 3. Partial ratio (handles extra words)
            scores.append(fuzz.partial_ratio(scraped_product.name.lower(), product.name.lower()))
            
            # 4. Keyword-based matching
            product_product_keywords = self._extract_product_keywords(product.name)
            if product_keywords and product_product_keywords:
                keyword_matches = len(set(product_keywords) & set(product_product_keywords))
                keyword_score = (keyword_matches / max(len(product_keywords), len(product_product_keywords))) * 100
                scores.append(keyword_score)
            
            # Use the highest score
            score = max(scores)
            
            if score > best_score and score >= self.similarity_threshold:
                best_score = score
                best_match = product
        
        if best_match:
            logger.info(f"Found matching product: {best_match.name} (score: {best_score})")
            return best_match
        
        # Create new product if no match found
        logger.info(f"Creating new product: {scraped_product.name}")
        return self._create_new_product(scraped_product, db)
    
    def _extract_product_keywords(self, product_name: str) -> List[str]:
        """Extract key product identifiers from product name"""
        import re
        
        # Convert to lowercase and remove common words
        name = product_name.lower()
        
        # Extract key patterns
        keywords = []
        
        # Brand names
        brands = ['apple', 'samsung', 'sony', 'bose', 'dell', 'hp', 'lenovo', 'microsoft', 'jbl']
        for brand in brands:
            if brand in name:
                keywords.append(brand)
        
        # Product types
        product_types = ['macbook', 'iphone', 'ipad', 'airpods', 'surface', 'xps', 'thinkpad', 'headphones', 'earbuds', 'speaker']
        for ptype in product_types:
            if ptype in name:
                keywords.append(ptype)
        
        # Model numbers and sizes
        model_patterns = [
            r'(m[1-4](?:\s+(?:pro|max|ultra))?)',  # M1, M2, M3, M4 chips
            r'(\d+(?:\.\d+)?["\-]?(?:inch)?)',      # Screen sizes like 14", 13-inch
            r'(pro|air|max|mini|plus)',             # Product variants
            r'(\d+gb|\d+tb)',                       # Storage sizes
        ]
        
        for pattern in model_patterns:
            matches = re.findall(pattern, name)
            keywords.extend(matches)
        
        return [k.strip() for k in keywords if k.strip()]
    
    def _create_new_product(self, scraped_product: ScrapedProduct, db: Session) -> Product:
        """Create a new product from scraped data"""
        # Try to determine category based on product name
        category = self._determine_category(scraped_product.name, db)
        
        # Extract brand from product name
        brand = self._extract_brand(scraped_product.name)
        
        new_product = Product(
            id=str(uuid.uuid4()),
            name=scraped_product.name,
            brand=brand,
            category_id=category.id if category else None,
            image_url=scraped_product.image_url,
            popularity_score=1
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        return new_product
    
    def _determine_category(self, product_name: str, db: Session) -> Category:
        """Determine product category based on name"""
        name_lower = product_name.lower()
        
        # Category keywords mapping
        category_keywords = {
            'laptops': ['laptop', 'macbook', 'notebook', 'ultrabook', 'chromebook'],
            'headphones': ['headphone', 'earphone', 'earbud', 'airpods', 'headset'],
            'speakers': ['speaker', 'soundbar', 'bluetooth speaker', 'wireless speaker']
        }
        
        for category_name, keywords in category_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                category = db.query(Category).filter(Category.name == category_name).first()
                if category:
                    return category
        
        # Default to laptops if no match
        return db.query(Category).filter(Category.name == 'laptops').first()
    
    def _extract_brand(self, product_name: str) -> str:
        """Extract brand name from product name"""
        common_brands = [
            'Apple', 'Samsung', 'Sony', 'Bose', 'Dell', 'HP', 'Lenovo', 
            'ASUS', 'Acer', 'Microsoft', 'Google', 'Amazon', 'JBL', 'Beats'
        ]
        
        name_words = product_name.split()
        for word in name_words:
            for brand in common_brands:
                if word.lower() == brand.lower():
                    return brand
        
        # Return first word as brand if no match
        return name_words[0] if name_words else "Unknown"


class ScraperPipeline:
    """Main scraper pipeline that coordinates all scrapers"""
    
    def __init__(self):
        self.product_matcher = ProductMatcher()
        self.scrapers = self._initialize_scrapers()
    
    def _initialize_scrapers(self) -> Dict[str, Any]:
        """Initialize all scrapers with their configurations"""
        return {
            'amazon': AmazonScraper({
                'headless': settings.scraper_headless,
                'max_retries': 3,
                'rate_limit_delay': 1.0
            }),
            'bestbuy': BestBuyScraper({
                'max_retries': 3,
                'rate_limit_delay': 0.5
            }),
            'walmart': WalmartScraper({
                'max_retries': 3,
                'rate_limit_delay': 0.5
            }),
            'brand': BrandScraper({
                'max_retries': 3,
                'rate_limit_delay': 2.0,
                'brand_configs': {
                    # Example brand configurations
                    'apple': {
                        'base_url': 'https://www.apple.com',
                        'search_url_template': 'https://www.apple.com/search/{query}',
                        'product_container_selector': '.rf-serp-productcard',
                        'search_name_selectors': ['.rf-serp-productcard-title'],
                        'search_price_selectors': ['.rf-serp-productcard-price'],
                        'search_link_selector': 'a',
                        'name_selectors': ['h1.pdp-product-name'],
                        'price_selectors': ['.current_price', '.price-current'],
                        'image_selectors': ['.product-hero img']
                    }
                }
            })
        }
    
    async def run_all_scrapers(self, search_queries: List[str]) -> Dict[str, Any]:
        """Run all scrapers for the given search queries"""
        results = {
            'total_products': 0,
            'total_errors': 0,
            'vendor_results': {}
        }
        
        db = SessionLocal()
        try:
            # Ensure vendors exist in database
            self._ensure_vendors_exist(db)
            
            for vendor_name, scraper in self.scrapers.items():
                logger.info(f"Starting {vendor_name} scraper...")
                
                vendor = db.query(Vendor).filter(Vendor.name == vendor_name).first()
                scraper_run = self._start_scraper_run(vendor, db)
                
                try:
                    vendor_results = await self._run_vendor_scraper(
                        scraper, vendor, search_queries, db
                    )
                    
                    self._complete_scraper_run(scraper_run, vendor_results, db)
                    results['vendor_results'][vendor_name] = vendor_results
                    results['total_products'] += vendor_results['products_scraped']
                    
                except Exception as e:
                    logger.error(f"Error in {vendor_name} scraper: {e}")
                    self._fail_scraper_run(scraper_run, str(e), db)
                    results['total_errors'] += 1
                
                # Clean up selenium for Amazon scraper
                if hasattr(scraper, 'quit_selenium'):
                    scraper.quit_selenium()
        
        finally:
            db.close()
        
        return results
    
    async def _run_vendor_scraper(self, scraper, vendor: Vendor, queries: List[str], db: Session) -> Dict[str, Any]:
        """Run a single vendor scraper"""
        products_scraped = 0
        errors = 0
        
        for query in queries:
            try:
                logger.info(f"Scraping {vendor.name} for query: {query}")
                scraped_products = await scraper.search_product(query)
                
                for scraped_product in scraped_products:
                    try:
                        self._store_product_data(scraped_product, vendor, db)
                        products_scraped += 1
                    except Exception as e:
                        logger.error(f"Error storing product data: {e}")
                        errors += 1
                
            except Exception as e:
                logger.error(f"Error scraping {vendor.name} for '{query}': {e}")
                errors += 1
        
        return {
            'products_scraped': products_scraped,
            'errors': errors
        }
    
    def _store_product_data(self, scraped_product: ScrapedProduct, vendor: Vendor, db: Session):
        """Store scraped product data in the database"""
        # Find or create matching product
        product = self.product_matcher.find_matching_product(scraped_product, db)
        
        # Update or create price record
        existing_price = db.query(Price).filter(
            Price.product_id == product.id,
            Price.vendor_id == vendor.id
        ).first()
        
        if existing_price:
            # Update existing price
            existing_price.price = scraped_product.price
            existing_price.original_price = scraped_product.original_price
            existing_price.stock_status = scraped_product.stock_status
            existing_price.product_url = scraped_product.product_url
            existing_price.last_updated_at = datetime.utcnow()
            
            if scraped_product.original_price and scraped_product.price:
                discount = ((scraped_product.original_price - scraped_product.price) / scraped_product.original_price) * 100
                existing_price.discount_percentage = round(discount, 2)
        else:
            # Create new price record
            discount_percentage = None
            if scraped_product.original_price and scraped_product.price:
                discount = ((scraped_product.original_price - scraped_product.price) / scraped_product.original_price) * 100
                discount_percentage = round(discount, 2)
            
            new_price = Price(
                id=str(uuid.uuid4()),
                product_id=product.id,
                vendor_id=vendor.id,
                price=scraped_product.price,
                original_price=scraped_product.original_price,
                discount_percentage=discount_percentage,
                stock_status=scraped_product.stock_status,
                product_url=scraped_product.product_url,
                variation_details=scraped_product.variations
            )
            db.add(new_price)
        
        # Update product popularity
        product.popularity_score += 1
        
        db.commit()
    
    def _ensure_vendors_exist(self, db: Session):
        """Ensure all vendors exist in the database"""
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
    
    def _start_scraper_run(self, vendor: Vendor, db: Session) -> ScraperRun:
        """Start a new scraper run record"""
        scraper_run = ScraperRun(
            id=str(uuid.uuid4()),
            vendor_id=vendor.id,
            status='running',
            started_at=datetime.utcnow()
        )
        db.add(scraper_run)
        db.commit()
        db.refresh(scraper_run)
        return scraper_run
    
    def _complete_scraper_run(self, scraper_run: ScraperRun, results: Dict[str, Any], db: Session):
        """Complete a scraper run with results"""
        scraper_run.status = 'completed'
        scraper_run.products_scraped = results['products_scraped']
        scraper_run.errors_count = results['errors']
        scraper_run.completed_at = datetime.utcnow()
        
        if scraper_run.started_at:
            duration = (scraper_run.completed_at - scraper_run.started_at).total_seconds()
            scraper_run.duration_seconds = int(duration)
        
        db.commit()
    
    def _fail_scraper_run(self, scraper_run: ScraperRun, error_message: str, db: Session):
        """Mark a scraper run as failed"""
        scraper_run.status = 'failed'
        scraper_run.completed_at = datetime.utcnow()
        scraper_run.error_details = {'error': error_message}
        
        if scraper_run.started_at:
            duration = (scraper_run.completed_at - scraper_run.started_at).total_seconds()
            scraper_run.duration_seconds = int(duration)
        
        db.commit()


async def main():
    """Main function to run all scrapers"""
    logger.info("Starting PricePilot scraper pipeline...")
    
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Define search queries for high-ticket tech items
    search_queries = [
        "MacBook Pro",
        "Dell XPS 13",
        "Sony WH-1000XM4",
        "Bose QuietComfort",
        "JBL Charge 5",
        "iPad Pro",
        "Surface Laptop",
        "AirPods Pro",
        "Samsung Galaxy Buds"
    ]
    
    pipeline = ScraperPipeline()
    
    try:
        results = await pipeline.run_all_scrapers(search_queries)
        
        logger.info("Scraper pipeline completed!")
        logger.info(f"Total products scraped: {results['total_products']}")
        logger.info(f"Total errors: {results['total_errors']}")
        
        for vendor, vendor_results in results['vendor_results'].items():
            logger.info(f"{vendor}: {vendor_results['products_scraped']} products, {vendor_results['errors']} errors")
    
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())