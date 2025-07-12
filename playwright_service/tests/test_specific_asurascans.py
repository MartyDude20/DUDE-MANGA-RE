#!/usr/bin/env python3
"""
Test script to debug Asura Scans search with specific manga titles
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from sources.asurascans import search, handle_ads_and_popups
import time

def test_specific_manga():
    """Test Asura Scans search with specific manga titles"""
    
    # The specific manga titles to test
    test_titles = [
        "The Demonic Cult Instructor Returns",
        "The Great Mage Returns After 4000 Years", 
        "Nano Machine",
        "Return of the Apocalypse-Class Death Knight",
        "Eternally Regressing Knight",
        "Revenge of the Iron-Blooded Sword Hound",
        "Swordmaster's Youngest Son",
        "The Greatest Estate Developer",
        "Dragon-Devouring Mage"
    ]
    
    print("🔍 Testing Asura Scans with Specific Manga Titles\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            for title in test_titles:
                print(f"\n📖 Testing: {title}")
                print("=" * 50)
                
                try:
                    # Test the search function
                    results = search(page, title)
                    
                    if results:
                        print(f"✅ Found {len(results)} results")
                        
                        # Show first few results
                        for i, result in enumerate(results[:3]):
                            print(f"  {i+1}. Title: '{result.get('title')}'")
                            print(f"     URL: {result.get('details_url')}")
                            print(f"     Image: {result.get('image', 'No image')[:50]}...")
                            print()
                    else:
                        print("❌ No results found")
                        
                        # Try to debug by checking the page structure
                        print("🔍 Debugging page structure...")
                        search_url = f"https://asuracomic.net/series?page=1&name={title.replace(' ', '+')}"
                        print(f"URL: {search_url}")
                        
                        page.goto(search_url)
                        handle_ads_and_popups(page)
                        
                        # Check for cards with different selectors
                        selectors_to_try = [
                            'a[href^="series/"]',
                            'a[href*="/series/"]',
                            'a[href*="series"]',
                            '[href*="/series/"]'
                        ]
                        
                        for selector in selectors_to_try:
                            cards = page.query_selector_all(selector)
                            if cards:
                                print(f"  Found {len(cards)} cards with '{selector}'")
                                
                                # Check the first card structure
                                if cards:
                                    first_card = cards[0]
                                    href = first_card.get_attribute('href')
                                    print(f"  First card href: {href}")
                                    
                                    # Try different title selectors
                                    title_selectors = [
                                        'span.text-\\[13\\.3px\\].block',
                                        'span.block',
                                        'span',
                                        'h3',
                                        'h2',
                                        'div[class*="title"]',
                                        'div[class*="name"]',
                                        'img[alt]'
                                    ]
                                    
                                    for title_selector in title_selectors:
                                        try:
                                            elem = first_card.query_selector(title_selector)
                                            if elem:
                                                if title_selector == 'img[alt]':
                                                    text = elem.get_attribute('alt')
                                                else:
                                                    text = elem.inner_text().strip()
                                                if text and len(text) > 0:
                                                    print(f"    Title (using {title_selector}): '{text}'")
                                                    break
                                        except:
                                            continue
                                break
                        else:
                            print("  No cards found with any selector")
                    
                    # Rate limiting between searches
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Error testing '{title}': {e}")
                    continue
            
            print("\n" + "=" * 60)
            print("🎯 Summary: Asura Scans Search Test Complete")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_specific_manga() 