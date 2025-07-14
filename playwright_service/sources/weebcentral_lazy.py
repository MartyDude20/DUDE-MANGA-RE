from playwright.sync_api import Page
import re
import time
import logging
import json
from typing import Dict, List, Optional, Callable, Tuple
from flask import jsonify, request, Response
from flask import Blueprint
import urllib.parse

logger = logging.getLogger(__name__)

def extract_manga_id_from_url(url):
    """Extract manga ID from URL using regex"""
    match = re.search(r'/series/([^/]+)/', url)
    return match.group(1) if match else None

class LazyProgressCallback:
    """Progress callback system for lazy loading with web UI support"""
    
    def __init__(self, callback: Optional[Callable] = None, session_id: Optional[str] = None):
        self.callback = callback or self._default_callback
        self.session_id = session_id
        self.steps = []
        self.current_step = 0
        self.progress_data = {}
    
    def _default_callback(self, step: str, progress: float, message: str = ""):
        """Default progress callback"""
        logger.info(f"Progress: {step} - {progress:.1%} - {message}")
    
    def add_step(self, step: str):
        """Add a new step to track"""
        self.steps.append(step)
        self.progress_data[step] = {'progress': 0.0, 'message': ''}
    
    def update(self, step: str, progress: float, message: str = ""):
        """Update progress for a specific step"""
        self.progress_data[step] = {'progress': progress, 'message': message}
        self.callback(step, progress, message)
    
    def complete_step(self, step: str, message: str = ""):
        """Mark a step as complete"""
        self.update(step, 1.0, message)
    
    def get_progress_data(self):
        """Get current progress data for web UI"""
        return self.progress_data

def get_manga_details_lazy(page: Page, manga_id: str, progress_callback: Optional[LazyProgressCallback] = None):
    """Get manga details without loading all chapters (lazy loading)"""
    start_time = time.time()
    
    if progress_callback:
        progress_callback.add_step("details")
        progress_callback.update("details", 0.0, "Starting details extraction...")
    
    try:
        # Navigate to manga page
        manga_url = f"https://weebcentral.com/series/{manga_id}"
        
        if progress_callback:
            progress_callback.update("details", 0.1, "Navigating to manga page...")
        
        page.goto(manga_url, wait_until='domcontentloaded', timeout=10000)
        
        if progress_callback:
            progress_callback.update("details", 0.3, "Waiting for content to load...")
        
        page.wait_for_timeout(1000)
        
        details = {}
        
        if progress_callback:
            progress_callback.update("details", 0.4, "Extracting title...")
        
        # Extract title
        title_elem = page.query_selector('h1.text-2xl.font-bold')
        title = title_elem.inner_text().strip() if title_elem else "Unknown Title"
        details['title'] = title
        
        if progress_callback:
            progress_callback.update("details", 0.5, "Extracting image...")
        
        # Extract image
        image_url = None
        picture_elem = page.query_selector('picture')
        if picture_elem:
            source_elem = picture_elem.query_selector('source[type="image/webp"]')
            if source_elem:
                image_url = source_elem.get_attribute('srcset')
            
            if not image_url:
                img_elem = picture_elem.query_selector('img')
                if img_elem:
                    image_url = img_elem.get_attribute('src')
        
        details['image'] = image_url
        
        if progress_callback:
            progress_callback.update("details", 0.6, "Extracting description...")
        
        # Extract description
        desc_elem = page.query_selector('p.whitespace-pre-wrap.break-words')
        description = "No description available"
        if desc_elem:
            ps = desc_elem.query_selector_all('p')
            if ps:
                description = '\n'.join([p.inner_text().strip() for p in ps])
            else:
                description = desc_elem.inner_text().strip()
        
        details['description'] = description
        
        if progress_callback:
            progress_callback.update("details", 0.7, "Extracting metadata...")
        
        # Extract author and status
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
            progress_callback.update("details", 0.8, "Getting chapter count...")
        
        # Get total chapter count without loading all chapters
        total_chapters = get_chapter_count(page)
        details['total_chapters'] = total_chapters
        
        # Only load first 10 chapters for initial display
        if progress_callback:
            progress_callback.update("details", 0.9, "Loading initial chapters...")
        
        initial_chapters = get_chapters_paginated(page, 0, 10)
        details['chapters'] = initial_chapters
        details['has_more_chapters'] = total_chapters > 10
        
        details_time = time.time() - start_time
        
        if progress_callback:
            progress_callback.complete_step("details", f"Details extracted in {details_time:.2f}s")
        
        logger.info(f"WeebCentral lazy details completed in {details_time:.2f}s")
        
        return details
        
    except Exception as e:
        logger.error(f"WeebCentral lazy details failed: {e}")
        if progress_callback:
            progress_callback.update("details", 1.0, f"Details extraction failed: {e}")
        return {}

