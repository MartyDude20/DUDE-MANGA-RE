import time
import logging
from typing import List, Dict
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

def search(page: Page, query: str) -> List[Dict]:
    """Optimized search for WeebCentral with performance improvements"""
    start_time = time.time()
    
    try:
        # Optimize page settings for speed
        page.set_viewport_size({"width": 1280, "height": 720})
        
        # Block unnecessary resources
        page.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2,ttf,eot}", lambda route: route.abort())
        page.route("**/*.css", lambda route: route.abort())
        page.route("**/ads/**", lambda route: route.abort())
        page.route("**/analytics/**", lambda route: route.abort())
        
        # Navigate to search page
        search_url = f"https://weebcentral.com/search?q={query}"
        page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
        
        # Wait for content to load (reduced wait time)
        page.wait_for_timeout(2000)
        
        # Extract manga results with optimized selectors
        results = []
        
        # Try multiple selectors for better reliability
        selectors = [
            '.manga-item',
            '.search-result',
            '.manga-card',
            '[data-testid="manga-item"]',
            '.item'
        ]
        
        manga_elements = []
        for selector in selectors:
            manga_elements = page.query_selector_all(selector)
            if manga_elements:
                logger.debug(f"Found {len(manga_elements)} manga using selector: {selector}")
                break
        
        if not manga_elements:
            # Fallback: look for any elements with manga-like structure
            manga_elements = page.query_selector_all('a[href*="/series/"]')
        
        for element in manga_elements[:20]:  # Limit to 20 results for speed
            try:
                # Extract title
                title_element = element.query_selector('h3, .title, .manga-title, [data-testid="title"]')
                title = title_element.inner_text().strip() if title_element else "Unknown Title"
                
                # Extract link
                link_element = element if element.evaluate('el => el.tagName.toLowerCase()') == 'a' else element.query_selector('a')
                href = link_element.get_attribute('href') if link_element else None
                
                if not href:
                    continue
                
                # Extract manga ID from URL
                manga_id = href.split('/')[-1] if href else None
                
                # Extract image (with fallback)
                img_element = element.query_selector('img')
                image_url = img_element.get_attribute('src') if img_element else None
                
                # Extract status
                status_element = element.query_selector('.status, .manga-status, [data-testid="status"]')
                status = status_element.inner_text().strip() if status_element else "Unknown"
                
                # Extract chapter info
                chapter_element = element.query_selector('.chapter, .manga-chapter, [data-testid="chapter"]')
                chapter = chapter_element.inner_text().strip() if chapter_element else None
                
                if title and manga_id:
                    results.append({
                        'id': manga_id,
                        'title': title,
                        'image': image_url,
                        'url': f"https://weebcentral.com{href}" if href.startswith('/') else href,
                        'status': status,
                        'chapter': chapter,
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

def get_details(page: Page, manga_id: str) -> Dict:
    """Optimized manga details extraction"""
    start_time = time.time()
    
    try:
        # Block unnecessary resources
        page.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2,ttf,eot}", lambda route: route.abort())
        page.route("**/*.css", lambda route: route.abort())
        page.route("**/ads/**", lambda route: route.abort())
        
        # Navigate to manga page
        manga_url = f"https://weebcentral.com/series/{manga_id}"
        page.goto(manga_url, wait_until='domcontentloaded', timeout=15000)
        
        # Wait for content
        page.wait_for_timeout(2000)
        
        # Extract manga details
        title = "Unknown Title"
        description = ""
        author = "Unknown"
        image_url = None
        chapters = []
        
        # Extract title
        title_selectors = ['h1', '.manga-title', '.title', '[data-testid="title"]']
        for selector in title_selectors:
            title_element = page.query_selector(selector)
            if title_element:
                title = title_element.inner_text().strip()
                break
        
        # Extract description
        desc_selectors = ['.description', '.manga-description', '.synopsis', '[data-testid="description"]']
        for selector in desc_selectors:
            desc_element = page.query_selector(selector)
            if desc_element:
                description = desc_element.inner_text().strip()
                break
        
        # Extract author
        author_selectors = ['.author', '.manga-author', '[data-testid="author"]']
        for selector in author_selectors:
            author_element = page.query_selector(selector)
            if author_element:
                author = author_element.inner_text().strip()
                break
        
        # Extract image
        img_selectors = ['.manga-cover img', '.cover img', 'img[alt*="cover"]']
        for selector in img_selectors:
            img_element = page.query_selector(selector)
            if img_element:
                image_url = img_element.get_attribute('src')
                break
        
        # Extract chapters (limited for speed)
        chapter_selectors = [
            '.chapter-item',
            '.chapter',
            '[data-testid="chapter"]',
            'a[href*="/chapter/"]'
        ]
        
        chapter_elements = []
        for selector in chapter_selectors:
            chapter_elements = page.query_selector_all(selector)
            if chapter_elements:
                break
        
        for element in chapter_elements[:50]:  # Limit to 50 chapters
            try:
                chapter_title = element.inner_text().strip()
                chapter_url = element.get_attribute('href') if element.evaluate('el => el.tagName.toLowerCase()') == 'a' else None
                
                if chapter_title and chapter_url:
                    chapters.append({
                        'title': chapter_title,
                        'url': f"https://weebcentral.com{chapter_url}" if chapter_url.startswith('/') else chapter_url
                    })
            except Exception as e:
                logger.debug(f"Error extracting chapter: {e}")
                continue
        
        details_time = time.time() - start_time
        logger.info(f"WeebCentral details completed in {details_time:.2f}s")
        
        return {
            'id': manga_id,
            'title': title,
            'description': description,
            'author': author,
            'image': image_url,
            'url': manga_url,
            'chapters': chapters,
            'source': 'weebcentral'
        }
        
    except Exception as e:
        logger.error(f"WeebCentral details failed: {e}")
        return {}

def get_chapter_images(page: Page, chapter_url: str) -> List[str]:
    """Optimized chapter image extraction"""
    start_time = time.time()
    
    try:
        # Navigate to chapter page
        page.goto(chapter_url, wait_until='domcontentloaded', timeout=15000)
        
        # Wait for images to load
        page.wait_for_timeout(3000)
        
        # Extract image URLs
        image_selectors = [
            '.manga-page img',
            '.reader-page img',
            'img[alt*="Page"]',
            'img[data-src]',
            'img[src*="chapter"]'
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