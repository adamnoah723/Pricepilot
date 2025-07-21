#!/usr/bin/env python3
"""
Advanced Pricing Engine - Handles price analysis, trends, and best deal identification
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
import statistics

from .models import Product, Price, Vendor, PriceHistory
from .database import SessionLocal

class PricingEngine:
    """Advanced pricing analysis and best deal identification"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    def analyze_product_pricing(self, product_id: str) -> Dict:
        """Comprehensive pricing analysis for a product"""
        
        # Get all current prices
        current_prices = self.db.query(Price).filter(
            Price.product_id == product_id
        ).all()
        
        if not current_prices:
            return {"error": "No prices found"}
        
        # Get price history for trend analysis
        price_history = self.get_price_history(product_id, days=30)
        
        # Calculate best deal metrics
        best_deal_analysis = self.identify_best_deals(current_prices, price_history)
        
        # Calculate price trends
        trend_analysis = self.calculate_price_trends(price_history)
        
        # Calculate savings opportunities
        savings_analysis = self.calculate_savings_opportunities(current_prices)
        
        return {
            "product_id": product_id,
            "current_prices": self.format_current_prices(current_prices),
            "best_deals": best_deal_analysis,
            "price_trends": trend_analysis,
            "savings_opportunities": savings_analysis,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def identify_best_deals(self, current_prices: List[Price], price_history: List) -> Dict:
        """Identify various types of best deals"""
        
        if not current_prices:
            return {}
        
        # Sort by price to find absolute best
        sorted_prices = sorted(current_prices, key=lambda p: float(p.price))
        absolute_best = sorted_prices[0]
        
        # Find best discount percentage
        best_discount = max(
            [p for p in current_prices if p.discount_percentage], 
            key=lambda p: float(p.discount_percentage or 0),
            default=None
        )
        
        # Find best value (considering stock status)
        in_stock_prices = [p for p in current_prices if p.stock_status == 'in_stock']
        best_available = min(in_stock_prices, key=lambda p: float(p.price)) if in_stock_prices else None
        
        # Historical best deal analysis
        historical_best = self.find_historical_best_deal(price_history)
        
        return {
            "absolute_best": {
                "vendor_id": absolute_best.vendor_id,
                "price": float(absolute_best.price),
                "stock_status": absolute_best.stock_status,
                "is_available": absolute_best.stock_status == 'in_stock'
            },
            "best_discount": {
                "vendor_id": best_discount.vendor_id,
                "price": float(best_discount.price),
                "original_price": float(best_discount.original_price) if best_discount.original_price else None,
                "discount_percentage": float(best_discount.discount_percentage),
                "savings_amount": float(best_discount.original_price - best_discount.price) if best_discount.original_price else 0
            } if best_discount else None,
            "best_available": {
                "vendor_id": best_available.vendor_id,
                "price": float(best_available.price),
                "stock_status": best_available.stock_status
            } if best_available else None,
            "historical_context": historical_best
        }
    
    def calculate_price_trends(self, price_history: List) -> Dict:
        """Calculate price trends over time"""
        if len(price_history) < 2:
            return {"trend": "insufficient_data"}
        
        # Group by vendor for trend analysis
        vendor_trends = {}
        
        for vendor_id in set(h['vendor_id'] for h in price_history):
            vendor_history = [h for h in price_history if h['vendor_id'] == vendor_id]
            vendor_history.sort(key=lambda x: x['timestamp'])
            
            if len(vendor_history) >= 2:
                recent_price = vendor_history[-1]['price']
                older_price = vendor_history[0]['price']
                
                price_change = recent_price - older_price
                percentage_change = (price_change / older_price) * 100
                
                # Determine trend direction
                if abs(percentage_change) < 2:
                    trend = "stable"
                elif percentage_change > 0:
                    trend = "increasing"
                else:
                    trend = "decreasing"
                
                vendor_trends[vendor_id] = {
                    "trend": trend,
                    "price_change": float(price_change),
                    "percentage_change": round(percentage_change, 2),
                    "current_price": float(recent_price),
                    "previous_price": float(older_price),
                    "data_points": len(vendor_history)
                }
        
        # Overall market trend
        all_recent_prices = [h['price'] for h in price_history[-10:]]  # Last 10 data points
        all_older_prices = [h['price'] for h in price_history[:10]]   # First 10 data points
        
        if all_recent_prices and all_older_prices:
            recent_avg = statistics.mean(all_recent_prices)
            older_avg = statistics.mean(all_older_prices)
            overall_change = ((recent_avg - older_avg) / older_avg) * 100
            
            overall_trend = {
                "direction": "increasing" if overall_change > 2 else "decreasing" if overall_change < -2 else "stable",
                "percentage_change": round(overall_change, 2),
                "recent_average": round(recent_avg, 2),
                "historical_average": round(older_avg, 2)
            }
        else:
            overall_trend = {"direction": "insufficient_data"}
        
        return {
            "vendor_trends": vendor_trends,
            "overall_market_trend": overall_trend,
            "analysis_period_days": 30
        }
    
    def calculate_savings_opportunities(self, current_prices: List[Price]) -> Dict:
        """Calculate potential savings opportunities"""
        if len(current_prices) < 2:
            return {"savings_available": False}
        
        # Sort by price
        sorted_prices = sorted(current_prices, key=lambda p: float(p.price))
        cheapest = sorted_prices[0]
        most_expensive = sorted_prices[-1]
        
        # Calculate savings vs each vendor
        savings_vs_vendors = []
        for price in sorted_prices[1:]:  # Skip the cheapest
            savings_amount = float(price.price) - float(cheapest.price)
            savings_percentage = (savings_amount / float(price.price)) * 100
            
            savings_vs_vendors.append({
                "vendor_id": price.vendor_id,
                "their_price": float(price.price),
                "best_price": float(cheapest.price),
                "savings_amount": round(savings_amount, 2),
                "savings_percentage": round(savings_percentage, 2),
                "stock_status": price.stock_status
            })
        
        # Maximum possible savings
        max_savings = float(most_expensive.price) - float(cheapest.price)
        max_savings_percentage = (max_savings / float(most_expensive.price)) * 100
        
        return {
            "savings_available": max_savings > 0,
            "maximum_savings": {
                "amount": round(max_savings, 2),
                "percentage": round(max_savings_percentage, 2),
                "cheapest_vendor": cheapest.vendor_id,
                "most_expensive_vendor": most_expensive.vendor_id
            },
            "savings_vs_vendors": savings_vs_vendors,
            "best_deal_vendor": cheapest.vendor_id,
            "best_deal_price": float(cheapest.price),
            "best_deal_available": cheapest.stock_status == 'in_stock'
        }
    
    def get_price_history(self, product_id: str, days: int = 30) -> List[Dict]:
        """Get price history for trend analysis"""
        # This would query a PriceHistory table if we had one
        # For now, we'll simulate with current Price table
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        prices = self.db.query(Price).filter(
            Price.product_id == product_id,
            Price.last_updated_at >= cutoff_date
        ).order_by(Price.last_updated_at.desc()).all()
        
        return [
            {
                "vendor_id": p.vendor_id,
                "price": float(p.price),
                "original_price": float(p.original_price) if p.original_price else None,
                "timestamp": p.last_updated_at,
                "stock_status": p.stock_status
            }
            for p in prices
        ]
    
    def find_historical_best_deal(self, price_history: List) -> Dict:
        """Find the best historical deal"""
        if not price_history:
            return {"available": False}
        
        # Find lowest price in history
        lowest_price_record = min(price_history, key=lambda x: x['price'])
        current_prices = [h for h in price_history if h['timestamp'] >= datetime.utcnow() - timedelta(days=1)]
        
        if current_prices:
            current_best = min(current_prices, key=lambda x: x['price'])
            
            return {
                "available": True,
                "historical_best_price": lowest_price_record['price'],
                "historical_best_vendor": lowest_price_record['vendor_id'],
                "historical_best_date": lowest_price_record['timestamp'].isoformat(),
                "current_best_price": current_best['price'],
                "difference_from_historical": round(current_best['price'] - lowest_price_record['price'], 2),
                "is_current_best_historical": current_best['price'] <= lowest_price_record['price']
            }
        
        return {"available": False}
    
    def format_current_prices(self, prices: List[Price]) -> List[Dict]:
        """Format current prices for API response"""
        return [
            {
                "vendor_id": p.vendor_id,
                "price": float(p.price),
                "original_price": float(p.original_price) if p.original_price else None,
                "discount_percentage": float(p.discount_percentage) if p.discount_percentage else None,
                "stock_status": p.stock_status,
                "last_updated": p.last_updated_at.isoformat(),
                "product_url": p.product_url
            }
            for p in prices
        ]
    
    def get_price_alerts(self, product_id: str, target_price: float) -> Dict:
        """Check if product has reached target price"""
        current_prices = self.db.query(Price).filter(
            Price.product_id == product_id,
            Price.stock_status == 'in_stock'
        ).all()
        
        deals_at_target = [
            p for p in current_prices 
            if float(p.price) <= target_price
        ]
        
        if deals_at_target:
            best_deal = min(deals_at_target, key=lambda p: float(p.price))
            return {
                "alert_triggered": True,
                "target_price": target_price,
                "best_available_price": float(best_deal.price),
                "vendor_id": best_deal.vendor_id,
                "savings_vs_target": round(target_price - float(best_deal.price), 2)
            }
        
        return {
            "alert_triggered": False,
            "target_price": target_price,
            "closest_price": float(min(current_prices, key=lambda p: float(p.price)).price) if current_prices else None
        }

# Utility functions for API endpoints
def get_product_pricing_analysis(product_id: str, db: Session = None) -> Dict:
    """Get comprehensive pricing analysis for a product"""
    engine = PricingEngine(db)
    return engine.analyze_product_pricing(product_id)

def get_best_deals_across_products(category_id: str = None, limit: int = 10, db: Session = None) -> List[Dict]:
    """Get best deals across multiple products"""
    engine = PricingEngine(db or SessionLocal())
    
    # Get products in category
    query = engine.db.query(Product)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    products = query.limit(limit * 2).all()  # Get more to filter
    
    best_deals = []
    for product in products:
        analysis = engine.analyze_product_pricing(product.id)
        if analysis.get('best_deals', {}).get('absolute_best'):
            best_deal = analysis['best_deals']['absolute_best']
            best_deals.append({
                "product_id": product.id,
                "product_name": product.name,
                "brand": product.brand,
                "best_price": best_deal['price'],
                "vendor_id": best_deal['vendor_id'],
                "is_available": best_deal['is_available'],
                "savings_info": analysis.get('savings_opportunities', {})
            })
    
    # Sort by best deals (considering availability)
    best_deals.sort(key=lambda x: (not x['is_available'], x['best_price']))
    
    return best_deals[:limit]