def get_chapter_count(page: Page) -> int:
    """Get total number of chapters without loading them all"""
    try:
        # Try to find chapter count in page text
        page_text = page.inner_text('body')
        
        # Look for patterns like "Chapter 123" or "123 Chapters"
        chapter_patterns = [
            r'Chapter\s+(\d+)',
            r'(\d+)\s+Chapters?',
            r'Total:\s*(\d+)\s*chapters?'
        ]
        
        max_chapter = 0
        for pattern in chapter_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                try:
                    chapter_num = int(match)
                    max_chapter = max(max_chapter, chapter_num)
                except ValueError:
                    continue
        
        # If we found chapters, return the highest number
        if max_chapter > 0:
            return max_chapter
        
        # Fallback: try to count chapter links without expanding
        chapter_links = page.query_selector_all('a[href*="/chapter"]')
        return len(chapter_links) if chapter_links else 0
        
    except Exception as e:
        logger.error(f"Error getting chapter count: {e}")
        return 0

def get_chapters_paginated(page: Page, offset: int = 0, limit: int = 10, progress_callback: Optional[LazyProgressCallback] = None) -> List[Dict]:
    """Get chapters with pagination support"""
    start_time = time.time()
    
    if progress_callback:
        progress_callback.add_step("chapters")
        progress_callback.update("chapters", 0.0, f"Loading chapters {offset+1}-{offset+limit}...")
    
    try:
        # Try to click "Show All Chapters" button if it exists
        show_all_btn = page.query_selector('button:has-text("Show All Chapters"), button:has-text("Show All")')
        if show_all_btn:
            show_all_btn.click()
            page.wait_for_timeout(1000)
        
        if progress_callback:
            progress_callback.update("chapters", 0.3, "Finding chapter container...")
        
        # Find chapter container
        chapter_container = page.query_selector('#chapter-list')
        
        if not chapter_container:
            if progress_callback:
                progress_callback.complete_step("chapters", "No chapters found")
            return []
        
        if progress_callback:
            progress_callback.update("chapters", 0.5, "Extracting chapter links...")
        
        # Get all chapter links
        chapter_links = chapter_container.query_selector_all('a[href*="/chapter"]')
        
        if progress_callback:
            progress_callback.update("chapters", 0.7, f"Processing {len(chapter_links)} chapters...")
        
        chapters = []
        for i, link in enumerate(chapter_links):
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
                chapter_progress = 0.7 + (0.3 * (i / len(chapter_links)))
                progress_callback.update("chapters", chapter_progress, f"Processed {i+1}/{len(chapter_links)} chapters")
        
        # Apply pagination
        start_idx = offset
        end_idx = offset + limit
        paginated_chapters = chapters[start_idx:end_idx]
        
        chapters_time = time.time() - start_time
        
        if progress_callback:
            progress_callback.complete_step("chapters", f"Loaded {len(paginated_chapters)} chapters in {chapters_time:.2f}s")
        
        return paginated_chapters
        
    except Exception as e:
        logger.error(f"Error loading chapters: {e}")
        if progress_callback:
            progress_callback.update("chapters", 1.0, f"Chapter loading failed: {e}")
        return []

