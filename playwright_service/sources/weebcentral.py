from playwright.sync_api import Page
import re
from flask import Blueprint, jsonify, request

def extract_manga_id_from_url(url):
    match = re.search(r'/series/([^/]+)/', url)
    return match.group(1) if match else None

def search(page: Page, query: str):
    search_url = f"https://weebcentral.com/search?text={query}&sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
    page.goto(search_url)
    page.wait_for_load_state('networkidle')
    results = []
    sections = page.query_selector_all('section.w-full')
    for section in sections:
        try:
            card = section.query_selector('a[href*="/series/"]')
            if not card:
                continue
            link = card.get_attribute('href')
            manga_id = extract_manga_id_from_url(link) if link else None
            
            # Handle picture element structure for images
            image_url = None
            picture_elem = card.query_selector('picture')
            if picture_elem:
                # Try to get the webp source first (better quality)
                source_elem = picture_elem.query_selector('source[type="image/webp"]')
                if source_elem:
                    image_url = source_elem.get_attribute('srcset')
                # Fallback to img tag if no webp source
                if not image_url:
                    img_elem = picture_elem.query_selector('img')
                    if img_elem:
                        image_url = img_elem.get_attribute('src')
            else:
                # Fallback to direct img tag if no picture element
                img_elem = card.query_selector('img')
                image_url = img_elem.get_attribute('src') if img_elem else None
            
            title = None
            # Try to get title from img alt attribute first
            if picture_elem:
                img_elem = picture_elem.query_selector('img')
                if img_elem:
                    alt_text = img_elem.get_attribute('alt')
                    if alt_text:
                        # Remove "cover" from the alt text to get clean title
                        title = alt_text.replace(' cover', '').replace(' Cover', '').strip()
            elif img_elem:
                alt_text = img_elem.get_attribute('alt')
                if alt_text:
                    # Remove "cover" from the alt text to get clean title
                    title = alt_text.replace(' cover', '').replace(' Cover', '').strip()
            
            # Fallback to text element if no alt text
            if not title:
                title_div = card.query_selector('div.text-ellipsis')
                if title_div:
                    title = title_div.inner_text().strip()
            
            # Final fallback to URL-based title
            if not title:
                title = link.split('/')[-1].replace('-', ' ').title() if link else "Unknown Title"
            
            status = ""
            status_elem = section.query_selector('div.opacity-70:has(strong:text("Status:")) span')
            if status_elem:
                status = status_elem.inner_text().strip()
            
            chapter = ""
            chapter_elem = section.query_selector('div.opacity-70:has(strong:text("Chapter:")), div.opacity-70:has(strong:text("Chapters:")) span')
            if chapter_elem:
                chapter = chapter_elem.inner_text().strip()
            
            results.append({
                'id': manga_id,
                'title': title,
                'status': status,
                'chapter': chapter,
                'image': image_url,
                'details_url': link,
                'source': 'weebcentral'
            })
        except Exception as e:
            print(f"WeebCentral error: {e}")
            continue
    return results

