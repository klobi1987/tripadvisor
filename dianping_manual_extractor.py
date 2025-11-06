#!/usr/bin/env python3
"""
Dianping Manual HTML Extractor
For use when you can access the page manually but need help extracting reviews
"""

import json
import csv
import re
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from typing import List, Dict

def extract_reviews_from_html(html_file: str, restaurant_name: str) -> List[Dict]:
    """
    Extract reviews from a saved HTML file

    Usage:
    1. Open restaurant page in browser (logged in)
    2. Right-click -> Save As -> Complete webpage
    3. Run this script on the saved HTML file
    """

    print(f"\n{'='*60}")
    print(f"📖 Analyzing HTML file: {html_file}")
    print(f"{'='*60}\n")

    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    reviews = []

    # Try multiple patterns for finding reviews
    patterns = [
        {'selector': 'div.review-item', 'name': 'Review items (div)'},
        {'selector': 'div.comment-item', 'name': 'Comment items'},
        {'selector': 'li.review-item', 'name': 'Review items (li)'},
        {'selector': 'div[class*="ReviewItem"]', 'name': 'ReviewItem class'},
        {'selector': 'div.J-review-item', 'name': 'J-review-item'},
        {'selector': 'div.review-list li', 'name': 'Review list items'},
    ]

    print("🔍 Trying different selectors...\n")

    review_elements = []
    matched_pattern = None

    for pattern in patterns:
        elements = soup.select(pattern['selector'])
        if elements:
            print(f"✅ Found {len(elements)} elements with: {pattern['name']}")
            review_elements = elements
            matched_pattern = pattern
            break
        else:
            print(f"❌ No elements found with: {pattern['name']}")

    if not review_elements:
        print("\n⚠️  No review elements found with standard selectors")
        print("💡 Trying alternative extraction methods...")

        # Try to find any review-like content
        all_text = soup.get_text()

        # Look for Chinese review patterns
        chinese_patterns = [
            r'评价内容：(.+?)(?=评价时间|$)',
            r'口味\d+.*?环境\d+.*?服务\d+',
        ]

        for pattern in chinese_patterns:
            matches = re.findall(pattern, all_text, re.DOTALL)
            if matches:
                print(f"✅ Found {len(matches)} text patterns")
                for idx, match in enumerate(matches[:50], 1):
                    reviews.append({
                        'restaurant': restaurant_name,
                        'reviewer': 'Unknown',
                        'rating': None,
                        'review_text': match.strip(),
                        'date': None,
                        'scraped_at': datetime.now().isoformat(),
                        'extraction_method': 'regex'
                    })

    # Extract structured reviews
    print(f"\n📊 Extracting structured data from {len(review_elements)} elements...\n")

    for idx, elem in enumerate(review_elements, 1):
        try:
            review = extract_review_from_element(elem, restaurant_name)
            if review:
                reviews.append(review)
                print(f"  ✓ Review {idx:3d}: {review['reviewer'][:20]:20s} | Rating: {review['rating']} | Text: {len(review['review_text']):4d} chars")
        except Exception as e:
            print(f"  ✗ Review {idx:3d}: Error - {str(e)[:50]}")

    print(f"\n{'='*60}")
    print(f"✅ Extraction complete: {len(reviews)} reviews found")
    print(f"{'='*60}\n")

    return reviews


