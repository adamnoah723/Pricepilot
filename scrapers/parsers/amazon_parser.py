from typing import List, Optional
from bs4 import BeautifulSoup
import re
from .base_parser import BaseParser, ParsedProductData


class AmazonParser(BaseParser):
    """Amazon-specific parser with comprehensive extraction logic"""
    
    def __init__(self):
        super().__init__("Amazon")
    
    def parse_search_results(self, html: str, base_url: str = "https://www.amazon.com") -> List[ParsedProductData]:
        """Parse Amazon search results page using most reliable selectors"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Amazon search result containers - Updated based on 2024 structure
        # Priority order: most reliable to fallback
        search_containers = [
            'div[data-component-type="s-search-result"]',  # Primary container (most reliable)
            'div[data-asin]:not([data-asin=""])',          # ASIN-based containers
            '.s-result-item[data-asin]',                   # Legacy but still used
            '.s-widget-container .s-result-item',          # Widget containers
            '[data-cy="title-recipe-card"]'                # Recipe cards for some categories
        ]
        
        containers = []
        for container_selector in search_containers:
            containers = soup.select(container_selector)
            if containers:
                self.logger.info(f"Found {len(containers)} Amazon products using selector: {container_selector}")
                break
        
        if not containers:
            self.logger.warning("No Amazon search result containers found with any selector")
            return products
        
        for container in containers[:15]:  # Limit to first 15 results
            try:
                product_data = self._parse_search_result_item(container, base_url)
                if product_data and product_data.is_valid():
                    products.append(product_data)
            except Exception as e:
                self.logger.warning(f"Error parsing Amazon search result: {e}")
                continue
        
        return products
    
    def _parse_search_result_item(self, container: BeautifulSoup, base_url: str) -> Optional[ParsedProductData]:
        """Parse individual Amazon search result item using most reliable 2024 selectors"""
        product = ParsedProductData()
        
        # Extract ASIN for tracking (Amazon's unique identifier)
        asin = container.get('data-asin')
        if asin:
            product.specifications = {'asin': asin}
        
        # Extract product name - Updated selectors based on current Amazon structure
        name_selectors = [
            'h2.a-size-mini span',                    # Most common current structure
            'h2 a span[aria-label]',                  # Accessible name with aria-label
            'h2.s-size-mini span',                    # Alternative structure
            '.s-size-medium.s-inline.s-color-base',  # Fallback for older layouts
            'h2 a .a-truncate-cut',                   # Truncated titles
            '[data-cy="title-recipe-card"] h2'       # Recipe card format
        ]
        product.name = self.extract_text_by_selectors(container, name_selectors)
        if product.name:
            product.name = self.clean_product_name(product.name)
            product.brand = self.extract_brand_from_name(product.name)
        
        # Extract price - Amazon's most reliable price selectors (2024)
        price_selectors = [
            '.a-price .a-offscreen',                  # Hidden price for screen readers (most reliable)
            '.a-price-whole',                         # Whole dollar amount
            '.a-price-range .a-offscreen',           # Price range format
            'span.a-price-symbol + span',            # Symbol + price combination
            '.a-price .a-price-whole',               # Nested price structure
            '[data-a-color="price"] .a-offscreen'    # Color-coded price
        ]
        price_text = self.extract_text_by_selectors(container, price_selectors)
        product.price = self.normalize_price(price_text) if price_text else None
        
        # Extract original price (if on sale)
        original_price_selectors = [
            '.a-price.a-text-price .a-offscreen',
            '.a-price-was .a-offscreen',
            'span[data-a-strike="true"]'
        ]
        original_price_text = self.extract_text_by_selectors(container, original_price_selectors)
        product.original_price = self.normalize_price(original_price_text) if original_price_text else None
        
        # Extract product URL - Amazon's most reliable link selectors
        link_selectors = [
            'h2 a',                                   # Most common - title link
            '.s-link-style a',                        # Link style class
            'a[data-cy="title-recipe-card"]',        # Recipe card links
            '.a-link-normal',                         # Normal Amazon links
            'a[href*="/dp/"]',                        # Direct product links
            'a[href*="/gp/product/"]'                 # Alternative product links
        ]
        
        href = None
        for selector in link_selectors:
            try:
                elem = container.select_one(selector)
                if elem and elem.get('href'):
                    href = elem.get('href')
                    # Validate it's a product link
                    if '/dp/' in href or '/gp/product/' in href:
                        break
            except Exception:
                continue
        
        if href:
            # Clean and normalize the URL
            if href.startswith('/'):
                product.product_url = f"{base_url}{href}"
            elif href.startswith('http'):
                product.product_url = href
            else:
                product.product_url = f"{base_url}/{href}"
            
            # Remove tracking parameters and clean URL
            if '?' in product.product_url:
                product.product_url = product.product_url.split('?')[0]
            if '/ref=' in product.product_url:
                product.product_url = product.product_url.split('/ref=')[0]
            
            # Extract ASIN and create clean direct URL
            import re
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', product.product_url)
            if asin_match:
                asin = asin_match.group(1)
                product.product_url = f"{base_url}/dp/{asin}"
                # Store ASIN in specifications for reference
                if not product.specifications:
                    product.specifications = {}
                product.specifications['asin'] = asin
        
        # Extract image URL
        image_selectors = [
            '.s-image',
            'img.s-image',
            '.a-dynamic-image'
        ]
        product.image_url = self.extract_attribute_by_selectors(container, image_selectors, 'src')
        
        # Extract rating
        rating_selectors = [
            '.a-icon-alt',
            'span.a-icon-alt'
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
            'a[href*="#customerReviews"] span',
            '.a-size-base'
        ]
        review_text = self.extract_text_by_selectors(container, review_selectors)
        if review_text:
            review_match = re.search(r'([\d,]+)', review_text.replace(',', ''))
            if review_match:
                try:
                    product.review_count = int(review_match.group(1))
                except:
                    pass
        
        # Calculate discount if both prices exist
        product.calculate_discount()
        
        return product
    
    def parse_product_page(self, html: str, product_url: str) -> ParsedProductData:
        """Parse Amazon product detail page"""
        soup = BeautifulSoup(html, 'html.parser')
        product = ParsedProductData()
        product.product_url = product_url
        
        # Extract product name
        name_selectors = [
            '#productTitle',
            '.product-title',
            'h1.a-size-large',
            'h1[data-automation-id="productTitle"]'
        ]
        product.name = self.extract_text_by_selectors(soup, name_selectors)
        if product.name:
            product.name = self.clean_product_name(product.name)
            product.brand = self.extract_brand_from_name(product.name)
        
        # Extract current price
        price_selectors = [
            '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
            '#price_inside_buybox',
            '.a-price .a-offscreen',
            '.a-price-whole'
        ]
        price_text = self.extract_text_by_selectors(soup, price_selectors)
        product.price = self.normalize_price(price_text) if price_text else None
        
        # Fallback: Extract price from text content
        if not product.price:
            product.price = self._extract_price_from_text_content(html)
        
        # Extract original price
        original_price_selectors = [
            '.a-price.a-text-price .a-offscreen',
            '.a-price-was .a-offscreen',
            'span.a-price-list .a-offscreen'
        ]
        original_price_text = self.extract_text_by_selectors(soup, original_price_selectors)
        product.original_price = self.normalize_price(original_price_text) if original_price_text else None
        
        # Extract main image
        image_selectors = [
            '#landingImage',
            '.a-dynamic-image',
            '#imgBlkFront',
            '.a-dynamic-image.a-stretch-horizontal'
        ]
        product.image_url = self.extract_attribute_by_selectors(soup, image_selectors, 'src')
        if not product.image_url:
            product.image_url = self.extract_attribute_by_selectors(soup, image_selectors, 'data-src')
        
        # Extract brand (more specific for product page)
        brand_selectors = [
            '#bylineInfo',
            '.a-size-base.po-brand .a-size-base',
            'tr.a-spacing-small td.a-span9 span'
        ]
        brand_text = self.extract_text_by_selectors(soup, brand_selectors)
        if brand_text and not product.brand:
            # Clean brand text (remove "Brand:", "Visit the", "Store", etc.)
            brand_clean = re.sub(r'(Brand:|Visit the|Store)', '', brand_text, flags=re.IGNORECASE).strip()
            product.brand = brand_clean if brand_clean else product.brand
        
        # Extract stock status
        product.stock_status = self.determine_stock_status(soup, html)
        
        # Extract rating and reviews
        rating_selectors = [
            '.a-icon-alt',
            'span.a-icon-alt'
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
            '#acrCustomerReviewText',
            'a[href*="#customerReviews"]'
        ]
        review_text = self.extract_text_by_selectors(soup, review_selectors)
        if review_text:
            review_match = re.search(r'([\d,]+)', review_text.replace(',', ''))
            if review_match:
                try:
                    product.review_count = int(review_match.group(1))
                except:
                    pass
        
        # Extract product variations
        product.variations = self._extract_variations(soup)
        
        # Extract specifications
        product.specifications = self._extract_specifications(soup)
        
        # Calculate discount
        product.calculate_discount()
        
        return product
    
    def _extract_price_from_text_content(self, html: str) -> Optional[float]:
        """Fallback method to extract price from raw text content"""
        # Amazon price patterns in text
        price_patterns = [
            r'\$([0-9,]+\.?[0-9]*)',
            r'Price:?\s*\$([0-9,]+\.?[0-9]*)',
            r'([0-9,]+\.?[0-9]*)\s*dollars?'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    price_str = match.group(1).replace(',', '')
                    return self.normalize_price(price_str)
                except:
                    continue
        
        return None
    
    def _extract_variations(self, soup: BeautifulSoup) -> List[dict]:
        """Extract product variations (color, size, model)"""
        variations = []
        
        # Look for variation containers
        variation_containers = soup.find_all('div', class_='a-section')
        
        for container in variation_containers:
            # Color/style variations
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
                            'availability': 'in_stock',
                            'type': 'color'
                        })
                        
                except Exception as e:
                    self.logger.debug(f"Error parsing variation: {e}")
                    continue
        
        return variations
    
    def _extract_specifications(self, soup: BeautifulSoup) -> dict:
        """Extract product specifications"""
        specs = {}
        
        # Look for specification tables
        spec_tables = soup.find_all('table', {'id': 'productDetails_techSpec_section_1'})
        
        for table in spec_tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        specs[key] = value
        
        # Also look for feature bullets
        feature_bullets = soup.find_all('span', class_='a-list-item')
        features = []
        for bullet in feature_bullets:
            text = bullet.get_text(strip=True)
            if text and len(text) > 10:  # Filter out short/empty bullets
                features.append(text)
        
        if features:
            specs['features'] = features[:5]  # Limit to first 5 features
        
        return specs