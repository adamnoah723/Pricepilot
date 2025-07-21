import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./pricepilot.db")
    
    # Scraper settings
    scraper_headless: bool = os.getenv("SCRAPER_HEADLESS", "true").lower() == "true"
    scraper_max_retries: int = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))
    
    # Rate limiting (seconds between requests)
    amazon_rate_limit: float = float(os.getenv("AMAZON_RATE_LIMIT", "1.0"))
    bestbuy_rate_limit: float = float(os.getenv("BESTBUY_RATE_LIMIT", "0.5"))
    walmart_rate_limit: float = float(os.getenv("WALMART_RATE_LIMIT", "0.5"))
    brand_rate_limit: float = float(os.getenv("BRAND_RATE_LIMIT", "2.0"))
    
    # API settings
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8001"))
    
    class Config:
        env_file = ".env"

settings = Settings()