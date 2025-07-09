import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import hashlib

# PostgreSQL support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

class CacheManager:
    def __init__(self, db_path: str = "manga_cache.db", use_postgres: bool = False, postgres_config: Optional[Dict] = None):
        self.db_path = db_path
        self.use_postgres = use_postgres and POSTGRES_AVAILABLE
        self.postgres_config = postgres_config or {
            'host': 'localhost',
            'port': 5432,
            'database': 'manga_cache',
            'user': 'postgres',
            'password': 'password'
        }
        self.init_database()
    
    def _get_connection(self):
        """Get database connection based on configuration"""
        if self.use_postgres:
            return psycopg2.connect(**self.postgres_config)
        else:
            return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize the database with required tables"""
        if self.use_postgres:
            self._init_postgres_database()
        else:
            self._init_sqlite_database()
    
    def _init_postgres_database(self):
        """Initialize PostgreSQL database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Search cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_cache (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    query_hash TEXT NOT NULL,
                    query TEXT NOT NULL,
                    source TEXT NOT NULL,
                    results JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    UNIQUE(user_id, query_hash, source)
                )
            ''')
            
            # Manga metadata cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS manga_cache (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    manga_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    image_url TEXT,
                    status TEXT,
                    author TEXT,
                    description TEXT,
                    chapters JSONB,
                    tags JSONB,
                    type TEXT,
                    released TEXT,
                    official_translation TEXT,
                    anime_adaptation TEXT,
                    adult_content TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_refreshed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, manga_id, source)
                )
            ''')
            
            # Chapter cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chapter_cache (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    chapter_url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    images JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, chapter_url)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_user_query_hash ON search_cache(user_id, query_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_expires ON search_cache(expires_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_manga_user_id_source ON manga_cache(user_id, manga_id, source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_manga_last_updated ON manga_cache(last_updated)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chapter_user_url ON chapter_cache(user_id, chapter_url)')
            
            # JSONB indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_manga_tags_gin ON manga_cache USING GIN (tags)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_manga_chapters_gin ON manga_cache USING GIN (chapters)')
            
            conn.commit()
    
    def _init_sqlite_database(self):
        """Initialize SQLite database (existing code)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Search cache table - add user_id column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    query_hash TEXT NOT NULL,
                    query TEXT NOT NULL,
                    source TEXT NOT NULL,
                    results TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    UNIQUE(user_id, query_hash, source)
                )
            ''')
            
            # Manga metadata cache table - add user_id column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS manga_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    manga_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    image_url TEXT,
                    status TEXT,
                    author TEXT,
                    description TEXT,
                    chapters TEXT,
                    tags TEXT,
                    type TEXT,
                    released TEXT,
                    official_translation TEXT,
                    anime_adaptation TEXT,
                    adult_content TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_refreshed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, manga_id, source)
                )
            ''')
            
            # Add new columns to existing table if they don't exist
            try:
                cursor.execute('ALTER TABLE manga_cache ADD COLUMN tags TEXT')
            except sqlite3.OperationalError:
                pass  # Column already exists
                
            try:
                cursor.execute('ALTER TABLE manga_cache ADD COLUMN type TEXT')
            except sqlite3.OperationalError:
                pass  # Column already exists
                
            try:
                cursor.execute('ALTER TABLE manga_cache ADD COLUMN released TEXT')
            except sqlite3.OperationalError:
                pass  # Column already exists
                
            try:
                cursor.execute('ALTER TABLE manga_cache ADD COLUMN official_translation TEXT')
            except sqlite3.OperationalError:
                pass  # Column already exists
                
            try:
                cursor.execute('ALTER TABLE manga_cache ADD COLUMN anime_adaptation TEXT')
            except sqlite3.OperationalError:
                pass  # Column already exists
                
            try:
                cursor.execute('ALTER TABLE manga_cache ADD COLUMN adult_content TEXT')
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            # Chapter cache table - add user_id column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chapter_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    chapter_url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    images TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, chapter_url)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_user_query_hash ON search_cache(user_id, query_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_expires ON search_cache(expires_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_manga_user_id_source ON manga_cache(user_id, manga_id, source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_manga_last_updated ON manga_cache(last_updated)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chapter_user_url ON chapter_cache(user_id, chapter_url)')
            
            conn.commit()
    
    def _hash_query(self, query: str) -> str:
        """Create a hash for the search query"""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def get_cached_search(self, query: str, source: str, user_id: Optional[int] = None) -> Optional[List[Dict]]:
        """Get cached search results"""
        query_hash = self._hash_query(query)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT results, expires_at FROM search_cache 
                WHERE user_id = ? AND query_hash = ? AND source = ? AND expires_at > ?
            ''', (user_id, query_hash, source, datetime.now()))
            
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
    
    def cache_search_results(self, query: str, source: str, results: List[Dict], 
                           user_id: Optional[int] = None, expire_hours: int = 24) -> None:
        """Cache search results"""
        query_hash = self._hash_query(query)
        expires_at = datetime.now() + timedelta(hours=expire_hours)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO search_cache 
                (user_id, query_hash, query, source, results, expires_at) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, query_hash, query, source, json.dumps(results), expires_at))
            conn.commit()
    
    def get_cached_manga(self, manga_id: str, source: str, user_id: Optional[int] = None) -> Optional[Dict]:
        """Get cached manga details"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if self.use_postgres:
                cursor.execute('''
                    SELECT title, image_url, status, author, description, chapters, 
                           tags, type, released, official_translation, anime_adaptation, adult_content,
                           last_updated, last_refreshed 
                    FROM manga_cache 
                    WHERE user_id = %s AND manga_id = %s AND source = %s
                ''', (user_id, manga_id, source))
            else:
                cursor.execute('''
                    SELECT title, image_url, status, author, description, chapters, 
                           tags, type, released, official_translation, anime_adaptation, adult_content,
                           last_updated, last_refreshed 
                    FROM manga_cache 
                    WHERE user_id = ? AND manga_id = ? AND source = ?
                ''', (user_id, manga_id, source))
            
            result = cursor.fetchone()
            if result:
                return {
                    'title': result[0],
                    'image': result[1],
                    'status': result[2],
                    'author': result[3],
                    'description': result[4],
                    'chapters': result[5] if self.use_postgres else (json.loads(result[5]) if result[5] else []),
                    'tags': result[6] if self.use_postgres else (json.loads(result[6]) if result[6] else []),
                    'type': result[7],
                    'released': result[8],
                    'official_translation': result[9],
                    'anime_adaptation': result[10],
                    'adult_content': result[11],
                    'last_updated': result[12],
                    'last_refreshed': result[13]
                }
            return None
    
    def cache_manga_details(self, manga_id: str, source: str, manga_data: Dict, user_id: Optional[int] = None) -> None:
        """Cache manga details"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            chapters_data = manga_data.get('chapters', [])
            tags_data = manga_data.get('tags', [])
            
            if self.use_postgres:
                cursor.execute('''
                    INSERT INTO manga_cache 
                    (user_id, manga_id, source, title, image_url, status, author, description, chapters, 
                     tags, type, released, official_translation, anime_adaptation, adult_content,
                     last_updated, last_refreshed) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, manga_id, source) 
                    DO UPDATE SET
                        title = EXCLUDED.title,
                        image_url = EXCLUDED.image_url,
                        status = EXCLUDED.status,
                        author = EXCLUDED.author,
                        description = EXCLUDED.description,
                        chapters = EXCLUDED.chapters,
                        tags = EXCLUDED.tags,
                        type = EXCLUDED.type,
                        released = EXCLUDED.released,
                        official_translation = EXCLUDED.official_translation,
                        anime_adaptation = EXCLUDED.anime_adaptation,
                        adult_content = EXCLUDED.adult_content,
                        last_updated = EXCLUDED.last_updated,
                        last_refreshed = EXCLUDED.last_refreshed
                ''', (
                    user_id, manga_id, source, manga_data.get('title'), manga_data.get('image'),
                    manga_data.get('status'), manga_data.get('author'), manga_data.get('description'),
                    json.dumps(chapters_data), 
                    json.dumps(tags_data), manga_data.get('type'), manga_data.get('released'),
                    manga_data.get('official_translation'), manga_data.get('anime_adaptation'), 
                    manga_data.get('adult_content'), datetime.now(), datetime.now()
                ))
            else:
                cursor.execute('''
                    INSERT OR REPLACE INTO manga_cache 
                    (user_id, manga_id, source, title, image_url, status, author, description, chapters, 
                     tags, type, released, official_translation, anime_adaptation, adult_content,
                     last_updated, last_refreshed) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, manga_id, source, manga_data.get('title'), manga_data.get('image'),
                    manga_data.get('status'), manga_data.get('author'), manga_data.get('description'),
                    json.dumps(chapters_data), 
                    json.dumps(tags_data), manga_data.get('type'), manga_data.get('released'),
                    manga_data.get('official_translation'), manga_data.get('anime_adaptation'), 
                    manga_data.get('adult_content'), datetime.now(), datetime.now()
                ))
            conn.commit()
    
    def update_manga_refresh_time(self, manga_id: str, source: str, user_id: Optional[int] = None) -> None:
        """Update the last refresh time for a manga"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE manga_cache 
                SET last_refreshed = ? 
                WHERE user_id = ? AND manga_id = ? AND source = ?
            ''', (datetime.now(), user_id, manga_id, source))
            conn.commit()
    
    def get_cached_chapter_images(self, chapter_url: str, user_id: Optional[int] = None) -> Optional[List[str]]:
        """Get cached chapter images"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT images FROM chapter_cache 
                WHERE user_id = ? AND chapter_url = ?
            ''', (user_id, chapter_url))
            
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
    
    def cache_chapter_images(self, chapter_url: str, source: str, images: List[str], user_id: Optional[int] = None) -> None:
        """Cache chapter images"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO chapter_cache 
                (user_id, chapter_url, source, images) 
                VALUES (?, ?, ?, ?)
            ''', (user_id, chapter_url, source, json.dumps(images)))
            conn.commit()
    
    def clear_expired_cache(self, user_id: Optional[int] = None) -> None:
        """Clear expired search cache entries"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute('DELETE FROM search_cache WHERE user_id = ? AND expires_at < ?', (user_id, datetime.now()))
            else:
                cursor.execute('DELETE FROM search_cache WHERE expires_at < ?', (datetime.now(),))
            conn.commit()
    
    def clear_manga_cache(self, user_id: Optional[int] = None, manga_id: Optional[str] = None, source: Optional[str] = None) -> None:
        """Clear manga cache for specific user, manga or source"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                if manga_id and source:
                    cursor.execute('DELETE FROM manga_cache WHERE user_id = ? AND manga_id = ? AND source = ?', 
                                 (user_id, manga_id, source))
                elif source:
                    cursor.execute('DELETE FROM manga_cache WHERE user_id = ? AND source = ?', (user_id, source))
                elif manga_id:
                    cursor.execute('DELETE FROM manga_cache WHERE user_id = ? AND manga_id = ?', (user_id, manga_id))
                else:
                    cursor.execute('DELETE FROM manga_cache WHERE user_id = ?', (user_id,))
            else:
                if manga_id and source:
                    cursor.execute('DELETE FROM manga_cache WHERE manga_id = ? AND source = ?', 
                                 (manga_id, source))
                elif source:
                    cursor.execute('DELETE FROM manga_cache WHERE source = ?', (source,))
                elif manga_id:
                    cursor.execute('DELETE FROM manga_cache WHERE manga_id = ?', (manga_id,))
                else:
                    cursor.execute('DELETE FROM manga_cache')
            conn.commit()
    
    def clear_search_cache(self, user_id: Optional[int] = None, query: Optional[str] = None, source: Optional[str] = None) -> None:
        """Clear search cache for specific user, query or source"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                if query and source:
                    query_hash = self._hash_query(query)
                    cursor.execute('DELETE FROM search_cache WHERE user_id = ? AND query_hash = ? AND source = ?', 
                                 (user_id, query_hash, source))
                elif source:
                    cursor.execute('DELETE FROM search_cache WHERE user_id = ? AND source = ?', (user_id, source))
                elif query:
                    query_hash = self._hash_query(query)
                    cursor.execute('DELETE FROM search_cache WHERE user_id = ? AND query_hash = ?', (user_id, query_hash))
                else:
                    cursor.execute('DELETE FROM search_cache WHERE user_id = ?', (user_id,))
            else:
                if query and source:
                    query_hash = self._hash_query(query)
                    cursor.execute('DELETE FROM search_cache WHERE query_hash = ? AND source = ?', 
                                 (query_hash, source))
                elif source:
                    cursor.execute('DELETE FROM search_cache WHERE source = ?', (source,))
                elif query:
                    query_hash = self._hash_query(query)
                    cursor.execute('DELETE FROM search_cache WHERE query_hash = ?', (query_hash,))
                else:
                    cursor.execute('DELETE FROM search_cache')
            conn.commit()
    
    def clear_chapter_cache(self, user_id: Optional[int] = None, source: Optional[str] = None) -> None:
        """Clear chapter cache for specific user or source"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                if source:
                    cursor.execute('DELETE FROM chapter_cache WHERE user_id = ? AND source = ?', (user_id, source))
                else:
                    cursor.execute('DELETE FROM chapter_cache WHERE user_id = ?', (user_id,))
            else:
                if source:
                    cursor.execute('DELETE FROM chapter_cache WHERE source = ?', (source,))
                else:
                    cursor.execute('DELETE FROM chapter_cache')
            conn.commit()
    
    def get_cache_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get cache statistics for specific user or all users"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build WHERE clause for user filtering
            user_filter = "WHERE user_id = ?" if user_id is not None else ""
            user_params = (user_id,) if user_id is not None else ()
            
            # Search cache stats
            cursor.execute(f'SELECT COUNT(*) FROM search_cache {user_filter}', user_params)
            search_count = cursor.fetchone()[0]
            
            if user_id is not None:
                cursor.execute('SELECT COUNT(*) FROM search_cache WHERE user_id = ? AND expires_at < ?', (user_id, datetime.now()))
            else:
                cursor.execute('SELECT COUNT(*) FROM search_cache WHERE expires_at < ?', (datetime.now(),))
            expired_search_count = cursor.fetchone()[0]
            
            # Manga cache stats
            cursor.execute(f'SELECT COUNT(*) FROM manga_cache {user_filter}', user_params)
            manga_count = cursor.fetchone()[0]
            
            # Chapter cache stats
            cursor.execute(f'SELECT COUNT(*) FROM chapter_cache {user_filter}', user_params)
            chapter_count = cursor.fetchone()[0]
            
            # Source breakdown
            if user_id is not None:
                cursor.execute('SELECT source, COUNT(*) FROM manga_cache WHERE user_id = ? GROUP BY source', (user_id,))
            else:
                cursor.execute('SELECT source, COUNT(*) FROM manga_cache GROUP BY source')
            source_breakdown = dict(cursor.fetchall())
            
            return {
                'search_cache': {
                    'total': search_count,
                    'expired': expired_search_count,
                    'active': search_count - expired_search_count
                },
                'manga_cache': {
                    'total': manga_count,
                    'sources': source_breakdown
                },
                'chapter_cache': {
                    'total': chapter_count
                }
            } 