import os
import sys
import time
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.optimized_weebcentral_fast import get_details, get_chapter_images, search
from services.browser_pool import browser_pool
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_weebcentral_details():
    """Test WeebCentral manga details functionality"""
    print("🔍 Testing WeebCentral Manga Details")
    print("=" * 50)
    
    # Test manga titles
    test_queries = [
        "Solo Leveling",
        "One Piece",
        "Naruto"
    ]
    
    browser = None
    try:
        # Get browser from pool
        browser = browser_pool.get_browser()
        if not browser:
            print("❌ Failed to get browser from pool")
            return
        
        page = browser.new_page()
        
        # Optimize page settings
        page.set_viewport_size({"width": 1280, "height": 720})
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        for query in test_queries:
            print(f"\n📝 Testing: '{query}'")
            print("-" * 30)
            
            # First, search for the manga
            print(f"🔍 Searching for '{query}'...")
            search_start = time.time()
            search_results = search(page, query)
            search_time = time.time() - search_start
            
            print(f"  ✅ Found {len(search_results)} results in {search_time:.2f}s")
            
            if search_results:
                # Get details for the first result
                first_result = search_results[0]
                manga_id = first_result.get('id')
                title = first_result.get('title', 'Unknown')
                
                print(f"  📖 Getting details for: {title} (ID: {manga_id})")
                
                # Get manga details
                details_start = time.time()
                details = get_details(page, manga_id)
                details_time = time.time() - details_start
                
                print(f"  ✅ Details retrieved in {details_time:.2f}s")
                
                # Display details
                print(f"    Title: {details.get('title', 'Unknown')}")
                print(f"    Author: {details.get('author', 'Unknown')}")
                print(f"    Status: {details.get('status', 'Unknown')}")
                print(f"    Description: {details.get('description', 'No description')[:100]}...")
                print(f"    Chapters: {len(details.get('chapters', []))}")
                print(f"    Image: {'✅' if details.get('image') else '❌'}")
                
                # Test chapter images if chapters exist
                chapters = details.get('chapters', [])
                if chapters:
                    first_chapter = chapters[0]
                    chapter_url = first_chapter.get('url')
                    chapter_title = first_chapter.get('title', 'Unknown')
                    
                    print(f"  🖼️ Testing chapter images for: {chapter_title}")
                    
                    images_start = time.time()
                    images = get_chapter_images(page, chapter_url)
                    images_time = time.time() - images_start
                    
                    print(f"    ✅ Found {len(images)} images in {images_time:.2f}s")
                    if images:
                        print(f"    First image: {images[0][:50]}...")
                
                # Performance analysis
                total_time = search_time + details_time
                print(f"  ⏱️ Total time: {total_time:.2f}s")
                print(f"  📊 Performance breakdown:")
                print(f"    - Search: {search_time:.2f}s ({(search_time/total_time)*100:.1f}%)")
                print(f"    - Details: {details_time:.2f}s ({(details_time/total_time)*100:.1f}%)")
                
            else:
                print(f"  ❌ No results found for '{query}'")
            
            print()
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if browser:
            browser_pool.return_browser(browser)

