#!/usr/bin/env python3
"""
Dubravka 1836 Google Reviews Scraper
Extracts ALL reviews from Google and saves to DubravkaGoogle.csv
"""

import json
import csv
import time
import re
from datetime import datetime
from typing import List, Dict, Optional

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not installed. Install with: pip install selenium")
    exit(1)


# Dubravka 1836 Google Reviews URL
DUBRAVKA_URL = "https://www.google.com/search?q=Dubravka+1836&num=10&hl=hr-HR&tbm=lcl#lkt=LocalPoiReviews"

# Alternative URLs (fallback)
DUBRAVKA_URLS = [
    "https://www.google.com/search?q=Dubravka+1836&num=10&hl=hr-HR&tbm=lcl#lkt=LocalPoiReviews",
    "https://www.google.com/search?q=Dubravka+1836+Dubrovnik&tbm=lcl",
    "https://www.google.com/maps/search/Dubravka+1836+Dubrovnik",
]


class DubravkaScraper:
    """Specialized scraper for Dubravka 1836 Google reviews"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.reviews = []

    def setup_driver(self):
        """Setup Chrome with anti-detection"""
        chrome_options = Options()

        # Always use headless in server environment
        chrome_options.add_argument('--headless=new')

        # Critical for Docker/sandbox environments
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')

        # Anti-detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--lang=hr-HR,hr,en-US,en')

        # Additional sandbox options
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')

        # Stability options for server environments
        chrome_options.add_argument('--disable-crash-reporter')
        chrome_options.add_argument('--disable-in-process-stack-traces')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--disable-features=BlockInsecurePrivateNetworkRequests')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-insecure-localhost')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-breakpad')
        chrome_options.add_argument('--disable-component-extensions-with-background-pages')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--disable-hang-monitor')
        chrome_options.add_argument('--disable-prompt-on-repost')
        chrome_options.add_argument('--disable-sync')

        # Memory options
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--shm-size=2gb')

        # Performance
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('prefs', {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0,
        })

        try:
            # Try to use Chrome binary explicitly
            chrome_options.binary_location = '/usr/bin/google-chrome'

            self.driver = webdriver.Chrome(options=chrome_options)

            # Mask webdriver
            try:
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    '''
                })
            except:
                pass  # CDP commands might fail in headless, continue anyway

            print("✅ Chrome driver initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Chrome: {e}")
            print("💡 Make sure chromedriver is installed")
            return False

    def open_reviews_page(self) -> bool:
        """Open Dubravka reviews page"""
        print("\n🔄 Opening Dubravka 1836 reviews...")

        for idx, url in enumerate(DUBRAVKA_URLS, 1):
            try:
                print(f"\n📍 Trying URL {idx}/{len(DUBRAVKA_URLS)}...")
                print(f"   {url[:80]}...")

                self.driver.get(url)
                time.sleep(5)

                # Check if page loaded
                if "google" in self.driver.current_url.lower():
                    print(f"✅ Page loaded: {self.driver.title[:50]}...")

                    # Save debug HTML
                    with open('debug_dubravka_initial.html', 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    print("💾 Saved debug_dubravka_initial.html")

                    # Wait a bit more for content to load
                    time.sleep(3)
                    return True
                else:
                    print(f"⚠️  Unexpected redirect")
                    continue

            except Exception as e:
                print(f"❌ Error with URL {idx}: {e}")
                continue

        print("\n❌ Failed to open any URL")
        return False

    def accept_google_consent(self) -> bool:
        """Click Google consent/privacy buttons if present"""
        try:
            print("\n🍪 Checking for Google consent/privacy popups...")

            # Common Google consent button selectors
            consent_button_selectors = [
                # English
                "//button[contains(., 'Accept all')]",
                "//button[contains(., 'I agree')]",
                "//button[contains(., 'Agree')]",
                "//button[@aria-label='Accept all']",
                "//button[contains(@class, 'VfPpkd')]//span[contains(., 'Accept')]",
                # Croatian
                "//button[contains(., 'Prihvaćam')]",
                "//button[contains(., 'Prihvati sve')]",
                "//button[contains(., 'Slažem se')]",
                # Generic
                "//button[contains(@jsname, 'higCR')]",  # Google's "Accept" button
                "//div[@role='dialog']//button[2]",  # Second button in dialog (usually "Accept")
            ]

            for selector in consent_button_selectors:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    print(f"✅ Clicked consent button")
                    time.sleep(2)
                    return True
                except:
                    continue

            print("   No consent popup found (or already accepted)")
            return True

        except Exception as e:
            print(f"   No consent popup (continuing anyway)")
            return True

    def click_all_reviews(self) -> bool:
        """Click to show all reviews"""
        try:
            print("\n🔍 Looking for reviews section...")

            # Multiple selectors to find reviews
            review_section_selectors = [
                "//div[contains(@class, 'review')]",
                "//div[@role='feed']",
                "//div[contains(@aria-label, 'Review')]",
                "//div[contains(@aria-label, 'Recenzij')]",  # Croatian
                "//button[contains(., 'reviews')]",
                "//button[contains(., 'recenzij')]",  # Croatian
            ]

            for selector in review_section_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        print(f"✅ Found reviews section with: {selector}")
                        time.sleep(2)
                        return True
                except:
                    continue

            # Try clicking "See all reviews" button
            see_all_selectors = [
                "//button[contains(., 'See all')]",
                "//button[contains(., 'Vidi sve')]",
                "//a[contains(., 'All reviews')]",
                "//a[contains(., 'Sve recenzije')]",
            ]

            for selector in see_all_selectors:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self.driver.execute_script("arguments[0].click();", button)
                    print(f"✅ Clicked 'See all reviews'")
                    time.sleep(3)
                    return True
                except:
                    continue

            print("⚠️  Reviews section found (continuing anyway)")
            return True

        except Exception as e:
            print(f"❌ Error finding reviews: {e}")
            return False

    def sort_by_newest(self) -> bool:
        """Sort reviews by newest"""
        try:
            print("\n📅 Sorting by newest...")

            sort_selectors = [
                "//button[contains(@aria-label, 'Sort')]",
                "//button[contains(., 'Sort')]",
                "//button[contains(., 'Sortiraj')]",  # Croatian
                "//div[contains(@role, 'button') and contains(., 'Sort')]",
            ]

            for selector in sort_selectors:
                try:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    time.sleep(2)

                    # Click "Newest"
                    newest_selectors = [
                        "//div[@role='menuitemradio' and contains(., 'Newest')]",
                        "//div[@role='menuitemradio' and contains(., 'Najnovije')]",
                        "//span[contains(., 'Newest')]",
                        "//span[contains(., 'Najnovije')]",
                    ]

                    for newest_sel in newest_selectors:
                        try:
                            newest = self.driver.find_element(By.XPATH, newest_sel)
                            newest.click()
                            print("✅ Sorted by newest")
                            time.sleep(2)
                            return True
                        except:
                            continue

                except:
                    continue

            print("⚠️  Could not sort (continuing anyway)")
            return False

        except Exception as e:
            print(f"⚠️  Sort error: {e}")
            return False

    def expand_all_reviews(self):
        """Click all 'More' buttons to expand review text"""
        try:
            print("\n📖 Expanding review texts...")

            more_button_selectors = [
                "//button[contains(@aria-label, 'See more')]",
                "//button[contains(., 'More')]",
                "//button[contains(., 'Više')]",  # Croatian
                "//span[contains(., 'more')]/..",
            ]

            total_clicked = 0
            for selector in more_button_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)

                    for button in buttons:
                        try:
                            if button.is_displayed() and button.is_enabled():
                                self.driver.execute_script("arguments[0].click();", button)
                                total_clicked += 1
                                time.sleep(0.2)
                        except:
                            continue

                except:
                    continue

            if total_clicked > 0:
                print(f"✅ Expanded {total_clicked} reviews")
            else:
                print("⚠️  No 'More' buttons found (reviews might be short)")

        except Exception as e:
            print(f"⚠️  Expand error: {e}")

    def scroll_to_load_all_reviews(self, max_scrolls: int = 300) -> int:
        """Scroll to load all reviews"""
        try:
            print(f"\n📜 Scrolling to load all reviews (max {max_scrolls} scrolls)...")

            # Find scrollable container
            scrollable_selectors = [
                "//div[@role='feed']",
                "//div[contains(@class, 'm6QErb')]//div[@role='feed']",
                "//div[contains(@class, 'review-dialog-list')]",
                "//div[@aria-label and contains(@class, 'scrollable')]",
            ]

            scrollable = None
            for selector in scrollable_selectors:
                try:
                    scrollable = self.driver.find_element(By.XPATH, selector)
                    print(f"✅ Found scrollable container")
                    break
                except:
                    continue

            if not scrollable:
                print("⚠️  Scrollable container not found, trying page scroll")
                # Fallback to whole page scroll
                for i in range(min(max_scrolls, 50)):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    if (i + 1) % 10 == 0:
                        print(f"   Scrolled {i+1}x...")
                return i + 1

            # Scroll the container
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable)
            scrolls = 0
            no_change_count = 0

            for i in range(max_scrolls):
                # Scroll to bottom
                self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight)",
                    scrollable
                )
                time.sleep(1.5)

                # Check new height
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable)
                scrolls += 1

                if new_height == last_height:
                    no_change_count += 1
                    if no_change_count >= 5:
                        print(f"✅ Reached end after {scrolls} scrolls")
                        break
                else:
                    no_change_count = 0

                last_height = new_height

                if (i + 1) % 20 == 0:
                    print(f"   Scrolled {i+1}x...")

            return scrolls

        except Exception as e:
            print(f"❌ Scroll error: {e}")
            return 0

    def extract_all_reviews(self) -> List[Dict]:
        """Extract all reviews from page"""
        print("\n🔍 Extracting reviews...")

        reviews = []

        try:
            # Save final page HTML for debugging
            with open('debug_dubravka_final.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("💾 Saved debug_dubravka_final.html")

            # Find all review elements
            review_element_selectors = [
                "//div[@data-review-id]",
                "//div[@jslog and contains(@class, 'fontBodyMedium')]",
                "//div[contains(@class, 'jftiEf')]",
                "//div[@data-review-id or @data-review]",
            ]

            review_elements = []
            for selector in review_element_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements and len(elements) > len(review_elements):
                        review_elements = elements
                        print(f"✅ Found {len(elements)} review elements with: {selector}")
                except Exception as e:
                    continue

            if not review_elements:
                print("⚠️  No review elements found with standard selectors")
                print("💡 Trying alternative extraction...")

                # Alternative: look for any div with review-like content
                try:
                    all_divs = self.driver.find_elements(By.TAG_NAME, "div")
                    print(f"   Found {len(all_divs)} total divs, analyzing...")

                    # Look for divs that might contain reviews
                    for div in all_divs[:500]:  # Check first 500
                        try:
                            text = div.text.strip()
                            if len(text) > 30 and len(text) < 5000:  # Reasonable review length
                                # Check if it looks like a review
                                if any(word in text.lower() for word in ['stars', 'star', 'rating', 'review', '★']):
                                    review_elements.append(div)
                        except:
                            continue

                    if review_elements:
                        print(f"✅ Found {len(review_elements)} potential reviews via alternative method")
                except:
                    pass

            if not review_elements:
                print("❌ No reviews found")
                return reviews

            # Extract data from each review
            print(f"\n📊 Extracting data from {len(review_elements)} reviews...")

            for idx, element in enumerate(review_elements, 1):
                try:
                    review = self._extract_review_data(element)
                    if review:
                        reviews.append(review)

                        if idx % 25 == 0:
                            print(f"   ✓ Extracted {idx}/{len(review_elements)} reviews...")
                except Exception as e:
                    continue

            print(f"\n✅ Successfully extracted {len(reviews)} reviews")

        except Exception as e:
            print(f"❌ Extraction error: {e}")
            import traceback
            traceback.print_exc()

        return reviews

    def _extract_review_data(self, element) -> Optional[Dict]:
        """Extract data from single review element"""
        review = {
            'restaurant': 'Dubravka 1836',
            'reviewer_name': None,
            'reviewer_local_guide': False,
            'reviewer_reviews_count': None,
            'reviewer_photos_count': None,
            'rating': None,
            'review_text': None,
            'review_date': None,
            'review_likes': None,
            'owner_response': None,
            'owner_response_date': None,
            'review_photos_count': 0,
            'scraped_at': datetime.now().isoformat(),
            'source': 'Google'
        }

        try:
            # Reviewer name
            try:
                name_selectors = [
                    ".//div[contains(@class, 'd4r55')]",
                    ".//button[contains(@aria-label, 'Photo of')]",
                    ".//span[contains(@class, 'author')]",
                ]
                for sel in name_selectors:
                    try:
                        name_elem = element.find_element(By.XPATH, sel)
                        if 'Photo of' in name_elem.get_attribute('aria-label') or '':
                            review['reviewer_name'] = name_elem.get_attribute('aria-label').replace('Photo of ', '').strip()
                        else:
                            review['reviewer_name'] = name_elem.text.strip()
                        if review['reviewer_name']:
                            break
                    except:
                        continue
            except:
                pass

            # Local Guide status
            try:
                lg = element.find_element(By.XPATH, ".//div[contains(., 'Local Guide')]")
                review['reviewer_local_guide'] = True
            except:
                pass

            # Reviewer stats (reviews count)
            try:
                stats_elem = element.find_element(By.XPATH, ".//div[contains(@class, 'RfnDt')]")
                stats_text = stats_elem.text

                # Extract review count
                review_match = re.search(r'(\d+)\s*review', stats_text, re.IGNORECASE)
                if review_match:
                    review['reviewer_reviews_count'] = int(review_match.group(1))

                # Extract photo count
                photo_match = re.search(r'(\d+)\s*photo', stats_text, re.IGNORECASE)
                if photo_match:
                    review['reviewer_photos_count'] = int(photo_match.group(1))
            except:
                pass

            # Rating (stars)
            try:
                rating_elem = element.find_element(By.XPATH, ".//span[contains(@class, 'kvMYJc') or @role='img']")
                rating_aria = rating_elem.get_attribute('aria-label') or ''

                # Match patterns like "5 stars" or "5 out of 5 stars"
                rating_match = re.search(r'(\d+)\s*(?:out of \d+ )?star', rating_aria, re.IGNORECASE)
                if rating_match:
                    review['rating'] = int(rating_match.group(1))
            except:
                pass

            # Review text
            try:
                text_selectors = [
                    ".//span[contains(@class, 'wiI7pd')]",
                    ".//div[contains(@class, 'MyEned')]//span",
                    ".//span[@lang]",
                ]
                for sel in text_selectors:
                    try:
                        text_elem = element.find_element(By.XPATH, sel)
                        text = text_elem.text.strip()
                        if text and len(text) > 5:
                            review['review_text'] = text
                            break
                    except:
                        continue
            except:
                pass

            # Review date
            try:
                date_selectors = [
                    ".//span[contains(@class, 'rsqaWe')]",
                    ".//span[contains(@class, 'date')]",
                ]
                for sel in date_selectors:
                    try:
                        date_elem = element.find_element(By.XPATH, sel)
                        review['review_date'] = date_elem.text.strip()
                        if review['review_date']:
                            break
                    except:
                        continue
            except:
                pass

            # Owner response
            try:
                response_selectors = [
                    ".//div[contains(@class, 'CDe7pd')]",
                    ".//div[contains(., 'Response from the owner')]",
                    ".//div[contains(., 'Odgovor vlasnika')]",
                ]
                for sel in response_selectors:
                    try:
                        response_elem = element.find_element(By.XPATH, sel)
                        review['owner_response'] = response_elem.text.strip()
                        if review['owner_response']:
                            break
                    except:
                        continue
            except:
                pass

            # Review photos count
            try:
                photos = element.find_elements(By.XPATH, ".//button[contains(@aria-label, 'Photo')]")
                review['review_photos_count'] = len(photos)
            except:
                pass

            # Only return if we have meaningful content
            if review['review_text'] or review['rating']:
                return review

        except Exception as e:
            pass

        return None

    def save_to_csv(self, filename: str = 'DubravkaGoogle.csv'):
        """Save reviews to CSV"""
        if not self.reviews:
            print("\n⚠️  No reviews to save")
            return False

        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                fieldnames = [
                    'restaurant',
                    'reviewer_name',
                    'reviewer_local_guide',
                    'reviewer_reviews_count',
                    'reviewer_photos_count',
                    'rating',
                    'review_text',
                    'review_date',
                    'review_likes',
                    'owner_response',
                    'owner_response_date',
                    'review_photos_count',
                    'scraped_at',
                    'source'
                ]

                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()

                for review in self.reviews:
                    writer.writerow(review)

            print(f"\n💾 ✅ Saved {len(self.reviews)} reviews to {filename}")
            return True

        except Exception as e:
            print(f"\n❌ Error saving CSV: {e}")
            return False

    def save_to_json(self, filename: str = 'DubravkaGoogle.json'):
        """Save reviews to JSON (backup)"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.reviews, f, ensure_ascii=False, indent=2)
            print(f"💾 Saved backup to {filename}")
            return True
        except Exception as e:
            print(f"❌ JSON save error: {e}")
            return False

    def cleanup(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 Browser closed")

    def run(self, max_scrolls: int = 300):
        """Main scraping workflow"""
        print("\n" + "="*70)
        print("🍽️  DUBRAVKA 1836 - GOOGLE REVIEWS SCRAPER")
        print("="*70)

        # Setup
        if not self.setup_driver():
            return False

        # Open page
        if not self.open_reviews_page():
            print("\n❌ Failed to open reviews page")
            self.cleanup()
            return False

        # Accept Google consent/privacy popup
        time.sleep(3)
        self.accept_google_consent()

        # Click to show reviews
        time.sleep(2)
        self.click_all_reviews()

        # Sort by newest
        time.sleep(2)
        self.sort_by_newest()

        # Scroll to load all
        time.sleep(2)
        scrolls = self.scroll_to_load_all_reviews(max_scrolls)
        print(f"✅ Completed {scrolls} scrolls")

        # Expand all reviews
        time.sleep(2)
        self.expand_all_reviews()

        # Extract
        time.sleep(2)
        self.reviews = self.extract_all_reviews()

        if not self.reviews:
            print("\n❌ No reviews extracted")
            self.cleanup()
            return False

        # Save
        self.save_to_csv('DubravkaGoogle.csv')
        self.save_to_json('DubravkaGoogle.json')

        # Stats
        print("\n" + "="*70)
        print("📊 EXTRACTION SUMMARY")
        print("="*70)
        print(f"Total reviews: {len(self.reviews)}")

        # Rating breakdown
        ratings = {}
        for r in self.reviews:
            if r['rating']:
                ratings[r['rating']] = ratings.get(r['rating'], 0) + 1

        if ratings:
            print("\n⭐ Rating breakdown:")
            for stars in sorted(ratings.keys(), reverse=True):
                print(f"   {stars} stars: {ratings[stars]} reviews")

            # Average
            total_rated = sum(ratings.values())
            avg_rating = sum(stars * count for stars, count in ratings.items()) / total_rated
            print(f"\n📈 Average rating: {avg_rating:.2f} ⭐ ({total_rated} rated reviews)")

        # With text
        with_text = len([r for r in self.reviews if r['review_text']])
        print(f"\n📝 Reviews with text: {with_text}")

        # With owner response
        with_response = len([r for r in self.reviews if r['owner_response']])
        print(f"💬 Reviews with owner response: {with_response}")

        # Local Guides
        local_guides = len([r for r in self.reviews if r['reviewer_local_guide']])
        print(f"🎖️  Reviews from Local Guides: {local_guides}")

        print("\n" + "="*70)
        print("✅ SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📁 Output file: DubravkaGoogle.csv")
        print(f"📁 Backup file: DubravkaGoogle.json")
        print(f"🐛 Debug files: debug_dubravka_initial.html, debug_dubravka_final.html")

        self.cleanup()
        return True


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║         DUBRAVKA 1836 - GOOGLE REVIEWS SCRAPER                   ║
    ║                                                                  ║
    ║  Extracts ALL Google reviews and saves to DubravkaGoogle.csv    ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    if not SELENIUM_AVAILABLE:
        print("\n❌ Selenium not installed!")
        print("📦 Install with: pip install selenium")
        print("🌐 ChromeDriver: sudo apt-get install chromium-chromedriver")
        return

    try:
        # Configuration
        HEADLESS = True  # Must be True for server-side execution
        MAX_SCROLLS = 300  # Increase if needed for more reviews

        print(f"\n⚙️  Configuration:")
        print(f"   Headless mode: {HEADLESS}")
        print(f"   Max scrolls: {MAX_SCROLLS}")
        print(f"   Output file: DubravkaGoogle.csv")

        # Create and run scraper
        scraper = DubravkaScraper(headless=HEADLESS)
        success = scraper.run(max_scrolls=MAX_SCROLLS)

        if success:
            print("\n🎉 All done! Check DubravkaGoogle.csv")
        else:
            print("\n⚠️  Scraping incomplete. Check debug files for details.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        try:
            scraper.cleanup()
        except:
            pass

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        try:
            scraper.cleanup()
        except:
            pass


if __name__ == "__main__":
    main()
