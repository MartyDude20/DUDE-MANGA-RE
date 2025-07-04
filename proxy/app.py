from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

PLAYWRIGHT_URL = f"http://localhost:{os.getenv('PLAYWRIGHT_PORT', 5000)}"

@app.route('/api/search', methods=['GET'])
def search_manga():
    """Search for manga titles"""
    params = dict(request.args)
    print('Proxy forwarding params:', params)
    try:
        # Forward all query parameters to Playwright service
        response = requests.get(f"{PLAYWRIGHT_URL}/search", params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch search results: {str(e)}'}), 500

@app.route('/api/manga/<manga_id>', methods=['GET'])
def get_manga_details(manga_id):
    """Get detailed information about a specific manga"""
    try:
        # Forward request to Playwright service
        response = requests.get(f"{PLAYWRIGHT_URL}/manga/{manga_id}")
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch manga details: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'flask-proxy'})

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 3006))
    app.run(host='0.0.0.0', port=port, debug=True) 