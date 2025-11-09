#!/usr/bin/env python3
"""
Google Local/Business Reviews Scraper
Supports multiple Google review URL formats
"""

import json
import csv
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not installed. Install with: pip install selenium")


# MULTI-FORMAT SUPPORT
# Supports different Google review URL formats:
# 1. Google Maps: https://www.google.com/maps/place/...
# 2. Google Local: https://www.google.com/search?...&tbm=lcl&kgmid=...
# 3. Google My Business: https://g.page/r/...
# 4. Direct search: Just restaurant name (will search and extract)

RESTAURANTS = {
    "Arsenal": {
        "name": "Arsenal Restaurant Dubrovnik",
        "url": "",  # Add URL or just name for auto-search
        "search_query": "Arsenal Restaurant Dubrovnik",  # Fallback search
    },
    "Panorama": {
        "name": "Restaurant Panorama Dubrovnik",
        "url": "",
        "search_query": "Restaurant Panorama Dubrovnik",
    },
    "Dubravka": {
        "name": "Dubravka 1836 Restaurant & Cafe Dubrovnik",
        "url": "https://www.google.com/search?num=10&hl=hr-HR&tbm=lcl&kgmid=/g/1tdtxrgh&q=Dubravka+1836",
        "search_query": "Dubravka 1836 Dubrovnik",
    },
    "Nautika": {
        "name": "Restaurant Nautika Dubrovnik",
        "url": "",
        "search_query": "Restaurant Nautika Dubrovnik",
    }
}


