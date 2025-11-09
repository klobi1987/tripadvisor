#!/usr/bin/env python3
"""
Google Maps URL Finder - Helper script
Pomaže pronaći Google Maps URL-ove za restorane
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

RESTAURANTS = [
    "Restaurant Nautika Dubrovnik",
    "Arsenal Restaurant Dubrovnik",
    "Restaurant Panorama Dubrovnik",
    "Dubravka 1836 Restaurant Dubrovnik"
]


def setup_driver():
    """Setup Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def search_restaurant(driver, restaurant_name):
    """Search for restaurant on Google Maps"""
    print(f"\n🔍 Searching for: {restaurant_name}")

    # Go to Google Maps
    driver.get("https://www.google.com/maps")
    time.sleep(2)

    try:
        # Find search box
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchboxinput"))
        )

        # Enter restaurant name
        search_box.clear()
        search_box.send_keys(restaurant_name)
        search_box.send_keys(Keys.RETURN)

        # Wait for results to load
        time.sleep(5)

        # Get current URL
        url = driver.current_url
        print(f"✅ Found URL: {url}")

        return url

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   GOOGLE MAPS URL FINDER                                 ║
    ║   Automatski pronalazi Google Maps URL-ove              ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    driver = setup_driver()
    urls = {}

    try:
        for restaurant in RESTAURANTS:
            url = search_restaurant(driver, restaurant)
            if url:
                urls[restaurant] = url
            time.sleep(3)

        # Print results
        print("\n" + "="*60)
        print("📋 PRONAĐENI URL-OVI")
        print("="*60)

        print("\nKopiraj sljedeći kod u google_maps_scraper.py:\n")
        print("RESTAURANTS = {")

        restaurant_keys = ["Nautika", "Arsenal", "Panorama", "Dubravka"]
        for i, (restaurant, url) in enumerate(urls.items()):
            key = restaurant_keys[i] if i < len(restaurant_keys) else f"Restaurant_{i+1}"
            print(f'    "{key}": {{')
            print(f'        "name": "{restaurant}",')
            print(f'        "url": "{url}",')
            print(f'        "location": "Dubrovnik"')
            print('    },')

        print("}")

        # Save to file
        with open('google_maps_urls.txt', 'w', encoding='utf-8') as f:
            for restaurant, url in urls.items():
                f.write(f"{restaurant}\n{url}\n\n")

        print("\n💾 Saved to: google_maps_urls.txt")

        input("\n✅ Press ENTER to close browser...")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
