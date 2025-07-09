from playwright.sync_api import Page
import re
from flask import Blueprint, jsonify, request
import time

def extract_manga_id_from_url(url):
    match = re.search(r'/series/([^/]+)/', url)
    return match.group(1) if match else None

def search(page: Page, query: str):
    search_url = f"https://weebcentral.com/search?text={query}&sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
    page.goto(search_url)
    page.wait_for_load_state('networkidle')
    results = []
    
    # Use the correct selector for manga cards
    manga_articles = page.query_selector_all('article.bg-base-300')
    for article in manga_articles:
        try:
            # Get the left section (image and link)
            left_section = article.query_selector('section:first-child')
            if not left_section:
                continue
            
            # Get the main link
            card = left_section.query_selector('a[href*="/series/"]')
            if not card:
                continue
            link = card.get_attribute('href')
            manga_id = extract_manga_id_from_url(link) if link else None
            
            # Image extraction from left section
            image_url = None
            picture_elem = card.query_selector('picture')
            if picture_elem:
                source_elem = picture_elem.query_selector('source[type="image/webp"]')
                if source_elem:
                    image_url = source_elem.get_attribute('srcset')
                if not image_url:
                    img_elem = picture_elem.query_selector('img')
                    if img_elem:
                        image_url = img_elem.get_attribute('src')
            else:
                img_elem = card.query_selector('img')
                image_url = img_elem.get_attribute('src') if img_elem else None
            
            # Title extraction from left section
            title = None
            if picture_elem:
                img_elem = picture_elem.query_selector('img')
                if img_elem:
                    alt_text = img_elem.get_attribute('alt')
                    if alt_text:
                        title = alt_text.replace(' cover', '').replace(' Cover', '').strip()
            elif img_elem:
                alt_text = img_elem.get_attribute('alt')
                if alt_text:
                    title = alt_text.replace(' cover', '').replace(' Cover', '').strip()
            if not title:
                title_div = card.query_selector('div.text-ellipsis')
                if title_div:
                    title = title_div.inner_text().strip()
            if not title:
                title = link.split('/')[-1].replace('-', ' ').title() if link else "Unknown Title"
            
            # Get the right section (details)
            right_section = article.query_selector('section:last-child')
            
            # Author extraction from right section
            authors = []
            if right_section:
                author_links = right_section.query_selector_all('a[href*="/search?author="]')
                for link_elem in author_links:
                    href = link_elem.get_attribute('href')
                    if href and 'author=' in href:
                        author_part = href.split('author=')[1].split('&')[0]
                        author_name = author_part.replace('+', ' ')
                        if author_name:
                            authors.append(author_name)
            if not authors:
                authors = ["Unknown Author"]

            # Tags extraction from right section
            tags = []
            if right_section:
                tag_section = right_section.query_selector('div:has(strong:has-text("Tag(s):"))')
                if tag_section:
                    tag_spans = tag_section.query_selector_all('span')
                    for span in tag_spans:
                        tag_text = span.inner_text().strip()
                        if tag_text and tag_text != 'Tag(s):' and not tag_text.endswith(','):
                            tags.append(tag_text)

            # Status extraction from right section
            status = "Unknown"
            if right_section:
                status_section = right_section.query_selector('div:has(strong:has-text("Status:"))')
                if status_section:
                    status_span = status_section.query_selector('span')
                    if status_span:
                        status = status_span.inner_text().strip()

            # Year extraction from right section
            year = "Unknown"
            if right_section:
                year_section = right_section.query_selector('div:has(strong:has-text("Year:"))')
                if year_section:
                    year_span = year_section.query_selector('span')
                    if year_span:
                        year = year_span.inner_text().strip()

            # Chapter extraction (keeping existing logic for compatibility)
            chapter = ""
            if right_section:
                chapter_elem = right_section.query_selector('div:has(strong:has-text("Chapter:")), div:has(strong:has-text("Chapters:")) span')
            if chapter_elem:
                chapter = chapter_elem.inner_text().strip()
            
            results.append({
                'id': manga_id,
                'title': title,
                'status': status,
                'chapter': chapter,
                'image': image_url,
                'details_url': link,
                'source': 'weebcentral',
                'authors': authors,
                'tags': tags,
                'year': year
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
            # Wait for the specific Alpine.js section to be populated
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
    # Extract metadata from the structured list
    metadata_list = page.query_selector('ul.flex.flex-col.gap-4')
    
    # Initialize metadata fields
    author = ""
    status = ""
    tags = []
    manga_type = ""
    released_year = ""
    official_translation = ""
    anime_adaptation = ""
    adult_content = ""
    
    if metadata_list:
        # Get all list items
        list_items = metadata_list.query_selector_all('li')
        
        for item in list_items:
            # Get the strong element (label)
            strong_elem = item.query_selector('strong')
            if not strong_elem:
                continue
                
            label = strong_elem.inner_text().strip().lower()
            
            if 'author' in label:
                # Extract author from link or span
                author_link = item.query_selector('a.link.link-info.link-hover')
                if author_link:
                    author = author_link.inner_text().strip()
                else:
                    # Fallback to span content
                    author_span = item.query_selector('span')
                    if author_span:
                        author = author_span.inner_text().strip()
                        
            elif 'tag' in label:
                # Extract all tags
                tag_links = item.query_selector_all('a.link.link-info.link-hover')
                for tag_link in tag_links:
                    tag_text = tag_link.inner_text().strip()
                    if tag_text and tag_text != ',':
                        tags.append(tag_text)
                        
            elif 'type' in label:
                # Extract manga type
                type_link = item.query_selector('a.link.link-info.link-hover')
                if type_link:
                    manga_type = type_link.inner_text().strip()
                    
            elif 'status' in label:
                # Extract status
                status_link = item.query_selector('a.link.link-info.link-hover')
                if status_link:
                    status = status_link.inner_text().strip()
                    
            elif 'released' in label:
                # Extract release year
                released_span = item.query_selector('span')
                if released_span:
                    released_year = released_span.inner_text().strip()
                    
            elif 'official translation' in label:
                # Extract official translation status
                official_link = item.query_selector('a.link.link-info.link-hover')
                if official_link:
                    official_translation = official_link.inner_text().strip()
                    
            elif 'anime adaptation' in label:
                # Extract anime adaptation status
                anime_link = item.query_selector('a.link.link-info.link-hover')
                if anime_link:
                    anime_adaptation = anime_link.inner_text().strip()
                    
            elif 'adult content' in label:
                # Extract adult content status
                adult_link = item.query_selector('a.link.link-info.link-hover')
                if adult_link:
                    adult_content = adult_link.inner_text().strip()
    
    # Fallback to old methods if structured list not found
    if not author:
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
    
    if not status:
        status_elem = page.query_selector('.status, [data-testid="status"], .series-status, div:has-text("Status")')
        if status_elem:
            status = status_elem.inner_text().replace('Status', '').strip()
    
    # Set the extracted values
    details['author'] = author or "Unknown Author"
    details['status'] = status
    details['tags'] = tags
    details['type'] = manga_type
    details['released'] = released_year
    details['official_translation'] = official_translation
    details['anime_adaptation'] = anime_adaptation
    details['adult_content'] = adult_content
    details['id'] = manga_id
    details['url'] = manga_url
    details['source'] = 'weebcentral'
    # Chapters
    try:
        # Look for the specific Alpine.js section with mark_chapters data
        chapter_section = page.query_selector('section[x-data*="mark_chapters"]')
        
        if chapter_section:
            # Get all chapter links within the Alpine.js section
            chapter_links = chapter_section.query_selector_all('a[href*="/chapter"], a[href*="/read"], .chapter-link, [data-testid="chapter-link"]')
            
            if not chapter_links:
                # Try alternative selectors within the section
                chapter_links = chapter_section.query_selector_all('a[href*="chapter"], a[href*="read"], a')
            
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
            # Fallback to the old method if Alpine.js section not found
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

def scrape_all_manga(page: Page, max_pages=None, delay_between_clicks=2):
    """
    Scrape all manga from Weeb Central search page with pagination support.
    This is useful for preloading all manga data.
    """
    url = "https://weebcentral.com/search?sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
    page.goto(url)
    page.wait_for_load_state('networkidle')
    
    all_results = []
    seen_urls = set()
    page_num = 0

    while True:
        print(f"Scraping page {page_num + 1}...")
        
        # Use the same extraction logic as search function
        manga_articles = page.query_selector_all('article.bg-base-300')
        for article in manga_articles:
            try:
                # Get the left section (image and link)
                left_section = article.query_selector('section:first-child')
                if not left_section:
                    continue
                
                # Get the main link
                card = left_section.query_selector('a[href*="/series/"]')
                if not card:
                    continue
                link = card.get_attribute('href')
                manga_id = extract_manga_id_from_url(link) if link else None
                
                # Skip if we've already seen this manga
                if link in seen_urls:
                    continue
                seen_urls.add(link)
                
                # Image extraction from left section
                image_url = None
                picture_elem = card.query_selector('picture')
                if picture_elem:
                    source_elem = picture_elem.query_selector('source[type="image/webp"]')
                    if source_elem:
                        image_url = source_elem.get_attribute('srcset')
                    if not image_url:
                        img_elem = picture_elem.query_selector('img')
                        if img_elem:
                            image_url = img_elem.get_attribute('src')
                else:
                    img_elem = card.query_selector('img')
                    image_url = img_elem.get_attribute('src') if img_elem else None
                
                # Title extraction from left section
                title = None
                if picture_elem:
                    img_elem = picture_elem.query_selector('img')
                    if img_elem:
                        alt_text = img_elem.get_attribute('alt')
                        if alt_text:
                            title = alt_text.replace(' cover', '').replace(' Cover', '').strip()
                elif img_elem:
                    alt_text = img_elem.get_attribute('alt')
                    if alt_text:
                        title = alt_text.replace(' cover', '').replace(' Cover', '').strip()
                if not title:
                    title_div = card.query_selector('div.text-ellipsis')
                    if title_div:
                        title = title_div.inner_text().strip()
                if not title:
                    title = link.split('/')[-1].replace('-', ' ').title() if link else "Unknown Title"

                # Get the right section (details)
                right_section = article.query_selector('section:last-child')
                
                # Author extraction from right section
                authors = []
                if right_section:
                    author_links = right_section.query_selector_all('a[href*="/search?author="]')
                    for link_elem in author_links:
                        href = link_elem.get_attribute('href')
                        if href and 'author=' in href:
                            author_part = href.split('author=')[1].split('&')[0]
                            author_name = author_part.replace('+', ' ')
                            if author_name:
                                authors.append(author_name)
                if not authors:
                    authors = ["Unknown Author"]

                # Tags extraction from right section
                tags = []
                if right_section:
                    tag_section = right_section.query_selector('div:has(strong:has-text("Tag(s):"))')
                    if tag_section:
                        tag_spans = tag_section.query_selector_all('span')
                        for span in tag_spans:
                            tag_text = span.inner_text().strip()
                            if tag_text and tag_text != 'Tag(s):' and not tag_text.endswith(','):
                                tags.append(tag_text)

                # Status extraction from right section
                status = "Unknown"
                if right_section:
                    status_section = right_section.query_selector('div:has(strong:has-text("Status:"))')
                    if status_section:
                        status_span = status_section.query_selector('span')
                        if status_span:
                            status = status_span.inner_text().strip()

                # Year extraction from right section
                year = "Unknown"
                if right_section:
                    year_section = right_section.query_selector('div:has(strong:has-text("Year:"))')
                    if year_section:
                        year_span = year_section.query_selector('span')
                        if year_span:
                            year = year_span.inner_text().strip()

                # Chapter extraction
                chapter = ""
                if right_section:
                    chapter_elem = right_section.query_selector('div:has(strong:has-text("Chapter:")), div:has(strong:has-text("Chapters:")) span')
                    if chapter_elem:
                        chapter = chapter_elem.inner_text().strip()
                
                all_results.append({
                    'id': manga_id,
                    'title': title,
                    'status': status,
                    'chapter': chapter,
                    'image': image_url,
                    'details_url': link,
                    'source': 'weebcentral',
                    'authors': authors,
                    'tags': tags,
                    'year': year
                })
            except Exception as e:
                print(f"WeebCentral error: {e}")
                continue

        # Try to click "View More Results" for pagination
        try:
            view_more = page.query_selector('button:has-text("View More Results")')
            if not view_more or not view_more.is_enabled():
                print("No more 'View More Results' button found or enabled.")
                break  # No more results

            view_more.click()
            print("Clicked 'View More Results', waiting for new content...")
            
            # Wait for new content to load
            page.wait_for_timeout(delay_between_clicks * 1000)
            page.wait_for_load_state('networkidle')
            
            page_num += 1
            if max_pages and page_num >= max_pages:
                print(f"Reached max_pages limit: {max_pages}")
                break
        except Exception as e:
            print(f"Error clicking 'View More Results': {e}")
            break

    print(f"Total manga scraped: {len(all_results)}")
    return all_results

def preload_manga_details(page: Page, manga_list, delay_between_requests=1):
    """
    Preload detailed information for a list of manga from Weeb Central.
    This fetches the full details page for each manga including description, all chapters, etc.
    
    Args:
        page: Playwright page object
        manga_list: List of manga dictionaries with 'id' and 'details_url' fields
        delay_between_requests: Delay in seconds between requests to avoid rate limiting
    
    Returns:
        List of detailed manga information
    """
    detailed_manga = []
    
    for i, manga in enumerate(manga_list):
        try:
            print(f"Preloading details for {manga.get('title', f'manga {i+1}')} ({i+1}/{len(manga_list)})")
            
            # Get detailed information using existing get_details function
            manga_id = manga.get('id')
            if not manga_id:
                print(f"Skipping manga without ID: {manga.get('title', 'Unknown')}")
                continue
                
            details = get_details(page, manga_id)
            
            # Merge the search results with detailed information
            merged_manga = {**manga, **details}
            
            # Ensure we have all the fields we want
            merged_manga.update({
                'source': 'weebcentral',
                'preloaded_at': time.time(),
                'has_full_details': True
            })
            
            detailed_manga.append(merged_manga)
            
            # Add delay between requests to be respectful
            if i < len(manga_list) - 1:  # Don't delay after the last request
                time.sleep(delay_between_requests)
                
        except Exception as e:
            print(f"Error preloading details for {manga.get('title', 'Unknown')}: {e}")
            # Add the original manga data without details
            manga['has_full_details'] = False
            manga['preloaded_at'] = time.time()
            detailed_manga.append(manga)
            continue
    
    print(f"Successfully preloaded details for {len(detailed_manga)} manga")
    return detailed_manga

def preload_weebcentral_complete(max_pages=None, delay_between_clicks=2, delay_between_requests=1):
    """
    Complete preload function for Weeb Central that scrapes all manga and then fetches detailed information.
    This is a convenience function that combines scrape_all_manga and preload_manga_details.
    
    Args:
        max_pages: Maximum number of pages to scrape from search results
        delay_between_clicks: Delay between pagination clicks
        delay_between_requests: Delay between detail page requests
    
    Returns:
        List of complete manga information with full details
    """
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Step 1: Scrape all manga from search results
            print("Step 1: Scraping all manga from search results...")
            all_manga = scrape_all_manga(page, max_pages, delay_between_clicks)
            
            # Step 2: Preload detailed information for each manga
            print(f"Step 2: Preloading detailed information for {len(all_manga)} manga...")
            detailed_manga = preload_manga_details(page, all_manga, delay_between_requests)
            
            return detailed_manga
            
        finally:
            browser.close()

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