def get_details(page: Page, manga_id: str):
    manga_url = f"https://weebcentral.com/series/{manga_id}"
    page.goto(manga_url)
    page.wait_for_load_state('networkidle')
    
    # Click the 'Show All Chapters' button if it exists
    try:
        show_all_button = page.query_selector('button:has-text("Show All Chapters")')
        if not show_all_button:
            # Fallback: try by class if text selector fails
            show_all_button = page.query_selector('button.hover\:bg-base-300.p-2')
        if show_all_button:
            show_all_button.click()
            # Wait for the chapter list to expand and load
            page.wait_for_timeout(2000)  # Wait 2 seconds for Alpine.js to update
            # Wait for the chapter list section to be populated
            page.wait_for_selector('section[x-data*="mark_chapters"]', timeout=5000)
    except Exception as e:
        print(f"Show All Chapters button not found or could not be clicked: {e}")
    
    details = {}
    # Select the main container
    container = page.query_selector('main, .main-content, .series-container')
    # Title
    title_elem = page.query_selector('h1.text-2xl.font-bold, h1.series-title, [data-testid="series-title"], h1')
    details['title'] = title_elem.inner_text().strip() if title_elem else "Unknown Title"
    # Image
    image_url = None
    picture_elem = page.query_selector('.series-cover picture, .manga-cover picture, [data-testid="cover-image"] picture, picture')
    if picture_elem:
        # Try to get the webp source first (better quality)
        source_elem = picture_elem.query_selector('source[type="image/webp"]')
        if source_elem:
            image_url = source_elem.get_attribute('srcset')
        # Fallback to img tag if no webp source
        if not image_url:
            img_elem = picture_elem.query_selector('img')
            if img_elem:
                image_url = img_elem.get_attribute('src')
    else:
        # Fallback to direct img tag if no picture element
        img_elem = page.query_selector('.series-cover img, .manga-cover img, [data-testid="cover-image"], img.cover-image')
        image_url = img_elem.get_attribute('src') if img_elem else None
    details['image'] = image_url
    # Description
    desc_elem = page.query_selector('p.whitespace-pre-wrap.break-words, .description, .synopsis, [data-testid="description"], .series-description, p.description')
    if desc_elem:
        # Join all <p> children as paragraphs
        ps = desc_elem.query_selector_all('p')
        description = '\n'.join([p.inner_text().strip() for p in ps]) if ps else desc_elem.inner_text().strip()
        details['description'] = description
    else:
        details['description'] = "No description available"
    # Author
    author = ""
    # Try direct author element first
    author_elem = page.query_selector('.author, .creator, [data-testid="author"], .series-author')
    if author_elem:
        author = author_elem.inner_text().strip()
    else:
        # Try to find Author label and get the next sibling
        author_label = page.query_selector('h3:has-text("Author"), .author-label, strong:has-text("Author")')
        if author_label:
            author_value = author_label.evaluate('el => el.nextElementSibling && el.nextElementSibling.innerText')
            if author_value:
                author = author_value.strip()
    details['author'] = author or "Unknown Author"
    # Status
    status = ""
    status_elem = page.query_selector('.status, [data-testid="status"], .series-status, div:has-text("Status")')
    if status_elem:
        status = status_elem.inner_text().replace('Status', '').strip()
    details['status'] = status
    details['id'] = manga_id
    details['url'] = manga_url
    details['source'] = 'weebcentral'
    # Chapters
    try:
        # First try to click "Show All Chapters" button if it exists
        show_all_btn = page.query_selector('button:has-text("Show All Chapters"), button:has-text("Show All"), .show-all-chapters, [data-testid="show-all-chapters"]')
        if show_all_btn:
            show_all_btn.click()
            page.wait_for_timeout(2000)  # Wait for chapters to load
        
        # Look for the specific chapter list container
        chapter_container = page.query_selector('#chapter-list, .chapter-list, [data-testid="chapter-list"], .chapters-container')
        
        if chapter_container:
            # Get all chapter links within the container
            chapter_links = chapter_container.query_selector_all('a[href*="/chapter"], a[href*="/read"], .chapter-link, [data-testid="chapter-link"]')
            
            if not chapter_links:
                # Try alternative selectors within the container
                chapter_links = chapter_container.query_selector_all('a[href*="chapter"], a[href*="read"], a')
            
            chapters = []
            for link in chapter_links:
                href = link.get_attribute('href')
                text = link.inner_text().strip()
                
                if href and text:
                    # Clean up chapter text
                    chapter_text = text.replace('Chapter', '').strip()
                    if chapter_text:
                        # Store the full chapter URL as provided by WeebCentral
                        full_url = href if href.startswith('http') else f"https://weebcentral.com{href}"
                        chapters.append({
                            'title': f"Chapter {chapter_text}",
                            'url': full_url
                        })
            
            details['chapters'] = chapters
        else:
            details['chapters'] = []
            
    except Exception as e:
        print(f"Error extracting chapters: {e}")
        details['chapters'] = []
    
    # Images - only for chapter pages, not series page
    details['images'] = []
    
    return details 

def get_chapter_images(page: Page, chapter_url: str):
    """Get chapter images from WeebCentral chapter URL"""
    page.goto(chapter_url)
    page.wait_for_load_state('networkidle')
    
    # Wait for images to load
    page.wait_for_timeout(3000)
    
    images = []
    try:
        # Print page content for debugging
        print(f"WeebCentral: Loading images from {chapter_url}")
        
        # Look for images with specific alt text pattern "Page {number}"
        img_elements = page.query_selector_all('img[alt*="Page"], img[alt*="page"], .manga-page img, .reader-page img, [data-testid="manga-page"] img')
        
        print(f"WeebCentral: Found {len(img_elements)} image elements")
        
        for img in img_elements:
            try:
                src = img.get_attribute('src')
                alt = img.get_attribute('alt') or ''
                
                print(f"WeebCentral: Image src={src}, alt={alt}")
                
                if src and src.startswith('http'):
                    # Only add the URL, not the object
                    images.append(src)
                    
            except Exception as e:
                print(f"WeebCentral image error: {e}")
                continue
                
    except Exception as e:
        print(f"WeebCentral images error: {e}")
    
    print(f"WeebCentral: Returning {len(images)} images")
    return images 

# If using Flask or FastAPI, add a route handler (example for Flask style):
weebcentral_chapter_bp = Blueprint('weebcentral_chapter_bp', __name__)

@weebcentral_chapter_bp.route('/chapter-images/weebcentral/<path:chapter_url>', methods=['GET'])
def chapter_images(chapter_url):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
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
            
            # Decode the URL if it's URL-encoded
            import urllib.parse
            decoded_url = urllib.parse.unquote(chapter_url)
            images = get_chapter_images(page, decoded_url)
            return jsonify({'images': images})
        finally:
            browser.close() 