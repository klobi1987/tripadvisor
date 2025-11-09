#!/usr/bin/env python3
"""
Google Maps Reviews Scraper using Selenium
Extracts all reviews from Google Maps for restaurants
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
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not installed. Install with: pip install selenium")

# Restaurant Google Maps URLs
RESTAURANTS = {
    "Arsenal": {
        "name": "Arsenal Restaurant",
        "url": "",  # Dodati Google Maps URL
        "location": "Dubrovnik"
    },
    "Panorama": {
        "name": "Restaurant Panorama",
        "url": "",  # Dodati Google Maps URL
        "location": "Dubrovnik"
    },
    "Dubravka": {
        "name": "Dubravka 1836 Restaurant & Cafe",
        "url": "",  # Dodati Google Maps URL
        "location": "Dubrovnik"
    },
    "Nautika": {
        "name": "Restaurant Nautika",
        "url": "",  # Dodati Google Maps URL
        "location": "Dubrovnik"
    }
}


class GoogleMapsScraper:
    def __init__(self, headless: bool = False):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required. Install with: pip install selenium")

        self.headless = headless
        self.driver = None
        self.all_reviews = []

    def setup_driver(self):
        """Setup Chrome driver with anti-detection options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        # Anti-detection settings
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--lang=en-US,en')
        chrome_options.add_argument('--window-size=1920,1080')

        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            self.driver = webdriver.Chrome(options=chrome_options)

            # Mask webdriver property
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

    def fetch_page(self, url: str, wait_time: int = 10) -> bool:
        """Fetch Google Maps page"""
        try:
            print(f"🔄 Loading: {url}")
            self.driver.get(url)
            time.sleep(5)  # Wait for initial load

            print("✅ Page loaded successfully")
            return True

        except Exception as e:
            print(f"❌ Error loading page: {e}")
            return False

    def click_all_reviews_tab(self) -> bool:
        """Click on 'All reviews' tab to expand reviews section"""
        try:
            # Wait for reviews button and click it
            reviews_button_selectors = [
                "//button[contains(@aria-label, 'Reviews')]",
                "//button[contains(., 'reviews')]",
                "//button[@data-tab-index='1']",
                "//div[contains(@class, 'review')]//button"
            ]

            for selector in reviews_button_selectors:
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

            print("⚠️  Could not find reviews tab button")
            return False

        except Exception as e:
            print(f"❌ Error clicking reviews tab: {e}")
            return False

    def sort_by_newest(self) -> bool:
        """Sort reviews by newest (optional, but helpful)"""
        try:
            # Look for sort button
            sort_button_selectors = [
                "//button[contains(@aria-label, 'Sort')]",
                "//button[contains(., 'Sort')]",
            ]

            for selector in sort_button_selectors:
                try:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    time.sleep(2)

                    # Click "Newest" option
                    newest = self.driver.find_element(By.XPATH, "//div[@role='menuitemradio' and contains(., 'Newest')]")
                    newest.click()
                    print("✅ Sorted by newest")
                    time.sleep(2)
                    return True
                except:
                    continue

            print("⚠️  Could not sort reviews")
            return False

        except Exception as e:
            print(f"⚠️  Error sorting: {e}")
            return False

    def expand_all_read_more_buttons(self):
        """Click all 'Read more' buttons to expand full review text"""
        try:
            # Find all "More" buttons
            more_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'See more') or contains(., 'More')]")

            clicked = 0
            for button in more_buttons:
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    clicked += 1
                    time.sleep(0.5)
                except:
                    pass

            if clicked > 0:
                print(f"✅ Expanded {clicked} 'Read more' buttons")

        except Exception as e:
            print(f"⚠️  Error expanding reviews: {e}")

    def scroll_reviews_panel(self, max_scrolls: int = 100) -> int:
        """Scroll the reviews panel to load all reviews"""
        try:
            # Find the scrollable reviews container
            scrollable_div_selectors = [
                "//div[contains(@class, 'review')]//div[@role='feed']",
                "//div[@tabindex='-1'][@role='feed']",
                "//div[contains(@class, 'm6QErb')]//div[@role='feed']"
            ]

            scrollable_div = None
            for selector in scrollable_div_selectors:
                try:
                    scrollable_div = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue

            if not scrollable_div:
                print("⚠️  Could not find scrollable reviews container")
                return 0

            print(f"📜 Scrolling reviews panel (max {max_scrolls} scrolls)...")

            last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            scrolls = 0
            no_change_count = 0

            for i in range(max_scrolls):
                # Scroll to bottom of the div
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scrollable_div)
                time.sleep(2)  # Wait for new content to load

                # Calculate new scroll height
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

                scrolls += 1

                if new_height == last_height:
                    no_change_count += 1
                    if no_change_count >= 3:
                        print(f"✅ Reached end of reviews after {scrolls} scrolls")
                        break
                else:
                    no_change_count = 0

                last_height = new_height

                if (i + 1) % 10 == 0:
                    print(f"  Scrolled {i + 1} times...")

            return scrolls

        except Exception as e:
            print(f"❌ Error scrolling: {e}")
            return 0

    def extract_reviews_from_page(self, restaurant_name: str) -> List[Dict]:
        """Extract all reviews from the current page"""
        reviews = []

        try:
            # Save page source for debugging
            debug_file = f"debug_google_maps_{restaurant_name.replace(' ', '_')}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"💾 Saved page source to {debug_file}")

            # Find all review elements
            review_selectors = [
                "//div[@data-review-id]",
                "//div[contains(@class, 'jftiEf')]",
                "//div[@jsaction and contains(@class, 'review')]"
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
                print("⚠️  No review elements found")
                return reviews

            # Extract each review
            for idx, element in enumerate(review_elements, 1):
                try:
                    review = self._extract_review_from_element(element, restaurant_name)
                    if review:
                        reviews.append(review)
                        if idx % 10 == 0:
                            print(f"  ✓ Extracted {idx} reviews...")
                except Exception as e:
                    print(f"  ✗ Error extracting review {idx}: {e}")
                    continue

            print(f"📊 Total reviews extracted: {len(reviews)}")

        except Exception as e:
            print(f"❌ Error in extraction: {e}")

        return reviews

    def _extract_review_from_element(self, element, restaurant_name: str) -> Optional[Dict]:
        """Extract review data from a single review element"""
        review = {
            'restaurant': restaurant_name,
            'reviewer_name': None,
            'reviewer_local_guide': False,
            'reviewer_total_reviews': None,
            'rating': None,
            'review_text': None,
            'review_date': None,
            'owner_response': None,
            'owner_response_date': None,
            'photos_count': 0,
            'helpful_count': None,
            'scraped_at': datetime.now().isoformat(),
            'source': 'Google Maps'
        }

        try:
            # Extract reviewer name
            try:
                name_elem = element.find_element(By.XPATH, ".//div[contains(@class, 'd4r55')]")
                review['reviewer_name'] = name_elem.text.strip()
            except:
                try:
                    name_elem = element.find_element(By.XPATH, ".//button[contains(@aria-label, 'Photo of')]")
                    review['reviewer_name'] = name_elem.get_attribute('aria-label').replace('Photo of ', '').strip()
                except:
                    pass

            # Extract rating (stars)
            try:
                rating_elem = element.find_element(By.XPATH, ".//span[contains(@class, 'kvMYJc')]")
                rating_aria = rating_elem.get_attribute('aria-label')
                rating_match = re.search(r'(\d+)\s*star', rating_aria)
                if rating_match:
                    review['rating'] = int(rating_match.group(1))
            except:
                pass

            # Extract review text
            try:
                text_elem = element.find_element(By.XPATH, ".//span[contains(@class, 'wiI7pd')]")
                review['review_text'] = text_elem.text.strip()
            except:
                try:
                    text_elem = element.find_element(By.XPATH, ".//div[contains(@class, 'MyEned')]//span")
                    review['review_text'] = text_elem.text.strip()
                except:
                    pass

            # Extract review date
            try:
                date_elem = element.find_element(By.XPATH, ".//span[contains(@class, 'rsqaWe')]")
                review['review_date'] = date_elem.text.strip()
            except:
                pass

            # Extract local guide status
            try:
                local_guide = element.find_element(By.XPATH, ".//div[contains(., 'Local Guide')]")
                review['reviewer_local_guide'] = True
            except:
                pass

            # Extract reviewer total reviews count
            try:
                reviews_elem = element.find_element(By.XPATH, ".//div[contains(@class, 'RfnDt')]//span[contains(., 'review')]")
                reviews_text = reviews_elem.text
                count_match = re.search(r'(\d+)\s*review', reviews_text)
                if count_match:
                    review['reviewer_total_reviews'] = int(count_match.group(1))
            except:
                pass

            # Extract owner response
            try:
                response_elem = element.find_element(By.XPATH, ".//div[contains(@class, 'CDe7pd')]")
                review['owner_response'] = response_elem.text.strip()

                # Try to get response date
                try:
                    response_date_elem = element.find_element(By.XPATH, ".//div[contains(@class, 'CDe7pd')]//following-sibling::div[contains(@class, 'rsqaWe')]")
                    review['owner_response_date'] = response_date_elem.text.strip()
                except:
                    pass
            except:
                pass

            # Count photos
            try:
                photos = element.find_elements(By.XPATH, ".//button[contains(@aria-label, 'Photo')]")
                review['photos_count'] = len(photos)
            except:
                pass

            # Only return if we have meaningful content
            if review['review_text'] or review['rating']:
                return review

        except Exception as e:
            print(f"❌ Error extracting review details: {e}")

        return None

    def scrape_restaurant(self, restaurant_key: str, max_scrolls: int = 100) -> List[Dict]:
        """Scrape all reviews for a specific restaurant"""
        restaurant = RESTAURANTS[restaurant_key]
        print(f"\n{'='*60}")
        print(f"🍽️  Scraping: {restaurant['name']}")
        print(f"{'='*60}")

        url = restaurant['url']
        if not url:
            print(f"❌ No URL provided for {restaurant['name']}")
            print("💡 Please add Google Maps URL in RESTAURANTS dictionary")
            return []

        if not self.fetch_page(url):
            return []

        # Click on reviews tab
        time.sleep(3)
        self.click_all_reviews_tab()

        # Optional: Sort by newest
        time.sleep(2)
        self.sort_by_newest()

        # Scroll to load all reviews
        time.sleep(2)
        scrolls = self.scroll_reviews_panel(max_scrolls)
        print(f"✅ Completed {scrolls} scrolls")

        # Expand all "Read more" buttons
        time.sleep(2)
        self.expand_all_read_more_buttons()

        # Extract reviews
        time.sleep(2)
        reviews = self.extract_reviews_from_page(restaurant['name'])

        return reviews

    def scrape_all_restaurants(self, max_scrolls_per_restaurant: int = 100) -> List[Dict]:
        """Scrape all restaurants"""
        if not self.driver:
            self.setup_driver()

        all_reviews = []
        for restaurant_key in RESTAURANTS.keys():
            reviews = self.scrape_restaurant(restaurant_key, max_scrolls_per_restaurant)
            all_reviews.extend(reviews)

            print(f"\n⏸️  Waiting 10 seconds before next restaurant...")
            time.sleep(10)

        self.all_reviews = all_reviews
        return all_reviews

    def save_to_json(self, filename: str = 'google_maps_reviews.json'):
        """Save reviews to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_reviews, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved {len(self.all_reviews)} reviews to {filename}")

    def save_to_csv(self, filename: str = 'google_maps_reviews.csv'):
        """Save reviews to CSV"""
        if not self.all_reviews:
            print("⚠️  No reviews to save")
            return

        with open(filename, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'restaurant', 'reviewer_name', 'reviewer_local_guide', 'reviewer_total_reviews',
                'rating', 'review_text', 'review_date', 'owner_response',
                'owner_response_date', 'photos_count', 'scraped_at', 'source'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for review in self.all_reviews:
                writer.writerow(review)

        print(f"💾 Saved {len(self.all_reviews)} reviews to {filename}")

    def cleanup(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 Browser closed")


def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   GOOGLE MAPS REVIEWS SCRAPER                            ║
    ║   Extract all reviews from Google Maps                   ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    if not SELENIUM_AVAILABLE:
        print("\n❌ Selenium is not installed!")
        print("📦 Install with: pip install selenium")
        return

    # Check if URLs are configured
    missing_urls = [key for key, data in RESTAURANTS.items() if not data['url']]
    if missing_urls:
        print("\n⚠️  Missing Google Maps URLs for:")
        for key in missing_urls:
            print(f"   • {RESTAURANTS[key]['name']}")
        print("\n💡 Please add URLs in the RESTAURANTS dictionary at the top of this script")
        print("\n📝 To get Google Maps URL:")
        print("   1. Go to Google Maps")
        print("   2. Search for the restaurant")
        print("   3. Click on the restaurant")
        print("   4. Copy the URL from browser address bar")
        print("   5. Paste it in RESTAURANTS dictionary\n")
        return

    try:
        # Configuration
        HEADLESS = False  # Set to True to run without GUI
        MAX_SCROLLS = 200  # Maximum scrolls per restaurant (increase for more reviews)

        # Create scraper
        scraper = GoogleMapsScraper(headless=HEADLESS)

        # Scrape
        print("\n🚀 Starting scraping process...")
        print(f"⚙️  Configuration: MAX_SCROLLS={MAX_SCROLLS}, HEADLESS={HEADLESS}\n")

        reviews = scraper.scrape_all_restaurants(max_scrolls_per_restaurant=MAX_SCROLLS)

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

            # Calculate average rating per restaurant
            print(f"\n📈 Average Ratings:")
            for name in by_restaurant.keys():
                restaurant_reviews = [r for r in reviews if r['restaurant'] == name and r['rating']]
                if restaurant_reviews:
                    avg_rating = sum(r['rating'] for r in restaurant_reviews) / len(restaurant_reviews)
                    print(f"  • {name}: {avg_rating:.2f} ⭐")

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
