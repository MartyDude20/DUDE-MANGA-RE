import os
from dotenv import load_dotenv
# Explicitly load .env from the project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import re
from sources import weebcentral, asurascans
from sources import mangadex
from sources.asurascans import chapter_bp
from sources.weebcentral import weebcentral_chapter_bp
from cache_manager import CacheManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from models import db, User, PasswordResetToken, ReadHistory, ReadingProgress, ReadingList, ReadingListEntry, Notification, Bookmark, Note, MangaUpdate
from auth import init_auth, auth_manager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import secrets
from datetime import datetime, timedelta
from email_config import init_email, send_password_reset_email, send_password_reset_success_email

# Import simple search service
from services.simple_search import simple_search_service

print("TEST_ENV_CHECK:", os.getenv("TEST_ENV_CHECK"))
print("MAIL_USERNAME:", os.getenv("MAIL_USERNAME"))

app = Flask(__name__)
# Configure CORS to allow credentials
CORS(app, 
     origins="*",
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

# Initialize email configuration
init_email(app)

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
    return user and getattr(user, 'hasadmin', False)

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
        # Use the simple search service with TTL cache
        results = simple_search_service.search(query, sources_to_use, force_refresh)
        
        # Determine if results are from cache
        cached = any(r.get('cached', False) for r in results) if results else False
                    
        return jsonify({'results': results, 'cached': cached})
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
        # For now, use the old cache manager for manga details
        # TODO: Implement manga details caching in simple search service
        details = cache_manager.get_cached_manga(manga_id, source, user_id)
        
        if not details or force_refresh:
            # Scrape fresh details
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                source_module = SOURCE_MODULES.get(source)
                if source_module:
                    details = source_module.get_details(page, manga_id)
                    if details:
                        details['source'] = source
                        details['cached'] = False
                        # Cache the fresh details
                        cache_manager.cache_manga_details(manga_id, source, details, user_id)
                
                browser.close()
        
        if not details:
            return jsonify({'error': 'Manga not found'}), 404
            
        return jsonify(details)
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

@app.route('/performance/metrics', methods=['GET'])
def get_performance_metrics():
    """Get search performance metrics"""
    try:
        metrics = simple_search_service.get_metrics()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': f'Failed to get metrics: {str(e)}'}), 500

@app.route('/test/cache/clear', methods=['POST'])
def test_clear_cache():
    """Clear cache for testing purposes (no auth required)"""
    try:
        # Clear all cache types for all users
        cache_manager.clear_search_cache()  # None = all users
        cache_manager.clear_manga_cache()   # None = all users
        cache_manager.clear_chapter_cache() # None = all users
        
        # Also clear preloaded manga for testing
        from models import PreloadedManga
        PreloadedManga.query.delete()
        db.session.commit()
        
        return jsonify({'message': 'All cache cleared for testing'})
    except Exception as e:
        return jsonify({'error': f'Failed to clear cache: {str(e)}'}), 500

# --- PRELOADER ENDPOINTS ---
@app.route('/preloader/status', methods=['GET'])
@admin_required
def preloader_status():
    """Get preloader and scheduler status (admin only)"""
    try:
        # from services.preloader import scheduler_service # This line is removed
        
        # Get preloaded manga count from database
        from models import PreloadedManga
        manga_count = PreloadedManga.query.count()
        
        return jsonify({
            'scheduler': 'N/A (Simple TTL cache)', # Changed from scheduler_service
            'preloaded_manga_count': manga_count,
            'sources': list(ENABLED_SOURCES.keys())
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get preloader status: {str(e)}'}), 500

@app.route('/preloader/trigger', methods=['POST'])
@admin_required
def trigger_preload():
    """Manually trigger preloading (admin only)"""
    try:
        data = request.get_json() or {}
        source = data.get('source')  # Optional: specific source
        
        # Trigger preload in background thread
        import threading
        # from services.preloader import preloader_service # This line is removed
        
        def run_comprehensive_preload():
            try:
                with app.app_context():
                    if source:
                        # Comprehensive preload for specific source
                        # preloader_service.preload_source(source, page_limit=3) # This line is removed
                        # preloader_service.preload_popular_search_terms(source) # This line is removed
                        print(f"Comprehensive preload triggered for specific source: {source}")
                    else:
                        # Comprehensive preload for all sources
                        for src in ['weebcentral', 'asurascans', 'mangadex']:
                            # preloader_service.preload_source(src, page_limit=3) # This line is removed
                            # preloader_service.preload_popular_search_terms(src) # This line is removed
                            print(f"Comprehensive preload triggered for all sources: {src}")
            except Exception as e:
                print(f"Comprehensive preload error: {e}")
        
        thread = threading.Thread(target=run_comprehensive_preload, daemon=True)
        thread.start()
        
        return jsonify({
            'message': f'Comprehensive preload triggered for {source if source else "all sources"}'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to trigger comprehensive preload: {str(e)}'}), 500

@app.route('/preloader/search-stats', methods=['GET'])
@admin_required
def preloader_search_stats():
    """Get statistics about preloaded searches (admin only)"""
    try:
        from models import PreloadedManga
        from sqlalchemy import func
        
        # Get top searched manga
        popular_manga = PreloadedManga.query.order_by(
            PreloadedManga.popularity.desc()
        ).limit(20).all()
        
        # Get source distribution
        source_stats = db.session.query(
            PreloadedManga.source,
            func.count(PreloadedManga.id).label('count')
        ).group_by(PreloadedManga.source).all()
        
        return jsonify({
            'popular_manga': [
                {
                    'title': m.title,
                    'source': m.source,
                    'popularity': m.popularity,
                    'last_accessed': m.last_accessed.isoformat() if m.last_accessed else None
                } for m in popular_manga
            ],
            'source_distribution': {
                source: count for source, count in source_stats
            }
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get search stats: {str(e)}'}), 500

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
        # Don't reveal if email exists or not for security
        return jsonify({'message': 'If an account with that email exists, a password reset link has been sent.'}), 200
    
    # Check if there's already an unused token for this user
    existing_token = PasswordResetToken.query.filter_by(user_id=user.id, used=False).first()
    if existing_token and existing_token.expires_at > datetime.utcnow():
        # Token still valid, return the same message
        return jsonify({'message': 'If an account with that email exists, a password reset link has been sent.'}), 200
    
    # Generate new token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    # Mark old tokens as used
    if existing_token:
        existing_token.used = True
    
    prt = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
    db.session.add(prt)
    db.session.commit()
    
    # Send email with reset link
    reset_url = f"http://localhost:5173/reset-password?token={token}"
    
    # Try to send email
    print(f"📧 Sending password reset email to {user.email}")
    email_sent, email_error = send_password_reset_email(user.email, user.username, reset_url)
    
    if email_sent:
        print(f"✅ Password reset email sent successfully to {user.email}")
        return jsonify({
            'message': 'Password reset link has been sent to your email.'
        }), 200
    else:
        # Log the error but don't expose it to the user
        print(f"❌ Failed to send password reset email to {user.email}: {email_error}")
        return jsonify({
            'message': 'If an account with that email exists, a password reset link has been sent.'
        }), 200

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
    
    # Send confirmation email
    email_sent, email_error = send_password_reset_success_email(user.email, user.username)
    if not email_sent:
        print(f"Failed to send password reset success email: {email_error}")
    
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
        'hasAdmin': user.hasadmin
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
    
    # Get limit parameter, default to 50 if not specified
    limit = request.args.get('limit', type=int, default=50)
    
    history = ReadHistory.query.filter_by(user_id=user.id).order_by(ReadHistory.read_at.desc()).limit(limit).all()
    return jsonify([
        {
            'manga_title': h.manga_title,
            'chapter_title': h.chapter_title,
            'source': h.source,
            'manga_id': h.manga_id,
            'chapter_url': h.chapter_url,
            'read_at': h.read_at,
            'reading_time': h.reading_time,
            'pages_read': h.pages_read,
            'total_pages': h.total_pages,
            'completion_percentage': h.completion_percentage
        } for h in history
    ])

@app.route('/read-history/clear', methods=['DELETE'])
@auth_manager.login_required
def clear_read_history():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Delete all read history entries for the current user
        deleted_count = ReadHistory.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully cleared {deleted_count} read history entries.',
            'deleted_count': deleted_count
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to clear read history: {str(e)}'}), 500

# --- READING PROGRESS ENDPOINTS ---
@app.route('/reading-progress', methods=['GET'])
@auth_manager.login_required
def get_reading_progress():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    progress = ReadingProgress.query.filter_by(user_id=user.id).order_by(ReadingProgress.last_read_at.desc()).all()
    return jsonify([
        {
            'id': p.id,
            'manga_id': p.manga_id,
            'source': p.source,
            'manga_title': p.manga_title,
            'current_chapter': p.current_chapter,
            'current_page': p.current_page,
            'total_pages_in_chapter': p.total_pages_in_chapter,
            'chapters_read': p.chapters_read,
            'total_chapters': p.total_chapters,
            'completion_percentage': p.completion_percentage,
            'started_at': p.started_at,
            'last_read_at': p.last_read_at,
            'completed_at': p.completed_at,
            'total_reading_time': p.total_reading_time,
            'average_reading_speed': p.average_reading_speed
        } for p in progress
    ])

@app.route('/reading-progress/continue', methods=['GET'])
@auth_manager.login_required
def get_continue_reading():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get manga that are in progress (not completed)
    progress = ReadingProgress.query.filter_by(
        user_id=user.id
    ).filter(
        ReadingProgress.completed_at.is_(None)
    ).order_by(ReadingProgress.last_read_at.desc()).limit(5).all()
    
    return jsonify([
        {
            'manga_id': p.manga_id,
            'source': p.source,
            'manga_title': p.manga_title,
            'current_chapter': p.current_chapter,
            'current_page': p.current_page,
            'completion_percentage': p.completion_percentage,
            'last_read_at': p.last_read_at
        } for p in progress
    ])

@app.route('/reading-progress', methods=['POST'])
@auth_manager.login_required
def update_reading_progress():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    manga_id = data.get('manga_id')
    source = data.get('source')
    manga_title = data.get('manga_title')
    current_chapter = data.get('current_chapter')
    current_page = data.get('current_page', 1)
    total_pages_in_chapter = data.get('total_pages_in_chapter')
    chapters_read = data.get('chapters_read', 0)
    total_chapters = data.get('total_chapters')
    reading_time = data.get('reading_time', 0)
    
    if not all([manga_id, source, manga_title]):
        return jsonify({'error': 'manga_id, source, and manga_title are required'}), 400
    
    # Check if progress already exists
    progress = ReadingProgress.query.filter_by(
        user_id=user.id, 
        manga_id=manga_id, 
        source=source
    ).first()
    
    if progress:
        # Update existing progress
        progress.current_chapter = current_chapter
        progress.current_page = current_page
        progress.total_pages_in_chapter = total_pages_in_chapter
        progress.chapters_read = chapters_read
        progress.total_chapters = total_chapters
        progress.last_read_at = datetime.utcnow()
        progress.total_reading_time += reading_time
        
        # Calculate completion percentage
        if total_chapters and chapters_read:
            progress.completion_percentage = (chapters_read / total_chapters) * 100
            if progress.completion_percentage >= 100:
                progress.completed_at = datetime.utcnow()
        
        # Calculate average reading speed
        if progress.total_reading_time > 0:
            total_pages_read = progress.chapters_read * (progress.total_pages_in_chapter or 1)
            progress.average_reading_speed = (total_pages_read / progress.total_reading_time) * 60  # pages per minute
    else:
        # Create new progress
        completion_percentage = 0
        if total_chapters and chapters_read:
            completion_percentage = (chapters_read / total_chapters) * 100
        
        progress = ReadingProgress(
            user_id=user.id,
            manga_id=manga_id,
            source=source,
            manga_title=manga_title,
            current_chapter=current_chapter,
            current_page=current_page,
            total_pages_in_chapter=total_pages_in_chapter,
            chapters_read=chapters_read,
            total_chapters=total_chapters,
            completion_percentage=completion_percentage,
            total_reading_time=reading_time,
            last_read_at=datetime.utcnow()
        )
        db.session.add(progress)
    
    db.session.commit()
    return jsonify({'message': 'Reading progress updated successfully'})

# --- READING STATISTICS ENDPOINTS ---
@app.route('/reading-stats', methods=['GET'])
@auth_manager.login_required
def get_reading_stats():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Calculate statistics for the current month
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Total manga read this month
    manga_read_this_month = ReadHistory.query.filter(
        ReadHistory.user_id == user.id,
        ReadHistory.read_at >= start_of_month
    ).distinct(ReadHistory.manga_id).count()
    
    # Total reading time this month
    total_reading_time = ReadHistory.query.filter(
        ReadHistory.user_id == user.id,
        ReadHistory.read_at >= start_of_month
    ).with_entities(db.func.sum(ReadHistory.reading_time)).scalar() or 0
    
    total_hours = total_reading_time / 3600  # Convert seconds to hours
    
    # Reading streak calculation
    # This is a simplified version - you might want to implement a more sophisticated streak calculation
    current_streak = 0
    last_read_date = ReadHistory.query.filter_by(user_id=user.id).order_by(ReadHistory.read_at.desc()).first()
    if last_read_date:
        days_since_last_read = (now - last_read_date.read_at).days
        if days_since_last_read <= 1:
            current_streak = 1  # Simplified - you'd want to calculate actual streak
    
    # Average rating (from reading list entries)
    avg_rating = db.session.query(db.func.avg(ReadingListEntry.rating)).filter(
        ReadingListEntry.reading_list.has(user_id=user.id),
        ReadingListEntry.rating.isnot(None)
    ).scalar() or 0
    
    # Reading goals (example goals)
    goals = [
        {
            'title': 'Read 10 manga this month',
            'progress': manga_read_this_month,
            'target': 10,
            'description': 'Complete 10 different manga series'
        },
        {
            'title': 'Read for 20 hours this month',
            'progress': int(total_hours),
            'target': 20,
            'description': 'Spend 20 hours reading manga'
        },
        {
            'title': 'Maintain 7-day reading streak',
            'progress': current_streak,
            'target': 7,
            'description': 'Read manga for 7 consecutive days'
        }
    ]
    
    return jsonify({
        'total_manga': manga_read_this_month,
        'total_hours': total_hours,
        'current_streak': current_streak,
        'average_rating': float(avg_rating),
        'goals': goals
    })

# --- NOTIFICATIONS ENDPOINTS ---
@app.route('/notifications', methods=['GET'])
@auth_manager.login_required
def get_notifications():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(20).all()
    unread_count = Notification.query.filter_by(user_id=user.id, read=False).count()
    
    return jsonify({
        'notifications': [
            {
                'id': n.id,
                'type': n.type,
                'title': n.title,
                'message': n.message,
                'data': n.data,
                'read': n.read,
                'created_at': n.created_at
            } for n in notifications
        ],
        'unread_count': unread_count
    })

@app.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@auth_manager.login_required
def mark_notification_read(notification_id):
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.read = True
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as read'})

# --- READING LISTS ENDPOINTS ---
@app.route('/reading-lists', methods=['GET'])
@auth_manager.login_required
def get_reading_lists():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    lists = ReadingList.query.filter_by(user_id=user.id).all()
    return jsonify([
        {
            'id': l.id,
            'name': l.name,
            'description': l.description,
            'is_default': l.is_default,
            'color': l.color,
            'created_at': l.created_at,
            'updated_at': l.updated_at,
            'manga_count': len(l.manga_entries)
        } for l in lists
    ])

@app.route('/reading-lists', methods=['POST'])
@auth_manager.login_required
def create_reading_list():
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    color = data.get('color', '#3B82F6')
    
    if not name:
        return jsonify({'error': 'List name is required'}), 400
    
    # Check if list with same name already exists
    existing_list = ReadingList.query.filter_by(user_id=user.id, name=name).first()
    if existing_list:
        return jsonify({'error': 'A list with this name already exists'}), 400
    
    reading_list = ReadingList(
        user_id=user.id,
        name=name,
        description=description,
        color=color
    )
    db.session.add(reading_list)
    db.session.commit()
    
    return jsonify({
        'message': 'Reading list created successfully',
        'list': {
            'id': reading_list.id,
            'name': reading_list.name,
            'description': reading_list.description,
            'color': reading_list.color
        }
    })

@app.route('/reading-lists/<int:list_id>/manga', methods=['POST'])
@auth_manager.login_required
def add_manga_to_list(list_id):
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Verify the list belongs to the user
    reading_list = ReadingList.query.filter_by(id=list_id, user_id=user.id).first()
    if not reading_list:
        return jsonify({'error': 'Reading list not found'}), 404
    
    data = request.get_json()
    manga_id = data.get('manga_id')
    source = data.get('source')
    manga_title = data.get('manga_title')
    cover_url = data.get('cover_url')
    notes = data.get('notes', '')
    rating = data.get('rating')
    tags = data.get('tags', [])
    
    if not all([manga_id, source, manga_title]):
        return jsonify({'error': 'manga_id, source, and manga_title are required'}), 400
    
    # Check if manga is already in the list
    existing_entry = ReadingListEntry.query.filter_by(
        reading_list_id=list_id,
        manga_id=manga_id,
        source=source
    ).first()
    
    if existing_entry:
        return jsonify({'error': 'Manga is already in this list'}), 400
    
    entry = ReadingListEntry(
        reading_list_id=list_id,
        manga_id=manga_id,
        source=source,
        manga_title=manga_title,
        cover_url=cover_url,
        notes=notes,
        rating=rating,
        tags=tags
    )
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({'message': 'Manga added to list successfully'})

if __name__ == '__main__':
    port = int(os.getenv('PLAYWRIGHT_PORT', 5000))
    with app.app_context():
        db.create_all()
        # Simple TTL cache system - no scheduler needed
    app.run(host='0.0.0.0', port=port, debug=True) 