from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
import logging

from .models import Product, Price, PriceHistory, Vendor
from .database import get_db

logger = logging.getLogger(__name__)


class PriceService:
    """Service for managing price data with historical tracking"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def update_or_create_price(self, product_id: str, vendor_id: str, 
                              scraped_data: Dict[str, Any]) -> Price:
        """
        Update existing price or create new one, with historical tracking
        
        Args:
            product_id: Product UUID
            vendor_id: Vendor UUID  
            scraped_data: Dictionary containing price data from scraper
            
        Returns:
            Price: Updated or created price record
        """
        try:
            # Get existing price record
            existing_price = self.db.query(Price).filter(
                and_(Price.product_id == product_id, Price.vendor_id == vendor_id)
            ).first()
            
            new_price = Decimal(str(scraped_data['price']))
            new_original_price = None
            if scraped_data.get('original_price'):
                new_original_price = Decimal(str(scraped_data['original_price']))
            
            # Calculate discount percentage
            discount_percentage = None
            if new_original_price and new_price < new_original_price:
                discount_percentage = float(
                    ((new_original_price - new_price) / new_original_price) * 100
                )
            
            if existing_price:
                # Check if price has changed significantly (more than $0.01)
                price_changed = abs(existing_price.price - new_price) > Decimal('0.01')
                
                if price_changed:
                    # Archive the old price to history
                    self._archive_price_to_history(existing_price)
                    logger.info(f"Price changed for product {product_id} at {vendor_id}: "
                              f"${existing_price.price} -> ${new_price}")
                
                # Update existing price record
                existing_price.price = new_price
                existing_price.original_price = new_original_price
                existing_price.discount_percentage = discount_percentage
                existing_price.stock_status = scraped_data.get('stock_status', 'in_stock')
                existing_price.product_url = scraped_data.get('product_url', existing_price.product_url)
                existing_price.variation_details = scraped_data.get('variations', {})
                existing_price.last_updated_at = datetime.utcnow()
                
                self.db.commit()
                return existing_price
            
            else:
                # Create new price record
                new_price_record = Price(
                    product_id=product_id,
                    vendor_id=vendor_id,
                    price=new_price,
                    original_price=new_original_price,
                    discount_percentage=discount_percentage,
                    stock_status=scraped_data.get('stock_status', 'in_stock'),
                    product_url=scraped_data.get('product_url', ''),
                    variation_details=scraped_data.get('variations', {}),
                    last_updated_at=datetime.utcnow()
                )
                
                self.db.add(new_price_record)
                self.db.commit()
                logger.info(f"Created new price record for product {product_id} at {vendor_id}: ${new_price}")
                return new_price_record
                
        except Exception as e:
            logger.error(f"Error updating price for product {product_id}, vendor {vendor_id}: {e}")
            self.db.rollback()
            raise
    
    def _archive_price_to_history(self, price_record: Price) -> PriceHistory:
        """Archive a price record to price history"""
        try:
            history_record = PriceHistory(
                price_id=price_record.id,
                product_id=price_record.product_id,
                vendor_id=price_record.vendor_id,
                price=price_record.price,
                original_price=price_record.original_price,
                discount_percentage=price_record.discount_percentage,
                stock_status=price_record.stock_status,
                product_url=price_record.product_url,
                variation_details=price_record.variation_details,
                recorded_at=price_record.last_updated_at
            )
            
            self.db.add(history_record)
            return history_record
            
        except Exception as e:
            logger.error(f"Error archiving price to history: {e}")
            raise
    
    def get_price_history(self, product_id: str, vendor_id: str, 
                         days_back: int = 30) -> List[PriceHistory]:
        """Get price history for a product from a specific vendor"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            history = self.db.query(PriceHistory).filter(
                and_(
                    PriceHistory.product_id == product_id,
                    PriceHistory.vendor_id == vendor_id,
                    PriceHistory.recorded_at >= cutoff_date
                )
            ).order_by(desc(PriceHistory.recorded_at)).all()
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            return []
    
    def get_price_trends(self, product_id: str, days_back: int = 30) -> Dict[str, List[Dict]]:
        """Get price trends across all vendors for a product"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get current prices
            current_prices = self.db.query(Price, Vendor).join(Vendor).filter(
                Price.product_id == product_id
            ).all()
            
            # Get historical prices
            historical_prices = self.db.query(PriceHistory, Vendor).join(Vendor).filter(
                and_(
                    PriceHistory.product_id == product_id,
                    PriceHistory.recorded_at >= cutoff_date
                )
            ).order_by(desc(PriceHistory.recorded_at)).all()
            
            trends = {}
            
            # Process current prices
            for price, vendor in current_prices:
                trends[vendor.name] = [{
                    'price': float(price.price),
                    'original_price': float(price.original_price) if price.original_price else None,
                    'discount_percentage': float(price.discount_percentage) if price.discount_percentage else None,
                    'stock_status': price.stock_status,
                    'recorded_at': price.last_updated_at.isoformat(),
                    'is_current': True
                }]
            
            # Add historical prices
            for history, vendor in historical_prices:
                if vendor.name not in trends:
                    trends[vendor.name] = []
                
                trends[vendor.name].append({
                    'price': float(history.price),
                    'original_price': float(history.original_price) if history.original_price else None,
                    'discount_percentage': float(history.discount_percentage) if history.discount_percentage else None,
                    'stock_status': history.stock_status,
                    'recorded_at': history.recorded_at.isoformat(),
                    'is_current': False
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting price trends: {e}")
            return {}
    
    def get_best_deals(self, category_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get products with the best current deals (highest discount percentages)"""
        try:
            query = self.db.query(Price, Product, Vendor).join(Product).join(Vendor)
            
            if category_id:
                query = query.filter(Product.category_id == category_id)
            
            # Filter for products with discounts and in stock
            query = query.filter(
                and_(
                    Price.discount_percentage.isnot(None),
                    Price.discount_percentage > 0,
                    Price.stock_status == 'in_stock'
                )
            )
            
            # Order by discount percentage descending
            best_deals = query.order_by(desc(Price.discount_percentage)).limit(limit).all()
            
            deals = []
            for price, product, vendor in best_deals:
                deals.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'brand': product.brand,
                    'vendor_name': vendor.display_name,
                    'current_price': float(price.price),
                    'original_price': float(price.original_price),
                    'discount_percentage': float(price.discount_percentage),
                    'savings': float(price.original_price - price.price),
                    'product_url': price.product_url,
                    'image_url': product.image_url,
                    'last_updated': price.last_updated_at.isoformat()
                })
            
            return deals
            
        except Exception as e:
            logger.error(f"Error getting best deals: {e}")
            return []
    
    def get_price_alerts(self, target_discount: float = 20.0) -> List[Dict]:
        """Get products that have reached a target discount threshold"""
        try:
            # Find products with recent price drops that meet the discount threshold
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            
            alerts = self.db.query(Price, Product, Vendor).join(Product).join(Vendor).filter(
                and_(
                    Price.discount_percentage >= target_discount,
                    Price.last_updated_at >= recent_cutoff,
                    Price.stock_status == 'in_stock'
                )
            ).order_by(desc(Price.discount_percentage)).all()
            
            alert_list = []
            for price, product, vendor in alerts:
                alert_list.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'brand': product.brand,
                    'vendor_name': vendor.display_name,
                    'current_price': float(price.price),
                    'original_price': float(price.original_price),
                    'discount_percentage': float(price.discount_percentage),
                    'savings': float(price.original_price - price.price),
                    'product_url': price.product_url,
                    'alert_triggered_at': price.last_updated_at.isoformat()
                })
            
            return alert_list
            
        except Exception as e:
            logger.error(f"Error getting price alerts: {e}")
            return []
    
    def get_data_freshness_info(self, product_id: Optional[str] = None) -> Dict[str, Any]:
        """Get information about how fresh the price data is"""
        try:
            if product_id:
                # Get freshness for specific product
                prices = self.db.query(Price, Vendor).join(Vendor).filter(
                    Price.product_id == product_id
                ).all()
            else:
                # Get overall freshness statistics
                prices = self.db.query(Price, Vendor).join(Vendor).all()
            
            if not prices:
                return {'error': 'No price data found'}
            
            now = datetime.utcnow()
            freshness_data = []
            
            for price, vendor in prices:
                time_diff = now - price.last_updated_at
                hours_old = time_diff.total_seconds() / 3600
                
                freshness_status = 'fresh'
                if hours_old > 24:
                    freshness_status = 'stale'
                elif hours_old > 12:
                    freshness_status = 'aging'
                
                freshness_data.append({
                    'vendor_name': vendor.display_name,
                    'last_updated': price.last_updated_at.isoformat(),
                    'hours_old': round(hours_old, 1),
                    'freshness_status': freshness_status,
                    'product_id': price.product_id if product_id else None
                })
            
            # Calculate overall statistics
            hours_old_list = [item['hours_old'] for item in freshness_data]
            avg_age = sum(hours_old_list) / len(hours_old_list)
            oldest_age = max(hours_old_list)
            newest_age = min(hours_old_list)
            
            return {
                'vendor_data': freshness_data,
                'statistics': {
                    'average_age_hours': round(avg_age, 1),
                    'oldest_data_hours': round(oldest_age, 1),
                    'newest_data_hours': round(newest_age, 1),
                    'total_vendors': len(freshness_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting data freshness info: {e}")
            return {'error': str(e)}
    
    def cleanup_old_history(self, days_to_keep: int = 90):
        """Clean up old price history records to manage database size"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            deleted_count = self.db.query(PriceHistory).filter(
                PriceHistory.recorded_at < cutoff_date
            ).delete()
            
            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old price history records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old history: {e}")
            self.db.rollback()
            return 0


def get_price_service(db: Session = None) -> PriceService:
    """Factory function to get PriceService instance"""
    if db is None:
        db = next(get_db())
    return PriceService(db)