from playwright.sync_api import Page
import re
import time
import logging
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

def extract_manga_id_from_url(url):
    """Extract manga ID from URL using regex"""
    match = re.search(r'/series/([^/]+)/', url)
    return match.group(1) if match else None

class ProgressCallback:
    """Progress callback system for real-time updates"""
    
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback or self._default_callback
        self.steps = []
        self.current_step = 0
    
    def _default_callback(self, step: str, progress: float, message: str = ""):
        """Default progress callback"""
        logger.info(f"Progress: {step} - {progress:.1%} - {message}")
    
    def add_step(self, step: str):
        """Add a new step to track"""
        self.steps.append(step)
    
    def update(self, step: str, progress: float, message: str = ""):
        """Update progress for a specific step"""
        self.callback(step, progress, message)
    
    def complete_step(self, step: str, message: str = ""):
        """Mark a step as complete"""
        self.update(step, 1.0, message)

def search(page: Page, query: str, progress_callback: Optional[ProgressCallback] = None):
    """Optimized search with progress indicators"""
    start_time = time.time()
    
    if progress_callback:
        progress_callback.add_step("search")
        progress_callback.update("search", 0.0, "Starting search...")
    
    try:
        # Navigate to search page
        search_url = f"https://weebcentral.com/search?text={query}&sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
        
        if progress_callback:
            progress_callback.update("search", 0.2, "Navigating to search page...")
        
        page.goto(search_url, wait_until='domcontentloaded', timeout=10000)  # Reduced timeout
        
        if progress_callback:
            progress_callback.update("search", 0.4, "Waiting for content to load...")
        
        # Reduced wait time for faster loading
        page.wait_for_timeout(1000)  # Reduced from 2000ms
        
        if progress_callback:
            progress_callback.update("search", 0.6, "Extracting search results...")
        
        results = []
        
        # OPTIMIZED: Use only the working selector from our analysis
        manga_items = page.query_selector_all('section.w-full')
        
        if not manga_items:
            # Fallback: try alternative selectors
            manga_items = page.query_selector_all('.manga-item, .search-result, [data-testid="manga-item"]')
        
        if progress_callback:
            progress_callback.update("search", 0.8, f"Processing {len(manga_items)} results...")
        
        logger.debug(f"Found {len(manga_items)} manga items")
        
        for i, item in enumerate(manga_items[:20]):  # Limit to 20 results for speed
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
        
        if progress_callback:
            progress_callback.complete_step("search", f"Found {len(results)} results in {search_time:.2f}s")
        
        logger.info(f"WeebCentral search completed in {search_time:.2f}s - Found {len(results)} results")
        
        return results
        
    except Exception as e:
        logger.error(f"WeebCentral search failed: {e}")
        if progress_callback:
            progress_callback.update("search", 1.0, f"Search failed: {e}")
        return []

