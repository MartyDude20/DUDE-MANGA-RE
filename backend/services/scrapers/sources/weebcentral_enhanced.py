from playwright.sync_api import Page, sync_playwright
import re
from flask import Blueprint, jsonify, request
import time
import urllib.parse
from typing import List, Dict, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_manga_id_from_url(url):
    """Extract manga ID from weebcentral URL"""
    match = re.search(r'/series/([^/]+)/', url)
    return match.group(1) if match else None

def extract_chapter_id_from_url(url):
    """Extract chapter ID from weebcentral chapter URL"""
    match = re.search(r'/chapters/([^/]+)', url)
    return match.group(1) if match else None

def get_chapter_images_enhanced(page: Page, chapter_url: str, timeout: int = 30000) -> Tuple[List[str], Dict]:
    """
    Enhanced chapter images extraction with better error handling and performance
    
    Args:
        page: Playwright page object
        chapter_url: URL of the chapter page
        timeout: Timeout in milliseconds for page operations
    
    Returns:
        Tuple of (images_list, metadata_dict)
    """
    start_time = time.time()
    images = []
    metadata = {
        'chapter_url': chapter_url,
        'extraction_time': 0,
        'image_count': 0,
        'errors': [],
        'warnings': [],
        'page_title': '',
        'chapter_title': '',
        'manga_title': ''
    }
    
    try:
        logger.info(f"WeebCentral: Loading chapter images from {chapter_url}")
        
        # Navigate to the chapter page
        page.goto(chapter_url, timeout=timeout)
        page.wait_for_load_state('networkidle', timeout=timeout)
        
        # Get page metadata
        page_title = page.title()
        metadata['page_title'] = page_title
        
        # Extract chapter and manga titles from page
        try:
            # Look for chapter title in various locations
            chapter_title_elem = page.query_selector('h1, .chapter-title, [data-testid="chapter-title"]')
            if chapter_title_elem:
                metadata['chapter_title'] = chapter_title_elem.inner_text().strip()
            
            # Look for manga title
            manga_title_elem = page.query_selector('.manga-title, .series-title, [data-testid="series-title"]')
            if manga_title_elem:
                metadata['manga_title'] = manga_title_elem.inner_text().strip()
        except Exception as e:
            metadata['warnings'].append(f"Could not extract titles: {e}")
        
        # Wait for images to load with progressive timeout
        logger.info("Waiting for images to load...")
        
        # First, wait for any image to appear
        try:
            page.wait_for_selector('img', timeout=10000)
        except Exception as e:
            metadata['warnings'].append(f"No images found initially: {e}")
        
        # Additional wait for dynamic content
        page.wait_for_timeout(2000)
        
        # Try multiple strategies to find images
        image_strategies = [
            # Strategy 1: Images with "Page" in alt text
            'img[alt*="Page"], img[alt*="page"]',
            # Strategy 2: Images in manga reader containers
            '.manga-page img, .reader-page img, [data-testid="manga-page"] img',
            # Strategy 3: Images in specific reader layouts
            '.reader-container img, .chapter-images img',
            # Strategy 4: All images (fallback)
            'img'
        ]
        
        for i, strategy in enumerate(image_strategies):
            try:
                img_elements = page.query_selector_all(strategy)
                logger.info(f"Strategy {i+1}: Found {len(img_elements)} images with selector '{strategy}'")
                
                if img_elements:
                    for img in img_elements:
                        try:
                            src = img.get_attribute('src')
                            alt = img.get_attribute('alt') or ''
                            class_attr = img.get_attribute('class') or ''
                            
                            # Validate image URL
                            if src and src.startswith('http'):
                                # Additional validation for manga images
                                if _is_valid_manga_image(src, alt, class_attr):
                                    if src not in images:  # Avoid duplicates
                                        images.append(src)
                                        logger.debug(f"Added image: {src}")
                                else:
                                    logger.debug(f"Skipped non-manga image: {src}")
                            else:
                                logger.debug(f"Skipped invalid image src: {src}")
                                
                        except Exception as e:
                            metadata['warnings'].append(f"Error processing image: {e}")
                            continue
                    
                    # If we found images with this strategy, break
                    if images:
                        break
                        
            except Exception as e:
                metadata['warnings'].append(f"Strategy {i+1} failed: {e}")
                continue
        
        # Sort images by page number if possible
        images = _sort_images_by_page_number(images)
        
        metadata['image_count'] = len(images)
        metadata['extraction_time'] = time.time() - start_time
        
        if images:
            logger.info(f"WeebCentral: Successfully extracted {len(images)} images in {metadata['extraction_time']:.2f}s")
        else:
            metadata['errors'].append("No images found with any strategy")
            logger.warning("WeebCentral: No images found")
            
            # Debug: Save page content for analysis
            try:
                page_content = page.content()
                with open(f'debug_weebcentral_chapter_{int(time.time())}.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info("Debug HTML saved for analysis")
            except Exception as e:
                metadata['warnings'].append(f"Could not save debug HTML: {e}")
        
    except Exception as e:
        error_msg = f"Error extracting chapter images: {e}"
        metadata['errors'].append(error_msg)
        logger.error(error_msg)
    
    return images, metadata

def _is_valid_manga_image(src: str, alt: str, class_attr: str) -> bool:
    """
    Validate if an image is likely a manga page image
    
    Args:
        src: Image source URL
        alt: Alt text
        class_attr: CSS classes
    
    Returns:
        True if image appears to be a manga page
    """
    # Skip common non-manga images
    skip_patterns = [
        'logo', 'banner', 'ad', 'advertisement', 'social', 'icon',
        'avatar', 'profile', 'thumbnail', 'preview', 'cover'
    ]
    
    src_lower = src.lower()
    alt_lower = alt.lower()
    class_lower = class_attr.lower()
    
    # Check for skip patterns
    for pattern in skip_patterns:
        if pattern in src_lower or pattern in alt_lower or pattern in class_lower:
            return False
    
    # Check for manga-specific patterns
    manga_patterns = [
        'manga', 'page', 'chapter', 'panel', 'scan'
    ]
    
    for pattern in manga_patterns:
        if pattern in alt_lower or pattern in class_lower:
            return True
    
    # Check for image file extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    if any(ext in src_lower for ext in image_extensions):
        # If it has a valid extension and doesn't match skip patterns, consider it valid
        return True
    
    return False

def _sort_images_by_page_number(images: List[str]) -> List[str]:
    """
    Sort images by page number if possible
    
    Args:
        images: List of image URLs
    
    Returns:
        Sorted list of image URLs
    """
    def extract_page_number(url):
        # Try to extract page number from URL or filename
        filename = url.split('/')[-1]
        
        # Look for patterns like "0013-001.png", "page_1.jpg", etc.
        patterns = [
            r'(\d+)-(\d+)',  # 0013-001
            r'page[_-]?(\d+)',  # page_1, page1
            r'(\d+)\.(jpg|jpeg|png|webp)',  # 001.jpg
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return int(match.group(2))  # Use second number for chapter-page format
                else:
                    return int(match.group(1))
        
        return 0  # Default to 0 if no pattern matches
    
    try:
        return sorted(images, key=extract_page_number)
    except Exception:
        # If sorting fails, return original order
        return images

def get_chapter_images_with_cache(page: Page, chapter_url: str, cache_manager=None, user_id=None) -> Tuple[List[str], Dict]:
    """
    Get chapter images with caching support
    
    Args:
        page: Playwright page object
        chapter_url: URL of the chapter page
        cache_manager: Cache manager instance
        user_id: User ID for caching
    
    Returns:
        Tuple of (images_list, metadata_dict)
    """
    # Check cache first if cache manager is provided
    if cache_manager:
        cached_images = cache_manager.get_cached_chapter_images(chapter_url, user_id)
        if cached_images:
            logger.info(f"Found {len(cached_images)} cached images for {chapter_url}")
            return cached_images, {
                'chapter_url': chapter_url,
                'cached': True,
                'image_count': len(cached_images),
                'extraction_time': 0
            }
    
    # Extract images if not cached
    images, metadata = get_chapter_images_enhanced(page, chapter_url)
    
    # Cache the results if cache manager is provided and images were found
    if cache_manager and images:
        try:
            cache_manager.cache_chapter_images(chapter_url, 'weebcentral', images, user_id)
            logger.info(f"Cached {len(images)} images for {chapter_url}")
        except Exception as e:
            metadata['warnings'].append(f"Failed to cache images: {e}")
    
    metadata['cached'] = False
    return images, metadata

# Flask Blueprint for enhanced chapter images
weebcentral_enhanced_bp = Blueprint('weebcentral_enhanced_bp', __name__)

@weebcentral_enhanced_bp.route('/chapter-images/weebcentral/enhanced/<path:chapter_url>', methods=['GET'])
def enhanced_chapter_images(chapter_url):
    """Enhanced chapter images endpoint with better error handling and metadata"""
    from playwright.sync_api import sync_playwright
    
    # Get query parameters
    use_cache = request.args.get('cache', 'true').lower() == 'true'
    timeout = int(request.args.get('timeout', '30000'))
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
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
            decoded_url = urllib.parse.unquote(chapter_url)
            
            # Get images with enhanced extraction
            images, metadata = get_chapter_images_enhanced(page, decoded_url, timeout)
            
            response_data = {
                'images': images,
                'metadata': metadata,
                'success': len(images) > 0,
                'timestamp': time.time()
            }
            
            # Set appropriate HTTP status
            status_code = 200 if images else 404
            
            return jsonify(response_data), status_code
            
        except Exception as e:
            error_response = {
                'images': [],
                'metadata': {
                    'chapter_url': chapter_url,
                    'errors': [f"Failed to extract images: {str(e)}"],
                    'extraction_time': 0,
                    'image_count': 0
                },
                'success': False,
                'timestamp': time.time()
            }
            return jsonify(error_response), 500
        finally:
            browser.close()

# Batch processing for multiple chapters
def batch_get_chapter_images(chapter_urls: List[str], max_concurrent: int = 3) -> Dict[str, Tuple[List[str], Dict]]:
    """
    Process multiple chapters in batches
    
    Args:
        chapter_urls: List of chapter URLs to process
        max_concurrent: Maximum number of concurrent browser instances
    
    Returns:
        Dictionary mapping chapter URLs to (images, metadata) tuples
    """
    import concurrent.futures
    
    results = {}
    
    def process_single_chapter(url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                images, metadata = get_chapter_images_enhanced(page, url)
                return url, (images, metadata)
            finally:
                browser.close()
    
    # Process in batches
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        future_to_url = {executor.submit(process_single_chapter, url): url for url in chapter_urls}
        
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                url, result = future.result()
                results[url] = result
            except Exception as e:
                results[url] = ([], {'errors': [str(e)], 'image_count': 0})
    
    return results

if __name__ == "__main__":
    # Test the enhanced functionality
    test_url = "https://weebcentral.com/chapters/01J76XYY6F5JMA5RKG89KXZAS1"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            images, metadata = get_chapter_images_enhanced(page, test_url)
            print(f"Enhanced extraction results:")
            print(f"Images found: {len(images)}")
            print(f"Extraction time: {metadata['extraction_time']:.2f}s")
            print(f"Errors: {metadata['errors']}")
            print(f"Warnings: {metadata['warnings']}")
            
            if images:
                print(f"First 3 images: {images[:3]}")
        finally:
            browser.close() 