from playwright.sync_api import Page
import re

def extract_manga_id_from_url(url):
    # AsuraScans URLs look like /series/series-slug
    match = re.search(r'/series/([^/]+)', url)
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
    # Title
    title_elem = page.query_selector('h1.entry-title')
    details['title'] = title_elem.inner_text().strip() if title_elem else "Unknown Title"
    # Image
    img_elem = page.query_selector('div.thumb img')
    details['image'] = img_elem.get_attribute('src') if img_elem else None
    # Description
    desc_elem = page.query_selector('div.entry-content.entry-content-single')
    details['description'] = desc_elem.inner_text().strip() if desc_elem else "No description available"
    # Author
    author = ""
    author_elem = page.query_selector('div.imptdt:has(i.fa-user) a')
    if author_elem:
        author = author_elem.inner_text().strip()
    details['author'] = author or "Unknown Author"
    # Status
    status = ""
    status_elem = page.query_selector('div.imptdt:has(i.fa-book)')
    if status_elem:
        status = status_elem.inner_text().replace('Status', '').strip()
    details['status'] = status
    details['id'] = manga_id
    details['url'] = manga_url
    details['source'] = 'asurascans'
    return details 