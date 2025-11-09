# Google Maps Reviews Extraction Report
## Dubravka 1836 Restaurant - Dubrovnik, Croatia

**Date:** November 9, 2025
**Target:** Google Maps reviews for "Dubravka 1836 Dubrovnik"
**Expected Reviews:** 200-400+
**Actual Reviews Extracted:** 0

---

## Executive Summary

❌ **FAILED**: Unable to extract Google Maps reviews using HTTP-based methods in server environment.

✅ **ALTERNATIVE DATA AVAILABLE**: 5,942 TripAdvisor reviews already extracted in `Dubravka.csv`

---

## Methods Attempted

### 1. ✗ Simple HTTP Requests (scrape_dubravka_api.py)
**Approach:** Direct HTTP GET requests to Google Search and Maps URLs
**Result:** Failed - No reviews in HTML response
**Reason:** Google loads reviews dynamically via JavaScript, not in initial HTML
**Files:** debug_local_search.html, debug_search.html

### 2. ✗ Google Maps Embed API (advanced_google_scraper.py - Method 1)
**Approach:** Attempted to use Google Maps Embed API endpoint
**Result:** Failed - 403 Forbidden / No review data
**Reason:** Endpoint doesn't provide review data without authentication

### 3. ✗ Google Local Results API (advanced_google_scraper.py - Method 2)
**Approach:** Tried undocumented Google Local Results API endpoint
**Result:** Failed - 404 Not Found
**Reason:** Endpoint not accessible or requires authentication

### 4. ✗ Google Search with Embedded Data Parsing (advanced_google_scraper.py - Method 3)
**Approach:** Parse AF_initDataCallback JavaScript structures in search results
**Result:** Failed - No AF_initDataCallback entries found
**Reason:** Google's JavaScript structure changed or not present without rendering

### 5. ✗ Google My Business API (advanced_google_scraper.py - Method 4)
**Approach:** Official Google Maps Platform API (Geocoding + Place Details)
**Result:** Failed - REQUEST_DENIED
**Reason:** Requires valid Google Cloud API key (not available)
**Error:** "You must use an API key to authenticate each request to Google Maps Platform APIs"

### 6. ✗ Mobile Version Scraping (advanced_google_scraper.py - Method 5)
**Approach:** Scrape mobile.google.com with mobile User-Agent
**Result:** Failed - No review elements found
**Reason:** Mobile version also requires JavaScript rendering

### 7. ✗ requests-html with JavaScript Rendering (requests_html_scraper.py)
**Approach:** Use requests-html library to render JavaScript with headless Chromium
**Result:** Failed - Cannot download/access Chromium
**Error:** "Max retries exceeded... Failed to establish a new connection: Temporary failure in name resolution"
**Reason:** Server environment restrictions prevent Chromium download/execution

### 8. ✗ Selenium/Chrome Browser Automation (scrape_dubravka_google.py)
**Status:** Not attempted
**Reason:** User confirmed server environment has NO GUI/X11 and Selenium/Chrome crashes
**Note:** This would work in local environment with GUI

---

## Why All Methods Failed

### Root Cause: JavaScript Rendering Required

Google Maps loads reviews **dynamically** via JavaScript after the page loads:

1. **Initial HTML** contains minimal content
2. **JavaScript code** makes AJAX requests to Google's internal APIs
3. **DOM manipulation** injects reviews into the page
4. **No browser = No reviews**

### Environmental Constraints

- **No GUI/X11 Display:** Cannot run Chrome/Chromium in headed mode
- **No Headless Browser:** Chromium download blocked by network restrictions
- **No API Keys:** Google Maps Platform API requires paid API key
- **Server Restrictions:** Limited network access, no display server

---

## Debug Files Created

| File | Size | Description |
|------|------|-------------|
| debug_local_search.html | 199KB | Google local search response (no reviews) |
| debug_search.html | 97KB | Google search response (no reviews) |
| debug_embed.html | 97KB | Google Maps embed attempt |
| debug_search_full.html | 199KB | Full search with AF_initDataCallback parsing |
| debug_mobile.html | 73KB | Mobile version response |

