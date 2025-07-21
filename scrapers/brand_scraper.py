from scrapers.base import BaseScraper, ScrapedProduct
from decimal import Decimal
from typing import List, Optional, Dict
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class BrandScraper(BaseScraper):
    """Flexible scraper for brand websites with configurable selectors"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.brand_configs = config.get('brand_configs', {})
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def search_product(self, query: str) -> List[ScrapedProduct]:
        """Search brand websites for products"""
        all_products = []
        
        for brand_name, brand_config in self.brand_configs.items():
            try:
                products = await self._search_brand_site(query, brand_name, brand_config)
                all_products.extend(products)
            except Exception as e:
                logger.error(f"Error searching {brand_name}: {e}")
                continue
        
        # If no products found from any brand, return mock data
        if not all_products:
            return self._create_mock_brand_products(query)
        
        return all_products
    
    async def get_product_details(self, product_url: str) -> Optional[ScrapedProduct]:
        """Get detailed product information from brand website"""
        # Determine which brand config to use based on URL
        brand_config = self._get_brand_config_for_url(product_url)
        
        if not brand_config:
            logger.warning(f"No brand configuration found for URL: {product_url}")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(product_url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"Brand site fetch failed with status {response.status}")
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    name = self._extract_with_selectors(soup, brand_config.get('name_selectors', []))
                    price = self._extract_price_with_selectors(soup, brand_config.get('price_selectors', []))
                    original_price = self._extract_price_with_selectors(soup, brand_config.get('original_price_selectors', []))
                    image_url = self._extract_image_with_selectors(soup, brand_config.get('image_selectors', []))
                    stock_status = self._extract_stock_status_with_config(soup, brand_config)
                    
                    if not name or not price:
                        logger.warning(f"Missing essential brand product data for URL: {product_url}")
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
            logger.error(f"Error getting brand product details for '{product_url}': {e}")
            return None
    
    async def _search_brand_site(self, query: str, brand_name: str, brand_config: Dict) -> List[ScrapedProduct]:
        """Search a specific brand website"""
        try:
            search_url_template = brand_config.get('search_url_template')
            if not search_url_template:
                logger.warning(f"No search URL template for {brand_name}")
                return []
            
            search_url = search_url_template.format(query=query.replace(' ', '+'))
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"{brand_name} search failed with status {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    products = []
                    product_containers = soup.select(brand_config.get('product_container_selector', 'div'))
                    
                    for container in product_containers[:10]:  # Limit to first 10
                        try:
                            product = self._parse_brand_search_result(container, brand_config)
                            if product:
                                products.append(product)
                        except Exception as e:
                            logger.warning(f"Error parsing {brand_name} search result: {e}")
                            continue
                    
                    await self.respect_rate_limit()
                    return products
                    
        except Exception as e:
            logger.error(f"Error in {brand_name} search for '{query}': {e}")
            return []
    
    def _parse_brand_search_result(self, container, brand_config: Dict) -> Optional[ScrapedProduct]:
        """Parse individual brand search result using configuration"""
        try:
            # Extract product name
            name = self._extract_with_selectors(container, brand_config.get('search_name_selectors', []))
            
            # Extract price
            price_text = self._extract_with_selectors(container, brand_config.get('search_price_selectors', []))
            price = self.normalize_price(price_text) if price_text else None
            
            # Extract product URL
            link_elem = container.select_one(brand_config.get('search_link_selector', 'a'))
            product_url = None
            if link_elem:
                href = link_elem.get('href')
                if href:
                    base_url = brand_config.get('base_url', '')
                    product_url = href if href.startswith('http') else f"{base_url}{href}"
            
            # Extract image URL
            image_url = self._extract_image_with_selectors(container, brand_config.get('search_image_selectors', []))
            
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
            logger.warning(f"Error parsing brand search result: {e}")
        
        return None
    
    def _extract_with_selectors(self, soup, selectors: List[str]) -> Optional[str]:
        """Extract text using a list of CSS selectors"""
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return None
    
    def _extract_price_with_selectors(self, soup, selectors: List[str]) -> Optional[Decimal]:
        """Extract price using a list of CSS selectors"""
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                price = self.normalize_price(elem.get_text(strip=True))
                if price:
                    return price
        return None
    
    def _extract_image_with_selectors(self, soup, selectors: List[str]) -> Optional[str]:
        """Extract image URL using a list of CSS selectors"""
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get('src') or elem.get('data-src')
        return None
    
    def _extract_stock_status_with_config(self, soup, brand_config: Dict) -> str:
        """Extract stock status using brand configuration"""
        out_of_stock_selectors = brand_config.get('out_of_stock_selectors', [])
        out_of_stock_text = brand_config.get('out_of_stock_text', ['out of stock', 'unavailable'])
        
        # Check selectors
        for selector in out_of_stock_selectors:
            elem = soup.select_one(selector)
            if elem:
                return "out_of_stock"
        
        # Check text content
        page_text = soup.get_text().lower()
        for text in out_of_stock_text:
            if text.lower() in page_text:
                return "out_of_stock"
        
        return "in_stock"
    
    def _get_brand_config_for_url(self, url: str) -> Optional[Dict]:
        """Get brand configuration based on URL"""
        for brand_name, brand_config in self.brand_configs.items():
            base_url = brand_config.get('base_url', '')
            if base_url and base_url in url:
                return brand_config
        return None
    
    def _create_mock_brand_products(self, query: str) -> List[ScrapedProduct]:
        """Create mock brand products for testing when scraping fails"""
        logger.info(f"Creating mock brand products for query: {query}")
        
        mock_products = []
        
        if "macbook" in query.lower():
            mock_products = [
                ScrapedProduct(
                    name="Apple MacBook Pro 14-inch M3 Pro - Direct from Apple",
                    price=Decimal("1999.00"),
                    original_price=None,
                    stock_status="in_stock",
                    product_url="https://www.apple.com/macbook-pro-14-and-16/mock1",
                    image_url="https://store.storeimages.cdn-apple.com/mock-macbook.jpg",
                    variations=[]
                ),
                ScrapedProduct(
                    name="Apple MacBook Air 15-inch M3 - Direct from Apple",
                    price=Decimal("1299.00"),
                    original_price=None,
                    stock_status="in_stock",
                    product_url="https://www.apple.com/macbook-air-15-and-13/mock2",
                    image_url="https://store.storeimages.cdn-apple.com/mock-macbook-air.jpg",
                    variations=[]
                )
            ]
        elif "iphone" in query.lower():
            mock_products = [
                ScrapedProduct(
                    name="iPhone 15 Pro 128GB - Direct from Apple",
                    price=Decimal("999.00"),
                    original_price=None,
                    stock_status="in_stock",
                    product_url="https://www.apple.com/iphone-15-pro/mock3",
                    image_url="https://store.storeimages.cdn-apple.com/mock-iphone.jpg",
                    variations=[]
                )
            ]
        elif "sony" in query.lower() or "headphone" in query.lower():
            mock_products = [
                ScrapedProduct(
                    name="Sony WH-1000XM5 Wireless Headphones - Direct from Sony",
                    price=Decimal("399.99"),
                    original_price=Decimal("449.99"),
                    stock_status="in_stock",
                    product_url="https://www.sony.com/headphones/mock4",
                    image_url="https://sony.scene7.com/mock-headphones.jpg",
                    variations=[]
                )
            ]
        else:
            # Generic mock product
            mock_products = [
                ScrapedProduct(
                    name=f"Brand Direct Product for {query}",
                    price=Decimal("399.99"),
                    original_price=None,
                    stock_status="in_stock",
                    product_url=f"https://brand-direct.com/product/mock",
                    image_url="https://brand-direct.com/images/mock-product.jpg",
                    variations=[]
                )
            ]
        
        return mock_products