def extract_review_from_element(elem, restaurant_name: str) -> Dict:
    """Extract review data from HTML element"""
    review = {
        'restaurant': restaurant_name,
        'reviewer': 'Unknown',
        'rating': None,
        'review_text': '',
        'date': None,
        'helpful_count': None,
        'photos': [],
        'scraped_at': datetime.now().isoformat(),
        'extraction_method': 'structured'
    }

    # Reviewer name - try multiple selectors
    for selector in ['.username', '.user-name', '.name', '[class*="name"]', '.J-name']:
        name_elem = elem.select_one(selector)
        if name_elem:
            review['reviewer'] = name_elem.text.strip()
            break

    # Rating - look for star classes
    for selector in ['.star', '.rating', '[class*="star"]', '[class*="sml-rank-stars"]']:
        rating_elem = elem.select_one(selector)
        if rating_elem:
            # Try to extract rating from class name
            class_str = ' '.join(rating_elem.get('class', []))
            rating_match = re.search(r'(?:star|sml-rank-stars)(\d+)', class_str)
            if rating_match:
                rating_value = int(rating_match.group(1))
                # Convert from 50-point scale to 5-star if needed
                if rating_value > 10:
                    review['rating'] = round(rating_value / 10, 1)
                else:
                    review['rating'] = rating_value
                break

            # Try to find rating in text
            rating_text = rating_elem.text.strip()
            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
            if rating_match:
                review['rating'] = float(rating_match.group(1))
                break

    # Review text - try multiple selectors
    for selector in ['.review-words', '.comment-txt', '.review-content', '.J-review-txt', '[class*="review"]']:
        text_elem = elem.select_one(selector)
        if text_elem:
            review['review_text'] = text_elem.text.strip()
            break

    # If no text found, get all text from element
    if not review['review_text']:
        review['review_text'] = elem.get_text(strip=True, separator=' ')

    # Date
    for selector in ['.time', '.date', '.review-time', '[class*="time"]', '.J-time']:
        date_elem = elem.select_one(selector)
        if date_elem:
            review['date'] = date_elem.text.strip()
            break

    # Helpful count
    for selector in ['.useful-count', '[class*="useful"]', '[class*="helpful"]']:
        helpful_elem = elem.select_one(selector)
        if helpful_elem:
            helpful_match = re.search(r'(\d+)', helpful_elem.text)
            if helpful_match:
                review['helpful_count'] = int(helpful_match.group(1))
                break

    # Photos
    img_elements = elem.select('img')
    for img in img_elements:
        src = img.get('src') or img.get('data-src') or img.get('data-lazyload')
        if src and 'avatar' not in src.lower():  # Skip avatar images
            review['photos'].append(src)

    # Clean up review text (remove extra whitespace)
    review['review_text'] = re.sub(r'\s+', ' ', review['review_text']).strip()

    return review


def analyze_html_structure(html_file: str):
    """Analyze HTML structure to help find review elements"""
    print(f"\n{'='*60}")
    print(f"🔬 HTML STRUCTURE ANALYSIS")
    print(f"{'='*60}\n")

    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Find all classes that contain review-related keywords
    review_keywords = ['review', 'comment', 'rating', 'star']

    print("📋 Classes containing review keywords:\n")

    all_classes = set()
    for elem in soup.find_all(class_=True):
        for cls in elem.get('class', []):
            if any(keyword in cls.lower() for keyword in review_keywords):
                all_classes.add(cls)

    for cls in sorted(all_classes)[:30]:  # Show first 30
        count = len(soup.find_all(class_=cls))
        print(f"  • .{cls}: {count} elements")

    # Find IDs
    print("\n📋 IDs containing review keywords:\n")

    all_ids = set()
    for elem in soup.find_all(id=True):
        elem_id = elem.get('id', '')
        if any(keyword in elem_id.lower() for keyword in review_keywords):
            all_ids.add(elem_id)

    for elem_id in sorted(all_ids)[:20]:
        print(f"  • #{elem_id}")

    # Look for JSON data
    print("\n📋 Checking for embedded JSON data...\n")

    scripts = soup.find_all('script')
    for idx, script in enumerate(scripts):
        if script.string:
            if 'review' in script.string.lower() or 'comment' in script.string.lower():
                print(f"  ✓ Script {idx} might contain review data ({len(script.string)} chars)")
                # Try to extract JSON
                try:
                    # Look for JSON objects
                    json_match = re.search(r'\{[\s\S]*"review"[\s\S]*\}', script.string)
                    if json_match:
                        print(f"    → Found JSON-like structure with 'review' key")
                except:
                    pass

    print(f"\n{'='*60}\n")