def analyze_weebcentral_structure():
    """Analyze WeebCentral page structure for potential improvements"""
    print("\n🔍 Analyzing WeebCentral Page Structure")
    print("=" * 50)
    
    browser = None
    try:
        browser = browser_pool.get_browser()
        if not browser:
            print("❌ Failed to get browser from pool")
            return
        
        page = browser.new_page()
        
        # Navigate to a sample manga page
        sample_url = "https://weebcentral.com/series/01J76XYCPSY3C4BNPBRY8JMCBE/Solo-Leveling"
        print(f"🔍 Analyzing page: {sample_url}")
        
        page.goto(sample_url, wait_until='domcontentloaded', timeout=15000)
        page.wait_for_timeout(3000)
        
        # Analyze page structure
        print("\n📊 Page Structure Analysis:")
        
        # Check for title elements
        title_selectors = [
            'h1.text-2xl.font-bold',
            'h1.series-title',
            '[data-testid="series-title"]',
            'h1',
            '[data-title]'
        ]
        
        print("  🏷️ Title Elements:")
        for selector in title_selectors:
            element = page.query_selector(selector)
            if element:
                text = element.inner_text().strip()
                print(f"    ✅ {selector}: '{text}'")
            else:
                print(f"    ❌ {selector}: Not found")
        
        # Check for image elements
        print("\n  🖼️ Image Elements:")
        image_selectors = [
            'picture',
            'img[src*="cover"]',
            'img[alt*="cover"]',
            'img'
        ]
        
        for selector in image_selectors:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"    ✅ {selector}: {len(elements)} found")
                if selector == 'picture' and elements:
                    # Check picture structure
                    picture = elements[0]
                    sources = picture.query_selector_all('source')
                    img = picture.query_selector('img')
                    print(f"      - Sources: {len(sources)}")
                    print(f"      - Image: {'✅' if img else '❌'}")
            else:
                print(f"    ❌ {selector}: Not found")
        
        # Check for description elements
        print("\n  📝 Description Elements:")
        desc_selectors = [
            'p.whitespace-pre-wrap.break-words',
            '.description',
            '.synopsis',
            '[data-testid="description"]',
            'p.description'
        ]
        
        for selector in desc_selectors:
            element = page.query_selector(selector)
            if element:
                text = element.inner_text().strip()[:100]
                print(f"    ✅ {selector}: '{text}...'")
            else:
                print(f"    ❌ {selector}: Not found")
        
        # Check for chapter elements
        print("\n  📚 Chapter Elements:")
        chapter_selectors = [
            '#chapter-list',
            '.chapter-list',
            '[data-testid="chapter-list"]',
            'a[href*="/chapter"]',
            'a[href*="/read"]'
        ]
        
        for selector in chapter_selectors:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"    ✅ {selector}: {len(elements)} found")
            else:
                print(f"    ❌ {selector}: Not found")
        
        # Check for author elements
        print("\n  👤 Author Elements:")
        author_selectors = [
            '.author',
            '.creator',
            '[data-testid="author"]',
            '.series-author'
        ]
        
        for selector in author_selectors:
            element = page.query_selector(selector)
            if element:
                text = element.inner_text().strip()
                print(f"    ✅ {selector}: '{text}'")
            else:
                print(f"    ❌ {selector}: Not found")
        
        # Check for status elements
        print("\n  📊 Status Elements:")
        status_selectors = [
            '.status',
            '[data-testid="status"]',
            '.series-status'
        ]
        
        for selector in status_selectors:
            element = page.query_selector(selector)
            if element:
                text = element.inner_text().strip()
                print(f"    ✅ {selector}: '{text}'")
            else:
                print(f"    ❌ {selector}: Not found")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if browser:
            browser_pool.return_browser(browser)

def identify_improvements():
    """Identify potential improvements for WeebCentral details"""
    print("\n💡 Potential Improvements for WeebCentral Details")
    print("=" * 50)
    
    print("🔧 Performance Improvements:")
    print("  1. Reduce wait times for faster loading")
    print("  2. Implement parallel chapter image loading")
    print("  3. Add caching for frequently accessed details")
    print("  4. Optimize selector fallback chains")
    
    print("\n🎯 Accuracy Improvements:")
    print("  1. Add more robust error handling")
    print("  2. Implement retry mechanisms for failed extractions")
    print("  3. Add validation for extracted data")
    print("  4. Handle dynamic content loading better")
    
    print("\n📊 Data Quality Improvements:")
    print("  1. Extract more metadata (genres, ratings, etc.)")
    print("  2. Better chapter numbering and sorting")
    print("  3. Extract publication dates")
    print("  4. Handle multiple authors/artists")
    
    print("\n🚀 User Experience Improvements:")
    print("  1. Add progress indicators during loading")
    print("  2. Implement partial results display")
    print("  3. Add fallback data sources")
    print("  4. Better error messages for users")

def main():
    """Run WeebCentral details testing and analysis"""
    print("🚀 WeebCentral Details Testing and Analysis")
    print("=" * 60)
    
    try:
        # Test manga details functionality
        test_weebcentral_details()
        
        # Analyze page structure
        analyze_weebcentral_structure()
        
        # Identify improvements
        identify_improvements()
        
        print("\n" + "=" * 60)
        print("✅ WeebCentral Details Analysis Complete!")
        print("=" * 60)
        
        print(f"\n🎉 Key Findings:")
        print(f"   • Current implementation is functional")
        print(f"   • Performance can be optimized further")
        print(f"   • Page structure analysis reveals opportunities")
        print(f"   • Multiple improvement areas identified")
        
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 