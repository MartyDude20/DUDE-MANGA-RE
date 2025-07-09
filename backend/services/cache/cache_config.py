import os
from typing import Dict, Optional

# Cache Database Configuration
# Set USE_POSTGRES_CACHE=True to use PostgreSQL instead of SQLite

USE_POSTGRES_CACHE = os.getenv('USE_POSTGRES_CACHE', 'false').lower() == 'true'

# PostgreSQL Configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'database': os.getenv('POSTGRES_DB', 'manga_cache'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password')
}

# SQLite Configuration (fallback)
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'manga_cache.db')

def get_cache_config() -> Dict:
    """Get cache configuration based on environment"""
    if USE_POSTGRES_CACHE:
        return {
            'use_postgres': True,
            'postgres_config': POSTGRES_CONFIG
        }
    else:
        return {
            'use_postgres': False,
            'db_path': SQLITE_DB_PATH
        }

# Example usage:
# from cache_manager import CacheManager
# from cache_config import get_cache_config
# 
# config = get_cache_config()
# cache_manager = CacheManager(**config) 