def process_multiple_files(html_files: List[str], output_prefix: str = 'dianping'):
    """Process multiple HTML files and combine results"""
    all_reviews = []

    restaurant_mapping = {
        'arsenal': 'Gradska kavana Arsenal Restaurant',
        'panorama': 'Restaurant Panorama',
        'dubravka': 'Dubravka 1836 Restaurant & Cafe',
        'nautika': 'Restaurant Nautika',
    }

    for html_file in html_files:
        # Try to identify restaurant from filename
        filename_lower = Path(html_file).stem.lower()
        restaurant_name = None

        for key, name in restaurant_mapping.items():
            if key in filename_lower:
                restaurant_name = name
                break

        if not restaurant_name:
            restaurant_name = Path(html_file).stem

        print(f"\n{'#'*60}")
        print(f"Processing: {html_file}")
        print(f"Restaurant: {restaurant_name}")
        print(f"{'#'*60}")

        reviews = extract_reviews_from_html(html_file, restaurant_name)
        all_reviews.extend(reviews)

    # Save combined results
    if all_reviews:
        # JSON
        json_file = f'{output_prefix}_all_reviews.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_reviews, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved {len(all_reviews)} reviews to {json_file}")

        # CSV
        csv_file = f'{output_prefix}_all_reviews.csv'
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            if all_reviews:
                fieldnames = ['restaurant', 'reviewer', 'rating', 'review_text', 'date', 'helpful_count', 'scraped_at']
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(all_reviews)
        print(f"💾 Saved to {csv_file}")

        # Summary
        print(f"\n{'='*60}")
        print(f"📊 FINAL SUMMARY")
        print(f"{'='*60}")
        print(f"Total reviews extracted: {len(all_reviews)}\n")

        by_restaurant = {}
        for review in all_reviews:
            name = review['restaurant']
            by_restaurant[name] = by_restaurant.get(name, 0) + 1

        for name, count in sorted(by_restaurant.items()):
            print(f"  • {name}: {count} reviews")

        # Rating statistics
        ratings = [r['rating'] for r in all_reviews if r['rating']]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            print(f"\nAverage rating: {avg_rating:.2f} ⭐")

    return all_reviews


def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   DIANPING MANUAL HTML EXTRACTOR                         ║
    ║   Extract reviews from saved HTML files                  ║
    ╚══════════════════════════════════════════════════════════╝

    INSTRUCTIONS:

    1. Log in to Dianping.com in your browser
    2. Navigate to each restaurant page
    3. Scroll down to load all reviews
    4. Right-click → Save As → Complete webpage
    5. Save each restaurant page with a descriptive name:
       - arsenal.html
       - panorama.html
       - dubravka.html
       - nautika.html
    6. Run this script

    """)

    # Find HTML files in current directory
    html_files = list(Path('.').glob('*.html'))

    if not html_files:
        print("❌ No HTML files found in current directory")
        print("\n💡 Usage examples:")
        print("   python dianping_manual_extractor.py")
        print("   (Automatically finds .html files)")
        print("\n   Or specify files manually in the code")
        return

    print(f"✅ Found {len(html_files)} HTML files:\n")
    for f in html_files:
        print(f"  • {f.name}")

    # Ask for confirmation
    print("\n" + "="*60)
    response = input("Process these files? (y/n): ")

    if response.lower() != 'y':
        print("❌ Cancelled")
        return

    # Option to analyze structure first
    print("\n" + "="*60)
    analyze = input("Analyze HTML structure first? (y/n): ")

    if analyze.lower() == 'y':
        for html_file in html_files:
            analyze_html_structure(str(html_file))

    # Process files
    print("\n" + "="*60)
    print("🚀 Starting extraction...")
    print("="*60)

    process_multiple_files([str(f) for f in html_files])

    print("\n✅ Extraction completed!")
    print("\n💡 Tip: Check the generated CSV file for easy viewing in Excel")


if __name__ == "__main__":
    main()