**Note:** All HTML files contain JavaScript code but no actual review content in the initial response.

---

## Working Alternatives

### ✅ Recommended Solutions

#### 1. **Outscraper API** (Recommended - Best option)
- **Website:** https://outscraper.com/
- **Cost:** ~$9-49/month for API access
- **Reviews:** Can extract all Google reviews without browser
- **Quality:** High-quality, structured data
- **Implementation:**
  ```python
  from outscraper import ApiClient
  api = ApiClient(api_key='YOUR_KEY')
  results = api.google_maps_reviews(['Dubravka 1836 Dubrovnik'], limit=500)
  ```

#### 2. **SerpAPI**
- **Website:** https://serpapi.com/
- **Cost:** $50-250/month depending on volume
- **Reviews:** Supports Google Maps reviews extraction
- **Quality:** Clean, structured JSON data
- **Implementation:**
  ```python
  from serpapi import GoogleSearch
  params = {
      "engine": "google_maps_reviews",
      "place_id": "ChIJ...",  # Dubravka Place ID
      "api_key": "YOUR_KEY"
  }
  search = GoogleSearch(params)
  results = search.get_dict()
  ```

#### 3. **Local Selenium Scraper** (Free - Requires GUI)
- **File:** `scrape_dubravka_google.py` (already exists in this repo)
- **Requirements:**
  - Local computer with GUI (Windows/Mac/Linux Desktop)
  - Chrome browser installed
  - ChromeDriver installed
- **Command:** `python3 scrape_dubravka_google.py`
- **Pros:** Free, complete control, extracts all reviews
- **Cons:** Requires local machine with display

#### 4. **Cloud Browser Service**
- **Services:** BrowserStack, Sauce Labs, LambdaTest
- **Cost:** $29-99/month
- **How:** Run Selenium script on cloud VM with browser
- **Pros:** No local setup needed
- **Cons:** Requires subscription

#### 5. **Manual Export** (Free but tedious)
- Open Google Maps for Dubravka 1836
- Use browser extension like "Data Miner" or "Web Scraper"
- Export reviews to CSV manually
- **Pros:** Free, works for one-time extraction
- **Cons:** Time-consuming, not automated

---

## Data Available (Alternative Source)

### ✅ TripAdvisor Data Already Exists

**File:** `/home/user/tripadvisor/Dubravka.csv`
**Reviews:** 5,942 reviews
**Date Range:** September 2015 - October 2025
**Columns:**
- username
- location
- country
- rating (1-5)
- rating_value
- rating_service
- rating_food
- rating_atmosphere
- review (full text)
- title
- date

**Coverage:** 10 years of TripAdvisor reviews (excellent for analysis)

### Comparison: Google vs TripAdvisor

| Metric | Google Maps | TripAdvisor (Available) |
|--------|-------------|------------------------|
| **Reviews** | ~200-400 | ✅ **5,942** |
| **Date Range** | Recent (1-2 years) | ✅ **2015-2025 (10 years)** |
| **Details** | Basic (name, rating, text) | ✅ **Detailed (food, service, atmosphere)** |
| **Status** | ❌ Not extractable | ✅ **Already extracted** |

**Recommendation:** Use the excellent TripAdvisor dataset you already have!

---

## Technical Analysis

### Google's Anti-Scraping Measures

1. **JavaScript Rendering:** Reviews loaded via AJAX after page load
2. **Dynamic Selectors:** HTML class names change frequently
3. **API Authentication:** Official APIs require OAuth/API keys
4. **Rate Limiting:** Aggressive blocking of automated requests
5. **CAPTCHA:** Triggered by suspicious activity

### What Would Work (Not Available Here)

```python
# IF we had:
# - GUI/X11 display
# - Chromium/Chrome browser
# - ChromeDriver
# THEN this would work:

from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://www.google.com/maps/search/Dubravka+1836")
# ... scroll, extract reviews ...
# This works on local machine, NOT on server
```

