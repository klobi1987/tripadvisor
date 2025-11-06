#!/usr/bin/env python3
"""
Dianping Restaurant Review Scraper
Extracts reviews from Dianping.com for Dubrovnik restaurants
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
import re

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
    }
}

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
]

class DianpingScraper:
    def __init__(self, use_proxy: bool = False, proxy_url: Optional[str] = None):
        self.session = requests.Session()
        self.use_proxy = use_proxy
        self.proxy_url = proxy_url
        self.base_url = "https://www.dianping.com"
        self.all_reviews = []

    def get_headers(self) -> Dict[str, str]:
        """Generate headers with random user agent"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.dianping.com/',
        }

    def fetch_page(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch page with retries and exponential backoff"""
        for attempt in range(max_retries):
            try:
                print(f"🔄 Fetching {url} (attempt {attempt + 1}/{max_retries})")

                proxies = None
                if self.use_proxy and self.proxy_url:
                    proxies = {
                        'http': self.proxy_url,
                        'https': self.proxy_url
                    }

                response = self.session.get(
                    url,
                    headers=self.get_headers(),
                    proxies=proxies,
                    timeout=30,
                    allow_redirects=True
                )

                if response.status_code == 200:
                    print(f"✅ Successfully fetched page")
                    return response.text
                elif response.status_code == 302 or response.status_code == 301:
                    print(f"⚠️  Redirect detected to: {response.headers.get('Location')}")
                    return None
                else:
                    print(f"❌ Status code: {response.status_code}")

            except Exception as e:
                print(f"❌ Error: {str(e)}")

            # Exponential backoff
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt + random.uniform(0, 1)
                print(f"⏳ Waiting {sleep_time:.1f}s before retry...")
                time.sleep(sleep_time)

        return None

    def parse_reviews(self, html: str, restaurant_name: str) -> List[Dict]:
        """Parse reviews from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        reviews = []

        # Try multiple selectors for reviews
        review_selectors = [
            'div.review-item',
            'div.comment-item',
            'div.review-list > li',
            'div[class*="review"]',
            'div.main-review',
        ]

        for selector in review_selectors:
            review_elements = soup.select(selector)
            if review_elements:
                print(f"✅ Found {len(review_elements)} reviews using selector: {selector}")
                break

        if not review_elements:
            print("⚠️  No review elements found, trying to extract from JSON-LD")
            # Try to find JSON-LD structured data
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if 'review' in data:
                        reviews.extend(self._parse_json_reviews(data['review'], restaurant_name))
                except:
                    pass

        # Parse each review element
        for idx, elem in enumerate(review_elements[:50], 1):  # Limit to 50 reviews
            try:
                review = self._extract_review_data(elem, restaurant_name, idx)
                if review:
                    reviews.append(review)
            except Exception as e:
                print(f"❌ Error parsing review {idx}: {str(e)}")

        return reviews

    def _extract_review_data(self, elem, restaurant_name: str, idx: int) -> Optional[Dict]:
        """Extract review data from HTML element"""
        review = {
            'restaurant': restaurant_name,
            'reviewer': 'Unknown',
            'rating': None,
            'review_text': '',
            'date': None,
            'photos': [],
            'scraped_at': datetime.now().isoformat()
        }

        # Try to extract reviewer name
        name_selectors = ['.username', '.user-name', '.reviewer-name', '[class*="name"]']
        for selector in name_selectors:
            name_elem = elem.select_one(selector)
            if name_elem:
                review['reviewer'] = name_elem.text.strip()
                break

        # Try to extract rating
        rating_selectors = ['.star', '.rating', '[class*="star"]', '[class*="rating"]']
        for selector in rating_selectors:
            rating_elem = elem.select_one(selector)
            if rating_elem:
                # Extract number from class or text
                rating_text = rating_elem.get('class', []) + [rating_elem.text]
                rating_match = re.search(r'(\d+)', str(rating_text))
                if rating_match:
                    review['rating'] = int(rating_match.group(1))
                    break

        # Extract review text
        text_selectors = ['.review-text', '.comment-txt', '.review-content', '[class*="review"]']
        for selector in text_selectors:
            text_elem = elem.select_one(selector)
            if text_elem:
                review['review_text'] = text_elem.text.strip()
                break

        # If no text found, try getting all text from element
        if not review['review_text']:
            review['review_text'] = elem.get_text(strip=True)

        # Extract date
        date_selectors = ['.time', '.date', '.review-time', '[class*="time"]', '[class*="date"]']
        for selector in date_selectors:
            date_elem = elem.select_one(selector)
            if date_elem:
                review['date'] = date_elem.text.strip()
                break

        # Extract photos
        img_elements = elem.find_all('img')
        review['photos'] = [img.get('src', '') for img in img_elements if img.get('src')]

        # Only return if we have meaningful content
        if review['review_text'] or review['rating']:
            return review

        return None

    def _parse_json_reviews(self, review_data, restaurant_name: str) -> List[Dict]:
        """Parse reviews from JSON-LD structured data"""
        reviews = []
        if isinstance(review_data, list):
            for item in review_data:
                reviews.append(self._convert_json_review(item, restaurant_name))
        else:
            reviews.append(self._convert_json_review(review_data, restaurant_name))
        return reviews

    def _convert_json_review(self, item: Dict, restaurant_name: str) -> Dict:
        """Convert JSON-LD review to our format"""
        return {
            'restaurant': restaurant_name,
            'reviewer': item.get('author', {}).get('name', 'Unknown'),
            'rating': item.get('reviewRating', {}).get('ratingValue'),
            'review_text': item.get('reviewBody', ''),
            'date': item.get('datePublished'),
            'photos': [],
            'scraped_at': datetime.now().isoformat()
        }

    def scrape_restaurant(self, restaurant_key: str, max_reviews: int = 50) -> List[Dict]:
        """Scrape reviews for a specific restaurant"""
        restaurant = RESTAURANTS[restaurant_key]
        print(f"\n{'='*60}")
        print(f"🍽️  Scraping: {restaurant['name']}")
        print(f"{'='*60}")

        # Try multiple URL patterns
        url_patterns = [
            f"{self.base_url}/shop/{restaurant['id']}",
            f"{self.base_url}/shop/{restaurant['id']}/review_all",
            f"https://m.dianping.com/shop/{restaurant['id']}",  # Mobile version
        ]

        reviews = []
        for url in url_patterns:
            print(f"\n📍 Trying URL: {url}")
            html = self.fetch_page(url)

            if html:
                # Check if we got a login page
                if 'login' in html.lower() or '登录' in html:
                    print("⚠️  Login required - trying next URL pattern")
                    continue

                parsed_reviews = self.parse_reviews(html, restaurant['name'])
                if parsed_reviews:
                    reviews.extend(parsed_reviews)
                    print(f"✅ Extracted {len(parsed_reviews)} reviews")
                    break

            time.sleep(random.uniform(2, 4))

        if not reviews:
            print(f"⚠️  No reviews extracted for {restaurant['name']}")

        return reviews

    def scrape_all_restaurants(self) -> List[Dict]:
        """Scrape all restaurants"""
        all_reviews = []

        for restaurant_key in RESTAURANTS.keys():
            reviews = self.scrape_restaurant(restaurant_key)
            all_reviews.extend(reviews)

            # Be nice to the server
            time.sleep(random.uniform(3, 6))

        self.all_reviews = all_reviews
        return all_reviews

    def save_to_json(self, filename: str = 'dianping_reviews.json'):
        """Save reviews to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_reviews, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved {len(self.all_reviews)} reviews to {filename}")

    def save_to_csv(self, filename: str = 'dianping_reviews.csv'):
        """Save reviews to CSV file"""
        if not self.all_reviews:
            print("⚠️  No reviews to save")
            return

        with open(filename, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['restaurant', 'reviewer', 'rating', 'review_text', 'date', 'photos', 'scraped_at']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for review in self.all_reviews:
                # Convert photos list to string
                review_copy = review.copy()
                review_copy['photos'] = '; '.join(review_copy.get('photos', []))
                writer.writerow(review_copy)

        print(f"💾 Saved {len(self.all_reviews)} reviews to {filename}")

    def print_summary(self):
        """Print scraping summary"""
        print(f"\n{'='*60}")
        print(f"📊 SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Total reviews scraped: {len(self.all_reviews)}")

        # Group by restaurant
        by_restaurant = {}
        for review in self.all_reviews:
            restaurant = review['restaurant']
            by_restaurant[restaurant] = by_restaurant.get(restaurant, 0) + 1

        for restaurant, count in by_restaurant.items():
            print(f"  • {restaurant}: {count} reviews")

        # Rating distribution
        ratings = [r['rating'] for r in self.all_reviews if r['rating']]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            print(f"\nAverage rating: {avg_rating:.1f} ⭐")


def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     DIANPING RESTAURANT REVIEW SCRAPER                   ║
    ║     Dubrovnik Restaurants                                ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Configuration
    USE_PROXY = False  # Set to True to use proxy
    PROXY_URL = None   # e.g., "http://proxy-server:port"

    # Create scraper
    scraper = DianpingScraper(use_proxy=USE_PROXY, proxy_url=PROXY_URL)

    # Scrape all restaurants
    print("\n🚀 Starting scraping process...\n")
    reviews = scraper.scrape_all_restaurants()

    # Save results
    if reviews:
        scraper.save_to_json('dianping_reviews.json')
        scraper.save_to_csv('dianping_reviews.csv')
        scraper.print_summary()
    else:
        print("\n❌ No reviews were scraped. Possible reasons:")
        print("  1. Login required (need authentication)")
        print("  2. IP blocked (try using proxy)")
        print("  3. Changed HTML structure (need to update selectors)")
        print("\n💡 Try running with a proxy or VPN")

    print("\n✅ Scraping completed!\n")


if __name__ == "__main__":
    main()
