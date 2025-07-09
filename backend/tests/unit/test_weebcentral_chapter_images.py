from playwright.sync_api import sync_playwright
from sources.weebcentral import get_chapter_images
import json

def test_weebcentral_chapter_images():
    """Test the get_chapter_images function with a WeebCentral chapter URL"""
    
    # Test with a chapter URL from the Bleach manga
    chapter_url = "https://weebcentral.com/chapters/01J76XYY6F5JMA5RKG89KXZAS1"
    
    print(f"Testing chapter images from: {chapter_url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to False to see what's happening
        page = browser.new_page()
        
        try:
            # Set headers to avoid CORS issues
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # Get chapter images
            print("Fetching chapter images...")
            images = get_chapter_images(page, chapter_url)
            
            # Print results
            print("\n" + "="*50)
            print("WEEB CENTRAL CHAPTER IMAGES TEST")
            print("="*50)
            
            print(f"Chapter URL: {chapter_url}")
            print(f"Number of images found: {len(images)}")
            
            if images:
                print("\nFirst 5 image URLs:")
                for i, img_url in enumerate(images[:5]):
                    print(f"  {i+1}. {img_url}")
                
                if len(images) > 5:
                    print(f"  ... and {len(images) - 5} more images")
                
                # Save results to file for inspection
                with open('weebcentral_chapter_images_test.json', 'w') as f:
                    json.dump({
                        'chapter_url': chapter_url,
                        'image_count': len(images),
                        'images': images
                    }, f, indent=2)
                print(f"\nResults saved to: weebcentral_chapter_images_test.json")
            else:
                print("\nNo images found!")
                
                # Let's inspect the page content to debug
                print("\nInspecting page content for debugging...")
                page_content = page.content()
                
                # Look for common image selectors
                print("\nChecking for image elements...")
                all_images = page.query_selector_all('img')
                print(f"Total img elements found: {len(all_images)}")
                
                for i, img in enumerate(all_images[:10]):  # Show first 10
                    src = img.get_attribute('src')
                    alt = img.get_attribute('alt')
                    class_attr = img.get_attribute('class')
                    print(f"  Image {i+1}: src='{src}', alt='{alt}', class='{class_attr}'")
                
                # Check for specific manga reader containers
                print("\nChecking for manga reader containers...")
                reader_containers = page.query_selector_all('.manga-page, .reader-page, [data-testid="manga-page"]')
                print(f"Manga reader containers found: {len(reader_containers)}")
                
                # Save page HTML for debugging
                with open('weebcentral_chapter_debug.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                print(f"\nPage HTML saved to: weebcentral_chapter_debug.html")
            
        except Exception as e:
            print(f"Error during test: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    test_weebcentral_chapter_images() 