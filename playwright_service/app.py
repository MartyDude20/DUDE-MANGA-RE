from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import re
import os
from dotenv import load_dotenv
from sources import weebcentral, asurascans
from sources.asurascans import chapter_bp

load_dotenv()

app = Flask(__name__)
CORS(app)
app.register_blueprint(chapter_bp)

# Config: enable/disable sources
ENABLED_SOURCES = {
    'weebcentral': True,
    'asurascans': True
}

SOURCE_MODULES = {
    'weebcentral': weebcentral,
    'asurascans': asurascans
}

def extract_manga_id_from_url(url):
    """Extract manga ID from weebcentral URL"""
    match = re.search(r'/series/([^/]+)/', url)
    return match.group(1) if match else None

@app.route('/search', methods=['GET'])
def search_manga():
    query = request.args.get('q', '')
    sources_param = request.args.get('sources', None)
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    # Determine which sources to use
    if sources_param:
        requested_sources = [s.strip().lower() for s in sources_param.split(',')]
        sources_to_use = [s for s in requested_sources if ENABLED_SOURCES.get(s)]
    else:
        sources_to_use = [s for s, enabled in ENABLED_SOURCES.items() if enabled]
    if not sources_to_use:
        return jsonify({'error': 'No sources enabled or selected'}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            results = []
            for source in sources_to_use:
                try:
                    page = browser.new_page()
                    results += SOURCE_MODULES[source].search(page, query)
                    page.close()
                except Exception as e:
                    print(f"Error searching {source}: {e}")
                    continue
            browser.close()
            return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': f'Failed to search manga: {str(e)}'}), 500

@app.route('/manga/<source>/<manga_id>', methods=['GET'])
def get_manga_details(source, manga_id):
    source = source.lower()
    if source not in ENABLED_SOURCES or not ENABLED_SOURCES[source]:
        return jsonify({'error': f'Source {source} is not enabled'}), 400
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            details = SOURCE_MODULES[source].get_details(page, manga_id)
            page.close()
            browser.close()
            return jsonify(details)
    except Exception as e:
        return jsonify({'error': f'Failed to fetch manga details: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'playwright-scraper'})

if __name__ == '__main__':
    port = int(os.getenv('PLAYWRIGHT_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 