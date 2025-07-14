#!/usr/bin/env python3
"""
Test to demonstrate selector performance differences
"""

import time
import statistics
from playwright.sync_api import sync_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_selector_performance():
    """Test different selector types and their performance"""
    print("🔍 Selector Performance Test")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to a test page (WeebCentral search page)
        test_url = "https://weebcentral.com/search?text=solo&sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
        
        try:
            print(f"Navigating to test page: {test_url}")
            page.goto(test_url, wait_until='domcontentloaded', timeout=15000)
            page.wait_for_timeout(3000)  # Wait for content to load
            
            print("✅ Page loaded successfully")
            
            # Test different selector types
            test_selectors = {
                "ID Selector": "#main-content, #app, #root",
                "Class Selector": ".container, .main, .content",
                "Tag Selector": "main, div, section",
                "Attribute Selector": "[data-testid], [class], [id]",
                "Descendant Selector": "main .container, div .content",
                "Complex Selector": "body > main > div.container > section",
                "Direct Class": "section.w-full",
                "Direct Tag": "section",
                "Direct Attribute": "[data-testid='manga-item']",
                "Combined Fast": ".manga-item, .search-result"
            }
            
            results = {}
            iterations = 100
            
            print(f"\nTesting {iterations} iterations for each selector...")
            print("-" * 60)
            
            for selector_name, selector in test_selectors.items():
                print(f"Testing: {selector_name}")
                
                times = []
                for i in range(iterations):
                    start_time = time.time()
                    
                    try:
                        # Test query_selector
                        element = page.query_selector(selector)
                        
                        # Test query_selector_all
                        elements = page.query_selector_all(selector)
                        
                        end_time = time.time()
                        duration = (end_time - start_time) * 1000  # Convert to milliseconds
                        times.append(duration)
                        
                    except Exception as e:
                        logger.debug(f"Selector '{selector}' failed: {e}")
                        times.append(0)
                
                # Calculate statistics
                if times:
                    avg_time = statistics.mean(times)
                    median_time = statistics.median(times)
                    min_time = min(times)
                    max_time = max(times)
                    
                    results[selector_name] = {
                        'selector': selector,
                        'avg_time': avg_time,
                        'median_time': median_time,
                        'min_time': min_time,
                        'max_time': max_time,
                        'success_rate': len([t for t in times if t > 0]) / len(times) * 100
                    }
                    
                    print(f"  ✅ Avg: {avg_time:.3f}ms, Median: {median_time:.3f}ms, Success: {results[selector_name]['success_rate']:.1f}%")
                else:
                    print(f"  ❌ Failed")
            
            # Sort results by average time (fastest first)
            sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_time'])
            
            print(f"\n📊 Performance Ranking (Fastest to Slowest)")
            print("-" * 60)
            
            for i, (selector_name, data) in enumerate(sorted_results, 1):
                print(f"{i:2d}. {selector_name:20s} | {data['avg_time']:6.3f}ms avg | {data['success_rate']:5.1f}% success")
            
            # Performance analysis
            print(f"\n📈 Performance Analysis")
            print("-" * 60)
            
            if sorted_results:
                fastest = sorted_results[0]
                slowest = sorted_results[-1]
                
                speedup = slowest[1]['avg_time'] / fastest[1]['avg_time'] if fastest[1]['avg_time'] > 0 else 0
                
                print(f"Fastest: {fastest[0]} ({fastest[1]['avg_time']:.3f}ms)")
                print(f"Slowest: {slowest[0]} ({slowest[1]['avg_time']:.3f}ms)")
                print(f"Speedup: {speedup:.1f}x faster")
                
                # Recommendations
                print(f"\n💡 Recommendations:")
                print("-" * 60)
                
                fast_selectors = [name for name, data in sorted_results[:3]]
                slow_selectors = [name for name, data in sorted_results[-3:]]
                
                print(f"✅ Use these fast selectors: {', '.join(fast_selectors)}")
                print(f"❌ Avoid these slow selectors: {', '.join(slow_selectors)}")
                
                # Performance categories
                print(f"\n🏆 Performance Categories:")
                print("-" * 60)
                
                excellent = [name for name, data in sorted_results if data['avg_time'] < 0.1]
                good = [name for name, data in sorted_results if 0.1 <= data['avg_time'] < 0.5]
                moderate = [name for name, data in sorted_results if 0.5 <= data['avg_time'] < 1.0]
                slow = [name for name, data in sorted_results if data['avg_time'] >= 1.0]
                
                if excellent:
                    print(f"⚡ Excellent (< 0.1ms): {', '.join(excellent)}")
                if good:
                    print(f"🚀 Good (0.1-0.5ms): {', '.join(good)}")
                if moderate:
                    print(f"🟡 Moderate (0.5-1.0ms): {', '.join(moderate)}")
                if slow:
                    print(f"🔴 Slow (> 1.0ms): {', '.join(slow)}")
            
            # Test real-world scenario
            print(f"\n🌐 Real-world Scenario Test")
            print("-" * 60)
            
            # Test extracting manga items with different approaches
            approaches = {
                "Fast Approach": {
                    "container": "section.w-full",
                    "title": ".text-ellipsis, .title, h3",
                    "link": "a[href*='/series/']",
                    "image": "img"
                },
                "Slow Approach": {
                    "container": "body > main > div > section > div.manga-item",
                    "title": "div > h3 > a > span",
                    "link": "div > h3 > a",
                    "image": "div > div > picture > img"
                }
            }
            
            for approach_name, selectors in approaches.items():
                print(f"\nTesting {approach_name}:")
                
                start_time = time.time()
                
                try:
                    # Get manga items
                    manga_items = page.query_selector_all(selectors["container"])
                    
                    results_count = 0
                    for item in manga_items[:5]:  # Test first 5 items
                        title = item.query_selector(selectors["title"])
                        link = item.query_selector(selectors["link"])
                        image = item.query_selector(selectors["image"])
                        
                        if title and link:
                            results_count += 1
                    
                    end_time = time.time()
                    duration = (end_time - start_time) * 1000
                    
                    print(f"  ✅ Found {results_count} items in {duration:.3f}ms")
                    
                except Exception as e:
                    print(f"  ❌ Failed: {e}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        finally:
            browser.close()

def test_selector_fallbacks():
    """Test selector fallback strategy performance"""
    print(f"\n🔄 Selector Fallback Strategy Test")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to test page
            page.goto("https://weebcentral.com/search?text=solo", wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            
            # Test different fallback strategies
            strategies = {
                "Fast Fallback": [
                    '[data-testid="manga-title"]',
                    '.manga-title',
                    'h1',
                    '[data-title]'
                ],
                "Slow Fallback": [
                    'body > main > div.container > section > div.manga-details > h1.title',
                    'main > div > h1',
                    'div > h1',
                    'h1'
                ],
                "Mixed Fallback": [
                    '.manga-title',
                    'h1[data-title]',
                    'h1',
                    '[data-title]'
                ]
            }
            
            for strategy_name, selectors in strategies.items():
                print(f"\nTesting {strategy_name}:")
                
                start_time = time.time()
                
                for selector in selectors:
                    element = page.query_selector(selector)
                    if element:
                        title = element.inner_text().strip()
                        print(f"  ✅ Found with '{selector}': {title[:30]}...")
                        break
                else:
                    print(f"  ❌ No element found with any selector")
                
                end_time = time.time()
                duration = (end_time - start_time) * 1000
                print(f"  ⏱️  Total time: {duration:.3f}ms")
        
        except Exception as e:
            print(f"❌ Fallback test failed: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_selector_performance()
    test_selector_fallbacks() 