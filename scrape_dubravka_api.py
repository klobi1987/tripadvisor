#!/usr/bin/env python3
"""
Google Reviews Scraper - API/HTTP Approach
Tries to extract reviews without browser automation
"""

import requests
import json
import csv
import re
from datetime import datetime
from typing import List, Dict
from urllib.parse import quote

# Dubravka 1836 identifiers
PLACE_NAME = "Dubravka 1836 Dubrovnik"
PLACE_ID = None  # Will try to discover

class GoogleReviewsAPIScraper:
    """Scraper using HTTP requests instead of browser"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.reviews = []

    def find_place_id(self, place_name: str) -> str:
        """Try to find Google Place ID"""
        print(f"\n🔍 Searching for Place ID: {place_name}")

        # Try Google Maps search
        url = f"https://www.google.com/maps/search/{quote(place_name)}"

        try:
            response = self.session.get(url, timeout=10)

            # Save for debugging
            with open('debug_search.html', 'w', encoding='utf-8') as f:
                f.write(response.text)

            # Try to extract place ID from HTML
            # Google uses various formats like: /maps/place/.../@lat,lng.../data=...
            patterns = [
                r'!1s(0x[0-9a-f]+:0x[0-9a-f]+)',  # Hex format
                r'/maps/place/[^/]+/data=([^"\']+)',  # Data parameter
                r'ludocid=(\d+)',  # Ludocid (location unique document ID)
            ]

            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    place_id = match.group(1)
                    print(f"✅ Found potential Place ID: {place_id}")
                    return place_id

            print("⚠️  Could not extract Place ID from search")
            return None

        except Exception as e:
            print(f"❌ Error searching: {e}")
            return None

    def get_reviews_via_embed(self, place_name: str) -> List[Dict]:
        """Try to get reviews via Google Maps embed API"""
        print("\n📡 Trying embed API approach...")

        # Google Maps embed URL
        embed_url = f"https://www.google.com/maps/embed/v1/place?key=AIzaSyD&q={quote(place_name)}"

        try:
            response = self.session.get(embed_url, timeout=10)
            print(f"Status: {response.status_code}")

            # This probably won't work, but worth a try
            if 'reviews' in response.text.lower():
                print("✅ Found reviews in response!")
            else:
                print("⚠️  No reviews in embed response")

        except Exception as e:
            print(f"❌ Embed API failed: {e}")

        return []

    def scrape_via_simple_request(self, place_name: str) -> List[Dict]:
        """Try simple HTTP request to Local Search"""
        print("\n🌐 Trying simple HTTP request...")

        url = f"https://www.google.com/search?q={quote(place_name)}&tbm=lcl"

        try:
            response = self.session.get(url, timeout=15)
            print(f"✅ Got response: {response.status_code}")

            # Save for analysis
            with open('debug_local_search.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Saved to debug_local_search.html")

            # Try to parse reviews from HTML
            # Look for JSON-LD structured data
            json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
            matches = re.findall(json_ld_pattern, response.text, re.DOTALL)

            reviews_found = []
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict) and 'review' in data:
                        print(f"✅ Found {len(data['review'])} reviews in JSON-LD")
                        reviews_found = data['review']
                        break
                except:
                    continue

            if reviews_found:
                return self._parse_json_ld_reviews(reviews_found)
            else:
                print("⚠️  No JSON-LD reviews found, trying HTML parsing...")
                return self._parse_html_reviews(response.text)

        except Exception as e:
            print(f"❌ Request failed: {e}")
            return []

    def _parse_json_ld_reviews(self, reviews_data: List[Dict]) -> List[Dict]:
        """Parse reviews from JSON-LD format"""
        parsed = []

        for review in reviews_data:
            try:
                parsed_review = {
                    'restaurant': 'Dubravka 1836',
                    'reviewer_name': review.get('author', {}).get('name'),
                    'rating': review.get('reviewRating', {}).get('ratingValue'),
                    'review_text': review.get('reviewBody') or review.get('description'),
                    'review_date': review.get('datePublished'),
                    'scraped_at': datetime.now().isoformat(),
                    'source': 'Google (JSON-LD)'
                }

                if parsed_review['review_text'] or parsed_review['rating']:
                    parsed.append(parsed_review)

            except Exception as e:
                continue

        print(f"✅ Parsed {len(parsed)} reviews from JSON-LD")
        return parsed

    def _parse_html_reviews(self, html: str) -> List[Dict]:
        """Try to parse reviews from HTML (fallback)"""
        print("📝 Attempting HTML parsing...")

        # This is very basic - Google's HTML is heavily JavaScript-dependent
        # This will likely not work well, but worth trying

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        reviews = []

        # Look for review-like text patterns
        # Google might have review snippets even without JS
        review_candidates = soup.find_all(['div', 'span'], class_=re.compile(r'review|comment', re.I))

        for candidate in review_candidates[:50]:  # Check first 50
            text = candidate.get_text(strip=True)
            if len(text) > 50:  # Probably a review if > 50 chars
                reviews.append({
                    'restaurant': 'Dubravka 1836',
                    'reviewer_name': 'Unknown',
                    'rating': None,
                    'review_text': text,
                    'review_date': None,
                    'scraped_at': datetime.now().isoformat(),
                    'source': 'Google (HTML)'
                })

        print(f"⚠️  HTML parsing found {len(reviews)} potential reviews (low confidence)")
        return reviews

    def save_to_csv(self, filename: str = 'DubravkaGoogle.csv'):
        """Save reviews to CSV"""
        if not self.reviews:
            print("\n⚠️  No reviews to save")
            return False

        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['restaurant', 'reviewer_name', 'rating', 'review_text',
                            'review_date', 'scraped_at', 'source']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for review in self.reviews:
                    writer.writerow({k: v for k, v in review.items() if k in fieldnames})

            print(f"\n💾 ✅ Saved {len(self.reviews)} reviews to {filename}")
            return True

        except Exception as e:
            print(f"❌ Error saving: {e}")
            return False

    def run(self):
        """Main execution"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║   DUBRAVKA 1836 - HTTP/API SCRAPER (No Browser)                 ║
╚══════════════════════════════════════════════════════════════════╝
        """)

        # Try different approaches
        print("🔬 Trying multiple scraping approaches...\n")

        # Approach 1: Simple HTTP request
        reviews = self.scrape_via_simple_request(PLACE_NAME)
        if reviews:
            self.reviews.extend(reviews)

        # Approach 2: Try to find Place ID
        place_id = self.find_place_id(PLACE_NAME)

        # Approach 3: Embed API (probably won't work)
        embed_reviews = self.get_reviews_via_embed(PLACE_NAME)
        if embed_reviews:
            self.reviews.extend(embed_reviews)

        # Results
        if self.reviews:
            print(f"\n📊 Total reviews collected: {len(self.reviews)}")
            self.save_to_csv()

            print("\n" + "="*70)
            print("✅ SCRAPING COMPLETED!")
            print("="*70)
            print(f"📁 Check: DubravkaGoogle.csv")
            print(f"🐛 Debug files: debug_*.html")
        else:
            print("\n" + "="*70)
            print("⚠️  NO REVIEWS EXTRACTED")
            print("="*70)
            print("This approach requires JavaScript rendering.")
            print("Google Maps loads reviews dynamically via JavaScript.")
            print("\n💡 Recommended: Use Selenium scraper locally")
            print("   python3 scrape_dubravka_google.py")


def main():
    scraper = GoogleReviewsAPIScraper()
    scraper.run()


if __name__ == "__main__":
    main()
