#!/usr/bin/env python3
"""
Advanced Google Reviews Scraper - Multiple HTTP-based approaches
Extracts reviews WITHOUT browser automation
"""

import requests
import json
import csv
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import quote, urlencode
import base64

class AdvancedGoogleScraper:
    """Advanced HTTP-based scraper with multiple fallback methods"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'Origin': 'https://www.google.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
        self.reviews = []

    def method_1_google_maps_embed(self, place_name: str) -> List[Dict]:
        """Try Google Maps Embed API"""
        print("\n[METHOD 1] Google Maps Embed API")
        print("="*60)

        # Try to search for the place first
        search_url = f"https://www.google.com/maps/search/{quote(place_name)}"

        try:
            response = self.session.get(search_url, timeout=10)

            # Look for data in JavaScript
            # Google embeds data in window.APP_INITIALIZATION_STATE or similar
            patterns = [
                r'window\.APP_INITIALIZATION_STATE=(\[\[.*?\]\]);',
                r'window\.APP_OPTIONS=({.*?});',
                r'\\"ludocid\\":\\"(\d+)\\"',
                r'data:application/json;charset=utf-8;base64,([A-Za-z0-9+/=]+)',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    print(f"✅ Found data with pattern: {pattern[:50]}...")
                    print(f"   Matches: {len(matches)}")

                    # Try to parse
                    for match in matches[:5]:
                        try:
                            if 'base64' in pattern:
                                # Decode base64
                                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                                print(f"   Decoded base64 data (first 200 chars): {decoded[:200]}")
                            else:
                                print(f"   Data (first 200 chars): {str(match)[:200]}")
                        except:
                            pass

            # Save for analysis
            with open('debug_embed.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Saved debug_embed.html")

        except Exception as e:
            print(f"❌ Embed API failed: {e}")

        return []

    def method_2_google_local_results_api(self, place_name: str) -> List[Dict]:
        """Try Google Local Results API (undocumented)"""
        print("\n[METHOD 2] Google Local Results API")
        print("="*60)

        # Try the local search API endpoint
        base_url = "https://www.google.com/async/reviewDialog"

        # Build query parameters
        params = {
            'async': 'feature_id:,review_source:All%20reviews,sort_by:qualityScore,is_owner:false,filter_text:,associated_topic:,next_page_token:,_fmt:pc',
            'hl': 'en',
        }

        try:
            response = self.session.get(base_url, params=params, timeout=10)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                # Save response
                with open('debug_api_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("💾 Saved debug_api_response.html")

                # Try to parse
                if 'review' in response.text.lower():
                    print("✅ Found 'review' in response!")
                    # TODO: Parse the actual reviews
                else:
                    print("⚠️  No reviews in response")
            else:
                print(f"⚠️  Status code: {response.status_code}")

        except Exception as e:
            print(f"❌ API request failed: {e}")

        return []

    def method_3_google_search_with_reviews(self, place_name: str) -> List[Dict]:
        """Try Google search and parse embedded review data"""
        print("\n[METHOD 3] Google Search + Embedded Data")
        print("="*60)

        # Search with specific parameters to get knowledge panel
        search_url = "https://www.google.com/search"
        params = {
            'q': place_name,
            'tbm': 'lcl',  # Local search
            'hl': 'en',
        }

        try:
            response = self.session.get(search_url, params=params, timeout=15)
            print(f"✅ Status: {response.status_code}")

            # Look for AF_initDataCallback which contains structured data
            pattern = r'AF_initDataCallback\((.*?)\);'
            matches = re.findall(pattern, response.text, re.DOTALL)

            print(f"Found {len(matches)} AF_initDataCallback entries")

            reviews_found = []

            for idx, match in enumerate(matches):
                try:
                    # Try to extract JSON from the callback
                    # Format is usually: {key: "...", data: [...]}
                    json_match = re.search(r'data:(.*?)(?:,\s*sideChannel|\}$)', match, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)

                        # Try to find review-like structures
                        if 'review' in json_str.lower() or 'rating' in json_str.lower():
                            print(f"✅ Found potential review data in callback {idx}")
                            print(f"   Preview: {json_str[:300]}...")

                            # Try to parse as JSON
                            try:
                                data = json.loads(json_str)
                                # Recursively search for review structures
                                reviews = self._extract_reviews_from_structure(data)
                                if reviews:
                                    reviews_found.extend(reviews)
                            except json.JSONDecodeError:
                                # Try to fix common JSON issues
                                # Google sometimes uses non-standard JSON
                                pass

                except Exception as e:
                    continue

            if reviews_found:
                print(f"✅ Extracted {len(reviews_found)} reviews!")
                return reviews_found
            else:
                print("⚠️  No reviews extracted from callbacks")

            # Save for debugging
            with open('debug_search_full.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Saved debug_search_full.html")

        except Exception as e:
            print(f"❌ Search failed: {e}")

        return []

    def method_4_google_mybusiness_api(self, place_name: str) -> List[Dict]:
        """Try to find Google My Business public API endpoint"""
        print("\n[METHOD 4] Google My Business Public API")
        print("="*60)

        # First, try to get the Place ID
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"

        # Try without API key (sometimes works for basic info)
        params = {
            'address': place_name,
            'sensor': 'false'
        }

        try:
            response = self.session.get(geocode_url, params=params, timeout=10)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)[:500]}")

                if data.get('status') == 'OK':
                    place_id = data['results'][0].get('place_id')
                    print(f"✅ Found Place ID: {place_id}")

                    # Try to get reviews with Place ID
                    # (This usually requires API key, but worth trying)
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    details_params = {
                        'placeid': place_id,
                        'fields': 'name,rating,reviews',
                    }

                    details_response = self.session.get(details_url, params=details_params, timeout=10)
                    print(f"Details Status: {details_response.status_code}")
                    print(f"Details Response: {details_response.text[:500]}")
                else:
                    print(f"⚠️  Geocode status: {data.get('status')}")
            else:
                print(f"⚠️  Status code: {response.status_code}")

        except Exception as e:
            print(f"❌ API call failed: {e}")

        return []

    def method_5_scrape_mobile_version(self, place_name: str) -> List[Dict]:
        """Try mobile version which might have simpler HTML"""
        print("\n[METHOD 5] Google Mobile Version")
        print("="*60)

        # Mobile user agent
        mobile_headers = self.session.headers.copy()
        mobile_headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'

        search_url = f"https://www.google.com/search?q={quote(place_name)}"

        try:
            response = requests.get(search_url, headers=mobile_headers, timeout=10)
            print(f"✅ Status: {response.status_code}")

            # Save mobile version
            with open('debug_mobile.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Saved debug_mobile.html")

            # Mobile version might have simpler structure
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for review elements
            review_elements = soup.find_all(['div', 'article'], class_=re.compile(r'review', re.I))
            print(f"Found {len(review_elements)} potential review elements")

            if review_elements:
                for elem in review_elements[:5]:
                    print(f"   Preview: {elem.get_text()[:100]}...")

        except Exception as e:
            print(f"❌ Mobile scraping failed: {e}")

        return []

    def _extract_reviews_from_structure(self, data, depth=0, max_depth=10) -> List[Dict]:
        """Recursively search for review structures in nested data"""
        if depth > max_depth:
            return []

        reviews = []

        try:
            if isinstance(data, dict):
                # Look for review-like keys
                review_keys = ['review', 'reviews', 'userReview', 'customerReview']
                for key in review_keys:
                    if key in data and isinstance(data[key], (list, dict)):
                        # Found potential reviews
                        review_data = data[key]
                        if isinstance(review_data, list):
                            for item in review_data:
                                review = self._parse_review_item(item)
                                if review:
                                    reviews.append(review)
                        elif isinstance(review_data, dict):
                            review = self._parse_review_item(review_data)
                            if review:
                                reviews.append(review)

                # Recurse into nested structures
                for value in data.values():
                    if isinstance(value, (dict, list)):
                        reviews.extend(self._extract_reviews_from_structure(value, depth+1, max_depth))

            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, (dict, list)):
                        reviews.extend(self._extract_reviews_from_structure(item, depth+1, max_depth))

        except Exception as e:
            pass

        return reviews

    def _parse_review_item(self, item: Dict) -> Optional[Dict]:
        """Parse a single review item"""
        try:
            review = {
                'restaurant': 'Dubravka 1836',
                'reviewer_name': None,
                'rating': None,
                'review_text': None,
                'review_date': None,
                'scraped_at': datetime.now().isoformat(),
                'source': 'Google (HTTP)',
            }

            # Common keys for review data
            name_keys = ['author', 'reviewer', 'name', 'authorName', 'reviewerName']
            rating_keys = ['rating', 'ratingValue', 'starRating']
            text_keys = ['text', 'reviewBody', 'description', 'comment']
            date_keys = ['date', 'publishedDate', 'datePublished', 'time']

            # Extract fields
            for key in name_keys:
                if key in item:
                    review['reviewer_name'] = str(item[key])
                    break

            for key in rating_keys:
                if key in item:
                    try:
                        review['rating'] = int(float(item[key]))
                    except:
                        pass
                    break

            for key in text_keys:
                if key in item:
                    review['review_text'] = str(item[key])
                    break

            for key in date_keys:
                if key in item:
                    review['review_date'] = str(item[key])
                    break

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
                fieldnames = ['restaurant', 'reviewer_name', 'rating', 'review_text',
                            'review_date', 'scraped_at', 'source']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for review in self.reviews:
                    writer.writerow({k: v for k, v in review.items() if k in fieldnames})

            print(f"\n✅ Saved {len(self.reviews)} reviews to {filename}")
            return True

        except Exception as e:
            print(f"❌ Error saving: {e}")
            return False

    def run(self, place_name: str = "Dubravka 1836 Dubrovnik"):
        """Try all methods"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║   ADVANCED GOOGLE SCRAPER - HTTP ONLY (No Browser)              ║
