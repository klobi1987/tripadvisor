#!/usr/bin/env python3
"""
Google Reviews Scraper using requests-html (JavaScript rendering)
"""

import csv
import re
from datetime import datetime
from typing import List, Dict

try:
    from requests_html import HTMLSession
    AVAILABLE = True
except ImportError:
    AVAILABLE = False
    print("❌ requests-html not installed")
    print("Install: pip install requests-html")
    exit(1)


def scrape_dubravka_reviews() -> List[Dict]:
    """Scrape Dubravka reviews using requests-html"""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║   DUBRAVKA 1836 - requests-html Scraper (JS Rendering)          ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    reviews = []

    try:
        # Create session
        session = HTMLSession()

        # Target URL
        url = "https://www.google.com/search?q=Dubravka+1836+Dubrovnik&tbm=lcl"

        print(f"🔄 Fetching: {url}")
        print("⏳ Rendering JavaScript... (this may take 30-60 seconds)")

        # Get page
        response = session.get(url, timeout=30)

        # Render JavaScript
        try:
            response.html.render(timeout=60, sleep=5, keep_page=False)
            print("✅ JavaScript rendered successfully!")

            # Save rendered HTML
            with open('debug_rendered.html', 'w', encoding='utf-8') as f:
                f.write(response.html.html)
            print("💾 Saved debug_rendered.html")

            # Find review elements
            review_selectors = [
                'div[data-review-id]',
                'div.jftiEf',
                'div.gws-localreviews__google-review',
            ]

            review_elements = []
            for selector in review_selectors:
                elements = response.html.find(selector)
                if elements:
                    review_elements = elements
                    print(f"✅ Found {len(elements)} reviews with selector: {selector}")
                    break

            if not review_elements:
                print("⚠️  No review elements found")
                print("📝 Searching for any div with review-like content...")

                # Try to find any divs
                all_divs = response.html.find('div')
                print(f"Found {len(all_divs)} total divs")

                # Look for rating/review patterns
                for div in all_divs[:100]:
                    text = div.text
                    if text and ('star' in text.lower() or 'review' in text.lower()):
                        print(f"   Potential review div: {text[:100]}")

            # Extract reviews
            for element in review_elements:
                try:
                    review = {
                        'restaurant': 'Dubravka 1836',
                        'reviewer_name': None,
                        'rating': None,
                        'review_text': None,
                        'review_date': None,
                        'scraped_at': datetime.now().isoformat(),
                        'source': 'Google (requests-html)',
                    }

                    # Extract name
                    name_elem = element.find('div.d4r55', first=True)
                    if name_elem:
                        review['reviewer_name'] = name_elem.text.strip()

                    # Extract rating
                    rating_elem = element.find('span.kvMYJc', first=True)
                    if rating_elem:
                        aria_label = rating_elem.attrs.get('aria-label', '')
                        match = re.search(r'(\d+)\s*star', aria_label, re.I)
                        if match:
                            review['rating'] = int(match.group(1))

                    # Extract text
                    text_elem = element.find('span.wiI7pd', first=True)
                    if text_elem:
                        review['review_text'] = text_elem.text.strip()

                    # Extract date
                    date_elem = element.find('span.rsqaWe', first=True)
                    if date_elem:
                        review['review_date'] = date_elem.text.strip()

                    if review['review_text'] or review['rating']:
                        reviews.append(review)

                except Exception as e:
                    print(f"⚠️  Error extracting review: {e}")
                    continue

            print(f"\n📊 Extracted {len(reviews)} reviews")

        except Exception as e:
            print(f"❌ JavaScript rendering failed: {e}")
            print(f"Error type: {type(e).__name__}")
            print("\nThis likely means:")
            print("  • Chromium is not installed or not accessible")
            print("  • No display server available (X11/Xvfb)")
            print("  • Running in restricted environment")

    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        try:
            session.close()
        except:
            pass

    return reviews


def save_to_csv(reviews: List[Dict], filename: str = 'DubravkaGoogle.csv'):
    """Save reviews to CSV"""
    if not reviews:
        print("\n⚠️  No reviews to save")
        return False

    try:
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['restaurant', 'reviewer_name', 'rating', 'review_text',
                        'review_date', 'scraped_at', 'source']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for review in reviews:
                writer.writerow({k: v for k, v in review.items() if k in fieldnames})

        print(f"\n✅ Saved {len(reviews)} reviews to {filename}")
        return True

    except Exception as e:
        print(f"❌ Error saving: {e}")
        return False


def main():
    if not AVAILABLE:
        return

    reviews = scrape_dubravka_reviews()

    if reviews:
        save_to_csv(reviews, 'DubravkaGoogle.csv')

        print("\n" + "="*70)
        print("✅ SUCCESS!")
        print("="*70)
        print(f"📁 File: DubravkaGoogle.csv")
        print(f"📊 Reviews: {len(reviews)}")

        # Show sample
        if reviews:
            print("\n📝 Sample review:")
            sample = reviews[0]
            print(f"   Name: {sample.get('reviewer_name')}")
            print(f"   Rating: {sample.get('rating')}")
            print(f"   Text: {sample.get('review_text', '')[:100]}...")
    else:
        print("\n" + "="*70)
        print("⚠️  NO REVIEWS EXTRACTED")
        print("="*70)
        print("\n💡 Unfortunately, all HTTP-based methods have failed.")
        print("\n📊 What we tried:")
        print("  ✗ Simple HTTP requests")
        print("  ✗ Google Maps Embed API")
        print("  ✗ Google Local Results API")
        print("  ✗ Google My Business API")
        print("  ✗ Mobile version scraping")
        print("  ✗ requests-html with JavaScript rendering")
        print("\n❓ Why it failed:")
        print("  • Google loads reviews dynamically via JavaScript")
        print("  • API endpoints require API keys")
        print("  • Server environment lacks GUI/X11 for browser rendering")
        print("\n✅ Working alternatives:")
        print("  1. Outscraper API (outscraper.com) - recommended, paid")
        print("  2. SerpAPI (serpapi.com) - paid")
        print("  3. Run Selenium locally with GUI")
        print("  4. Use cloud browser service")


if __name__ == "__main__":
    main()
