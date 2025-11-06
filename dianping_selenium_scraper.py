#!/usr/bin/env python3
"""
Advanced Dianping Scraper using Selenium
Handles JavaScript rendering and cookies
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
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not installed. Install with: pip install selenium")

# Restaurant mappings
RESTAURANTS = {
    "Arsenal": {
        "name": "Gradska kavana Arsenal Restaurant",
        "id": "qB4r61711ac153e9c2b00ae22cce1e053615fcf47764c6e8720ce0d6677aab3126c49d2a41ed92aaaff8282c246900vxu5",
        "reviews": 189
    },
    "Panorama": {
        "name": "Restaurant Panorama",
        "id": "qB4r4d7c30a347b1eeb81bfe76fa5a021e14fcf47764c6e8720ce0d6677aab3126c49d2a41ed92aaaff8282c246900vxu5",
        "reviews": 224
    },
    "Dubravka": {
        "name": "Dubravka 1836 Restaurant & Cafe",
        "id": "qB4r617f7ed90fe7cbe317eb70d11d0e386efcf47764c6e8720ce0d6677aab3126c49d2a41ed92aaaff8282c246900vxu5",
        "reviews": 153
    },
    "Nautika": {
        "name": "Restaurant Nautika",
        "id": "unknown",  # To be discovered
        "reviews": 0
    }
}


class DianpingSeleniumScraper:
    def __init__(self, headless: bool = True, cookies_file: Optional[str] = None):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required. Install with: pip install selenium")

        self.headless = headless
        self.cookies_file = cookies_file
        self.driver = None
        self.all_reviews = []
        self.base_url = "https://www.dianping.com"

    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        chrome_options.add_argument('--lang=zh-CN')

        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            print("✅ Chrome driver initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver: {e}")
            print("💡 Make sure chromedriver is installed and in PATH")
            raise

    def load_cookies(self):
        """Load cookies from file"""
        if not self.cookies_file or not Path(self.cookies_file).exists():
            return False

        try:
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)

            for cookie in cookies:
                self.driver.add_cookie(cookie)

            print(f"✅ Loaded {len(cookies)} cookies")
            return True
        except Exception as e:
            print(f"❌ Failed to load cookies: {e}")
            return False

    def save_cookies(self):
        """Save current cookies to file"""
        if not self.cookies_file:
            self.cookies_file = 'dianping_cookies.json'

        cookies = self.driver.get_cookies()
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"💾 Saved {len(cookies)} cookies to {self.cookies_file}")

    def wait_for_manual_login(self, timeout: int = 300):
        """Wait for user to manually login"""
        print("\n" + "="*60)
        print("⏳ WAITING FOR MANUAL LOGIN")
        print("="*60)
        print("""
Please complete the following steps:

1. A browser window should have opened (or check your taskbar)
2. Login to Dianping.com using your credentials
3. After successful login, return here
4. Press ENTER to continue...