║   Trying 5 different HTTP-based methods                         ║
╚══════════════════════════════════════════════════════════════════╝
        """)

        print(f"🎯 Target: {place_name}\n")

        # Try all methods
        methods = [
            self.method_1_google_maps_embed,
            self.method_2_google_local_results_api,
            self.method_3_google_search_with_reviews,
            self.method_4_google_mybusiness_api,
            self.method_5_scrape_mobile_version,
        ]

        for method in methods:
            try:
                reviews = method(place_name)
                if reviews:
                    self.reviews.extend(reviews)
                    print(f"✅ This method found {len(reviews)} reviews!")

                # Wait between methods to be respectful
                time.sleep(2)

            except Exception as e:
                print(f"❌ Method failed: {e}")
                continue

        # Summary
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"Total reviews collected: {len(self.reviews)}")

        if self.reviews:
            self.save_to_csv('DubravkaGoogle.csv')

            # Show sample
            print("\n📝 Sample review:")
            sample = self.reviews[0]
            for key, value in sample.items():
                print(f"   {key}: {str(value)[:80]}")
        else:
            print("\n⚠️  NO REVIEWS EXTRACTED")
            print("\nReason: Google Maps requires JavaScript rendering")
            print("All HTTP-based methods failed because:")
            print("  • Google loads reviews dynamically via JavaScript")
            print("  • Reviews are not in initial HTML response")
            print("  • API endpoints require authentication")
            print("\n💡 Alternatives:")
            print("  1. Use Outscraper API (outscraper.com) - paid service")
            print("  2. Use SerpAPI (serpapi.com) - paid service")
            print("  3. Use local Selenium scraper (requires GUI/X11)")
            print("  4. Use cloud browser service (e.g., BrowserStack)")
            print("\n🔍 Debug files created for analysis:")
            print("  • debug_embed.html")
            print("  • debug_api_response.html")
            print("  • debug_search_full.html")
            print("  • debug_mobile.html")


def main():
    scraper = AdvancedGoogleScraper()
    scraper.run("Dubravka 1836 Dubrovnik")


if __name__ == "__main__":
    main()
