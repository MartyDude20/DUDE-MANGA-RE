from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import re

def extract_manga_id_from_url(url):
    match = re.search(r'/series/([^/]+)/', url)
    return match.group(1) if match else None

def scrape_weebcentral_all_manga(
    max_pages=None,
    delay_between_clicks=2,
    headless=True,
    verbose=False
):
    url = "https://weebcentral.com/search?sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
    manga_list = []
    seen_urls = set()
    page_num = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_selector('article.bg-base-300', timeout=20000)

        while True:
            if verbose:
                print(f"Scraping page {page_num+1}...")

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
                        # Look for tags in the Tag(s) section
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

                    # Avoid duplicates
                    if link and link not in seen_urls:
                        manga_list.append({
                            "id": manga_id,
                            "title": title,
                            "url": link,
                            "img": image_url,
                            "authors": authors,
                            "tags": tags,
                            "status": status,
                            "year": year
                        })
                        seen_urls.add(link)
                except Exception as e:
                    if verbose:
                        print(f"Error extracting manga card: {e}")

            # Try to click "View More Results"
            try:
                view_more = page.query_selector('button:has-text("View More Results")')
                if not view_more or not view_more.is_enabled():
                    if verbose:
                        print("No more 'View More Results' button found or enabled.")
                    break  # No more results

                view_more.click()
                if verbose:
                    print("Clicked 'View More Results', waiting for new content...")

                page.wait_for_timeout(delay_between_clicks * 1000)
                page_num += 1
                if max_pages and page_num >= max_pages:
                    if verbose:
                        print(f"Reached max_pages limit: {max_pages}")
                    break
            except PlaywrightTimeoutError:
                if verbose:
                    print("Timeout waiting for new results after clicking.")
                break
            except Exception as e:
                if verbose:
                    print(f"Error clicking 'View More Results': {e}")
                break

        browser.close()
    return manga_list

if __name__ == "__main__":
    manga = scrape_weebcentral_all_manga(
        max_pages=2,                # Try 2 pages for a quick test
        delay_between_clicks=2,     # Seconds between clicks
        headless=True,
        verbose=True
    )
    print(f"\nTotal manga scraped: {len(manga)}")
    for m in manga:
        print(m) 