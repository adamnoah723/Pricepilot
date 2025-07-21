# 🧪 PricePilot Testing Guide

## Current Status
✅ **Frontend**: Working beautifully with modern design  
✅ **Backend**: Configured on port 8001  
✅ **Scrapers**: Ready for live testing  
❌ **Data**: Needs to be populated  

## 🚀 Quick Fix for "Something went wrong" Error

The error occurs because there's no data in the database. Let's fix this:

### **Option 1: Test with Sample Data (Recommended First)**

```bash
# 1. Make sure backend is running
npm run dev:backend

# 2. Populate sample data
cd backend
python populate_sample_data.py

# 3. Test the frontend
# Visit http://localhost:3001 and try:
# - Clicking category cards (Laptops, Headphones, Speakers)
# - Searching for "MacBook" or "Sony"
# - Clicking "View Deal" buttons
```

### **Option 2: Test with Live Scraped Data**

```bash
# Run the live scraper test
python test_scrapers.py
```

This will:
- ✅ Scrape real products from Amazon
- ✅ Save them to your database
- ✅ Make them searchable in your frontend

## 🔍 **What Each Test Does**

### **Sample Data Test**
- Creates 6 realistic products (MacBook Pro, Dell XPS, Sony headphones, AirPods, JBL speaker, Bose speaker)
- Adds price comparisons across Amazon, Best Buy, Walmart
- Includes realistic discounts and stock status
- **Perfect for**: Testing UI, navigation, price comparison features

### **Live Scraper Test**
- Actually visits Amazon.com
- Scrapes real product data
- Saves live prices and availability
- **Perfect for**: Testing scraper functionality, real-world data

## 🎯 **Expected Results After Running Tests**

### **Homepage Should Show:**
- ✅ Category cards that are clickable
- ✅ "Today's Best Deals" with real products
- ✅ Working "View Deal" buttons
- ✅ Functional search bar

### **Search Results Should Show:**
- ✅ Product cards with images, names, prices
- ✅ "Best Deal" badges
- ✅ Clickable product links

### **Product Pages Should Show:**
- ✅ Detailed product information
- ✅ Price comparison table
- ✅ Stock status and discounts
- ✅ Links to vendor websites

### **Category Pages Should Show:**
- ✅ Filtered products by category
- ✅ Sorting options (price, popularity, name)
- ✅ Product grid layout

## 🐛 **Troubleshooting**

### **If you still see "Something went wrong":**

1. **Check if backend is running:**
   ```bash
   curl http://localhost:8001/api/health
   # Should return: {"status":"healthy","service":"PricePilot API"}
   ```

2. **Check if data exists:**
   ```bash
   curl http://localhost:8001/api/products
   # Should return JSON with products
   ```

3. **Check browser console:**
   - Open Developer Tools (F12)
   - Look for API errors in Console tab
   - Check Network tab for failed requests

### **If scrapers fail:**
- Make sure you have Chrome/Chromium installed
- Install missing Python packages:
  ```bash
  cd backend
  pip install selenium webdriver-manager beautifulsoup4 fake-useragent selenium-stealth
  ```

### **If ports conflict:**
- Backend should be on port 8001
- Frontend should be on port 3001
- Check with: `lsof -i :8001` and `lsof -i :3001`

## 🚀 **Advanced Testing**

### **Test All Scrapers:**
```bash
# Test Amazon, Best Buy, and Walmart scrapers
cd backend
python run_scrapers.py
```

### **Test Specific Products:**
```bash
# Search for specific items
curl "http://localhost:8001/api/search?q=MacBook"
curl "http://localhost:8001/api/search?q=headphones"
```

### **Test Price Comparison:**
```bash
# Get product details with price comparison
curl "http://localhost:8001/api/products/[PRODUCT_ID]"
```

## 📊 **Performance Testing**

### **Load Testing:**
- Try searching for 20+ different products
- Test category filtering with large datasets
- Check response times for API calls

### **Scraper Stress Testing:**
- Run scrapers multiple times
- Test with different search queries
- Monitor for rate limiting or blocking

## 🎉 **Success Criteria**

Your PricePilot is working perfectly when:
- ✅ All navigation works without errors
- ✅ Search returns relevant results
- ✅ Price comparisons show multiple vendors
- ✅ Product pages load with full details
- ✅ "View Deal" buttons work
- ✅ Categories filter products correctly
- ✅ Live scraped data appears in search results

## 🔄 **Next Steps After Testing**

1. **Add more products** with the scrapers
2. **Set up automated scraping** with cron jobs
3. **Add more vendor scrapers** (Target, Newegg, etc.)
4. **Implement price alerts** and notifications
5. **Add user accounts** and wishlists