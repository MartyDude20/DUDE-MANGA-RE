#!/usr/bin/env python3
"""
Test to compare WeebCentral selector speeds
"""

import time
import statistics
from playwright.sync_api import sync_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_weebcentral_selectors():
    """Test different WeebCentral selector approaches"""
    print("🔍 WeebCentral Selector Speed Test")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Test URL
        test_url = "https://weebcentral.com/search?text=solo&sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
        
        try:
            print(f"Navigating to: {test_url}")
            page.goto(test_url, wait_until='domcontentloaded', timeout=15000)
            page.wait_for_timeout(3000)  # Wait for content to load
            
            print("✅ Page loaded successfully")
            
            # Test different selector approaches
            selector_tests = {
                "Current (section.w-full)": "section.w-full",
                "Correct (article.bg-base-300.flex.gap-4.p-4)": "article.bg-base-300.flex.gap-4.p-4",
                "Flexible (article.bg-base-300)": "article.bg-base-300",
                "Has Link (article:has(a[href*='/series/']))": "article:has(a[href*='/series/'])",
                "Any Article": "article",
                "Any Section": "section"
            }
            
            results = {}
            iterations = 50  # Test each selector 50 times
            
            print(f"\nTesting {iterations} iterations for each selector...")
            print("-" * 60)
            
            for selector_name, selector in selector_tests.items():
                print(f"Testing: {selector_name}")
                
                times = []
                element_counts = []
                
                for i in range(iterations):
                    start_time = time.time()
                    
                    try:
                        elements = page.query_selector_all(selector)
                        end_time = time.time()
                        
                        duration = (end_time - start_time) * 1000  # Convert to milliseconds
                        times.append(duration)
                        element_counts.append(len(elements))
                        
                    except Exception as e:
                        logger.debug(f"Selector '{selector}' failed: {e}")
                        times.append(0)
                        element_counts.append(0)
                
                # Calculate statistics
                if times:
                    avg_time = statistics.mean(times)
                    median_time = statistics.median(times)
                    min_time = min(times)
                    max_time = max(times)
                    avg_elements = statistics.mean(element_counts)
                    
                    results[selector_name] = {
                        'selector': selector,
                        'avg_time': avg_time,
                        'median_time': median_time,
                        'min_time': min_time,
                        'max_time': max_time,
                        'avg_elements': avg_elements,
                        'success_rate': len([t for t in times if t > 0]) / len(times) * 100
                    }
                    
                    print(f"  ✅ Avg: {avg_time:.3f}ms, Elements: {avg_elements:.1f}, Success: {results[selector_name]['success_rate']:.1f}%")
                else:
                    print(f"  ❌ Failed")
            
            # Sort results by average time (fastest first)
            sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_time'])
            
            print(f"\n📊 Performance Ranking (Fastest to Slowest)")
            print("-" * 60)
            
            for i, (selector_name, data) in enumerate(sorted_results, 1):
                print(f"{i:2d}. {selector_name:35s} | {data['avg_time']:6.3f}ms | {data['avg_elements']:5.1f} elements")
            
            # Accuracy test - check which selectors actually find manga cards
            print(f"\n🎯 Accuracy Test - Which selectors find actual manga cards?")
            print("-" * 60)
            
            for selector_name, selector in selector_tests.items():
                try:
                    elements = page.query_selector_all(selector)
                    manga_links = 0
                    
                    for element in elements:
                        link = element.query_selector('a[href*="/series/"]')
                        if link:
                            manga_links += 1
                    
                    accuracy = (manga_links / len(elements) * 100) if elements else 0
                    print(f"{selector_name:35s} | {len(elements):3d} total | {manga_links:3d} manga | {accuracy:5.1f}% accuracy")
                    
                except Exception as e:
                    print(f"{selector_name:35s} | Error: {e}")
            
            # Real-world extraction test
            print(f"\n🌐 Real-world Extraction Test")
            print("-" * 60)
            
            # Test the two main approaches
            approaches = {
                "Current Approach": "section.w-full",
                "Correct Approach": "article.bg-base-300.flex.gap-4.p-4"
            }
            
            for approach_name, selector in approaches.items():
                print(f"\nTesting {approach_name}:")
                
                start_time = time.time()
                
                try:
                    elements = page.query_selector_all(selector)
                    manga_found = 0
                    
                    for element in elements:
                        link_elem = element.query_selector('a[href*="/series/"]')
                        if link_elem:
                            href = link_elem.get_attribute('href')
                            if href and '/series/' in href:
                                manga_found += 1
                    
                    end_time = time.time()
                    duration = (end_time - start_time) * 1000
                    
                    print(f"  ✅ Found {manga_found} manga cards in {duration:.3f}ms")
                    print(f"  📊 Total elements: {len(elements)}, Manga accuracy: {(manga_found/len(elements)*100):.1f}%" if elements else "  📊 No elements found")
                    
                except Exception as e:
                    print(f"  ❌ Failed: {e}")
            
            # Recommendations
            print(f"\n💡 Recommendations:")
            print("-" * 60)
            
            if sorted_results:
                fastest = sorted_results[0]
                fastest_accurate = None
                
                # Find the fastest selector that has good accuracy
                for name, data in sorted_results:
                    if data['avg_elements'] > 0 and data['success_rate'] > 90:
                        fastest_accurate = (name, data)
                        break
                
                if fastest_accurate:
                    print(f"✅ Best choice: {fastest_accurate[0]}")
                    print(f"   - Speed: {fastest_accurate[1]['avg_time']:.3f}ms average")
                    print(f"   - Elements: {fastest_accurate[1]['avg_elements']:.1f} per page")
                    print(f"   - Success rate: {fastest_accurate[1]['success_rate']:.1f}%")
                
                print(f"❌ Avoid: {sorted_results[-1][0]} (slowest)")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        finally:
            browser.close()

def test_selector_accuracy():
    """Test which selectors actually find manga content"""
    print(f"\n🎯 Detailed Accuracy Test")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto("https://weebcentral.com/search?text=solo", wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            
            selectors = [
                "section.w-full",
                "article.bg-base-300.flex.gap-4.p-4",
                "article.bg-base-300",
                "article:has(a[href*='/series/'])"
            ]
            
            for selector in selectors:
                print(f"\nTesting: {selector}")
                
                elements = page.query_selector_all(selector)
                print(f"  Total elements found: {len(elements)}")
                
                manga_count = 0
                for i, element in enumerate(elements[:5]):  # Check first 5 elements
                    link = element.query_selector('a[href*="/series/"]')
                    if link:
                        href = link.get_attribute('href')
                        print(f"    Element {i+1}: ✅ Manga link found - {href}")
                        manga_count += 1
                    else:
                        print(f"    Element {i+1}: ❌ No manga link")
                
                accuracy = (manga_count / len(elements) * 100) if elements else 0
                print(f"  Accuracy: {accuracy:.1f}% ({manga_count}/{len(elements)})")
        
        except Exception as e:
            print(f"❌ Accuracy test failed: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_weebcentral_selectors()
    test_selector_accuracy() 