def get_details(page: Page, manga_id: str, progress_callback: Optional[ProgressCallback] = None):
    """Optimized manga details extraction with progress indicators"""
    start_time = time.time()
    
    if progress_callback:
        progress_callback.add_step("details")
        progress_callback.update("details", 0.0, "Starting details extraction...")
    
    try:
        # Navigate to manga page
        manga_url = f"https://weebcentral.com/series/{manga_id}"
        
        if progress_callback:
            progress_callback.update("details", 0.1, "Navigating to manga page...")
        
        page.goto(manga_url, wait_until='domcontentloaded', timeout=10000)  # Reduced timeout
        
        if progress_callback:
            progress_callback.update("details", 0.3, "Waiting for content to load...")
        
        # Reduced wait time for faster loading
        page.wait_for_timeout(1000)  # Reduced from 2000ms
        
        details = {}
        
        if progress_callback:
            progress_callback.update("details", 0.4, "Extracting title...")
        
        # OPTIMIZED: Use only the working selector from our analysis
        title_elem = page.query_selector('h1.text-2xl.font-bold')
        title = title_elem.inner_text().strip() if title_elem else "Unknown Title"
        details['title'] = title
        
        if progress_callback:
            progress_callback.update("details", 0.5, "Extracting image...")
        
        # OPTIMIZED: Use only the working selector from our analysis
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
        
        details['image'] = image_url
        
        if progress_callback:
            progress_callback.update("details", 0.6, "Extracting description...")
        
        # OPTIMIZED: Use only the working selector from our analysis
        desc_elem = page.query_selector('p.whitespace-pre-wrap.break-words')
        description = "No description available"
        if desc_elem:
            # Join all <p> children as paragraphs
            ps = desc_elem.query_selector_all('p')
            if ps:
                description = '\n'.join([p.inner_text().strip() for p in ps])
            else:
                description = desc_elem.inner_text().strip()
        
        details['description'] = description
        
        if progress_callback:
            progress_callback.update("details", 0.7, "Extracting author and status...")
        
        # INVESTIGATE: Try alternative selectors for author and status
        author = "Unknown Author"
        author_selectors = [
            'span:has-text("Author")',
            'div:has-text("Creator")',
            '[data-author]',
            'meta[name="author"]'
        ]
        
        for selector in author_selectors:
            try:
                author_elem = page.query_selector(selector)
                if author_elem:
                    author = author_elem.inner_text().strip()
                    break
            except:
                continue
        
        details['author'] = author
        
        # INVESTIGATE: Try alternative selectors for status
        status = ""
        status_selectors = [
            'span:has-text("Status")',
            'div:has-text("Ongoing")',
            'div:has-text("Completed")',
            '[data-status]'
        ]
        
        for selector in status_selectors:
            try:
                status_elem = page.query_selector(selector)
                if status_elem:
                    status = status_elem.inner_text().strip()
                    break
            except:
                continue
        
        details['status'] = status
        details['id'] = manga_id
        details['url'] = manga_url
        details['source'] = 'weebcentral'
        
        if progress_callback:
            progress_callback.update("details", 0.8, "Extracting chapters...")
        
        # OPTIMIZED: Chapter extraction with progress
        chapters = []
        try:
            # Try to click "Show All Chapters" button
            show_all_btn = page.query_selector('button:has-text("Show All Chapters"), button:has-text("Show All")')
            if show_all_btn:
                show_all_btn.click()
                page.wait_for_timeout(1000)  # Reduced wait time
            
            # OPTIMIZED: Use only the working selector from our analysis
            chapter_container = page.query_selector('#chapter-list')
            
            if chapter_container:
                # OPTIMIZED: Direct chapter link selectors
                chapter_links = chapter_container.query_selector_all('a[href*="/chapter"]')
                
                if progress_callback:
                    progress_callback.update("details", 0.9, f"Processing {len(chapter_links)} chapters...")
                
                for i, link in enumerate(chapter_links[:50]):  # Limit to 50 chapters for speed
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
                    
                    # Update progress for chapter processing
                    if progress_callback and len(chapter_links) > 0:
                        chapter_progress = 0.9 + (0.1 * (i / len(chapter_links)))
                        progress_callback.update("details", chapter_progress, f"Processed {i+1}/{len(chapter_links)} chapters")
            
            details['chapters'] = chapters
            
        except Exception as e:
            logger.debug(f"Chapter extraction failed: {e}")
            details['chapters'] = []
        
        details_time = time.time() - start_time
        
        if progress_callback:
            progress_callback.complete_step("details", f"Details extracted in {details_time:.2f}s")
        
        logger.info(f"WeebCentral details completed in {details_time:.2f}s")
        
        return details
        
    except Exception as e:
        logger.error(f"WeebCentral details failed: {e}")
        if progress_callback:
            progress_callback.update("details", 1.0, f"Details extraction failed: {e}")
        return {}

def get_chapter_images(page: Page, chapter_url: str, progress_callback: Optional[ProgressCallback] = None):
    """Optimized chapter image extraction with progress indicators"""
    start_time = time.time()
    
    if progress_callback:
        progress_callback.add_step("images")
        progress_callback.update("images", 0.0, "Starting image extraction...")
    
    try:
        # Navigate to chapter page
        if progress_callback:
            progress_callback.update("images", 0.2, "Navigating to chapter page...")
        
        page.goto(chapter_url, wait_until='domcontentloaded', timeout=10000)  # Reduced timeout
        
        if progress_callback:
            progress_callback.update("images", 0.4, "Waiting for images to load...")
        
        # Reduced wait time for faster loading
        page.wait_for_timeout(1500)  # Reduced from 3000ms
        
        if progress_callback:
            progress_callback.update("images", 0.6, "Extracting image URLs...")
        
        # OPTIMIZED: Use only the working selectors from our analysis
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
                if progress_callback:
                    progress_callback.update("images", 0.8, f"Processing {len(img_elements)} images...")
                
                for i, img in enumerate(img_elements):
                    src = img.get_attribute('src') or img.get_attribute('data-src')
                    if src and src.startswith('http'):
                        images.append(src)
                    
                    # Update progress for image processing
                    if progress_callback and len(img_elements) > 0:
                        image_progress = 0.8 + (0.2 * (i / len(img_elements)))
                        progress_callback.update("images", image_progress, f"Processed {i+1}/{len(img_elements)} images")
                break
        
        chapter_time = time.time() - start_time
        
        if progress_callback:
            progress_callback.complete_step("images", f"Found {len(images)} images in {chapter_time:.2f}s")
        
        logger.info(f"WeebCentral chapter images completed in {chapter_time:.2f}s - Found {len(images)} images")
        
        return images
        
    except Exception as e:
        logger.error(f"WeebCentral chapter images failed: {e}")
        if progress_callback:
            progress_callback.update("images", 1.0, f"Image extraction failed: {e}")
        return []

# Performance monitoring
def get_performance_metrics():
    """Get performance metrics for monitoring"""
    return {
        'search_timeout': 10000,  # Reduced from 15000
        'details_timeout': 10000,  # Reduced from 15000
        'search_wait_time': 1000,  # Reduced from 2000
        'details_wait_time': 1000,  # Reduced from 2000
        'chapter_wait_time': 1500,  # Reduced from 3000
        'max_results': 20,  # Limited for speed
        'max_chapters': 50,  # Limited for speed
    } 