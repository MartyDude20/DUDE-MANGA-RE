from playwright.sync_api import Page
import re
import time
import logging

logger = logging.getLogger(__name__)

def extract_manga_id_from_url(url):
    """Extract manga ID from URL using regex"""
    match = re.search(r'/series/([^/]+)/', url)
    return match.group(1) if match else None

def search(page: Page, query: str):
    """Optimized search with fastest selectors"""
    start_time = time.time()
    
    try:
        # Navigate to search page
        search_url = f"https://weebcentral.com/search?text={query}&sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
        page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
        
        # Wait for content to load (reduced wait time)
        page.wait_for_timeout(2000)
        
        results = []
        
        # FASTEST: Use direct class selector for manga items
        manga_items = page.query_selector_all('section.w-full')
        
        if not manga_items:
            # Fallback: try alternative selectors
            manga_items = page.query_selector_all('.manga-item, .search-result, [data-testid="manga-item"]')
        
        logger.debug(f"Found {len(manga_items)} manga items")
        
        for item in manga_items[:20]:  # Limit to 20 results for speed
            try:
                # FAST: Direct link selector
                link_elem = item.query_selector('a[href*="/series/"]')
                if not link_elem:
                    continue
                
                href = link_elem.get_attribute('href')
                manga_id = extract_manga_id_from_url(href) if href else None
                
                # FAST: Optimized image extraction with fallback chain
                image_url = None
                
                # Try picture element first (common for modern sites)
                picture_elem = item.query_selector('picture')
                if picture_elem:
                    # Try webp source first (better quality)
                    source_elem = picture_elem.query_selector('source[type="image/webp"]')
                    if source_elem:
                        image_url = source_elem.get_attribute('srcset')
                    
                    # Fallback to img tag
                    if not image_url:
                        img_elem = picture_elem.query_selector('img')
                        if img_elem:
                            image_url = img_elem.get_attribute('src')
                else:
                    # Direct img tag fallback
                    img_elem = item.query_selector('img')
                    image_url = img_elem.get_attribute('src') if img_elem else None
                
                # FAST: Optimized title extraction with fallback chain
                title = None
                
                # Try alt attribute first (fastest)
                if picture_elem:
                    img_elem = picture_elem.query_selector('img')
                    if img_elem:
                        alt_text = img_elem.get_attribute('alt')
                        if alt_text:
                            title = alt_text.replace(' cover', '').replace(' Cover', '').strip()
                
                # Fallback to text element
                if not title:
                    title_elem = item.query_selector('.text-ellipsis, .title, h3, [data-testid="title"]')
                    if title_elem:
                        title = title_elem.inner_text().strip()
                
                # Final fallback to URL-based title
                if not title and href:
                    title = href.split('/')[-1].replace('-', ' ').title()
                
                # FAST: Direct status and chapter selectors
                status = ""
                status_elem = item.query_selector('span:has-text("Status:"), .status, [data-testid="status"]')
                if status_elem:
                    status = status_elem.inner_text().strip()
                
                chapter = ""
                chapter_elem = item.query_selector('span:has-text("Chapter:"), .chapter, [data-testid="chapter"]')
                if chapter_elem:
                    chapter = chapter_elem.inner_text().strip()
                
                if title and manga_id:
                    results.append({
                        'id': manga_id,
                        'title': title,
                        'status': status,
                        'chapter': chapter,
                        'image': image_url,
                        'details_url': href,
                        'source': 'weebcentral'
                    })
                    
            except Exception as e:
                logger.debug(f"Error extracting manga element: {e}")
                continue
        
        search_time = time.time() - start_time
        logger.info(f"WeebCentral search completed in {search_time:.2f}s - Found {len(results)} results")
        
        return results
        
    except Exception as e:
        logger.error(f"WeebCentral search failed: {e}")
        return []