def get_chapter_images_lazy(page: Page, chapter_url: str, progress_callback: Optional[LazyProgressCallback] = None):
    """Get chapter images with lazy loading support"""
    start_time = time.time()
    
    if progress_callback:
        progress_callback.add_step("images")
        progress_callback.update("images", 0.0, "Starting image extraction...")
    
    try:
        if progress_callback:
            progress_callback.update("images", 0.2, "Navigating to chapter page...")
        
        page.goto(chapter_url, wait_until='domcontentloaded', timeout=10000)
        
        if progress_callback:
            progress_callback.update("images", 0.4, "Waiting for images to load...")
        
        page.wait_for_timeout(1500)
        
        if progress_callback:
            progress_callback.update("images", 0.6, "Extracting image URLs...")
        
        # Optimized image selectors
        image_selectors = [
            '.manga-page img',
            '.reader-page img',
            'img[alt*="Page"]',
            'img[data-src]',
            'img[src*="chapter"]',
            'img'
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
        
        logger.info(f"WeebCentral lazy chapter images completed in {chapter_time:.2f}s - Found {len(images)} images")
        
        return images
        
    except Exception as e:
        logger.error(f"WeebCentral lazy chapter images failed: {e}")
        if progress_callback:
            progress_callback.update("images", 1.0, f"Image extraction failed: {e}")
        return []

# Flask Blueprint for lazy loading endpoints
weebcentral_lazy_bp = Blueprint('weebcentral_lazy_bp', __name__)

# Global progress storage for web UI
progress_storage = {}

@weebcentral_lazy_bp.route('/manga/<manga_id>/details', methods=['GET'])
def get_manga_details_endpoint(manga_id):
    """Get manga details with lazy loading"""
    from playwright.sync_api import sync_playwright
    
    session_id = request.args.get('session_id', 'default')
    progress_callback = LazyProgressCallback(session_id=session_id)
    progress_storage[session_id] = progress_callback
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            details = get_manga_details_lazy(page, manga_id, progress_callback)
            
            browser.close()
            
            if details:
                return jsonify(details)
            else:
                return jsonify({'error': 'Manga not found'}), 404
                
    except Exception as e:
        return jsonify({'error': f'Failed to fetch manga details: {str(e)}'}), 500
    finally:
        # Clean up progress storage
        if session_id in progress_storage:
            del progress_storage[session_id]

@weebcentral_lazy_bp.route('/manga/<manga_id>/chapters', methods=['GET'])
def get_chapters_endpoint(manga_id):
    """Get chapters with pagination"""
    from playwright.sync_api import sync_playwright
    
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    session_id = request.args.get('session_id', 'default')
    
    progress_callback = LazyProgressCallback(session_id=session_id)
    progress_storage[session_id] = progress_callback
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate to manga page first
            manga_url = f"https://weebcentral.com/series/{manga_id}"
            page.goto(manga_url, wait_until='domcontentloaded', timeout=10000)
            page.wait_for_timeout(1000)
            
            chapters = get_chapters_paginated(page, offset, limit, progress_callback)
            
            browser.close()
            
            return jsonify({
                'chapters': chapters,
                'offset': offset,
                'limit': limit,
                'has_more': len(chapters) == limit
            })
                
    except Exception as e:
        return jsonify({'error': f'Failed to fetch chapters: {str(e)}'}), 500
    finally:
        # Clean up progress storage
        if session_id in progress_storage:
            del progress_storage[session_id]

@weebcentral_lazy_bp.route('/chapter-images/<path:chapter_url>', methods=['GET'])
def get_chapter_images_endpoint(chapter_url):
    """Get chapter images with lazy loading"""
    from playwright.sync_api import sync_playwright
    
    session_id = request.args.get('session_id', 'default')
    progress_callback = LazyProgressCallback(session_id=session_id)
    progress_storage[session_id] = progress_callback
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Decode the URL if it's URL-encoded
            decoded_url = urllib.parse.unquote(chapter_url)
            images = get_chapter_images_lazy(page, decoded_url, progress_callback)
            
            browser.close()
            
            return jsonify({'images': images})
                
    except Exception as e:
        return jsonify({'error': f'Failed to fetch chapter images: {str(e)}'}), 500
    finally:
        # Clean up progress storage
        if session_id in progress_storage:
            del progress_storage[session_id]

@weebcentral_lazy_bp.route('/progress/<session_id>', methods=['GET'])
def get_progress_endpoint(session_id):
    """Get progress updates for web UI"""
    if session_id in progress_storage:
        progress_data = progress_storage[session_id].get_progress_data()
        return jsonify(progress_data)
    else:
        return jsonify({'error': 'Session not found'}), 404

# Performance monitoring
def get_performance_metrics():
    """Get performance metrics for monitoring"""
    return {
        'details_timeout': 10000,
        'chapters_timeout': 10000,
        'images_timeout': 10000,
        'details_wait_time': 1000,
        'chapters_wait_time': 1000,
        'images_wait_time': 1500,
        'default_chapter_limit': 10,
        'max_chapter_limit': 50,
    } 