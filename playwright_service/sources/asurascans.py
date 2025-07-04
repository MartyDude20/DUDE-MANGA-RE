from playwright.sync_api import Page
import re

def extract_manga_id_from_url(url):
    # AsuraScans URLs look like series/series-slug or /series/series-slug
    match = re.search(r'series/([^/]+)', url)
    return match.group(1) if match else None

def search(page: Page, query: str):
    search_url = f"https://asuracomic.net/series?page=1&name={query}"
    page.goto(search_url)
    page.wait_for_load_state('networkidle')
    results = []
    # Each manga card is an <a href^="series/"> inside the grid
    cards = page.query_selector_all('a[href^="series/"]')
    print(f"AsuraScans: found {len(cards)} cards for query '{query}'")
    for card in cards:
        try:
            link = card.get_attribute('href')
            manga_id = extract_manga_id_from_url(link) if link else None
            # Image
            img_elem = card.query_selector('img')
            image_url = img_elem.get_attribute('src') if img_elem else None
            # Title (use span.text-[13.3px].block for most specific selection)
            title_elem = card.query_selector('span.text-\[13\.3px\].block')
            title = title_elem.inner_text().strip() if title_elem else None
            # Chapter (regex-based extraction using page.locator)
            chapter = ''
            try:
                chapter_span = page.locator(f'a[href="{link}"] span', has_text=re.compile(r'Chapter'))
                if chapter_span.count() > 0:
                    chapter = chapter_span.first.inner_text().replace('Chapter', '').strip()
            except Exception as e:
                print(f"AsuraScans chapter regex error: {e}")
            results.append({
                'id': manga_id,
                'title': title,
                'status': '',
                'chapter': chapter,
                'image': image_url,
                'details_url': link,
                'source': 'asurascans'
            })
        except Exception as e:
            print(f"AsuraScans error: {e}")
            continue
    print(f"AsuraScans: returning {len(results)} results for query '{query}'")
    return results

def get_details(page: Page, manga_id: str):
    manga_url = f"https://asuracomic.net/series/{manga_id}"
    page.goto(manga_url)
    page.wait_for_load_state('networkidle')
    details = {}
    # Select the main container
    container = page.query_selector('div.col-span-12.sm\\:col-span-9')
    # Title
    title_elem = page.query_selector('div.text-center.sm\\:text-left span.text-xl.font-bold')
    details['title'] = title_elem.inner_text().strip() if title_elem else "Unknown Title"
    # Image
    img_elem = page.query_selector('div.relative.col-span-full.sm\\:col-span-3 img.rounded')
    details['image'] = img_elem.get_attribute('src') if img_elem else None
    # Description
    desc_elem = page.query_selector('span.font-medium.text-sm.text-\[\#A2A2A2\]')
    if desc_elem:
        # Join all <p> children as paragraphs
        ps = desc_elem.query_selector_all('p')
        description = '\n'.join([p.inner_text().strip() for p in ps]) if ps else desc_elem.inner_text().strip()
        details['description'] = description
    else:
        details['description'] = "No description available"
    # Author
    author = ""
    # Find the Author label and get the next sibling
    author_label = page.query_selector('h3.text-\[\#D9D9D9\].font-medium.text-sm:text("Author")')
    if author_label:
        author_value = author_label.evaluate('el => el.nextElementSibling && el.nextElementSibling.innerText')
        if author_value:
            author = author_value.strip()
    details['author'] = author or "Unknown Author"
    # Status
    status = ""
    status_elem = container.query_selector('div.imptdt:has(i.fa-book)') if container else page.query_selector('div.imptdt:has(i.fa-book)')
    if status_elem:
        status = status_elem.inner_text().replace('Status', '').strip()
    details['status'] = status
    details['id'] = manga_id
    details['url'] = manga_url
    details['source'] = 'asurascans'
    # Chapters
    chapters = []
    chapter_container = page.query_selector('div.pl-4.pr-2.pb-4.overflow-y-auto')
    if chapter_container:
        chapter_divs = chapter_container.query_selector_all('div.pl-4.py-2.border.rounded-md')
        for div in chapter_divs:
            try:
                a = div.query_selector('a')
                if not a:
                    continue
                chapter_url = a.get_attribute('href')
                h3s = a.query_selector_all('h3')
                chapter_title = h3s[0].inner_text().strip() if len(h3s) > 0 else ''
                chapter_date = h3s[1].inner_text().strip() if len(h3s) > 1 else ''
                if chapter_title and chapter_url:
                    chapters.append({'title': chapter_title, 'url': chapter_url, 'date': chapter_date})
            except Exception as e:
                print(f"AsuraScans chapter error: {e}")
                continue
    details['chapters'] = chapters
    return details

def get_chapter_images(page: Page, manga_id: str, chapter_id: str):
    # Extract chapter number from chapter_id (e.g., 'bones-b58b6f2f/chapter/29' -> '29')
    import re
    match = re.search(r'/chapter/(.+)$', chapter_id)
    chapter_number = match.group(1) if match else chapter_id
    chapter_url = f"https://asuracomic.net/series/{manga_id}/chapter/{chapter_number}"
    page.goto(chapter_url)
    page.wait_for_load_state('networkidle')
    # Print the HTML for debugging
    print('--- PAGE HTML START ---')
    print(page.content())
    print('--- PAGE HTML END ---')
    # Wait for at least one image to appear
    page.wait_for_selector('img')
    # Use JS to get all relevant image srcs
    images = page.eval_on_selector_all(
        'img',
        """(nodes) => nodes
            .filter(img => img.src && !img.src.endsWith('/images/EndDesign.webp'))
            .map(img => img.src)
        """
    )
    return images

# If using Flask or FastAPI, add a route handler (example for Flask style):
from flask import Blueprint, jsonify, request
chapter_bp = Blueprint('chapter_bp', __name__)

@chapter_bp.route('/chapter-images/asurascans/<manga_id>/<path:chapter_id>', methods=['GET'])
def chapter_images(manga_id, chapter_id):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            images = get_chapter_images(page, manga_id, chapter_id)
            return jsonify({'images': images})
        finally:
            browser.close() 