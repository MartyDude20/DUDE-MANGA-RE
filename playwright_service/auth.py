import jwt
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from flask_bcrypt import Bcrypt
from models import db, User

# Initialize Redis for token blacklisting (optional)
try:
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    redis_client = None

class AuthManager:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.secret_key = app.config.get('SECRET_KEY', 'your-secret-key-change-this')
        self.access_token_expiry = timedelta(minutes=30)  # 30 minutes
        self.refresh_token_expiry = timedelta(days=7)     # 7 days
        
        # Configure secure cookies
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    def create_tokens(self, user_id):
        """Create access and refresh tokens"""
        # Access token (short-lived)
        access_payload = {
            'user_id': user_id,
            'type': 'access',
            'exp': datetime.utcnow() + self.access_token_expiry
        }
        access_token = jwt.encode(access_payload, self.secret_key, algorithm='HS256')
        
        # Refresh token (long-lived)
        refresh_payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + self.refresh_token_expiry
        }
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm='HS256')
        
        return access_token, refresh_token
    
    def verify_token(self, token, token_type='access'):
        """Verify and decode a token"""
        try:
            # Check if token is blacklisted (only if Redis is available)
            if REDIS_AVAILABLE and redis_client:
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                if redis_client.exists(f"blacklist:{token_hash}"):
                    return None, "Token has been revoked"
            
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Verify token type
            if payload.get('type') != token_type:
                return None, "Invalid token type"
            
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
    
    def blacklist_token(self, token):
        """Add token to blacklist"""
        if REDIS_AVAILABLE and redis_client:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            # Store for the same duration as the token expiry
            redis_client.setex(f"blacklist:{token_hash}", 3600, "revoked")  # 1 hour
    
    def authenticate_user(self, username, password):
        """Authenticate user with username/password"""
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            return user
        return None
    
    def login_required(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            
            if not token:
                return jsonify({'error': 'Token is missing'}), 401
            
            payload, error = self.verify_token(token, 'access')
            if error:
                return jsonify({'error': error}), 401
            
            # Get user from database
            user = User.query.get(payload['user_id'])
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            # Add user to request context
            request.current_user = user
            return f(*args, **kwargs)
        
        return decorated_function
    
    def optional_auth(self, f):
        """Decorator for optional authentication (for anonymous users)"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            if token:
                payload, error = self.verify_token(token, 'access')
                if not error:
                    user = User.query.get(payload['user_id'])
                    if user:
                        request.current_user = user
                        request.is_authenticated = True
                        return f(*args, **kwargs)
            # No valid token, continue as anonymous user
            request.current_user = None
            request.is_authenticated = False
            return f(*args, **kwargs)
        return decorated_function

# Initialize bcrypt
bcrypt = Bcrypt()

# Create auth manager instance
auth_manager = AuthManager()

def init_auth(app):
    """Initialize authentication with Flask app"""
    auth_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Add auth endpoints
    @app.route('/login', methods=['POST'])
    def login():
        """Login endpoint"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = auth_manager.authenticate_user(username, password)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create tokens
        access_token, refresh_token = auth_manager.create_tokens(user.id)
        
        # Set refresh token as httpOnly cookie
        response = jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'access_token': access_token
        })
        
        # Set secure httpOnly cookie for refresh token
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=False,  # Set to False for HTTP development
            samesite='Lax',
            max_age=7 * 24 * 3600  # 7 days
        )
        
        # Set CORS headers to allow Authorization header
        response.headers['Access-Control-Expose-Headers'] = 'Authorization'
        
        return response, 200, {
            'Authorization': f'Bearer {access_token}'
        }
    
    @app.route('/refresh', methods=['POST'])
    def refresh():
        """Refresh access token"""
        refresh_token = request.cookies.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token is missing'}), 401
        
        payload, error = auth_manager.verify_token(refresh_token, 'refresh')
        if error:
            return jsonify({'error': error}), 401
        
        # Create new access token
        access_token, new_refresh_token = auth_manager.create_tokens(payload['user_id'])
        
        # Blacklist old refresh token (token rotation)
        auth_manager.blacklist_token(refresh_token)
        
        response = jsonify({'message': 'Token refreshed successfully'})
        
        # Set new refresh token as httpOnly cookie
        response.set_cookie(
            'refresh_token',
            new_refresh_token,
            httponly=True,
            secure=False,  # Set to False for HTTP development
            samesite='Lax',
            max_age=7 * 24 * 3600
        )
        
        # Set CORS headers to allow Authorization header
        response.headers['Access-Control-Expose-Headers'] = 'Authorization'
        
        return response, 200, {
            'Authorization': f'Bearer {access_token}'
        }
    
    @app.route('/logout', methods=['POST'])
    def logout():
        """Logout endpoint"""
        # Get current access token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
            auth_manager.blacklist_token(access_token)
        
        # Get refresh token from cookie
        refresh_token = request.cookies.get('refresh_token')
        if refresh_token:
            auth_manager.blacklist_token(refresh_token)
        
        response = jsonify({'message': 'Logout successful'})
        response.delete_cookie('refresh_token')
        
        return response
    
    @app.route('/me', methods=['GET'])
    @auth_manager.login_required
    def get_current_user():
        """Get current user info"""
        user = request.current_user
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat()
        }) 