#!/usr/bin/env python3
"""
Test script for AsuraScans pagination preload functionality
This demonstrates how the system can crawl all manga from AsuraScans using pagination
"""

import sys
import os
import time
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'services'))

from scrapers.sources import asurascans
from playwright.sync_api import sync_playwright

def test_asurascans_pagination():
    """Test the pagination functionality for AsuraScans"""
    print("=" * 60)
    print("ASURASCANS PAGINATION PRELOAD TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    print()
    
    start_time = time.time()
    
    try:
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Set a respectful user agent
            page.set_extra_http_headers({
                'User-Agent': 'MangaReader/1.0 (+https://github.com/your-repo)'
            })
            
            print("Testing AsuraScans pagination crawl...")
            print("This will crawl through pages to get all manga...")
            print()
            
            # Test with a smaller number of pages first
            max_pages = 5  # Start with 5 pages for testing
            all_manga = asurascans.get_all_manga_from_pagination(page, max_pages)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print()
            print("=" * 60)
            print("PAGINATION TEST RESULTS")
            print("=" * 60)
            print(f"Duration: {duration:.2f} seconds")
            print(f"Pages crawled: {max_pages}")
            print(f"Total manga found: {len(all_manga)}")
            print(f"Average manga per page: {len(all_manga) / max_pages:.1f}")
            print()
            
            if all_manga:
                print("Sample manga found:")
                print("-" * 40)
                for i, manga in enumerate(all_manga[:10]):  # Show first 10
                    print(f"{i+1:2d}. {manga['title']} (ID: {manga['id']})")
                    if manga['chapter']:
                        print(f"     Latest: Chapter {manga['chapter']}")
                    print()
                
                if len(all_manga) > 10:
                    print(f"... and {len(all_manga) - 10} more manga")
                    print()
                
                # Show some statistics
                print("STATISTICS:")
                print("-" * 20)
                titles_with_chapters = [m for m in all_manga if m['chapter']]
                print(f"Manga with chapter info: {len(titles_with_chapters)}")
                print(f"Manga with images: {len([m for m in all_manga if m['image']])}")
                
                # Check for duplicates
                manga_ids = [m['id'] for m in all_manga]
                unique_ids = set(manga_ids)
                print(f"Unique manga IDs: {len(unique_ids)}")
                if len(manga_ids) != len(unique_ids):
                    print(f"⚠️  Duplicates found: {len(manga_ids) - len(unique_ids)}")
                
            else:
                print("❌ No manga found during pagination crawl")
            
            browser.close()
            
            return len(all_manga) > 0
            
    except Exception as e:
        print(f"❌ Error during pagination test: {e}")
        return False

def test_pagination_performance():
    """Test performance characteristics of pagination"""
    print("\n" + "=" * 60)
    print("PAGINATION PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Test different page counts
    page_counts = [1, 3, 5, 10]
    
    for page_count in page_counts:
        print(f"\nTesting {page_count} page(s)...")
        start_time = time.time()
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_extra_http_headers({
                    'User-Agent': 'MangaReader/1.0 (+https://github.com/your-repo)'
                })
                
                all_manga = asurascans.get_all_manga_from_pagination(page, page_count)
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"  Pages: {page_count}")
                print(f"  Manga found: {len(all_manga)}")
                print(f"  Duration: {duration:.2f}s")
                print(f"  Manga per second: {len(all_manga) / duration:.1f}")
                print(f"  Seconds per page: {duration / page_count:.2f}")
                
                browser.close()
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def main():
    """Main test function"""
    print("AsuraScans Pagination Preload Test")
    print("This test demonstrates the new pagination-based preload system")
    print("that crawls all manga from AsuraScans instead of using search terms.")
    print()
    
    # Test basic pagination
    success = test_asurascans_pagination()
    
    if success:
        # Test performance
        test_pagination_performance()
        
        print("\n" + "=" * 60)
        print("RECOMMENDATIONS")
        print("=" * 60)
        print("✅ Pagination preload is working correctly!")
        print()
        print("For production use:")
        print("- Set max_pages to 50-100 for comprehensive coverage")
        print("- Run during off-peak hours (2-6 AM)")
        print("- Monitor for rate limiting and adjust delays")
        print("- Cache results for 24-48 hours")
        print("- Consider incremental updates (only new pages)")
        print()
        print("Benefits of pagination approach:")
        print("- Gets ALL manga, not just popular searches")
        print("- Better cache coverage for user searches")
        print("- More efficient than multiple search queries")
        print("- Provides complete catalog for browsing")
    else:
        print("\n❌ Pagination test failed. Check the error messages above.")

if __name__ == "__main__":
    main() 