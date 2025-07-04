from playwright.sync_api import Page
import re

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
            img_elem = card.query_selector('img')
            image_url = img_elem.get_attribute('src') if img_elem else None
            title = None
            if img_elem:
                alt_text = img_elem.get_attribute('alt')
                if alt_text:
                    title = alt_text.replace(' cover', '')
            if not title:
                title_div = card.query_selector('div.text-ellipsis')
                if title_div:
                    title = title_div.inner_text().strip()
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
    details = {}
    title_elem = page.query_selector('h1, .series-title, [data-testid="series-title"]')
    details['title'] = title_elem.inner_text().strip() if title_elem else "Unknown Title"
    img_elem = page.query_selector('.series-cover img, .manga-cover img, [data-testid="cover-image"]')
    details['image'] = img_elem.get_attribute('src') if img_elem else None
    desc_elem = page.query_selector('.description, .synopsis, [data-testid="description"]')
    details['description'] = desc_elem.inner_text().strip() if desc_elem else "No description available"
    author_elem = page.query_selector('.author, .creator, [data-testid="author"]')
    details['author'] = author_elem.inner_text().strip() if author_elem else "Unknown Author"
    details['id'] = manga_id
    details['url'] = manga_url
    details['source'] = 'weebcentral'
    chapters = []
    for a in page.query_selector_all('a[href*="/chapter/"]'):
        try:
            chapter_title = a.inner_text().strip()
            chapter_url = a.get_attribute('href')
            if chapter_title and chapter_url:
                chapters.append({'title': chapter_title, 'url': chapter_url})
        except Exception as e:
            print(f"WeebCentral chapter error: {e}")
            continue
    details['chapters'] = chapters
    return details 