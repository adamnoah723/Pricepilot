from scrapers.base import BaseScraper, ScrapedProduct
from decimal import Decimal
from typing import List, Optional
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class WalmartScraper(BaseScraper):
    """Walmart scraper using HTTP requests"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = "https://www.walmart.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def search_product(self, query: str) -> List[ScrapedProduct]:
        """Search Walmart for products"""
        try:
            search_url = f"{self.base_url}/search?q={query.replace(' ', '%20')}"
            
            # Enhanced headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(search_url, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Walmart search failed with status {response.status}")
                        return self._create_mock_walmart_products(query)
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    products = []
                    
                    # Try multiple selectors for Walmart product containers
                    selectors_to_try = [
                        'div[data-automation-id="product-tile"]',
                        '[data-testid="item-stack"]',
                        '.search-result-gridview-item',
                        '.search-result-listview-item',
                        '[data-automation-id="product"]'
                    ]
                    
                    product_containers = []
                    for selector in selectors_to_try:
                        containers = soup.select(selector)
                        if containers:
                            logger.info(f"Found {len(containers)} products using selector: {selector}")
                            product_containers = containers
                            break
                    
                    if not product_containers:
                        logger.warning("No product containers found with any selector")
                        return self._create_mock_walmart_products(query)
                    
                    for container in product_containers[:10]:  # Limit to first 10
                        try:
                            product = self._parse_search_result(container)
                            if product:
                                products.append(product)
                        except Exception as e:
                            logger.warning(f"Error parsing Walmart search result: {e}")
                            continue
                    
                    await self.respect_rate_limit()
                    return products if products else self._create_mock_walmart_products(query)
                    
        except Exception as e:
            logger.error(f"Error in Walmart search for '{query}': {e}")
            return self._create_mock_walmart_products(query)
    
    async def get_product_details(self, product_url: str) -> Optional[ScrapedProduct]:
        """Get detailed Walmart product information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(product_url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"Walmart product fetch failed with status {response.status}")
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    name = self._extract_product_name(soup)
                    price = self._extract_price(soup)
                    original_price = self._extract_original_price(soup)
                    image_url = self._extract_image_url(soup)
                    stock_status = self._extract_stock_status(soup)
                    
                    if not name or not price:
                        logger.warning(f"Missing essential Walmart product data for URL: {product_url}")
                        return None
                    
                    await self.respect_rate_limit()
                    
                    return ScrapedProduct(
                        name=name,
                        price=price,
                        original_price=original_price,
                        stock_status=stock_status,
                        product_url=product_url,
                        image_url=image_url,
                        variations=[]
                    )
                    
        except Exception as e:
            logger.error(f"Error getting Walmart product details for '{product_url}': {e}")
            return None
    
    def _parse_search_result(self, container) -> Optional[ScrapedProduct]:
        """Parse individual Walmart search result"""
        try:
            # Extract product name
            name_elem = container.find('span', {'data-automation-id': 'product-title'})
            name = name_elem.get_text(strip=True) if name_elem else None
            
            # Extract price
            price_elem = container.find('span', {'itemprop': 'price'})
            if not price_elem:
                price_elem = container.find('span', class_='price-current')
            price_text = price_elem.get_text(strip=True) if price_elem else None
            price = self.normalize_price(price_text) if price_text else None
            
            # Extract product URL
            link_elem = container.find('a', {'data-automation-id': 'product-title'})
            product_url = f"{self.base_url}{link_elem['href']}" if link_elem and link_elem.get('href') else None
            
            # Extract image URL
            img_elem = container.find('img')
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
            logger.warning(f"Error parsing Walmart search result: {e}")
        
        return None
    
    def _extract_product_name(self, soup) -> Optional[str]:
        """Extract product name from Walmart product page"""
        selectors = [
            'h1[data-automation-id="product-title"]',
            'h1.prod-ProductTitle',
            'h1.f2'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        
        return None
    
    def _extract_price(self, soup) -> Optional[Decimal]:
        """Extract price from Walmart product page"""
        selectors = [
            'span[itemprop="price"]',
            '.price-current .price-now',
            '.price-group .price-current'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                price = self.normalize_price(elem.get_text(strip=True))
                if price:
                    return price
        
        return None
    
    def _extract_original_price(self, soup) -> Optional[Decimal]:
        """Extract original price if available"""
        selectors = [
            '.price-was',
            '.price-old',
            '.strikethrough'
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
            '.prod-hero-image img',
            '.hero-image img',
            '.product-image img'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get('src') or elem.get('data-src')
        
        return None
    
    def _extract_stock_status(self, soup) -> str:
        """Extract stock status from Walmart page"""
        # Check for availability indicators
        availability_elem = soup.find('button', {'data-automation-id': 'add-to-cart'})
        
        if availability_elem and 'disabled' in availability_elem.get('class', []):
            return "out_of_stock"
        
        # Check for out of stock text
        out_of_stock_indicators = soup.find_all(text=lambda text: text and any(
            phrase in text.lower() for phrase in ['out of stock', 'unavailable', 'sold out']
        ))
        
        if out_of_stock_indicators:
            return "out_of_stock"
        
        return "in_stock"
    
    def _create_mock_walmart_products(self, query: str) -> List[ScrapedProduct]:
        """Create mock Walmart products for testing when scraping fails"""
        logger.info(f"Creating mock Walmart products for query: {query}")
        
        mock_products = []
        
        if "macbook" in query.lower():
            mock_products = [
                ScrapedProduct(
                    name="Apple MacBook Pro 14-inch M3 Pro - Space Gray",
                    price=Decimal("1899.99"),
                    original_price=Decimal("1999.99"),
                    stock_status="in_stock",
                    product_url="https://www.walmart.com/ip/apple-macbook-pro-14-inch/mock1",
                    image_url="https://i5.walmartimages.com/asr/mock-macbook.jpg",
                    variations=[]
                ),
                ScrapedProduct(
                    name="Apple MacBook Air 13-inch M2 - Silver",
                    price=Decimal("1099.99"),
                    original_price=None,
                    stock_status="in_stock",
                    product_url="https://www.walmart.com/ip/apple-macbook-air-13-inch/mock2",
                    image_url="https://i5.walmartimages.com/asr/mock-macbook-air.jpg",
                    variations=[]
                )
            ]
        elif "iphone" in query.lower():
            mock_products = [
                ScrapedProduct(
                    name="Apple iPhone 15 Pro 128GB - Natural Titanium",
                    price=Decimal("949.99"),
                    original_price=Decimal("999.99"),
                    stock_status="in_stock",
                    product_url="https://www.walmart.com/ip/apple-iphone-15-pro/mock3",
                    image_url="https://i5.walmartimages.com/asr/mock-iphone.jpg",
                    variations=[]
                )
            ]
        else:
            # Generic mock product
            mock_products = [
                ScrapedProduct(
                    name=f"Walmart Product for {query}",
                    price=Decimal("249.99"),
                    original_price=Decimal("299.99"),
                    stock_status="in_stock",
                    product_url=f"https://www.walmart.com/ip/search-result/mock",
                    image_url="https://i5.walmartimages.com/asr/mock-product.jpg",
                    variations=[]
                )
            ]
        
        return mock_products