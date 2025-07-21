from typing import List, Optional
from bs4 import BeautifulSoup
import re
from .base_parser import BaseParser, ParsedProductData


class BestBuyParser(BaseParser):
    """Best Buy-specific parser with comprehensive extraction logic"""
    
    def __init__(self):
        super().__init__("BestBuy")
    
    def parse_search_results(self, html: str, base_url: str = "https://www.bestbuy.com") -> List[ParsedProductData]:
        """Parse Best Buy search results page using most reliable 2024 selectors"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Best Buy search result containers - Updated based on current structure
        # Priority order: most reliable to fallback
        search_containers = [
            'li.sku-item',                           # Primary container (most reliable)
            '.product-item-wrapper',                 # Wrapper containers
            '[data-testid="product-card"]',         # Test ID based (very reliable)
            '.list-item',                           # List view format
            '.product-tile',                        # Tile view format
            '.sr-item'                              # Search result item fallback
        ]
        
        containers = []
        for container_selector in search_containers:
            containers = soup.select(container_selector)
            if containers:
                self.logger.info(f"Found {len(containers)} Best Buy products using selector: {container_selector}")
                break
        
        if not containers:
            self.logger.warning("No Best Buy search result containers found with any selector")
            return products
        
        for container in containers[:15]:  # Limit to first 15 results
            try:
                product_data = self._parse_search_result_item(container, base_url)
                if product_data and product_data.is_valid():
                    products.append(product_data)
            except Exception as e:
                self.logger.warning(f"Error parsing Best Buy search result: {e}")
                continue
        
        return products
    
    def _parse_search_result_item(self, container: BeautifulSoup, base_url: str) -> Optional[ParsedProductData]:
        """Parse individual Best Buy search result item using 2024 reliable selectors"""
        product = ParsedProductData()
        
        # Extract SKU for tracking (Best Buy's unique identifier)
        sku = container.get('data-sku-id') or container.get('data-testid')
        if sku:
            product.specifications = {'sku': sku}
        
        # Extract product name - Updated selectors based on current Best Buy structure
        name_selectors = [
            'h4.sr-only',                            # Screen reader optimized (most reliable)
            '.sku-title a',                          # Direct title link
            '.sku-header a',                         # Header link format
            'h4.sku-title',                          # Direct title element
            '[data-testid="product-title"]',         # Test ID based (very reliable)
            '.product-title-link',                   # Alternative title link
            'a[title]'                               # Fallback to any link with title
        ]
        product.name = self.extract_text_by_selectors(container, name_selectors)
        
        # Fallback: Try getting from title attribute of image link
        if not product.name:
            link_elem = container.find('a', class_='image-link')
            if link_elem and link_elem.get('title'):
                product.name = link_elem.get('title')
        
        if product.name:
            product.name = self.clean_product_name(product.name)
            product.brand = self.extract_brand_from_name(product.name)
        
        # Extract price - Best Buy's most reliable price selectors (2024)
        price_selectors = [
            '.pricing-price__range .sr-only',        # Screen reader price (most reliable)
            '.visuallyhidden',                       # Hidden accessible text
            '.sr-only',                              # General screen reader text
            '.pricing-current-price .sr-only',       # Current price screen reader
            '[data-testid="pricing-price"] .sr-only', # Test ID based pricing
            '.price-current .sr-only',               # Alternative current price
            '.price .visuallyhidden'                 # Price with hidden text
        ]
        
        # Best Buy often hides actual prices in screen reader text for accessibility
        for selector in price_selectors:
            price_elem = container.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Look for price indicators in the text
                if any(indicator in price_text.lower() for indicator in ['current price', '$', 'price']):
                    product.price = self.normalize_price(price_text)
                    if product.price:
                        break
        
        # Extract original price (if on sale)
        original_price_selectors = [
            '.pricing-price__range-max .sr-only',
            '.sr-only:contains("was")',
            '.pricing-was-price .sr-only'
        ]
        original_price_text = self.extract_text_by_selectors(container, original_price_selectors)
        product.original_price = self.normalize_price(original_price_text) if original_price_text else None
        
        # Extract product URL
        link_selectors = [
            'a.image-link',
            '.sku-header a',
            '.sku-title a'
        ]
        href = self.extract_attribute_by_selectors(container, link_selectors, 'href')
        if href:
            product.product_url = f"{base_url}{href}" if href.startswith('/') else href
        
        # Extract image URL
        image_selectors = [
            '.product-image img',
            'img.product-image',
            '.sku-image img'
        ]
        product.image_url = self.extract_attribute_by_selectors(container, image_selectors, 'src')
        if not product.image_url:
            product.image_url = self.extract_attribute_by_selectors(container, image_selectors, 'data-src')
        
        # Extract rating
        rating_selectors = [
            '.sr-only[aria-label*="rating"]',
            '.visuallyhidden[aria-label*="rating"]'
        ]
        rating_text = self.extract_text_by_selectors(container, rating_selectors)
        if rating_text:
            rating_match = re.search(r'(\d+\.?\d*)\s*out of', rating_text)
            if rating_match:
                try:
                    product.rating = float(rating_match.group(1))
                except:
                    pass
        
        # Calculate discount
        product.calculate_discount()
        
        return product
    
    def parse_product_page(self, html: str, product_url: str) -> ParsedProductData:
        """Parse Best Buy product detail page"""
        soup = BeautifulSoup(html, 'html.parser')
        product = ParsedProductData()
        product.product_url = product_url
        
        # Extract product name
        name_selectors = [
            'h1.heading-5',
            '.sku-title h1',
            'h1[data-automation-id="product-title"]',
            '.pdp-product-name h1'
        ]
        product.name = self.extract_text_by_selectors(soup, name_selectors)
        if product.name:
            product.name = self.clean_product_name(product.name)
            product.brand = self.extract_brand_from_name(product.name)
        
        # Extract current price
        price_selectors = [
            '.pricing-price__range .sr-only',
            '.sr-only:contains("current price")',
            '.visuallyhidden:contains("current price")',
            '.pricing-current-price .sr-only'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                if 'current price' in price_text.lower():
                    product.price = self.normalize_price(price_text)
                    if product.price:
                        break
        
        # Extract original price
        original_price_selectors = [
            '.pricing-price__range-max .sr-only',
            '.sr-only:contains("was")',
            '.pricing-was-price .sr-only'
        ]
        original_price_text = self.extract_text_by_selectors(soup, original_price_selectors)
        product.original_price = self.normalize_price(original_price_text) if original_price_text else None
        
        # Extract main image
        image_selectors = [
            '.primary-image img',
            '.hero-image img',
            '.product-image img',
            '.pdp-hero-image img'
        ]
        product.image_url = self.extract_attribute_by_selectors(soup, image_selectors, 'src')
        if not product.image_url:
            product.image_url = self.extract_attribute_by_selectors(soup, image_selectors, 'data-src')
        
        # Extract brand (more specific for product page)
        brand_selectors = [
            '.sr-only:contains("Brand")',
            '.product-brand',
            '.brand-name'
        ]
        brand_text = self.extract_text_by_selectors(soup, brand_selectors)
        if brand_text and not product.brand:
            brand_clean = re.sub(r'Brand:', '', brand_text, flags=re.IGNORECASE).strip()
            product.brand = brand_clean if brand_clean else product.brand
        
        # Extract stock status
        product.stock_status = self._determine_bestbuy_stock_status(soup)
        
        # Extract rating and reviews
        rating_selectors = [
            '.sr-only[aria-label*="rating"]',
            '.visuallyhidden[aria-label*="rating"]',
            '.average-rating .sr-only'
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
            '.sr-only:contains("reviews")',
            '.review-count',
            '.number-of-reviews'
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
        product.specifications = self._extract_bestbuy_specifications(soup)
        
        # Calculate discount
        product.calculate_discount()
        
        return product
    
    def _determine_bestbuy_stock_status(self, soup: BeautifulSoup) -> str:
        """Determine Best Buy specific stock status"""
        # Check for add to cart button
        add_to_cart_button = soup.find('button', class_='add-to-cart-button')
        if add_to_cart_button and 'disabled' in add_to_cart_button.get('class', []):
            return "out_of_stock"
        
        # Check for availability text
        availability_indicators = [
            'out of stock', 'sold out', 'unavailable', 'not available',
            'coming soon', 'pre-order'
        ]
        
        page_text = soup.get_text().lower()
        for indicator in availability_indicators:
            if indicator in page_text:
                if indicator in ['coming soon', 'pre-order']:
                    return "pre_order"
                else:
                    return "out_of_stock"
        
        return "in_stock"
    
    def _extract_bestbuy_specifications(self, soup: BeautifulSoup) -> dict:
        """Extract Best Buy product specifications"""
        specs = {}
        
        # Look for specification sections
        spec_sections = soup.find_all('div', class_='specification-section')
        
        for section in spec_sections:
            spec_items = section.find_all('div', class_='specification-item')
            for item in spec_items:
                try:
                    key_elem = item.find('div', class_='specification-label')
                    value_elem = item.find('div', class_='specification-value')
                    
                    if key_elem and value_elem:
                        key = key_elem.get_text(strip=True)
                        value = value_elem.get_text(strip=True)
                        if key and value:
                            specs[key] = value
                except Exception as e:
                    self.logger.debug(f"Error parsing specification: {e}")
                    continue
        
        # Also look for key features
        feature_bullets = soup.find_all('li', class_='key-feature')
        features = []
        for bullet in feature_bullets:
            text = bullet.get_text(strip=True)
            if text and len(text) > 10:
                features.append(text)
        
        if features:
            specs['key_features'] = features[:5]
        
        return specs