import requests
from flask import Blueprint, jsonify

def search(page, query):
    """Search MangaDex for manga titles matching the query."""
    url = "https://api.mangadex.org/manga"
    params = {
        "title": query,
        "limit": 10,
        "availableTranslatedLanguage[]": "en",
        "order[relevance]": "desc"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for manga in data.get("data", []):
        attributes = manga["attributes"]
        title = attributes["title"].get("en") or next(iter(attributes["title"].values()), "Unknown Title")
        description = attributes["description"].get("en") or ""
        cover_id = None
        for rel in manga.get("relationships", []):
            if rel["type"] == "cover_art":
                cover_id = rel["id"]
        image_url = None
        if cover_id:
            # Fetch cover filename from MangaDex API
            cover_resp = requests.get(f"https://api.mangadex.org/cover/{cover_id}")
            if cover_resp.ok:
                cover_data = cover_resp.json()
                file_name = cover_data.get("data", {}).get("attributes", {}).get("fileName")
                if file_name:
                    image_url = f"https://uploads.mangadex.org/covers/{manga['id']}/{file_name}"
        results.append({
            "id": manga["id"],
            "title": title,
            "description": description,
            "image": image_url,
            "details_url": f"https://mangadex.org/title/{manga['id']}",
            "source": "mangadex"
        })
    return results

def get_details(page, manga_id):
    """Get manga details and chapters from MangaDex."""
    # Get manga details
    manga_url = f"https://api.mangadex.org/manga/{manga_id}"
    resp = requests.get(manga_url)
    resp.raise_for_status()
    manga = resp.json()["data"]
    attributes = manga["attributes"]
    title = attributes["title"].get("en") or next(iter(attributes["title"].values()), "Unknown Title")
    description = attributes["description"].get("en") or ""
    status = attributes.get("status", "Unknown")
    author = None
    cover_id = None
    # Find author and cover_id from relationships
    for rel in manga.get("relationships", []):
        if rel["type"] == "author":
            # If attributes are present, use them; otherwise, fetch author details
            if "attributes" in rel and rel["attributes"].get("name"):
                author = rel["attributes"]["name"]
            else:
                # Fetch author details
                author_resp = requests.get(f"https://api.mangadex.org/author/{rel['id']}")
                if author_resp.ok:
                    author_data = author_resp.json()
                    author = author_data.get("data", {}).get("attributes", {}).get("name", author)
        if rel["type"] == "cover_art":
            cover_id = rel["id"]
    # Fetch cover filename for thumbnail
    image_url = None
    if cover_id:
        cover_resp = requests.get(f"https://api.mangadex.org/cover/{cover_id}")
        if cover_resp.ok:
            cover_data = cover_resp.json()
            file_name = cover_data.get("data", {}).get("attributes", {}).get("fileName")
            if file_name:
                image_url = f"https://uploads.mangadex.org/covers/{manga_id}/{file_name}"
    # Get chapters (first 100, English only)
    chapters_url = f"https://api.mangadex.org/chapter"
    params = {
        "manga": manga_id,
        "translatedLanguage[]": "en",
        "order[chapter]": "asc",
        "limit": 100
    }
    resp = requests.get(chapters_url, params=params)
    resp.raise_for_status()
    chapters_data = resp.json()
    chapters = []
    for ch in chapters_data.get("data", []):
        ch_attr = ch["attributes"]
        ch_num = ch_attr.get("chapter", "?")
        ch_title = ch_attr.get("title", "")
        title_str = f"Chapter {ch_num}" + (f": {ch_title}" if ch_title else "")
        chapters.append({
            "title": title_str,
            "url": f"https://mangadex.org/chapter/{ch['id']}"
        })
    if not chapters:
        chapters = [{"title": "No chapters found", "url": None}]
    return {
        "id": manga_id,
        "title": title,
        "description": description,
        "status": status,
        "author": author or "Unknown Author",
        "image": image_url,
        "chapters": chapters,
        "url": f"https://mangadex.org/title/{manga_id}",
        "source": "mangadex"
    }

mangadex_chapter_bp = Blueprint('mangadex_chapter_bp', __name__)

@mangadex_chapter_bp.route('/chapter-images/mangadex/<manga_id>/<chapter_id>', methods=['GET'])
def get_chapter_images(manga_id, chapter_id):
    """Get image URLs for a MangaDex chapter (original quality)."""
    at_home_url = f"https://api.mangadex.org/at-home/server/{chapter_id}"
    resp = requests.get(at_home_url)
    if not resp.ok:
        return jsonify({'error': 'Failed to fetch chapter images from MangaDex'}), 500
    data = resp.json()
    base_url = data.get('baseUrl')
    chapter = data.get('chapter', {})
    hash_ = chapter.get('hash')
    page_files = chapter.get('data', [])  # original quality
    if not (base_url and hash_ and page_files):
        return jsonify({'error': 'Invalid response from MangaDex at-home API'}), 500
    image_urls = [f"{base_url}/data/{hash_}/{filename}" for filename in page_files]
    return jsonify({'images': image_urls}) 