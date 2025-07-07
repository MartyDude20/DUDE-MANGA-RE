from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

PLAYWRIGHT_URL = f"http://localhost:{os.getenv('PLAYWRIGHT_PORT', 5000)}"

def get_forward_headers():
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    if 'Cookie' in request.headers:
        headers['Cookie'] = request.headers['Cookie']
    return headers

@app.route('/api/search', methods=['GET'])
def search_manga():
    """Search for manga titles"""
    params = dict(request.args)
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/search", params=params, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch search results: {str(e)}'}), 500

@app.route('/api/manga/<manga_id>', methods=['GET'])
def get_manga_details(manga_id):
    """Get detailed information about a specific manga"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/manga/{manga_id}", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch manga details: {str(e)}'}), 500

@app.route('/api/manga/<source>/<manga_id>', methods=['GET'])
def get_manga_details_with_source(source, manga_id):
    """Get detailed information about a specific manga from a specific source"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/manga/{source}/{manga_id}", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch manga details: {str(e)}'}), 500

@app.route('/api/chapter-images/<source>/<manga_id>/<path:chapter_id>', methods=['GET'])
def get_chapter_images(source, manga_id, chapter_id):
    try:
        headers = get_forward_headers()
        if source == 'weebcentral':
            response = requests.get(f"{PLAYWRIGHT_URL}/chapter-images/{source}/{chapter_id}", headers=headers)
        else:
            response = requests.get(f"{PLAYWRIGHT_URL}/chapter-images/{source}/{manga_id}/{chapter_id}", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch chapter images: {str(e)}'}), 500

@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """Get cache statistics"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/cache/stats", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get cache stats: {str(e)}'}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache based on parameters"""
    try:
        data = request.get_json() or {}
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/cache/clear", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to clear cache: {str(e)}'}), 500

@app.route('/api/cache/cleanup', methods=['POST'])
def cleanup_cache():
    """Clean up expired cache entries"""
    try:
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/cache/cleanup", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to cleanup cache: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'flask-proxy'})

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 3006))
    app.run(host='0.0.0.0', port=port, debug=True) 