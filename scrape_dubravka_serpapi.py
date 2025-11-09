#!/usr/bin/env python3
"""
Dubravka 1836 Google Reviews Scraper - SerpAPI Version
Uses SerpAPI to extract Google Maps reviews (no browser needed!)
"""

import requests
import json
import csv
import time
from datetime import datetime
from typing import List, Dict

# SerpAPI Configuration
SERPAPI_KEY = "807d4942dab293ce7b85522d48ad160c6cfe92b7"
RESTAURANT_NAME = "Dubravka 1836 Dubrovnik"

class SerpAPIScraper:
    """Google Maps reviews scraper using SerpAPI"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        self.reviews = []

    def search_place(self, query: str) -> Dict:
        """Search for place and get data_id"""
        print(f"\n🔍 Searching for: {query}")

        params = {
            "engine": "google_maps",
            "q": query,
            "type": "search",
            "api_key": self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Save debug info
            with open('serpapi_search.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("💾 Saved search results to serpapi_search.json")

            # Extract place data_id
            if 'local_results' in data and len(data['local_results']) > 0:
                place = data['local_results'][0]
                data_id = place.get('data_id')
                title = place.get('title')
                rating = place.get('rating')
                reviews_count = place.get('reviews')

                print(f"✅ Found: {title}")
                print(f"   Rating: {rating} ⭐")
                print(f"   Reviews: {reviews_count}")
                print(f"   Data ID: {data_id}")

                return {
                    'data_id': data_id,
                    'title': title,
                    'rating': rating,
                    'reviews_count': reviews_count
                }
            else:
                print("❌ No results found")
                return None

        except Exception as e:
            print(f"❌ Search error: {e}")
            return None

    def get_all_reviews(self, data_id: str, place_name: str) -> List[Dict]:
        """Get all reviews for a place using data_id"""
        print(f"\n📊 Fetching reviews for {place_name}...")
        print(f"   Data ID: {data_id}")

        all_reviews = []
        next_page_token = None
        page = 1

        while True:
            print(f"\n📄 Fetching page {page}...")

            params = {
                "engine": "google_maps_reviews",
                "data_id": data_id,
                "api_key": self.api_key,
                "hl": "hr"  # Croatian language
            }

            if next_page_token:
                params['next_page_token'] = next_page_token

            try:
                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                # Save page data
                with open(f'serpapi_reviews_page_{page}.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                # Extract reviews from this page
                if 'reviews' in data:
                    page_reviews = data['reviews']
                    print(f"✅ Got {len(page_reviews)} reviews from page {page}")

                    for review in page_reviews:
                        parsed_review = self._parse_review(review, place_name)
                        if parsed_review:
                            all_reviews.append(parsed_review)

                    print(f"   Total so far: {len(all_reviews)} reviews")
                else:
                    print("⚠️  No reviews in response")
                    break

                # Check for next page
                serpapi_pagination = data.get('serpapi_pagination', {})
                next_page_token = serpapi_pagination.get('next_page_token')

                if next_page_token:
                    print(f"   ➡️  More pages available, continuing...")
                    page += 1
                    time.sleep(1)  # Be nice to API
                else:
                    print(f"✅ Reached last page")
                    break

            except Exception as e:
                print(f"❌ Error fetching page {page}: {e}")
                break

        return all_reviews

    def _parse_review(self, review: Dict, restaurant_name: str) -> Dict:
        """Parse single review from SerpAPI format"""
        try:
            # Extract user info
            user = review.get('user', {})

            # Extract likes/helpful count
            likes = review.get('likes', 0)

            # Extract owner response if present
            owner_answer = review.get('owner_answer')
            owner_response = None
            owner_response_date = None
            if owner_answer:
                owner_response = owner_answer.get('text')
                owner_response_date = owner_answer.get('date')

            parsed = {
                'restaurant': restaurant_name,
                'reviewer_name': user.get('name'),
                'reviewer_link': user.get('link'),
                'reviewer_thumbnail': user.get('thumbnail'),
                'reviewer_local_guide': user.get('local_guide', False),
                'reviewer_reviews_count': user.get('reviews'),
                'reviewer_photos_count': user.get('photos'),
                'rating': review.get('rating'),
                'review_text': review.get('snippet'),
                'review_date': review.get('date'),
                'review_likes': likes,
                'owner_response': owner_response,
                'owner_response_date': owner_response_date,
                'images_count': len(review.get('images', [])),
                'scraped_at': datetime.now().isoformat(),
                'source': 'Google Maps (SerpAPI)',
                'review_id': review.get('review_id')
            }

            return parsed

        except Exception as e:
            print(f"⚠️  Error parsing review: {e}")
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
                    'images_count',
                    'scraped_at',
                    'source',
                    'review_id'
                ]

                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()

                for review in self.reviews:
                    writer.writerow(review)

            print(f"\n💾 ✅ Saved {len(self.reviews)} reviews to {filename}")
            return True

        except Exception as e:
            print(f"❌ Error saving CSV: {e}")
            return False

    def save_to_json(self, filename: str = 'DubravkaGoogle.json'):
        """Save reviews to JSON (backup)"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.reviews, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved backup to {filename}")
            return True
        except Exception as e:
            print(f"❌ JSON save error: {e}")
            return False

    def run(self):
        """Main execution"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         DUBRAVKA 1836 - GOOGLE REVIEWS SCRAPER                   ║
║         Powered by SerpAPI (No Browser Required!)                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """)

        # Step 1: Search for the place
        place_data = self.search_place(RESTAURANT_NAME)

        if not place_data or not place_data.get('data_id'):
            print("\n❌ Could not find restaurant. Please check the name.")
            return False

        # Step 2: Get all reviews
        reviews = self.get_all_reviews(place_data['data_id'], place_data['title'])

        if reviews:
            self.reviews = reviews

            # Step 3: Save results
            self.save_to_csv()
            self.save_to_json()

            # Step 4: Statistics
            print("\n" + "="*70)
            print("📊 EXTRACTION SUMMARY")
            print("="*70)
            print(f"Restaurant: {place_data['title']}")
            print(f"Total reviews: {len(reviews)}")

            # Rating breakdown
            ratings = {}
            for r in reviews:
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
            with_text = len([r for r in reviews if r['review_text']])
            print(f"\n📝 Reviews with text: {with_text}")

            # With owner response
            with_response = len([r for r in reviews if r['owner_response']])
            print(f"💬 Reviews with owner response: {with_response}")

            # Local Guides
            local_guides = len([r for r in reviews if r['reviewer_local_guide']])
            print(f"🎖️  Reviews from Local Guides: {local_guides}")

            print("\n" + "="*70)
            print("✅ SCRAPING COMPLETED SUCCESSFULLY!")
            print("="*70)
            print(f"\n📁 Output files:")
            print(f"   • DubravkaGoogle.csv (main file)")
            print(f"   • DubravkaGoogle.json (backup)")
            print(f"   • serpapi_*.json (debug data)")

            return True

        else:
            print("\n❌ No reviews extracted")
            return False


def main():
    if not SERPAPI_KEY:
        print("❌ Error: SERPAPI_KEY not set!")
        print("Please set your SerpAPI key in the script")
        return

    scraper = SerpAPIScraper(SERPAPI_KEY)
    success = scraper.run()

    if success:
        print("\n🎉 All done! Check DubravkaGoogle.csv")
    else:
        print("\n⚠️  Scraping incomplete.")


if __name__ == "__main__":
    main()
