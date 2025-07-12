from playwright.sync_api import sync_playwright
from weebcentral import get_details, extract_manga_id_from_url
import json

def test_weebcentral_details():
    """Test the get_details function with the Bleach manga page"""
    
    # Extract manga ID from the URL
    url = "https://weebcentral.com/series/01J76XY7E4JCPK14V53BVQWD9Y/Bleach"
    manga_id = extract_manga_id_from_url(url)
    print(f"Testing manga ID: {manga_id}")
    
    if not manga_id:
        print("Error: Could not extract manga ID from URL")
        return
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to False to see what's happening
        page = browser.new_page()
        
        try:
            # Navigate to the page first to check for Alpine.js section
            manga_url = f"https://weebcentral.com/series/{manga_id}"
            page.goto(manga_url)
            page.wait_for_load_state('networkidle')
            
            # Check if Alpine.js section exists before clicking "Show All Chapters"
            alpine_section_before = page.query_selector('section[x-data*="mark_chapters"]')
            print(f"Alpine.js section found before clicking button: {alpine_section_before is not None}")
            
            # Click the 'Show All Chapters' button if it exists
            try:
                show_all_button = page.query_selector('button:has-text("Show All Chapters")')
                if not show_all_button:
                    # Fallback: try by class if text selector fails
                    show_all_button = page.query_selector('button.hover\:bg-base-300.p-2')
                if show_all_button:
                    print("Found 'Show All Chapters' button, clicking...")
                    show_all_button.click()
                    # Wait for the chapter list to expand and load
                    page.wait_for_timeout(2000)  # Wait 2 seconds for Alpine.js to update
                    # Wait for the specific Alpine.js section to be populated
                    page.wait_for_selector('section[x-data*="mark_chapters"]', timeout=5000)
                    print("Successfully clicked 'Show All Chapters' button")
                else:
                    print("'Show All Chapters' button not found")
            except Exception as e:
                print(f"Show All Chapters button not found or could not be clicked: {e}")
            
            # Check if Alpine.js section exists after clicking
            alpine_section_after = page.query_selector('section[x-data*="mark_chapters"]')
            print(f"Alpine.js section found after clicking button: {alpine_section_after is not None}")
            
            if alpine_section_after:
                # Count chapter links in the Alpine.js section
                chapter_links = alpine_section_after.query_selector_all('a[href*="/chapter"], a[href*="/read"]')
                print(f"Found {len(chapter_links)} chapter links in Alpine.js section")
                
                # Show first few chapter links for debugging
                for i, link in enumerate(chapter_links[:3]):
                    href = link.get_attribute('href')
                    text = link.inner_text().strip()
                    print(f"  Chapter {i+1}: {text} -> {href}")
            
            # Get detailed information
            print("\nFetching detailed information...")
            details = get_details(page, manga_id)
            
            # Print the results in a readable format
            print("\n" + "="*50)
            print("WEEB CENTRAL MANGA DETAILS TEST")
            print("="*50)
            
            print(f"Title: {details.get('title', 'N/A')}")
            print(f"ID: {details.get('id', 'N/A')}")
            print(f"URL: {details.get('url', 'N/A')}")
            print(f"Status: {details.get('status', 'N/A')}")
            print(f"Author: {details.get('author', 'N/A')}")
            print(f"Type: {details.get('type', 'N/A')}")
            print(f"Released: {details.get('released', 'N/A')}")
            print(f"Tags: {', '.join(details.get('tags', []))}")
            print(f"Official Translation: {details.get('official_translation', 'N/A')}")
            print(f"Anime Adaptation: {details.get('anime_adaptation', 'N/A')}")
            print(f"Adult Content: {details.get('adult_content', 'N/A')}")
            print(f"Image: {details.get('image', 'N/A')}")
            print(f"Description: {details.get('description', 'N/A')[:200]}...")
            print(f"Number of chapters: {len(details.get('chapters', []))}")
            
            # Show first few chapters
            chapters = details.get('chapters', [])
            if chapters:
                print("\nFirst 5 chapters:")
                for i, chapter in enumerate(chapters[:5]):
                    print(f"  {i+1}. {chapter.get('title', 'N/A')} - {chapter.get('url', 'N/A')}")
                
                # Verify that chapters are from Alpine.js section
                print(f"\nChapter extraction method verification:")
                print(f"  - Total chapters extracted: {len(chapters)}")
                print(f"  - First chapter title: {chapters[0].get('title', 'N/A') if chapters else 'N/A'}")
                print(f"  - First chapter URL: {chapters[0].get('url', 'N/A') if chapters else 'N/A'}")
            else:
                print("\nNo chapters found - this might indicate an issue with the Alpine.js section extraction")
            
            # Save full details to JSON file for inspection
            with open('weebcentral_bleach_details.json', 'w', encoding='utf-8') as f:
                json.dump(details, f, indent=2, ensure_ascii=False)
            print(f"\nFull details saved to: weebcentral_bleach_details.json")
            
            # Verify expected data based on the Bleach page
            expected_data = {
                'title': 'Bleach',
                'author': 'KUBO Tite',
                'status': 'Complete',
                'type': 'Manga',
                'released': '2001',
                'official_translation': 'Yes',
                'anime_adaptation': 'Yes',
                'adult_content': 'No',
                'description': 'Ichigo Kurosaki has always been able to see ghosts'
            }
            
            print("\n" + "="*50)
            print("DATA VERIFICATION")
            print("="*50)
            
            for field, expected_value in expected_data.items():
                actual_value = details.get(field, '')
                if field == 'description':
                    # Check if description contains the expected text
                    contains_expected = expected_value.lower() in actual_value.lower()
                    print(f"{field}: {'✓' if contains_expected else '✗'} (Expected: '{expected_value}', Found: '{actual_value[:50]}...')")
                else:
                    matches = expected_value.lower() in actual_value.lower()
                    print(f"{field}: {'✓' if matches else '✗'} (Expected: '{expected_value}', Found: '{actual_value}')")
            
            # Special verification for tags
            expected_tags = ['Action', 'Comedy', 'Drama', 'Martial Arts', 'Shounen', 'Supernatural']
            actual_tags = details.get('tags', [])
            tags_found = all(tag in actual_tags for tag in expected_tags)
            print(f"tags: {'✓' if tags_found else '✗'} (Expected: {expected_tags}, Found: {actual_tags})")
            
        except Exception as e:
            print(f"Error during testing: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    test_weebcentral_details() 