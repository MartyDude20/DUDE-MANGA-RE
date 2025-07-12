#!/usr/bin/env python3
"""
Test script to debug Asura Scans search functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from sources.asurascans import search, get_details
import time

def test_asurascans_search():
    """Test Asura Scans search functionality"""
    
    print("🔍 Testing Asura Scans Search Functionality\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to False to see what's happening
        page = browser.new_page()
        
        try:
            # Test 1: Basic search
            print("1️⃣ Testing basic search for 'naruto'...")
            results = search(page, 'naruto')
            print(f"✅ Found {len(results)} results for 'naruto'")
            
            if results:
                print("First result:")
                print(f"  Title: {results[0].get('title')}")
                print(f"  URL: {results[0].get('details_url')}")
                print(f"  Image: {results[0].get('image')}")
            
            # Test 2: Search for popular term
            print("\n2️⃣ Testing search for 'one piece'...")
            results2 = search(page, 'one piece')
            print(f"✅ Found {len(results2)} results for 'one piece'")
            
            # Test 3: Test the search URL directly
            print("\n3️⃣ Testing search URL directly...")
            search_url = "https://asuracomic.net/series?page=1&name=naruto"
            print(f"Navigating to: {search_url}")
            
            page.goto(search_url)
            page.wait_for_load_state('networkidle')
            
            # Check what's on the page
            print("Page title:", page.title())
            
            # Look for manga cards
            cards = page.query_selector_all('a[href^="series/"]')
            print(f"Found {len(cards)} manga cards")
            
            if cards:
                print("First card details:")
                first_card = cards[0]
                print(f"  href: {first_card.get_attribute('href')}")
                
                # Check for title
                title_elem = first_card.query_selector('span.text-\\[13\\.3px\\].block')
                if title_elem:
                    print(f"  title: {title_elem.inner_text().strip()}")
                else:
                    print("  title: Not found with selector 'span.text-[13.3px].block'")
                    
                    # Try alternative selectors
                    alt_selectors = [
                        'span.block',
                        'span',
                        'h3',
                        'div'
                    ]
                    
                    for selector in alt_selectors:
                        alt_elem = first_card.query_selector(selector)
                        if alt_elem:
                            text = alt_elem.inner_text().strip()
                            if text and len(text) > 0:
                                print(f"  title (using {selector}): {text}")
                                break
                
                # Check for image
                img_elem = first_card.query_selector('img')
                if img_elem:
                    print(f"  image: {img_elem.get_attribute('src')}")
                else:
                    print("  image: Not found")
            
            # Test 4: Check if search is working by looking at the page content
            print("\n4️⃣ Analyzing page structure...")
            
            # Get all links on the page
            all_links = page.query_selector_all('a')
            series_links = []
            for link in all_links:
                href = link.get_attribute('href')
                if href and href.startswith('series/'):
                    series_links.append(link)
            print(f"Total links: {len(all_links)}")
            print(f"Series links: {len(series_links)}")
            
            # Check page HTML structure
            print("\n5️⃣ Checking page HTML structure...")
            page_content = page.content()
            
            # Look for common patterns
            if 'series' in page_content.lower():
                print("✅ 'series' found in page content")
            else:
                print("❌ 'series' not found in page content")
                
            if 'manga' in page_content.lower():
                print("✅ 'manga' found in page content")
            else:
                print("❌ 'manga' not found in page content")
            
            # Save page HTML for debugging
            with open('asurascans_debug.html', 'w', encoding='utf-8') as f:
                f.write(page_content)
            print("💾 Saved page HTML to asurascans_debug.html")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_asurascans_search() 