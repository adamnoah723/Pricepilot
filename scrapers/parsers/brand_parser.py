from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import re
from .base_parser import BaseParser, ParsedProductData


class BrandParser(BaseParser):
    """Generic brand website parser with configurable selectors"""
    
    def __init__(self, brand_config: Dict[str, Any]):
        super().__init__(f"Brand-{brand_config.get('name', 'Generic')}")
        self.config = brand_config
        self.brand_name = brand_config.get('name', 'Unknown')
        self.base_url = brand_config.get('base_url', '')
        
        # Default selectors that work for many brand sites
        self.default_selectors = {
            'search_results': {
                'container': ['.product-item', '.product-card', '.product-tile', '.product'],
                'name': ['h2', 'h3', '.product-title', '.product-name', '.title'],
                'price': ['.price', '.product-price', '.cost', '.amount'],
                'original_price': ['.original-price', '.was-price', '.old-price', '.strikethrough'],
                'link': ['a', '.product-link'],
                'image': ['img', '.product-image img', '.image img']
            },
            'product_page': {
                'name': ['h1', '.product-title', '.product-name', '.page-title'],
                'price': ['.price', '.product-price', '.current-price', '.cost'],
                'original_price': ['.original-price', '.was-price', '.old-price', '.strikethrough'],
                'image': ['.product-image img', '.hero-image img', '.main-image img', 'img.primary'],
                'description': ['.product-description', '.description', '.product-details'],
                'specifications': ['.specs', '.specifications', '.product-specs', '.tech-specs']
            }
        }
        
        # Merge with brand-specific selectors
        self.selectors = self._merge_selectors(self.default_selectors, brand_config.get('selectors', {}))
    
    def _merge_selectors(self, default: Dict, custom: Dict) -> Dict:
        """Merge default selectors with brand-specific ones"""
        merged = default.copy()
        for section, selectors in custom.items():
            if section in merged:
                for key, values in selectors.items():
                    if key in merged[section]:
                        # Prepend custom selectors (higher priority)
                        merged[section][key] = values + merged[section][key]
                    else:
                        merged[section][key] = values
            else:
                merged[section] = selectors
        return merged
    
    def parse_search_results(self, html: str, base_url: str = "") -> List[ParsedProductData]:
        """Parse brand website search results"""
        if not base_url:
            base_url = self.base_url
            
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find product containers
        containers = []
        for selector in self.selectors['search_results']['container']:
            containers = soup.select(selector)
            if containers:
                break
        
        if not containers:
            self.logger.warning(f"No product containers found for {self.brand_name}")
            return products
        
        for container in containers[:15]:  # Limit to first 15 results
            try:
                product_data = self._parse_search_result_item(container, base_url)
                if product_data and product_data.is_valid():
                    products.append(product_data)
            except Exception as e:
                self.logger.warning(f"Error parsing {self.brand_name} search result: {e}")
                continue
        
        return products
    
    def _parse_search_result_item(self, container: BeautifulSoup, base_url: str) -> Optional[ParsedProductData]:
        """Parse individual brand website search result item"""
        product = ParsedProductData()
        product.brand = self.brand_name
        
        # Extract product name
        product.name = self.extract_text_by_selectors(container, self.selectors['search_results']['name'])
        if product.name:
            product.name = self.clean_product_name(product.name)
        
        # Extract price
        price_text = self.extract_text_by_selectors(container, self.selectors['search_results']['price'])
        product.price = self.normalize_price(price_text) if price_text else None
        
        # Extract original price
        original_price_text = self.extract_text_by_selectors(container, self.selectors['search_results']['original_price'])
        product.original_price = self.normalize_price(original_price_text) if original_price_text else None
        
        # Extract product URL
        href = self.extract_attribute_by_selectors(container, self.selectors['search_results']['link'], 'href')
        if href:
            product.product_url = self._normalize_url(href, base_url)
        
        # Extract image URL
        product.image_url = self.extract_attribute_by_selectors(container, self.selectors['search_results']['image'], 'src')
        if not product.image_url:
            product.image_url = self.extract_attribute_by_selectors(container, self.selectors['search_results']['image'], 'data-src')
        
        if product.image_url:
            product.image_url = self._normalize_url(product.image_url, base_url)
        
        # Calculate discount
        product.calculate_discount()
        
        return product
    
    def parse_product_page(self, html: str, product_url: str) -> ParsedProductData:
        """Parse brand website product detail page"""
        soup = BeautifulSoup(html, 'html.parser')
        product = ParsedProductData()
        product.product_url = product_url
        product.brand = self.brand_name
        
        # Extract product name
        product.name = self.extract_text_by_selectors(soup, self.selectors['product_page']['name'])
        if product.name:
            product.name = self.clean_product_name(product.name)
        
        # Extract current price
        price_text = self.extract_text_by_selectors(soup, self.selectors['product_page']['price'])
        product.price = self.normalize_price(price_text) if price_text else None
        
        # Extract original price
        original_price_text = self.extract_text_by_selectors(soup, self.selectors['product_page']['original_price'])
        product.original_price = self.normalize_price(original_price_text) if original_price_text else None
        
        # Extract main image
        product.image_url = self.extract_attribute_by_selectors(soup, self.selectors['product_page']['image'], 'src')
        if not product.image_url:
            product.image_url = self.extract_attribute_by_selectors(soup, self.selectors['product_page']['image'], 'data-src')
        
        if product.image_url:
            product.image_url = self._normalize_url(product.image_url, self.base_url)
        
        # Extract stock status
        product.stock_status = self.determine_stock_status(soup, html)
        
        # Extract specifications
        product.specifications = self._extract_brand_specifications(soup)
        
        # Calculate discount
        product.calculate_discount()
        
        return product
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """Normalize relative URLs to absolute URLs"""
        if not url:
            return ""
        
        if url.startswith('http'):
            return url
        elif url.startswith('//'):
            return f"https:{url}"
        elif url.startswith('/'):
            return f"{base_url.rstrip('/')}{url}"
        else:
            return f"{base_url.rstrip('/')}/{url}"
    
    def _extract_brand_specifications(self, soup: BeautifulSoup) -> dict:
        """Extract specifications from brand website"""
        specs = {}
        
        # Try to find specifications section
        spec_containers = []
        for selector in self.selectors['product_page'].get('specifications', []):
            spec_containers = soup.select(selector)
            if spec_containers:
                break
        
        for container in spec_containers:
            # Look for key-value pairs in various formats
            
            # Format 1: Table rows
            rows = container.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        specs[key] = value
            
            # Format 2: Definition lists
            dt_elements = container.find_all('dt')
            for dt in dt_elements:
                dd = dt.find_next_sibling('dd')
                if dd:
                    key = dt.get_text(strip=True)
                    value = dd.get_text(strip=True)
                    if key and value:
                        specs[key] = value
            
            # Format 3: Divs with specific classes
            spec_items = container.find_all('div', class_=re.compile(r'spec|feature|detail'))
            for item in spec_items:
                text = item.get_text(strip=True)
                if ':' in text:
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if key and value:
                            specs[key] = value
        
        # Extract product description as a specification
        description_text = self.extract_text_by_selectors(soup, self.selectors['product_page'].get('description', []))
        if description_text and len(description_text) > 20:
            specs['description'] = description_text[:500]  # Limit description length
        
        return specs


