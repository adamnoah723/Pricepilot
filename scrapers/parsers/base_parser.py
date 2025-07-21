from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from decimal import Decimal
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)


class ParsedProductData:
    """Standardized product data structure from parsing"""
    def __init__(self):
        self.name: Optional[str] = None
        self.price: Optional[Decimal] = None
        self.original_price: Optional[Decimal] = None
        self.discount_percentage: Optional[float] = None
        self.stock_status: str = "unknown"
        self.image_url: Optional[str] = None
        self.product_url: Optional[str] = None
        self.brand: Optional[str] = None
        self.model: Optional[str] = None
        self.variations: List[Dict[str, Any]] = []
        self.specifications: Dict[str, Any] = {}
        self.rating: Optional[float] = None
        self.review_count: Optional[int] = None
        
    def is_valid(self) -> bool:
        """Check if we have minimum required data"""
        return bool(self.name and self.price and self.price > 0)
    
    def calculate_discount(self):
        """Calculate discount percentage if original price exists"""
        if self.original_price and self.price and self.original_price > self.price:
            self.discount_percentage = float(
                ((self.original_price - self.price) / self.original_price) * 100
            )


class BaseParser(ABC):
    """Base class for vendor-specific parsers"""
    
    def __init__(self, vendor_name: str):
        self.vendor_name = vendor_name
        self.logger = logging.getLogger(f"{__name__}.{vendor_name}")
    
    @abstractmethod
    def parse_search_results(self, html: str, base_url: str = "") -> List[ParsedProductData]:
        """Parse search results page and extract product listings"""
        pass
    
    @abstractmethod
    def parse_product_page(self, html: str, product_url: str) -> ParsedProductData:
        """Parse individual product page for detailed information"""
        pass
    
    def normalize_price(self, price_text: str) -> Optional[Decimal]:
        """Extract and normalize price from text"""
        if not price_text:
            return None
        
        # Remove common currency symbols and whitespace
        cleaned = re.sub(r'[^\d.,]', '', price_text.strip())
        
        # Handle different price formats
        price_patterns = [
            r'(\d{1,3}(?:,\d{3})*\.\d{2})',  # 1,234.56
            r'(\d{1,3}(?:,\d{3})*)',         # 1,234
            r'(\d+\.\d{2})',                 # 123.45
            r'(\d+)',                        # 123
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, cleaned)
            if match:
                try:
                    price_str = match.group(1).replace(',', '')
                    return Decimal(price_str)
                except:
                    continue
        
        return None
    
    def extract_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Try multiple CSS selectors to extract text"""
        for selector in selectors:
            try:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    if text:
                        return text
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        return None
    
    def extract_attribute_by_selectors(self, soup: BeautifulSoup, selectors: List[str], 
                                     attribute: str) -> Optional[str]:
        """Try multiple CSS selectors to extract an attribute"""
        for selector in selectors:
            try:
                elem = soup.select_one(selector)
                if elem:
                    attr_value = elem.get(attribute)
                    if attr_value:
                        return attr_value
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        return None
    
    def clean_product_name(self, name: str) -> str:
        """Clean and normalize product name"""
        if not name:
            return ""
        
        # Remove extra whitespace
        cleaned = ' '.join(name.split())
        
        # Remove common prefixes/suffixes that don't add value
        prefixes_to_remove = ['NEW', 'SALE', 'HOT']
        for prefix in prefixes_to_remove:
            if cleaned.upper().startswith(prefix.upper()):
                cleaned = cleaned[len(prefix):].strip()
        
        return cleaned
    
    def extract_brand_from_name(self, name: str) -> Optional[str]:
        """Extract brand from product name using common patterns"""
        if not name:
            return None
        
        # Common tech brands
        brands = [
            'Apple', 'Samsung', 'Sony', 'LG', 'Dell', 'HP', 'Lenovo', 'ASUS', 
            'Acer', 'Microsoft', 'Google', 'Amazon', 'Bose', 'JBL', 'Beats',
            'Sennheiser', 'Audio-Technica', 'Logitech', 'Razer', 'Corsair'
        ]
        
        name_upper = name.upper()
        for brand in brands:
            if brand.upper() in name_upper:
                return brand
        
        return None
    
    def determine_stock_status(self, soup: BeautifulSoup, text_content: str = "") -> str:
        """Determine stock status from page content"""
        # Common out of stock indicators
        out_of_stock_patterns = [
            'out of stock', 'sold out', 'unavailable', 'not available',
            'temporarily unavailable', 'currently unavailable', 'backorder'
        ]
        
        # Check in text content
        text_lower = text_content.lower()
        for pattern in out_of_stock_patterns:
            if pattern in text_lower:
                return "out_of_stock"
        
        # Check for disabled add to cart buttons
        add_to_cart_buttons = soup.find_all(['button', 'input'], 
                                          text=re.compile(r'add to cart|buy now', re.I))
        for button in add_to_cart_buttons:
            if button.get('disabled') or 'disabled' in button.get('class', []):
                return "out_of_stock"
        
        return "in_stock"