---

## Files Created

| File | Purpose | Status |
|------|---------|--------|
| `scrape_dubravka_api.py` | HTTP-based scraper (no browser) | ✅ Fixed syntax, tested, failed |
| `advanced_google_scraper.py` | 5 HTTP methods | ✅ Created, tested, failed |
| `requests_html_scraper.py` | JS rendering attempt | ✅ Created, tested, failed (Chromium issue) |
| `DubravkaGoogle.csv` | Template CSV file | ✅ Created (empty template) |
| `GOOGLE_SCRAPING_REPORT.md` | This report | ✅ Created |
| `debug_*.html` | Debug HTML files | ✅ Created (5 files) |

---

## Recommendations

### Immediate Action

1. **Use TripAdvisor data** - You already have 5,942 high-quality reviews
2. **If Google data is critical:**
   - Option A: Sign up for Outscraper API ($9-49/month) ← Recommended
   - Option B: Run `scrape_dubravka_google.py` on local computer with GUI
   - Option C: Use SerpAPI ($50/month)

### Long-term Solution

For automated Google reviews extraction:
- **Server:** Use Outscraper or SerpAPI (paid but reliable)
- **Local:** Use Selenium script (free but requires GUI)
- **Hybrid:** Scrape locally, upload to server for analysis

---

## Code Examples (For Future Use)

### If using Outscraper API:

```python
from outscraper import ApiClient
import csv

api = ApiClient(api_key='YOUR_OUTSCRAPER_API_KEY')

# Extract Dubravka reviews
results = api.google_maps_reviews(
    ['Dubravka 1836 Dubrovnik'],
    reviews_limit=500,
    language='en'
)

# Save to CSV
with open('DubravkaGoogle.csv', 'w', encoding='utf-8', newline='') as f:
    fieldnames = ['restaurant', 'reviewer_name', 'rating', 'review_text', 'review_date']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for place in results:
        for review in place.get('reviews_data', []):
            writer.writerow({
                'restaurant': 'Dubravka 1836',
                'reviewer_name': review.get('author_title'),
                'rating': review.get('review_rating'),
                'review_text': review.get('review_text'),
                'review_date': review.get('review_datetime_utc')
            })

print("✅ Reviews saved to DubravkaGoogle.csv")
```

### If using local Selenium (already exists):

```bash
# On local computer with GUI:
cd /path/to/tripadvisor
python3 scrape_dubravka_google.py

# This will:
# 1. Open Chrome browser
# 2. Navigate to Google Maps
# 3. Scroll through all reviews
# 4. Extract 200-400+ reviews
# 5. Save to DubravkaGoogle.csv
```

---

## Conclusion

**Status:** Google Maps reviews extraction **FAILED** due to server environment limitations.

**Reason:** Google requires JavaScript rendering which needs a browser (Chrome/Chromium), but server has no GUI and cannot run browsers.

**Solution:**
1. ✅ **Immediate:** Use existing 5,942 TripAdvisor reviews in `Dubravka.csv`
2. ✅ **Paid:** Use Outscraper API ($9-49/month) for automated Google reviews
3. ✅ **Free:** Run `scrape_dubravka_google.py` on local computer with GUI

**Files:**
- Template CSV: `/home/user/tripadvisor/DubravkaGoogle.csv`
- Report: `/home/user/tripadvisor/GOOGLE_SCRAPING_REPORT.md`
- Scrapers: `scrape_dubravka_api.py`, `advanced_google_scraper.py`, `requests_html_scraper.py`
- Debug files: `debug_*.html` (5 files)

---

**Tested Methods:** 7 different HTTP-based approaches
**Success Rate:** 0/7
**Root Cause:** Google Maps requires JavaScript/browser rendering
**Alternative Data:** 5,942 TripAdvisor reviews available ✅

---

*Report generated: November 9, 2025*
*Environment: Server (no GUI/X11)*
*Target: Dubravka 1836 Restaurant, Dubrovnik*
