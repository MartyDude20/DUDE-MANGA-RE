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