#!/usr/bin/env python3
"""
Simple test to check Asura Scans website structure
"""

from playwright.sync_api import sync_playwright
import time

def test_asurascans_site():
    """Test Asura Scans website structure"""
    
    print("🔍 Testing Asura Scans Website Structure\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Test 1: Check the main series page
            print("1️⃣ Testing main series page...")
            main_url = "https://asuracomic.net/series"
            print(f"Navigating to: {main_url}")
            
            page.goto(main_url)
            page.wait_for_load_state('networkidle')
            
            print(f"Page title: {page.title()}")
            print(f"Page URL: {page.url}")
            
            # Check for manga cards
            cards = page.query_selector_all('a[href^="series/"]')
            print(f"Found {len(cards)} manga cards on main page")
            
            if cards:
                print("First card href:", cards[0].get_attribute('href'))
            
            # Test 2: Check search with empty query
            print("\n2️⃣ Testing search with empty query...")
            search_url = "https://asuracomic.net/series?page=1&name="
            print(f"Navigating to: {search_url}")
            
            page.goto(search_url)
            page.wait_for_load_state('networkidle')
            
            print(f"Page title: {page.title()}")
            print(f"Page URL: {page.url}")
            
            # Check for manga cards
            cards2 = page.query_selector_all('a[href^="series/"]')
            print(f"Found {len(cards2)} manga cards on search page")
            
            # Test 3: Check if there's a different search endpoint
            print("\n3️⃣ Testing alternative search endpoints...")
            
            # Try different search patterns
            test_urls = [
                "https://asuracomic.net/search?q=naruto",
                "https://asuracomic.net/series?search=naruto",
                "https://asuracomic.net/series?query=naruto",
                "https://asuracomic.net/series?keyword=naruto"
            ]
            
            for test_url in test_urls:
                try:
                    print(f"Testing: {test_url}")
                    page.goto(test_url)
                    page.wait_for_load_state('networkidle')
                    
                    cards_test = page.query_selector_all('a[href^="series/"]')
                    print(f"  Found {len(cards_test)} cards")
                    
                    if cards_test:
                        print(f"  First card: {cards_test[0].get_attribute('href')}")
                        break
                        
                except Exception as e:
                    print(f"  Error: {e}")
                    continue
            
            # Test 4: Check the page content for clues
            print("\n4️⃣ Analyzing page content...")
            page_content = page.content()
            
            # Look for search-related elements
            if 'search' in page_content.lower():
                print("✅ 'search' found in page content")
            if 'series' in page_content.lower():
                print("✅ 'series' found in page content")
            if 'manga' in page_content.lower():
                print("✅ 'manga' found in page content")
            
            # Save a sample of the HTML for analysis
            with open('asurascans_sample.html', 'w', encoding='utf-8') as f:
                f.write(page_content[:5000])  # First 5000 chars
            print("💾 Saved sample HTML to asurascans_sample.html")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_asurascans_site() 