from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from decimal import Decimal
import re
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScrapedProduct:
    name: str
    price: Decimal
    original_price: Optional[Decimal]
    stock_status: str
    product_url: str
    image_url: Optional[str]
    variations: List[dict]
    brand: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None


class ScraperErrorHandler:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    async def handle_request_error(self, error: Exception, attempt: int) -> bool:
        if attempt < self.max_retries:
            delay = 2 ** attempt  # Exponential backoff
            logger.warning(f"Request failed (attempt {attempt}), retrying in {delay}s: {error}")
            await asyncio.sleep(delay)
            return True  # Retry
        logger.error(f"Request failed after {self.max_retries} attempts: {error}")
        return False  # Give up
    
    def handle_parsing_error(self, error: Exception, product_data: dict):
        logger.error(f"Parsing error for product {product_data.get('name', 'unknown')}: {error}")
        return None
    
    def handle_rate_limit(self, response_headers: dict) -> int:
        retry_after = response_headers.get('Retry-After', 60)
        return int(retry_after)


class BaseScraper(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.error_handler = ScraperErrorHandler(max_retries=config.get('max_retries', 3))
        self.rate_limit_delay = config.get('rate_limit_delay', 1.0)
    
    @abstractmethod
    async def search_product(self, query: str) -> List[ScrapedProduct]:
        """Search for products matching the query"""
        pass
    
    @abstractmethod
    async def get_product_details(self, product_url: str) -> ScrapedProduct:
        """Get detailed information for a specific product"""
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
    
    def extract_best_variation(self, variations: List[dict]) -> dict:
        """Find the lowest priced variation"""
        if not variations:
            return {}
        
        best_variation = min(variations, key=lambda x: x.get('price', float('inf')))
        return best_variation
    
    async def respect_rate_limit(self):
        """Apply rate limiting between requests"""
        if self.rate_limit_delay > 0:
            await asyncio.sleep(self.rate_limit_delay)