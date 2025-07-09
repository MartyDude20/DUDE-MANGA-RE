# PostgreSQL Cache Setup Guide

This guide shows how to use PostgreSQL instead of SQLite for the manga cache database.

## Benefits of PostgreSQL Cache

- **Better Performance**: Faster queries, better indexing
- **Concurrent Access**: Multiple users/processes can access simultaneously
- **Advanced Features**: JSONB columns, full-text search, better data types
- **Scalability**: Can handle much larger datasets
- **Production Ready**: More robust than SQLite for production use

## Setup Instructions

### 1. Install PostgreSQL Dependencies

```bash
pip install -r requirements_postgres.txt
```

### 2. Install PostgreSQL Server

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Or use WSL2 with Ubuntu

**macOS:**
```bash
brew install postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### 3. Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE manga_cache;
CREATE USER manga_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE manga_cache TO manga_user;
\q
```

### 4. Configure Environment Variables

Create a `.env` file in the `playwright_service` directory:

```env
# Enable PostgreSQL cache
USE_POSTGRES_CACHE=true

# PostgreSQL connection settings
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=manga_cache
POSTGRES_USER=manga_user
POSTGRES_PASSWORD=your_password

# Optional: Custom SQLite path (if not using PostgreSQL)
# SQLITE_DB_PATH=manga_cache.db
```

### 5. Test the Setup

```bash
# Test with PostgreSQL
python test_postgres_cache.py

# Test with SQLite (fallback)
USE_POSTGRES_CACHE=false python test_postgres_cache.py
```

## Usage in Your Application

### Option 1: Environment-based Configuration

```python
from cache_manager import CacheManager
from cache_config import get_cache_config

# Automatically uses PostgreSQL if USE_POSTGRES_CACHE=true
config = get_cache_config()
cache_manager = CacheManager(**config)
```

### Option 2: Direct Configuration

```python
from cache_manager import CacheManager

# Use PostgreSQL
cache_manager = CacheManager(
    use_postgres=True,
    postgres_config={
        'host': 'localhost',
        'port': 5432,
        'database': 'manga_cache',
        'user': 'manga_user',
        'password': 'your_password'
    }
)

# Use SQLite (fallback)
cache_manager = CacheManager(use_postgres=False)
```

## PostgreSQL-Specific Features

### JSONB Queries

```python
# Find manga with specific tags
cursor.execute('''
    SELECT title, tags FROM manga_cache 
    WHERE tags ? 'Action' AND source = 'weebcentral'
''')

# Find manga with multiple tags
cursor.execute('''
    SELECT title, tags FROM manga_cache 
    WHERE tags ?& ARRAY['Action', 'Comedy'] AND source = 'weebcentral'
''')

# Full-text search in descriptions
cursor.execute('''
    SELECT title, description FROM manga_cache 
    WHERE to_tsvector('english', description) @@ plainto_tsquery('english', 'ghost soul')
''')
```

### Performance Indexes

The cache manager automatically creates these indexes:

- **GIN indexes** on JSONB columns (tags, chapters)
- **B-tree indexes** on frequently queried columns
- **Composite indexes** for user-source combinations

## Migration from SQLite

If you have existing SQLite data:

1. **Export from SQLite:**
```python
import sqlite3
import json

with sqlite3.connect('manga_cache.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM manga_cache')
    data = cursor.fetchall()
    
# Save to JSON for migration
with open('manga_cache_export.json', 'w') as f:
    json.dump(data, f)
```

2. **Import to PostgreSQL:**
```python
from cache_manager import CacheManager

cache_manager = CacheManager(use_postgres=True, postgres_config={...})

# Load and insert data
with open('manga_cache_export.json', 'r') as f:
    data = json.load(f)
    
for row in data:
    # Convert row data to manga_data dict
    manga_data = {...}  # Convert from row format
    cache_manager.cache_manga_details(manga_id, source, manga_data)
```

## Troubleshooting

### Connection Issues
- Check PostgreSQL service is running: `sudo systemctl status postgresql`
- Verify connection settings in `.env`
- Test connection: `psql -h localhost -U manga_user -d manga_cache`

### Performance Issues
- Monitor query performance with `EXPLAIN ANALYZE`
- Add additional indexes for your specific query patterns
- Consider connection pooling for high-traffic applications

### Data Migration Issues
- Ensure JSON data is properly formatted
- Check for encoding issues with special characters
- Verify all required columns are present 