def get_details(page: Page, manga_id: str):
    """Optimized manga details extraction with fastest selectors"""
    start_time = time.time()
    
    try:
        # Navigate to manga page
        manga_url = f"https://weebcentral.com/series/{manga_id}"
        page.goto(manga_url, wait_until='domcontentloaded', timeout=15000)
        
        # Wait for content
        page.wait_for_timeout(2000)
        
        details = {}
        
        # FAST: Optimized title extraction with fallback chain
        title_selectors = [
            'h1.text-2xl.font-bold',      # Specific class
            'h1.series-title',            # Specific class
            '[data-testid="series-title"]', # Data attribute
            'h1',                         # Simple tag
            '[data-title]'                # Generic data attribute
        ]
        
        title = "Unknown Title"
        for selector in title_selectors:
            title_elem = page.query_selector(selector)
            if title_elem:
                title = title_elem.inner_text().strip()
                break
        
        details['title'] = title
        
        # FAST: Optimized image extraction
        image_url = None
        picture_elem = page.query_selector('picture')
        if picture_elem:
            # Try webp source first
            source_elem = picture_elem.query_selector('source[type="image/webp"]')
            if source_elem:
                image_url = source_elem.get_attribute('srcset')
            
            # Fallback to img tag
            if not image_url:
                img_elem = picture_elem.query_selector('img')
                if img_elem:
                    image_url = img_elem.get_attribute('src')
        else:
            # Direct img fallback
            img_elem = page.query_selector('img')
            image_url = img_elem.get_attribute('src') if img_elem else None
        
        details['image'] = image_url
        
        # FAST: Optimized description extraction
        desc_selectors = [
            'p.whitespace-pre-wrap.break-words',  # Specific class
            '.description',                       # Class
            '.synopsis',                          # Class
            '[data-testid="description"]',        # Data attribute
            'p.description'                       # Tag + class
        ]
        
        description = "No description available"
        for selector in desc_selectors:
            desc_elem = page.query_selector(selector)
            if desc_elem:
                # Join all <p> children as paragraphs
                ps = desc_elem.query_selector_all('p')
                if ps:
                    description = '\n'.join([p.inner_text().strip() for p in ps])
                else:
                    description = desc_elem.inner_text().strip()
                break
        
        details['description'] = description
        
        # FAST: Optimized author extraction
        author_selectors = [
            '.author',                    # Class
            '.creator',                   # Class
            '[data-testid="author"]',     # Data attribute
            '.series-author'              # Class
        ]
        
        author = "Unknown Author"
        for selector in author_selectors:
            author_elem = page.query_selector(selector)
            if author_elem:
                author = author_elem.inner_text().strip()
                break
        
        details['author'] = author
        
        # FAST: Optimized status extraction
        status_selectors = [
            '.status',                    # Class
            '[data-testid="status"]',     # Data attribute
            '.series-status'              # Class
        ]
        
        status = ""
        for selector in status_selectors:
            status_elem = page.query_selector(selector)
            if status_elem:
                status = status_elem.inner_text().replace('Status', '').strip()
                break
        
        details['status'] = status
        details['id'] = manga_id
        details['url'] = manga_url
        details['source'] = 'weebcentral'
        
        # FAST: Optimized chapter extraction
        chapters = []
        try:
            # Try to click "Show All Chapters" button
            show_all_btn = page.query_selector('button:has-text("Show All Chapters"), button:has-text("Show All")')
            if show_all_btn:
                show_all_btn.click()
                page.wait_for_timeout(2000)
            
            # FAST: Direct chapter container selector
            chapter_container = page.query_selector('#chapter-list, .chapter-list, [data-testid="chapter-list"]')
            
            if chapter_container:
                # FAST: Direct chapter link selectors
                chapter_links = chapter_container.query_selector_all('a[href*="/chapter"], a[href*="/read"]')
                
                for link in chapter_links[:50]:  # Limit to 50 chapters for speed
                    href = link.get_attribute('href')
                    text = link.inner_text().strip()
                    
                    if href and text:
                        chapter_text = text.replace('Chapter', '').strip()
                        if chapter_text:
                            full_url = href if href.startswith('http') else f"https://weebcentral.com{href}"
                            chapters.append({
                                'title': f"Chapter {chapter_text}",
                                'url': full_url
                            })
            
            details['chapters'] = chapters
            
        except Exception as e:
            logger.debug(f"Chapter extraction failed: {e}")
            details['chapters'] = []
        
        details_time = time.time() - start_time
        logger.info(f"WeebCentral details completed in {details_time:.2f}s")
        
        return details
        
    except Exception as e:
        logger.error(f"WeebCentral details failed: {e}")
        return {}

def get_chapter_images(page: Page, chapter_url: str):
    """Optimized chapter image extraction with fastest selectors"""
    start_time = time.time()
    
    try:
        # Navigate to chapter page
        page.goto(chapter_url, wait_until='domcontentloaded', timeout=15000)
        
        # Wait for images to load
        page.wait_for_timeout(3000)
        
        # FAST: Optimized image selectors with fallback chain
        image_selectors = [
            '.manga-page img',            # Class + tag
            '.reader-page img',           # Class + tag
            'img[alt*="Page"]',           # Tag + attribute
            'img[data-src]',              # Tag + attribute
            'img[src*="chapter"]',        # Tag + attribute
            'img'                         # Simple tag
        ]
        
        images = []
        for selector in image_selectors:
            img_elements = page.query_selector_all(selector)
            if img_elements:
                for img in img_elements:
                    src = img.get_attribute('src') or img.get_attribute('data-src')
                    if src and src.startswith('http'):
                        images.append(src)
                break
        
        chapter_time = time.time() - start_time
        logger.info(f"WeebCentral chapter images completed in {chapter_time:.2f}s - Found {len(images)} images")
        
        return images
        
    except Exception as e:
        logger.error(f"WeebCentral chapter images failed: {e}")
        return []

# Performance comparison function
def compare_selector_performance(page: Page, selectors, iterations=100):
    """Compare performance of different selectors"""
    results = {}
    
    for selector in selectors:
        start_time = time.time()
        
        for _ in range(iterations):
            page.query_selector(selector)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations * 1000  # Convert to milliseconds
        results[selector] = avg_time
    
    # Sort by speed (fastest first)
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    
    print("Selector Performance Comparison (ms per query):")
    for selector, time_ms in sorted_results:
        print(f"  {selector}: {time_ms:.3f}ms")
    
    return sorted_results 