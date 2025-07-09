from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# SQLAlchemy instance (to be initialized in app.py)
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    hasAdmin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Example for future cache table (user-scoped)
# class MangaCache(db.Model):
#     __tablename__ = 'manga_cache'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
#     ... # other fields 

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(128), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

class ReadHistory(db.Model):
    __tablename__ = 'read_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manga_title = db.Column(db.String(255), nullable=False)
    chapter_title = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(64), nullable=False)
    manga_id = db.Column(db.String(128), nullable=False)
    chapter_url = db.Column(db.String(255), nullable=False)
    read_at = db.Column(db.DateTime, default=datetime.utcnow)

class PreloadJob(db.Model):
    __tablename__ = 'preload_jobs'
    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(32), nullable=False)  # 'search', 'manga_details', 'chapter_images'
    source = db.Column(db.String(64), nullable=False)
    target_id = db.Column(db.String(255), nullable=False)  # query, manga_id, or chapter_url
    status = db.Column(db.String(32), default='pending')  # pending, running, completed, failed
    priority = db.Column(db.Integer, default=5)  # 1-10, lower is higher priority
    scheduled_at = db.Column(db.DateTime, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    max_retries = db.Column(db.Integer, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PreloadJob {self.job_type}:{self.source}:{self.target_id}>'

class PreloadStats(db.Model):
    __tablename__ = 'preload_stats'
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(64), nullable=False)
    job_type = db.Column(db.String(32), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_jobs = db.Column(db.Integer, default=0)
    successful_jobs = db.Column(db.Integer, default=0)
    failed_jobs = db.Column(db.Integer, default=0)
    total_errors = db.Column(db.Integer, default=0)
    avg_response_time = db.Column(db.Float)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('source', 'job_type', 'date'),)
    
    def __repr__(self):
        return f'<PreloadStats {self.source}:{self.job_type}:{self.date}>'

class RobotsTxtCache(db.Model):
    __tablename__ = 'robots_txt_cache'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False, unique=True)
    robots_content = db.Column(db.Text)
    crawl_delay = db.Column(db.Float)  # in seconds
    user_agent = db.Column(db.String(255))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    is_allowed = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<RobotsTxtCache {self.domain}>' 