Note: You have 5 minutes to complete the login.
        """)

        input("Press ENTER after you've logged in...")

        # Save cookies after login
        self.save_cookies()
        print("✅ Login completed and cookies saved!")

    def fetch_page(self, url: str, wait_time: int = 10) -> bool:
        """Fetch page and wait for content to load"""
        try:
            print(f"🔄 Loading: {url}")
            self.driver.get(url)

            # Wait for page to load
            time.sleep(3)

            # Check if login is required
            if 'login' in self.driver.current_url.lower():
                print("⚠️  Login page detected!")
                return False

            # Wait for main content
            try:
                WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print("✅ Page loaded successfully")
                return True
            except TimeoutException:
                print("⚠️  Timeout waiting for page to load")
                return False

        except Exception as e:
            print(f"❌ Error loading page: {e}")
            return False

    def scroll_page(self, scrolls: int = 3):
        """Scroll page to load dynamic content"""
        print(f"📜 Scrolling page {scrolls} times...")
        for i in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print(f"  Scroll {i+1}/{scrolls}")

    def extract_reviews_from_page(self, restaurant_name: str, max_reviews: int = 50) -> List[Dict]:
        """Extract reviews from current page"""
        reviews = []

        # Save page source for debugging
        page_source = self.driver.page_source
        debug_file = f"debug_{restaurant_name.replace(' ', '_')}.html"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"💾 Saved page source to {debug_file} for debugging")

        # Try multiple selectors for review elements
        review_selectors = [
            "//div[contains(@class, 'review-item')]",
            "//div[contains(@class, 'comment-item')]",
            "//li[contains(@class, 'review-item')]",
            "//div[contains(@class, 'ReviewItem')]",
            "//div[@class='reviews-items']/ul/li",
            "//div[contains(@class, 'J-review-item')]",
        ]

        review_elements = []
        for selector in review_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"✅ Found {len(elements)} review elements using: {selector}")
                    review_elements = elements
                    break
            except:
                continue

        if not review_elements:
            print("⚠️  No review elements found with any selector")
            print("💡 Trying to extract all text content...")

            # Try to find any review-like content
            try:
                # Look for common review patterns
                all_divs = self.driver.find_elements(By.TAG_NAME, "div")
                print(f"📊 Found {len(all_divs)} div elements, analyzing...")

                # Look for divs that might contain reviews
                for div in all_divs[:100]:  # Check first 100 divs
                    try:
                        text = div.text.strip()
                        class_name = div.get_attribute('class') or ''

                        # Check if this might be a review
                        if len(text) > 50 and ('review' in class_name.lower() or
                                                'comment' in class_name.lower() or
                                                len(text) > 100):
                            review = {
                                'restaurant': restaurant_name,
                                'reviewer': 'Unknown',
                                'rating': None,
                                'review_text': text,
                                'date': None,
                                'photos': [],
                                'scraped_at': datetime.now().isoformat(),
                                'source': 'generic_div'
                            }
                            reviews.append(review)

                            if len(reviews) >= max_reviews:
                                break
                    except:
                        continue

            except Exception as e:
                print(f"❌ Error in generic extraction: {e}")

        # Extract structured reviews
        for idx, element in enumerate(review_elements[:max_reviews], 1):
            try:
                review = self._extract_review_from_element(element, restaurant_name)
                if review:
                    reviews.append(review)
                    print(f"  ✓ Extracted review {idx}/{min(len(review_elements), max_reviews)}")
            except Exception as e:
                print(f"  ✗ Error extracting review {idx}: {e}")

        print(f"📊 Total reviews extracted: {len(reviews)}")
        return reviews

    def _extract_review_from_element(self, element, restaurant_name: str) -> Optional[Dict]:
        """Extract review data from a single element"""
        review = {
            'restaurant': restaurant_name,
            'reviewer': 'Unknown',
            'rating': None,
            'review_text': '',
            'date': None,
            'photos': [],
            'scraped_at': datetime.now().isoformat()
        }

        try:
            # Extract reviewer name
            try:
                name_elem = element.find_element(By.XPATH, ".//*[contains(@class, 'name') or contains(@class, 'username')]")
                review['reviewer'] = name_elem.text.strip()
            except:
                pass

            # Extract rating
            try:
                rating_elem = element.find_element(By.XPATH, ".//*[contains(@class, 'star') or contains(@class, 'rating')]")
                rating_class = rating_elem.get_attribute('class')
                rating_match = re.search(r'(\d+)', rating_class)
                if rating_match:
                    review['rating'] = int(rating_match.group(1))
            except:
                pass

            # Extract review text
            try:
                text_elem = element.find_element(By.XPATH, ".//*[contains(@class, 'review-text') or contains(@class, 'comment-txt')]")
                review['review_text'] = text_elem.text.strip()
            except:
                # Fallback to all text
                review['review_text'] = element.text.strip()

            # Extract date
            try:
                date_elem = element.find_element(By.XPATH, ".//*[contains(@class, 'time') or contains(@class, 'date')]")
                review['date'] = date_elem.text.strip()
            except:
                pass

            # Extract photos
            try:
                img_elements = element.find_elements(By.TAG_NAME, "img")
                review['photos'] = [img.get_attribute('src') for img in img_elements if img.get_attribute('src')]
            except:
                pass

            # Only return if we have meaningful content
            if review['review_text'] or review['rating']:
                return review

        except Exception as e:
            print(f"❌ Error extracting review details: {e}")

        return None

    def scrape_restaurant(self, restaurant_key: str, max_reviews: int = 50) -> List[Dict]:
        """Scrape reviews for a specific restaurant"""
        restaurant = RESTAURANTS[restaurant_key]
        print(f"\n{'='*60}")
        print(f"🍽️  Scraping: {restaurant['name']}")
        print(f"{'='*60}")

        reviews = []

        # Try different URL patterns
        url_patterns = [
            f"https://m.dianping.com/shop/{restaurant['id']}",  # Mobile often works better
            f"{self.base_url}/shop/{restaurant['id']}",
            f"{self.base_url}/shop/{restaurant['id']}/review_all",
        ]

        for url in url_patterns:
            print(f"\n📍 Trying: {url}")

            if self.fetch_page(url):
                # Scroll to load more content
                self.scroll_page(3)

                # Extract reviews
                extracted = self.extract_reviews_from_page(restaurant['name'], max_reviews)
                if extracted:
                    reviews.extend(extracted)
                    print(f"✅ Extracted {len(extracted)} reviews")
                    break
                else:
                    print("⚠️  No reviews found, trying next URL...")

            time.sleep(2)

        return reviews

    def scrape_all_restaurants(self, max_reviews_per_restaurant: int = 50) -> List[Dict]:
        """Scrape all restaurants"""
        if not self.driver:
            self.setup_driver()

        # Load homepage first to set cookies
        print("\n🌐 Loading Dianping homepage...")
        self.fetch_page(self.base_url)

        # Try to load cookies if available
        if self.cookies_file:
            self.load_cookies()
            self.driver.refresh()
            time.sleep(3)

        # Check if we need to login
        self.fetch_page(f"{self.base_url}/dubrovnik")
        if 'login' in self.driver.current_url.lower():
            print("\n⚠️  Login required!")
            self.wait_for_manual_login()
            self.driver.get(f"{self.base_url}/dubrovnik")

        # Scrape each restaurant
        all_reviews = []
        for restaurant_key in RESTAURANTS.keys():
            reviews = self.scrape_restaurant(restaurant_key, max_reviews_per_restaurant)
            all_reviews.extend(reviews)
            time.sleep(5)  # Be nice to the server

        self.all_reviews = all_reviews
        return all_reviews

    def save_to_json(self, filename: str = 'dianping_reviews_selenium.json'):
        """Save reviews to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_reviews, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved {len(self.all_reviews)} reviews to {filename}")

    def save_to_csv(self, filename: str = 'dianping_reviews_selenium.csv'):
        """Save reviews to CSV"""
        if not self.all_reviews:
            return

        with open(filename, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['restaurant', 'reviewer', 'rating', 'review_text', 'date', 'scraped_at']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for review in self.all_reviews:
                row = {k: v for k, v in review.items() if k in fieldnames}
                writer.writerow(row)

        print(f"💾 Saved {len(self.all_reviews)} reviews to {filename}")

    def cleanup(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 Browser closed")


def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   DIANPING SELENIUM SCRAPER                              ║
    ║   Advanced scraping with browser automation              ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    if not SELENIUM_AVAILABLE:
        print("\n❌ Selenium is not installed!")
        print("📦 Install with: pip install selenium")
        print("🌐 Also install ChromeDriver: https://chromedriver.chromium.org/")
        return

    try:
        # Configuration
        HEADLESS = False  # Set to True to run without GUI
        COOKIES_FILE = "dianping_cookies.json"  # Will be created after first login

        # Create scraper
        scraper = DianpingSeleniumScraper(
            headless=HEADLESS,
            cookies_file=COOKIES_FILE
        )

        # Scrape
        print("\n🚀 Starting scraping process...")
        reviews = scraper.scrape_all_restaurants(max_reviews_per_restaurant=50)

        # Save results
        if reviews:
            scraper.save_to_json()
            scraper.save_to_csv()

            print(f"\n{'='*60}")
            print(f"📊 SUMMARY")
            print(f"{'='*60}")
            print(f"Total reviews scraped: {len(reviews)}")

            by_restaurant = {}
            for r in reviews:
                name = r['restaurant']
                by_restaurant[name] = by_restaurant.get(name, 0) + 1

            for name, count in by_restaurant.items():
                print(f"  • {name}: {count} reviews")
        else:
            print("\n⚠️  No reviews were scraped")
            print("💡 Check the debug HTML files for page structure")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        try:
            scraper.cleanup()
        except:
            pass

    print("\n✅ Scraping completed!")


if __name__ == "__main__":
    main()
