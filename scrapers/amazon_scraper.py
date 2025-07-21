import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scrapers.base import BaseScraper, ScrapedProduct
from scrapers.parsers.amazon_parser import AmazonParser
from decimal import Decimal
from typing import List, Optional
import re
import asyncio
from bs4 import BeautifulSoup
import logging

# Import the existing SeleniumFetcher from the provided demo
from .amazon_scrape_demo import SeleniumFetcher, extract_document_text

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    """Amazon scraper built on the provided SeleniumFetcher foundation"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.selenium_fetcher = SeleniumFetcher(is_headless=config.get('headless', True))
        # Initialize human browser history for stealth (from existing demo)
        self.selenium_fetcher.initialize_human_browser_history()
        # Initialize the Amazon parser
        self.parser = AmazonParser()
    
    async def search_product(self, query: str) -> List[ScrapedProduct]:
        """Search Amazon for products using the existing selenium fetcher"""
        try:
            # Step 1: Get search results to find product URLs
            search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
            html = self.selenium_fetcher.fetch(search_url, verbose=True, return_content=True)
            
            if not html:
                logger.error(f"Failed to fetch search results for query: {query}")
                return []
            
            # Parse search results to get product URLs
            search_results = self.parser.parse_search_results(html, "https://www.amazon.com")
            logger.info(f"Found {len(search_results)} products in search results")
            
            # Step 2: Visit each product page for detailed information
            scraped_products = []
            for i, search_result in enumerate(search_results[:5]):  # Limit to first 5 for testing
                if not search_result.product_url:
                    logger.warning(f"No product URL for result {i+1}, skipping")
                    continue
                
                logger.info(f"Getting detailed info for product {i+1}: {search_result.product_url}")
                
                try:
                    # Get detailed product information from the actual product page
                    detailed_product = await self.get_product_details(search_result.product_url)
                    
                    if detailed_product:
                        scraped_products.append(detailed_product)
                        logger.info(f"✅ Successfully scraped: {detailed_product.name}")
                    else:
                        logger.warning(f"❌ Failed to get details for product {i+1}")
                    
                    # Rate limiting between product page visits
                    await self.respect_rate_limit()
                    
                except Exception as e:
                    logger.error(f"Error getting details for product {i+1}: {e}")
                    continue
            
            return scraped_products
            
        except Exception as e:
            logger.error(f"Error in Amazon search for '{query}': {e}")
            return []
    
    async def get_product_details(self, product_url: str) -> Optional[ScrapedProduct]:
        """Get detailed product info using selenium_fetcher.fetch()"""
        try:
            # Use selenium_fetcher.fetch(product_url) to get product page HTML
            html = self.selenium_fetcher.fetch(product_url, verbose=True, return_content=True)
            
            if not html:
                logger.error(f"Failed to fetch product details for URL: {product_url}")
                return None
            
            # Parse detailed product information from Amazon product page
            soup = BeautifulSoup(html, 'html.parser')
            
            # Use extract_document_text() for text content extraction
            text_content = extract_document_text(self.selenium_fetcher)
            
            # Extract product details
            name = self._extract_product_name(soup)
            price = self._extract_price_from_page(soup, text_content)
            original_price = self._extract_original_price(soup)
            image_url = self._extract_image_url(soup)
            stock_status = self._extract_stock_status(soup, text_content)
            variations = self._parse_product_variations(soup)
            
            if not name or not price:
                logger.warning(f"Missing essential product data for URL: {product_url}")
                return None
            
            await self.respect_rate_limit()
            
            return ScrapedProduct(
                name=name,
                price=price,
                original_price=original_price,
                stock_status=stock_status,
                product_url=product_url,
                image_url=image_url,
                variations=variations
            )
            
        except Exception as e:
            logger.error(f"Error getting product details for '{product_url}': {e}")
            return None
    
    def _parse_search_result(self, container) -> Optional[ScrapedProduct]:
        """Parse individual search result container"""
        try:
            # Extract product name
            name_elem = container.find('h2', class_='s-size-mini')
            if not name_elem:
                name_elem = container.find('span', class_='a-size-medium')
            name = name_elem.get_text(strip=True) if name_elem else None
            
            # Extract price
            price_elem = container.find('span', class_='a-price-whole')
            if not price_elem:
                price_elem = container.find('span', class_='a-offscreen')
            price_text = price_elem.get_text(strip=True) if price_elem else None
            price = self.normalize_price(price_text) if price_text else None
            
            # Extract product URL
            link_elem = container.find('h2').find('a') if container.find('h2') else None
            product_url = f"https://www.amazon.com{link_elem['href']}" if link_elem else None
            
            # Extract image URL
            img_elem = container.find('img', class_='s-image')
            image_url = img_elem.get('src') if img_elem else None
            
            if name and price and product_url:
                return ScrapedProduct(
                    name=name,
                    price=price,
                    original_price=None,
                    stock_status="in_stock",
                    product_url=product_url,
                    image_url=image_url,
                    variations=[]
                )
            
        except Exception as e:
            logger.warning(f"Error parsing search result: {e}")
        
        return None
    
    def _extract_product_name(self, soup) -> Optional[str]:
        """Extract product name from product page"""
        selectors = [
            '#productTitle',
            '.product-title',
            'h1.a-size-large'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        
        return None
    
    def _extract_price_from_page(self, soup, text_content: str) -> Optional[Decimal]:
        """Extract price from product page"""
        # Try CSS selectors first
        price_selectors = [
            '.a-price-whole',
            '.a-offscreen',
            '#price_inside_buybox',
            '.a-price .a-offscreen'
        ]
        
        for selector in price_selectors:
            elem = soup.select_one(selector)
            if elem:
                price = self.normalize_price(elem.get_text(strip=True))
                if price:
                    return price
        
        # Fallback to text parsing
        return self._extract_price_from_text(text_content)
    
    def _extract_price_from_text(self, text: str) -> Optional[Decimal]:
        """Parse Amazon price formats from text content"""
        if not text:
            return None
        
        # Amazon price patterns
        price_patterns = [
            r'\$([0-9,]+\.?[0-9]*)',  # $123.45 or $1,234
            r'Price:?\s*\$([0-9,]+\.?[0-9]*)',  # Price: $123.45
            r'([0-9,]+\.?[0-9]*)\s*dollars?',  # 123.45 dollars
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return Decimal(price_str)
                except:
                    continue
        
        return None
    
    def _extract_original_price(self, soup) -> Optional[Decimal]:
        """Extract original/list price if available"""
        selectors = [
            '.a-price.a-text-price .a-offscreen',
            '.a-price-was .a-offscreen'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                price = self.normalize_price(elem.get_text(strip=True))
                if price:
                    return price
        
        return None
    
    def _extract_image_url(self, soup) -> Optional[str]:
        """Extract main product image URL"""
        selectors = [
            '#landingImage',
            '.a-dynamic-image',
            '#imgBlkFront'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get('src') or elem.get('data-src')
        
        return None
    
    def _extract_stock_status(self, soup, text_content: str) -> str:
        """Extract stock status from page"""
        # Check for out of stock indicators
        out_of_stock_indicators = [
            'currently unavailable',
            'out of stock',
            'temporarily out of stock',
            'not available'
        ]
        
        text_lower = text_content.lower()
        for indicator in out_of_stock_indicators:
            if indicator in text_lower:
                return "out_of_stock"
        
        return "in_stock"
    
    def _parse_product_variations(self, soup) -> List[dict]:
        """Extract product variations (color, size, model) from Amazon page"""
        variations = []
        
        # Look for variation selectors
        variation_containers = soup.find_all('div', class_='a-section')
        
        for container in variation_containers:
            # Look for color/size variations
            variation_buttons = container.find_all('li', class_='swatchElement')
            
            for button in variation_buttons:
                try:
                    variation_name = button.get('title', '')
                    variation_price_elem = button.find('span', class_='a-price')
                    variation_price = None
                    
                    if variation_price_elem:
                        price_text = variation_price_elem.get_text(strip=True)
                        variation_price = self.normalize_price(price_text)
                    
                    if variation_name:
                        variations.append({
                            'name': variation_name,
                            'price': float(variation_price) if variation_price else None,
                            'availability': 'in_stock'
                        })
                        
                except Exception as e:
                    logger.warning(f"Error parsing variation: {e}")
                    continue
        
        return variations
    
    def quit_selenium(self):
        """Clean shutdown of selenium resources"""
        if self.selenium_fetcher:
            self.selenium_fetcher.quit()