# Predefined configurations for common brand websites
BRAND_CONFIGS = {
    'apple': {
        'name': 'Apple',
        'base_url': 'https://www.apple.com',
        'selectors': {
            'search_results': {
                'container': ['.rf-serp-productcard', '.as-producttile'],
                'name': ['.rf-serp-productcard-title', '.as-producttile-title'],
                'price': ['.rf-serp-productcard-price', '.as-price-current'],
                'link': ['.rf-serp-productcard-link', '.as-producttile-link'],
                'image': ['.rf-serp-productcard-img img', '.as-producttile-image img']
            },
            'product_page': {
                'name': ['.pd-title', '.hero-headline'],
                'price': ['.current_price', '.hero-price-value'],
                'image': ['.pd-gallery-image img', '.hero-image img']
            }
        }
    },
    'sony': {
        'name': 'Sony',
        'base_url': 'https://www.sony.com',
        'selectors': {
            'search_results': {
                'container': ['.ProductCard', '.product-tile'],
                'name': ['.ProductCard-title', '.product-title'],
                'price': ['.ProductCard-price', '.price'],
                'link': ['.ProductCard-link', '.product-link'],
                'image': ['.ProductCard-image img', '.product-image img']
            }
        }
    },
    'bose': {
        'name': 'Bose',
        'base_url': 'https://www.bose.com',
        'selectors': {
            'search_results': {
                'container': ['.product-tile', '.product-card'],
                'name': ['.product-title', '.tile-title'],
                'price': ['.price', '.product-price'],
                'link': ['.product-link', 'a'],
                'image': ['.product-image img', 'img']
            }
        }
    }
}


def create_brand_parser(brand_name: str) -> BrandParser:
    """Factory function to create brand parser with predefined config"""
    brand_key = brand_name.lower()
    if brand_key in BRAND_CONFIGS:
        return BrandParser(BRAND_CONFIGS[brand_key])
    else:
        # Return generic parser with minimal config
        return BrandParser({
            'name': brand_name,
            'base_url': f'https://www.{brand_name.lower()}.com'
        })