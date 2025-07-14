from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def custom_cors_origin(origin):
    allowed = {"http://localhost:5173", "http://127.0.0.1:5173"}
    if origin in allowed:
        return origin
    return None

CORS(
    app,
    origins="*",
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Authorization"]
)

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

# Lazy loading endpoints
@app.route('/api/lazy/manga/<manga_id>/details', methods=['GET'])
def get_lazy_manga_details(manga_id):
    """Get manga details with lazy loading"""
    try:
        headers = get_forward_headers()
        params = request.args.to_dict()
        response = requests.get(f"{PLAYWRIGHT_URL}/lazy/manga/{manga_id}/details", headers=headers, params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch manga details: {str(e)}'}), 500

@app.route('/api/lazy/manga/<manga_id>/chapters', methods=['GET'])
def get_lazy_chapters(manga_id):
    """Get chapters with pagination"""
    try:
        headers = get_forward_headers()
        params = request.args.to_dict()
        response = requests.get(f"{PLAYWRIGHT_URL}/lazy/manga/{manga_id}/chapters", headers=headers, params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch chapters: {str(e)}'}), 500

@app.route('/api/lazy/chapter-images/<path:chapter_url>', methods=['GET'])
def get_lazy_chapter_images(chapter_url):
    """Get chapter images with lazy loading"""
    try:
        headers = get_forward_headers()
        params = request.args.to_dict()
        response = requests.get(f"{PLAYWRIGHT_URL}/lazy/chapter-images/{chapter_url}", headers=headers, params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch chapter images: {str(e)}'}), 500

@app.route('/api/lazy/progress/<session_id>', methods=['GET'])
def get_lazy_progress(session_id):
    """Get progress updates for lazy loading"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/lazy/progress/{session_id}", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch progress: {str(e)}'}), 500

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

@app.route('/api/preloader/status', methods=['GET'])
def preloader_status():
    """Get preloader status"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/preloader/status", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get preloader status: {str(e)}'}), 500

@app.route('/api/preloader/trigger', methods=['POST'])
def trigger_preload():
    """Trigger preloading"""
    try:
        data = request.get_json() or {}
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/preloader/trigger", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to trigger preload: {str(e)}'}), 500

@app.route('/api/preloader/search-stats', methods=['GET'])
def preloader_search_stats():
    """Get preloader search statistics"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/preloader/search-stats", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get search stats: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'flask-proxy'})

# Authentication endpoints
@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        data = request.get_json()
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/login", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code, dict(response.headers)
    except requests.RequestException as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """Register endpoint"""
    try:
        data = request.get_json()
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/register", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh():
    """Refresh token endpoint"""
    try:
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/refresh", headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code, dict(response.headers)
    except requests.RequestException as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    try:
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/logout", headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@app.route('/api/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/me", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get user info: {str(e)}'}), 500

@app.route('/api/password-reset/request', methods=['POST'])
def password_reset_request():
    """Request password reset"""
    try:
        data = request.get_json()
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/password-reset/request", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Password reset request failed: {str(e)}'}), 500

@app.route('/api/password-reset/confirm', methods=['POST'])
def password_reset_confirm():
    """Confirm password reset"""
    try:
        data = request.get_json()
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/password-reset/confirm", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Password reset confirmation failed: {str(e)}'}), 500

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/profile", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        headers = get_forward_headers()
        response = requests.put(f"{PLAYWRIGHT_URL}/profile", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

@app.route('/api/profile/password', methods=['PUT'])
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        headers = get_forward_headers()
        response = requests.put(f"{PLAYWRIGHT_URL}/profile/password", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to change password: {str(e)}'}), 500

@app.route('/api/profile', methods=['DELETE'])
def delete_account():
    """Delete user account"""
    try:
        headers = get_forward_headers()
        response = requests.delete(f"{PLAYWRIGHT_URL}/profile", headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to delete account: {str(e)}'}), 500

@app.route('/api/read-history', methods=['GET'])
def get_read_history():
    """Get user read history"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/read-history", headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get read history: {str(e)}'}), 500

@app.route('/api/read-history', methods=['POST'])
def add_read_history():
    """Add to user read history"""
    try:
        data = request.get_json()
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/read-history", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to add read history: {str(e)}'}), 500

@app.route('/api/read-history/clear', methods=['DELETE'])
def clear_read_history():
    """Clear user read history"""
    try:
        headers = get_forward_headers()
        response = requests.delete(f"{PLAYWRIGHT_URL}/read-history/clear", headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to clear read history: {str(e)}'}), 500

# --- NEW API ENDPOINTS ---

@app.route('/api/reading-progress', methods=['GET'])
def get_reading_progress():
    """Get user reading progress"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/reading-progress", headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get reading progress: {str(e)}'}), 500

@app.route('/api/reading-progress/continue', methods=['GET'])
def get_continue_reading():
    """Get continue reading list"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/reading-progress/continue", headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get continue reading: {str(e)}'}), 500

@app.route('/api/reading-progress', methods=['POST'])
def update_reading_progress():
    """Update reading progress"""
    try:
        data = request.get_json()
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/reading-progress", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to update reading progress: {str(e)}'}), 500

@app.route('/api/reading-stats', methods=['GET'])
def get_reading_stats():
    """Get reading statistics"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/reading-stats", headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get reading stats: {str(e)}'}), 500

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get user notifications"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/notifications", headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get notifications: {str(e)}'}), 500

@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        headers = get_forward_headers()
        response = requests.put(f"{PLAYWRIGHT_URL}/notifications/{notification_id}/read", headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to mark notification as read: {str(e)}'}), 500

@app.route('/api/reading-lists', methods=['GET'])
def get_reading_lists():
    """Get user reading lists"""
    try:
        headers = get_forward_headers()
        response = requests.get(f"{PLAYWRIGHT_URL}/reading-lists", headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to get reading lists: {str(e)}'}), 500

@app.route('/api/reading-lists', methods=['POST'])
def create_reading_list():
    """Create new reading list"""
    try:
        data = request.get_json()
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/reading-lists", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to create reading list: {str(e)}'}), 500

@app.route('/api/reading-lists/<int:list_id>/manga', methods=['POST'])
def add_manga_to_list(list_id):
    """Add manga to reading list"""
    try:
        data = request.get_json()
        headers = get_forward_headers()
        response = requests.post(f"{PLAYWRIGHT_URL}/reading-lists/{list_id}/manga", json=data, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to add manga to list: {str(e)}'}), 500

@app.route('/api/proxy-image', methods=['GET'])
def proxy_image():
    """Proxy images to avoid CORS issues"""
    try:
        image_url = request.args.get('url')
        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(image_url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        
        # Forward the response headers
        headers_to_forward = {}
        for header, value in response.headers.items():
            if header.lower() in ['content-type', 'content-length', 'cache-control', 'etag', 'last-modified']:
                headers_to_forward[header] = value
        
        return response.content, response.status_code, headers_to_forward
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to proxy image: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 3006))
    app.run(host='0.0.0.0', port=port, debug=True) 