class GoogleReviewsScraper:
    """
    Universal Google Reviews Scraper
    Supports Maps, Local Search, and Business Profile formats
    """

    def __init__(self, headless: bool = False):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium required: pip install selenium")

        self.headless = headless
        self.driver = None
        self.all_reviews = []

    def setup_driver(self):
        """Setup Chrome with anti-detection"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        # Anti-detection
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
            print("✅ Chrome initialized")
        except Exception as e:
            print(f"❌ Chrome init failed: {e}")
            raise

    def detect_url_format(self, url: str) -> str:
        """Detect Google URL format"""
        if not url:
            return "search"
        elif "maps.google.com" in url or "/maps/place/" in url:
            return "maps"
        elif "tbm=lcl" in url or "kgmid=" in url:
            return "local"
        elif "g.page" in url:
            return "gpage"
        else:
            return "unknown"

    def search_and_open(self, search_query: str) -> bool:
        """Search for restaurant and open business page"""
        try:
            print(f"🔍 Searching for: {search_query}")

            # Go to Google
            self.driver.get("https://www.google.com/search?q=" + search_query.replace(" ", "+"))
            time.sleep(3)

            # Look for business card/knowledge panel
            knowledge_panel_selectors = [
                "//div[@data-attrid='kc:/location/location:address']",
                "//div[contains(@class, 'knowledge-panel')]",
                "//div[@role='heading' and contains(., 'Dubrovnik')]",
                "//a[contains(@href, 'maps/place')]",
                "//div[@data-attrid='kc:/location/location:reviews']"
            ]

            for selector in knowledge_panel_selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"✅ Found business info")

                    # Try to find and click "All reviews" or similar
                    try:
                        reviews_link = self.driver.find_element(By.XPATH,
                            "//a[contains(text(), 'reviews') or contains(text(), 'recenzije') or contains(@aria-label, 'reviews')]")
                        reviews_link.click()
                        time.sleep(3)
                        return True
                    except:
                        pass

                    return True
                except:
                    continue

            print("⚠️  Business info not found in search results")
            return False

        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False

    def open_reviews_from_local_search(self, url: str) -> bool:
        """Handle Google Local Search format (tbm=lcl)"""
        try:
            print(f"🔄 Opening Local Search URL...")
            self.driver.get(url)
            time.sleep(5)

            # Save debug HTML
            with open('debug_local_search.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("💾 Saved debug_local_search.html")

            # Look for business card
            selectors = [
                "//div[@data-attrid='kc:/location/location:address']",
                "//div[contains(@class, 'VkpGBb')]",  # Business card
                "//div[@jsname and contains(@class, 'fm06If')]",
                "//a[contains(@href, 'maps/place')]"
            ]

            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    print(f"✅ Found business element")

                    # Try to find Maps link
                    try:
                        maps_link = self.driver.find_element(By.XPATH, "//a[contains(@href, '/maps/place/')]")
                        maps_url = maps_link.get_attribute('href')
                        print(f"✅ Found Maps URL: {maps_url}")

                        # Navigate to Maps
                        self.driver.get(maps_url)
                        time.sleep(5)
                        return True
                    except:
                        pass

                    return True
                except:
                    continue

            print("⚠️  No business info found in local search")
            return False

        except Exception as e:
            print(f"❌ Local search failed: {e}")
            return False

    def click_reviews_tab(self) -> bool:
        """Click reviews tab (Maps format)"""
        try:
            selectors = [
                "//button[contains(@aria-label, 'Reviews')]",
                "//button[contains(., 'reviews')]",
                "//button[@data-tab-index='1']"
            ]

            for selector in selectors:
                try:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    print("✅ Clicked reviews tab")
                    time.sleep(3)
                    return True
                except:
                    continue

            print("⚠️  Reviews tab not found")
            return False
        except Exception as e:
            print(f"❌ Click reviews failed: {e}")
            return False

    def sort_by_newest(self) -> bool:
        """Sort reviews by newest"""
        try:
            sort_selectors = [
                "//button[contains(@aria-label, 'Sort')]",
                "//button[contains(., 'Sort')]"
            ]

            for selector in sort_selectors:
                try:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    time.sleep(2)

                    newest = self.driver.find_element(By.XPATH,
                        "//div[@role='menuitemradio' and contains(., 'Newest')]")
                    newest.click()
                    print("✅ Sorted by newest")
                    time.sleep(2)
                    return True
                except:
                    continue

            return False
        except:
            return False

    def expand_read_more(self):
        """Expand all 'Read more' buttons"""
        try:
            buttons = self.driver.find_elements(By.XPATH,
                "//button[contains(@aria-label, 'See more') or contains(., 'More')]")

            clicked = 0
            for button in buttons:
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    clicked += 1
                    time.sleep(0.3)
                except:
                    pass

            if clicked > 0:
                print(f"✅ Expanded {clicked} reviews")
        except Exception as e:
            print(f"⚠️  Expand failed: {e}")

    def scroll_reviews(self, max_scrolls: int = 200) -> int:
        """Scroll reviews panel to load all"""
        try:
            scrollable_selectors = [
                "//div[@role='feed']",
                "//div[contains(@class, 'm6QErb')]//div[@role='feed']"
            ]

            scrollable = None
            for selector in scrollable_selectors:
                try:
                    scrollable = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue

            if not scrollable:
                print("⚠️  Scrollable container not found")
                return 0

            print(f"📜 Scrolling (max {max_scrolls})...")
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable)
            scrolls = 0
            no_change = 0

            for i in range(max_scrolls):
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scrollable)
                time.sleep(2)

                new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable)
                scrolls += 1

                if new_height == last_height:
                    no_change += 1
                    if no_change >= 3:
                        print(f"✅ End reached after {scrolls} scrolls")
                        break
                else:
                    no_change = 0

                last_height = new_height

                if (i + 1) % 10 == 0:
                    print(f"  Scrolled {i+1}x...")

            return scrolls
        except Exception as e:
            print(f"❌ Scroll failed: {e}")
            return 0

    def extract_reviews(self, restaurant_name: str) -> List[Dict]:
        """Extract all reviews from current page"""
        reviews = []

        try:
            debug_file = f"debug_{restaurant_name.replace(' ', '_')}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"💾 Saved {debug_file}")

            # Find review elements
            review_selectors = [
                "//div[@data-review-id]",
                "//div[contains(@class, 'jftiEf')]",
                "//div[@jsaction and contains(@class, 'fontBodyMedium')]"
            ]

            elements = []
            for selector in review_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} reviews using: {selector}")
                        break
                except:
                    continue

            if not elements:
                print("⚠️  No review elements found")
                return reviews

            # Extract each review
            for idx, elem in enumerate(elements, 1):
                try:
                    review = self._extract_review_data(elem, restaurant_name)
                    if review:
                        reviews.append(review)
                        if idx % 10 == 0:
                            print(f"  ✓ Extracted {idx} reviews...")
                except Exception as e:
                    continue

            print(f"📊 Total extracted: {len(reviews)}")
        except Exception as e:
            print(f"❌ Extraction error: {e}")

        return reviews

    def _extract_review_data(self, element, restaurant_name: str) -> Optional[Dict]:
        """Extract data from single review element"""
        review = {
            'restaurant': restaurant_name,
            'reviewer_name': None,
            'rating': None,
            'review_text': None,
            'review_date': None,
            'owner_response': None,
            'scraped_at': datetime.now().isoformat()
        }

        try:
            # Name
            try:
                name = element.find_element(By.XPATH, ".//div[contains(@class, 'd4r55')]")
                review['reviewer_name'] = name.text.strip()
            except:
                pass

            # Rating
            try:
                rating = element.find_element(By.XPATH, ".//span[contains(@class, 'kvMYJc')]")
                rating_aria = rating.get_attribute('aria-label')
                match = re.search(r'(\d+)\s*star', rating_aria)
                if match:
                    review['rating'] = int(match.group(1))
            except:
                pass

            # Text
            try:
                text = element.find_element(By.XPATH, ".//span[contains(@class, 'wiI7pd')]")
                review['review_text'] = text.text.strip()
            except:
                pass

            # Date
            try:
                date = element.find_element(By.XPATH, ".//span[contains(@class, 'rsqaWe')]")
                review['review_date'] = date.text.strip()
            except:
                pass

            # Owner response
            try:
                response = element.find_element(By.XPATH, ".//div[contains(@class, 'CDe7pd')]")
                review['owner_response'] = response.text.strip()
            except:
                pass

            if review['review_text'] or review['rating']:
                return review
        except:
            pass

        return None

    def scrape_restaurant(self, restaurant_key: str, max_scrolls: int = 200) -> List[Dict]:
        """Scrape single restaurant"""
        restaurant = RESTAURANTS[restaurant_key]
        print(f"\n{'='*60}")
        print(f"🍽️  {restaurant['name']}")
        print(f"{'='*60}")

        url = restaurant.get('url', '')
        format_type = self.detect_url_format(url)

        print(f"📋 Format: {format_type}")

        success = False

        if format_type == "maps":
            # Direct Maps URL
            self.driver.get(url)
            time.sleep(5)
            success = True
        elif format_type == "local":
            # Local search format
            success = self.open_reviews_from_local_search(url)
        elif format_type == "search" or not url:
            # Search-based
            success = self.search_and_open(restaurant.get('search_query', restaurant['name']))

        if not success:
            print(f"❌ Failed to open {restaurant['name']}")
            return []

        # Click reviews tab (Maps format)
        time.sleep(3)
        self.click_reviews_tab()

        # Sort
        time.sleep(2)
        self.sort_by_newest()

        # Scroll
        time.sleep(2)
        scrolls = self.scroll_reviews(max_scrolls)

        # Expand
        time.sleep(2)
        self.expand_read_more()

        # Extract
        time.sleep(2)
        reviews = self.extract_reviews(restaurant['name'])

        return reviews

    def scrape_all(self, max_scrolls: int = 200) -> List[Dict]:
        """Scrape all restaurants"""
        if not self.driver:
            self.setup_driver()

        all_reviews = []
        for key in RESTAURANTS.keys():
            reviews = self.scrape_restaurant(key, max_scrolls)
            all_reviews.extend(reviews)
            print(f"\n⏸️  Waiting 10s...")
            time.sleep(10)

        self.all_reviews = all_reviews
        return all_reviews

    def save_csv(self, filename: str = 'google_reviews_all.csv'):
        """Save to CSV"""
        if not self.all_reviews:
            return

        with open(filename, 'w', encoding='utf-8', newline='') as f:
            fields = ['restaurant', 'reviewer_name', 'rating', 'review_text',
                     'review_date', 'owner_response', 'scraped_at']
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

            for review in self.all_reviews:
                writer.writerow({k: v for k, v in review.items() if k in fields})

        print(f"\n💾 Saved {len(self.all_reviews)} reviews to {filename}")

    def save_json(self, filename: str = 'google_reviews_all.json'):
        """Save to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_reviews, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved to {filename}")

    def cleanup(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 Browser closed")


def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   GOOGLE REVIEWS SCRAPER - UNIVERSAL                     ║
    ║   Supports Maps, Local Search, and auto-search          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    if not SELENIUM_AVAILABLE:
        print("❌ Install: pip install selenium")
        return

    try:
        HEADLESS = False
        MAX_SCROLLS = 200

        scraper = GoogleReviewsScraper(headless=HEADLESS)

        print(f"\n🚀 Starting scraper...")
        print(f"⚙️  Config: HEADLESS={HEADLESS}, MAX_SCROLLS={MAX_SCROLLS}\n")

        reviews = scraper.scrape_all(max_scrolls=MAX_SCROLLS)

        if reviews:
            scraper.save_csv()
            scraper.save_json()

            print(f"\n{'='*60}")
            print(f"📊 SUMMARY")
            print(f"{'='*60}")
            print(f"Total: {len(reviews)} reviews")

            by_rest = {}
            for r in reviews:
                name = r['restaurant']
                by_rest[name] = by_rest.get(name, 0) + 1

            for name, count in by_rest.items():
                print(f"  • {name}: {count}")

            # Ratings
            print(f"\n📈 Average Ratings:")
            for name in by_rest.keys():
                rest_reviews = [r for r in reviews if r['restaurant'] == name and r['rating']]
                if rest_reviews:
                    avg = sum(r['rating'] for r in rest_reviews) / len(rest_reviews)
                    print(f"  • {name}: {avg:.2f} ⭐")
        else:
            print("\n⚠️  No reviews scraped")
            print("💡 Check debug HTML files")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        try:
            scraper.cleanup()
        except:
            pass

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
