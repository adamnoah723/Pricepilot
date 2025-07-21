from typing import List, Optional
from bs4 import BeautifulSoup
import re
from .base_parser import BaseParser, ParsedProductData


class WalmartParser(BaseParser):
    """Walmart-specific parser with comprehensive extraction logic"""
    
    def __init__(self):
        super().__init__("Walmart")
    
    def parse_search_results(self, html: str, base_url: str = "https://www.walmart.com") -> List[ParsedProductData]:
        """Parse Walmart search results page using most reliable 2024 selectors"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Walmart search result containers - Updated based on current structure
        # Priority order: most reliable to fallback
        search_containers = [
            'div[data-automation-id="product-tile"]',    # Primary container (most reliable)
            '[data-testid="item-stack"]',                # Test ID based (very reliable)
            '.search-result-gridview-item',              # Grid view format
            '.search-product-result',                    # Alternative search result
            '[data-item-id]',                           # Item ID based containers
            '.mb1.ph1.pa0-xl.bb.b--near-white'         # Walmart's specific styling classes
        ]
        
        containers = []
        for container_selector in search_containers:
            containers = soup.select(container_selector)
            if containers:
                self.logger.info(f"Found {len(containers)} Walmart products using selector: {container_selector}")
                break
        
        if not containers:
            self.logger.warning("No Walmart search result containers found with any selector")
            return products
        
        for container in containers[:15]:  # Limit to first 15 results
            try:
                product_data = self._parse_search_result_item(container, base_url)
                if product_data and product_data.is_valid():
                    products.append(product_data)
            except Exception as e:
                self.logger.warning(f"Error parsing Walmart search result: {e}")
                continue
        
        return products
    
    def _parse_search_result_item(self, container: BeautifulSoup, base_url: str) -> Optional[ParsedProductData]:
        """Parse individual Walmart search result item using 2024 reliable selectors"""
        product = ParsedProductData()
        
        # Extract item ID for tracking (Walmart's unique identifier)
        item_id = container.get('data-item-id') or container.get('data-us-item-id')
        if item_id:
            product.specifications = {'item_id': item_id}
        
        # Extract product name - Updated selectors based on current Walmart structure
        name_selectors = [
            'span[data-automation-id="product-title"]',    # Primary title (most reliable)
            'a[data-automation-id="product-title"]',       # Title link format
            '[data-testid="product-title"]',               # Test ID based (very reliable)
            '.product-title-link span',                    # Alternative title link
            '.search-product-title',                       # Search specific title
            'h3[data-automation-id="product-title"]',      # Header format
            '.normal.dark-gray.mb0.mt1.lh-title'          # Walmart's specific styling classes
        ]
        product.name = self.extract_text_by_selectors(container, name_selectors)
        if product.name:
            product.name = self.clean_product_name(product.name)
            product.brand = self.extract_brand_from_name(product.name)
        
        # Extract price - Walmart's most reliable price selectors (2024)
        price_selectors = [
            'span[itemprop="price"]',                      # Schema.org price (most reliable)
            'div[data-automation-id="product-price"] span', # Automation ID based
            '[data-testid="price-current"]',               # Test ID based pricing
            '.price-current',                              # Current price class
            '.price-main .visuallyhidden',                 # Hidden accessible price
            '.f2.b.black.lh-copy.f1-l',                   # Walmart's price styling
            '.price-group .price-current'                  # Price group format
        ]
        price_text = self.extract_text_by_selectors(container, price_selectors)
        product.price = self.normalize_price(price_text) if price_text else None
        
        # Extract original price (if on sale)
        original_price_selectors = [
            '.price-was',
            '.price-old',
            '.strikethrough',
            'span[data-automation-id="product-price-strikethrough"]'
        ]
        original_price_text = self.extract_text_by_selectors(container, original_price_selectors)
        product.original_price = self.normalize_price(original_price_text) if original_price_text else None
        
        # Extract product URL
        link_selectors = [
            'a[data-automation-id="product-title"]',
            '.product-title-link',
            '.search-product-title a'
        ]
        href = self.extract_attribute_by_selectors(container, link_selectors, 'href')
        if href:
            product.product_url = f"{base_url}{href}" if href.startswith('/') else href
        
        # Extract image URL
        image_selectors = [
            'img[data-automation-id="product-image"]',
            '.product-image img',
            '.search-product-image img'
        ]
        product.image_url = self.extract_attribute_by_selectors(container, image_selectors, 'src')
        if not product.image_url:
            product.image_url = self.extract_attribute_by_selectors(container, image_selectors, 'data-src')
        
        # Extract rating
        rating_selectors = [
            '.average-rating .visuallyhidden',
            'span[data-testid="reviews-section"] .visuallyhidden',
            '.stars-reviews-count-node .visuallyhidden'
        ]
        rating_text = self.extract_text_by_selectors(container, rating_selectors)
        if rating_text:
            rating_match = re.search(r'(\d+\.?\d*)\s*out of', rating_text)
            if rating_match:
                try:
                    product.rating = float(rating_match.group(1))
                except:
                    pass
        
        # Extract review count
        review_selectors = [
            '.reviews-count',
            'span[data-testid="reviews-section"]',
            '.stars-reviews-count-node'
        ]
        review_text = self.extract_text_by_selectors(container, review_selectors)
        if review_text:
            review_match = re.search(r'([\d,]+)', review_text.replace(',', ''))
            if review_match:
                try:
                    product.review_count = int(review_match.group(1))
                except:
                    pass
        
        # Calculate discount
        product.calculate_discount()
        
        return product
    
    def parse_product_page(self, html: str, product_url: str) -> ParsedProductData:
        """Parse Walmart product detail page"""
        soup = BeautifulSoup(html, 'html.parser')
        product = ParsedProductData()
        product.product_url = product_url
        
        # Extract product name
        name_selectors = [
            'h1[data-automation-id="product-title"]',
            'h1.prod-ProductTitle',
            'h1.f2',
            '.prod-product-title-label h1'
        ]
        product.name = self.extract_text_by_selectors(soup, name_selectors)
        if product.name:
            product.name = self.clean_product_name(product.name)
            product.brand = self.extract_brand_from_name(product.name)
        
        # Extract current price
        price_selectors = [
            'span[itemprop="price"]',
            '.price-current .price-now',
            '.price-group .price-current',
            'div[data-testid="price-wrap"] span'
        ]
        price_text = self.extract_text_by_selectors(soup, price_selectors)
        product.price = self.normalize_price(price_text) if price_text else None
        
        # Extract original price
        original_price_selectors = [
            '.price-was',
            '.price-old',
            '.strikethrough',
            'span[data-automation-id="product-price-strikethrough"]'
        ]
        original_price_text = self.extract_text_by_selectors(soup, original_price_selectors)
        product.original_price = self.normalize_price(original_price_text) if original_price_text else None
        
        # Extract main image
        image_selectors = [
            '.prod-hero-image img',
            '.hero-image img',
            '.product-image img',
            'img[data-testid="hero-image"]'
        ]
        product.image_url = self.extract_attribute_by_selectors(soup, image_selectors, 'src')
        if not product.image_url:
            product.image_url = self.extract_attribute_by_selectors(soup, image_selectors, 'data-src')
        
        # Extract brand (more specific for product page)
        brand_selectors = [
            '.prod-brand a',
            'span[data-automation-id="product-brand"]',
            '.brand-name'
        ]
        brand_text = self.extract_text_by_selectors(soup, brand_selectors)
        if brand_text and not product.brand:
            product.brand = brand_text.strip()
        
        # Extract stock status
        product.stock_status = self._determine_walmart_stock_status(soup)
        
        # Extract rating and reviews
        rating_selectors = [
            '.average-rating .visuallyhidden',
            'span[data-testid="reviews-section"] .visuallyhidden',
            '.stars-reviews-count-node .visuallyhidden'
        ]
        rating_text = self.extract_text_by_selectors(soup, rating_selectors)
        if rating_text:
            rating_match = re.search(r'(\d+\.?\d*)\s*out of', rating_text)
            if rating_match:
                try:
                    product.rating = float(rating_match.group(1))
                except:
                    pass
        
        # Extract review count
        review_selectors = [
            '.reviews-count',
            'span[data-testid="reviews-section"]',
            '.stars-reviews-count-node',
            'button[data-testid="reviews-section"]'
        ]
        review_text = self.extract_text_by_selectors(soup, review_selectors)
        if review_text:
            review_match = re.search(r'([\d,]+)', review_text.replace(',', ''))
            if review_match:
                try:
                    product.review_count = int(review_match.group(1))
                except:
                    pass
        
        # Extract specifications
        product.specifications = self._extract_walmart_specifications(soup)
        
        # Calculate discount
        product.calculate_discount()
        
        return product
    
    def _determine_walmart_stock_status(self, soup: BeautifulSoup) -> str:
        """Determine Walmart specific stock status"""
        # Check for add to cart button
        add_to_cart_button = soup.find('button', {'data-automation-id': 'add-to-cart'})
        if add_to_cart_button and 'disabled' in add_to_cart_button.get('class', []):
            return "out_of_stock"
        
        # Check for availability text
        availability_indicators = [
            'out of stock', 'sold out', 'unavailable', 'not available',
            'temporarily unavailable', 'limited stock'
        ]
        
        page_text = soup.get_text().lower()
        for indicator in availability_indicators:
            if indicator in page_text:
                if indicator == 'limited stock':
                    return "limited_stock"
                else:
                    return "out_of_stock"
        
        # Check for pickup/delivery availability
        pickup_elem = soup.find('div', {'data-testid': 'fulfillment-pickup'})
        delivery_elem = soup.find('div', {'data-testid': 'fulfillment-shipping'})
        
        if pickup_elem or delivery_elem:
            return "in_stock"
        
        return "in_stock"
    
    def _extract_walmart_specifications(self, soup: BeautifulSoup) -> dict:
        """Extract Walmart product specifications"""
        specs = {}
        
        # Look for specification tables
        spec_tables = soup.find_all('table', class_='specifications-table')
        
        for table in spec_tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        specs[key] = value
        
        # Look for product highlights
        highlights = soup.find_all('div', class_='product-highlights')
        features = []
        for highlight in highlights:
            bullets = highlight.find_all('li')
            for bullet in bullets:
                text = bullet.get_text(strip=True)
                if text and len(text) > 10:
                    features.append(text)
        
        if features:
            specs['highlights'] = features[:5]
        
        # Look for product details section
        details_section = soup.find('div', {'data-testid': 'product-details'})
        if details_section:
            detail_items = details_section.find_all('div', class_='detail-item')
            for item in detail_items:
                try:
                    key_elem = item.find('span', class_='detail-label')
                    value_elem = item.find('span', class_='detail-value')
                    
                    if key_elem and value_elem:
                        key = key_elem.get_text(strip=True)
                        value = value_elem.get_text(strip=True)
                        if key and value:
                            specs[key] = value
                except Exception as e:
                    self.logger.debug(f"Error parsing detail: {e}")
                    continue
        
        return specs