from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import re
import os
from dotenv import load_dotenv
from sources import weebcentral, asurascans
from sources import mangadex
from sources.asurascans import chapter_bp
from sources.weebcentral import weebcentral_chapter_bp
from cache_manager import CacheManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from models import db, User, PasswordResetToken, ReadHistory
from auth import init_auth, auth_manager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import secrets
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
# Configure CORS to allow credentials
CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173"],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Authorization"])
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///manga_cache.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
bcrypt = Bcrypt(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize authentication
init_auth(app)

app.register_blueprint(chapter_bp)
app.register_blueprint(weebcentral_chapter_bp)
app.register_blueprint(mangadex.mangadex_chapter_bp)

# Initialize cache manager
cache_manager = CacheManager()

# Config: enable/disable sources
ENABLED_SOURCES = {
    'weebcentral': True,
    'asurascans': True,
    'mangadex': True
}

SOURCE_MODULES = {
    'weebcentral': weebcentral,
    'asurascans': asurascans,
    'mangadex': mangadex
}

def is_admin(user):
    return user and getattr(user, 'hasAdmin', False)

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if user is authenticated
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        payload, error = auth_manager.verify_token(token, 'access')
        if error:
            return jsonify({'error': error}), 401
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        if not is_admin(user):
            return jsonify({'error': 'Admin privileges required'}), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def extract_manga_id_from_url(url):
    """Extract manga ID from weebcentral URL"""
    match = re.search(r'/series/([^/]+)/', url)
    return match.group(1) if match else None

@app.route('/search', methods=['GET'])
@auth_manager.optional_auth
def search_manga():
    query = request.args.get('q', '')
    sources_param = request.args.get('sources', None)
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # Get user_id from request context (None for anonymous users)
    user_id = getattr(request, 'current_user', None)
    user_id = user_id.id if user_id else None
    
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
        results = []
        
        # Check cache first (unless force refresh is requested)
        if not force_refresh:
            cached_results = []
            for source in sources_to_use:
                cached = cache_manager.get_cached_search(query, source, user_id)
                if cached:
                    cached_results.extend(cached)
            
            if cached_results:
                return jsonify({'results': cached_results, 'cached': True})
        
        # If no cache or force refresh, scrape fresh data
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for source in sources_to_use:
                try:
                    page = browser.new_page()
                    source_results = SOURCE_MODULES[source].search(page, query)
                    results.extend(source_results)
                    
                    # Cache the results for this source
                    cache_manager.cache_search_results(query, source, source_results, user_id)
                    
                    page.close()
                except Exception as e:
                    # Only print actual errors
                    print(f"Error searching {source}: {e}")
                    continue
            browser.close()
            
            return jsonify({'results': results, 'cached': False})
    except Exception as e:
        return jsonify({'error': f'Failed to search manga: {str(e)}'}), 500

@app.route('/manga/<source>/<manga_id>', methods=['GET'])
@auth_manager.optional_auth
def get_manga_details(source, manga_id):
    source = source.lower()
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # Get user_id from request context (None for anonymous users)
    user_id = getattr(request, 'current_user', None)
    user_id = user_id.id if user_id else None
    
    if source not in ENABLED_SOURCES or not ENABLED_SOURCES[source]:
        return jsonify({'error': f'Source {source} is not enabled'}), 400
    
    try:
        # Check cache first (unless force refresh is requested)
        if not force_refresh:
            cached_details = cache_manager.get_cached_manga(manga_id, source, user_id)
            if cached_details:
                return jsonify({**cached_details, 'cached': True})
        
        # If no cache or force refresh, scrape fresh data
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            details = SOURCE_MODULES[source].get_details(page, manga_id)
            page.close()
            browser.close()
            
            # Cache the manga details
            cache_manager.cache_manga_details(manga_id, source, details, user_id)
            
            return jsonify({**details, 'cached': False})
    except Exception as e:
        return jsonify({'error': f'Failed to fetch manga details: {str(e)}'}), 500

@app.route('/cache/stats', methods=['GET'])
@auth_manager.login_required
def get_cache_stats():
    """Get cache statistics for the current user"""
    try:
        # Get user_id from request context
        user_id = request.current_user.id
        stats = cache_manager.get_cache_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': f'Failed to get cache stats: {str(e)}'}), 500

@app.route('/cache/clear', methods=['POST'])
@auth_manager.login_required
def clear_cache():
    """Clear cache based on parameters for the current user"""
    try:
        # Get user_id from request context
        user_id = request.current_user.id
        
        data = request.get_json() or {}
        cache_type = data.get('type', 'all')  # 'all', 'search', 'manga', 'chapter'
        source = data.get('source')
        query = data.get('query')
        manga_id = data.get('manga_id')
        
        if cache_type == 'search':
            cache_manager.clear_search_cache(user_id, query, source)
        elif cache_type == 'manga':
            cache_manager.clear_manga_cache(user_id, manga_id, source)
        elif cache_type == 'chapter':
            cache_manager.clear_chapter_cache(user_id, source)
        else:  # 'all'
            cache_manager.clear_search_cache(user_id)
            cache_manager.clear_manga_cache(user_id)
            cache_manager.clear_chapter_cache(user_id)
        
        return jsonify({'message': f'Cache cleared successfully', 'type': cache_type})
    except Exception as e:
        return jsonify({'error': f'Failed to clear cache: {str(e)}'}), 500

@app.route('/cache/cleanup', methods=['POST'])
@auth_manager.login_required
def cleanup_cache():
    """Clean up expired cache entries for the current user"""
    try:
        # Get user_id from request context
        user_id = request.current_user.id
        cache_manager.clear_expired_cache(user_id)
        return jsonify({'message': 'Expired cache entries cleaned up successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to cleanup cache: {str(e)}'}), 500

# Admin endpoints for managing cache across all users
@app.route('/admin/cache/stats', methods=['GET'])
@admin_required
def admin_get_cache_stats():
    """Get cache statistics for all users (admin only)"""
    try:
        stats = cache_manager.get_cache_stats()  # No user_id = all users
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': f'Failed to get cache stats: {str(e)}'}), 500

@app.route('/admin/cache/clear', methods=['POST'])
@admin_required
def admin_clear_cache():
    """Clear cache for all users (admin only)"""
    try:
        data = request.get_json() or {}
        cache_type = data.get('type', 'all')  # 'all', 'search', 'manga', 'chapter'
        source = data.get('source')
        query = data.get('query')
        manga_id = data.get('manga_id')
        
        if cache_type == 'search':
            cache_manager.clear_search_cache(None, query, source)  # None = all users
        elif cache_type == 'manga':
            cache_manager.clear_manga_cache(None, manga_id, source)  # None = all users
        elif cache_type == 'chapter':
            cache_manager.clear_chapter_cache(None, source)  # None = all users
        else:  # 'all'
            cache_manager.clear_search_cache()  # None = all users
            cache_manager.clear_manga_cache()  # None = all users
            cache_manager.clear_chapter_cache()  # None = all users
        
        return jsonify({'message': f'All users cache cleared successfully', 'type': cache_type})
    except Exception as e:
        return jsonify({'error': f'Failed to clear cache: {str(e)}'}), 500

@app.route('/admin/cache/cleanup', methods=['POST'])
@admin_required
def admin_cleanup_cache():
    """Clean up expired cache entries for all users (admin only)"""
    try:
        cache_manager.clear_expired_cache()  # None = all users
        return jsonify({'message': 'All users expired cache entries cleaned up successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to cleanup cache: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'playwright-scraper'})

# --- User Registration Endpoint ---
@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    if email and User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

# --- PASSWORD RESET ENDPOINTS ---
@app.route('/password-reset/request', methods=['POST'])
def password_reset_request():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'If the email exists, a reset link will be sent.'}), 200
    # Generate token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    prt = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
    db.session.add(prt)
    db.session.commit()
    # TODO: Send email with token (for now, return token in response)
    return jsonify({'message': 'Password reset link generated.', 'token': token}), 200

@app.route('/password-reset/confirm', methods=['POST'])
def password_reset_confirm():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    if not token or not new_password:
        return jsonify({'error': 'Token and new password are required'}), 400
    prt = PasswordResetToken.query.filter_by(token=token, used=False).first()
    if not prt or prt.expires_at < datetime.utcnow():
        return jsonify({'error': 'Invalid or expired token'}), 400
    user = User.query.get(prt.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    prt.used = True
    db.session.commit()
    return jsonify({'message': 'Password has been reset.'}), 200

# --- PROFILE MANAGEMENT ENDPOINTS ---
@app.route('/profile', methods=['GET'])
@auth_manager.login_required
def get_profile():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at,
        'hasAdmin': user.hasAdmin
    })

