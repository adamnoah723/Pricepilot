#!/usr/bin/env python3
"""
Scheduled scraper - Runs every 6 hours to update prices
"""

import asyncio
import schedule
import time
import sys
import os
from datetime import datetime, timedelta

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from scrape_all_vendors import ProductionScraperRunner
from app.database import SessionLocal
from app.models import ScraperRun, Vendor

class ScheduledScraper:
    def __init__(self):
        self.db = SessionLocal()
    
    async def run_scheduled_scrape(self):
        """Run the scheduled scraping job"""
        print(f"\\n🕐 Scheduled scrape started at {datetime.now()}")
        
        runner = ProductionScraperRunner()
        try:
            await runner.run_production_scraping()
            print(f"✅ Scheduled scrape completed at {datetime.now()}")
        except Exception as e:
            print(f"❌ Scheduled scrape failed: {e}")
        finally:
            runner.cleanup()
    
    def get_last_scrape_time(self) -> datetime:
        """Get the last successful scrape time"""
        last_run = self.db.query(ScraperRun).filter(
            ScraperRun.status == 'completed'
        ).order_by(ScraperRun.completed_at.desc()).first()
        
        if last_run:
            return last_run.completed_at
        return datetime.now() - timedelta(days=1)  # Default to 1 day ago
    
    def should_scrape_now(self) -> bool:
        """Check if we should scrape now (every 6 hours)"""
        last_scrape = self.get_last_scrape_time()
        time_since_last = datetime.now() - last_scrape
        return time_since_last >= timedelta(hours=6)
    
    def run_scheduler(self):
        """Run the scheduler"""
        print("🚀 PricePilot Scheduler Started")
        print("📅 Will scrape every 6 hours")
        print("⏰ Press Ctrl+C to stop")
        
        # Schedule scraping every 6 hours
        schedule.every(6).hours.do(lambda: asyncio.run(self.run_scheduled_scrape()))
        
        # Run immediately if it's been more than 6 hours
        if self.should_scrape_now():
            print("🏃 Running initial scrape (been >6 hours since last run)")
            asyncio.run(self.run_scheduled_scrape())
        
        # Keep scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    scheduler = ScheduledScraper()
    try:
        scheduler.run_scheduler()
    except KeyboardInterrupt:
        print("\\n👋 Scheduler stopped by user")
    except Exception as e:
        print(f"❌ Scheduler error: {e}")