@app.route('/profile', methods=['PUT'])
@auth_manager.login_required
def update_profile():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    if username:
        user.username = username
    if email:
        user.email = email
    db.session.commit()
    return jsonify({'message': 'Profile updated.'})

@app.route('/profile/password', methods=['PUT'])
@auth_manager.login_required
def change_password():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if not old_password or not new_password:
        return jsonify({'error': 'Old and new password required'}), 400
    if not check_password_hash(user.password_hash, old_password):
        return jsonify({'error': 'Old password incorrect'}), 400
    user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()
    return jsonify({'message': 'Password changed.'})

@app.route('/profile', methods=['DELETE'])
@auth_manager.login_required
def delete_account():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Account deleted.'})

# --- READ HISTORY ENDPOINTS ---
@app.route('/read-history', methods=['POST'])
@auth_manager.login_required
def add_read_history():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.get_json()
    manga_title = data.get('manga_title')
    chapter_title = data.get('chapter_title')
    source = data.get('source')
    manga_id = data.get('manga_id')
    chapter_url = data.get('chapter_url')
    if not all([manga_title, chapter_title, source, manga_id, chapter_url]):
        return jsonify({'error': 'All fields are required'}), 400
    rh = ReadHistory(user_id=user.id, manga_title=manga_title, chapter_title=chapter_title, source=source, manga_id=manga_id, chapter_url=chapter_url)
    db.session.add(rh)
    db.session.commit()
    return jsonify({'message': 'Read history recorded.'})

@app.route('/read-history', methods=['GET'])
@auth_manager.login_required
def get_read_history():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    history = ReadHistory.query.filter_by(user_id=user.id).order_by(ReadHistory.read_at.desc()).all()
    return jsonify([
        {
            'manga_title': h.manga_title,
            'chapter_title': h.chapter_title,
            'source': h.source,
            'manga_id': h.manga_id,
            'chapter_url': h.chapter_url,
            'read_at': h.read_at
        } for h in history
    ])

if __name__ == '__main__':
    port = int(os.getenv('PLAYWRIGHT_PORT', 5000))
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=port, debug=True) 