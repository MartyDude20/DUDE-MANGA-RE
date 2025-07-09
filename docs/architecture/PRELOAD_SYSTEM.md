# Preload System Documentation

## Overview

The preload system is designed to improve user experience by preloading popular manga data in the background. It operates with respectful rate limiting, robots.txt compliance, and intelligent scheduling to avoid overwhelming external sources.

## Features

### 🚀 Daily Preloading
- **Search Results**: Preloads popular search terms across all sources
- **Manga Details**: Preloads details for recently popular manga
- **Chapter Images**: Preloads first few chapters of popular manga
- **Randomized Timing**: Jobs are scheduled at random times between 2-6 AM to spread load

### 🛡️ Respectful Crawling
- **Robots.txt Compliance**: Automatically fetches and respects robots.txt files
- **Rate Limiting**: Configurable delays between requests per source
- **Randomization**: Adds ±20% randomization to delays to avoid patterns
- **User Agent**: Proper user agent identification for all requests

### 📊 Monitoring & Statistics
- **Job Tracking**: Monitor job status, success rates, and response times
- **Error Handling**: Comprehensive error tracking and retry logic
- **Performance Metrics**: Average response times and success rates per source
- **Admin Dashboard**: Web interface for managing the preload system

### 🔧 Admin Controls
- **Worker Management**: Start/stop the background worker
- **Job Creation**: Manually create daily preload jobs
- **Cleanup**: Remove old completed/failed jobs
- **Robots.txt Updates**: Refresh robots.txt cache for all sources

## Database Schema

### PreloadJob Table
```sql
CREATE TABLE preload_jobs (
    id INTEGER PRIMARY KEY,
    job_type TEXT NOT NULL,           -- 'search', 'manga_details', 'chapter_images'
    source TEXT NOT NULL,             -- 'weebcentral', 'asurascans', 'mangadex'
    target_id TEXT NOT NULL,          -- query, manga_id, or chapter_url
    status TEXT DEFAULT 'pending',    -- 'pending', 'running', 'completed', 'failed'
    priority INTEGER DEFAULT 5,       -- 1-10, lower is higher priority
    scheduled_at TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### PreloadStats Table
```sql
CREATE TABLE preload_stats (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    job_type TEXT NOT NULL,
    date DATE NOT NULL,
    total_jobs INTEGER DEFAULT 0,
    successful_jobs INTEGER DEFAULT 0,
    failed_jobs INTEGER DEFAULT 0,
    total_errors INTEGER DEFAULT 0,
    avg_response_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, job_type, date)
);
```

### RobotsTxtCache Table
```sql
CREATE TABLE robots_txt_cache (
    id INTEGER PRIMARY KEY,
    domain TEXT NOT NULL UNIQUE,
    robots_content TEXT,
    crawl_delay FLOAT,
    user_agent TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_allowed BOOLEAN DEFAULT TRUE
);
```

## Configuration

### Source Configurations
Each source has specific rate limiting and crawling settings:

```python
source_configs = {
    'weebcentral': {
        'base_delay': 2.0,           # seconds between requests
        'crawl_delay': 1.0,          # from robots.txt
        'max_requests_per_hour': 100,
        'user_agent': 'MangaReader/1.0 (+https://github.com/your-repo)',
        'domain': 'weebcentral.com'
    },
    'asurascans': {
        'base_delay': 3.0,
        'crawl_delay': 2.0,
        'max_requests_per_hour': 50,
        'user_agent': 'MangaReader/1.0 (+https://github.com/your-repo)',
        'domain': 'asura.gg'
    },
    'mangadex': {
        'base_delay': 1.0,
        'crawl_delay': 0.5,
        'max_requests_per_hour': 200,
        'user_agent': 'MangaReader/1.0 (+https://github.com/your-repo)',
        'domain': 'api.mangadex.org'
    }
}
```

### Popular Search Terms
The system preloads these popular manga titles:
- One Piece, Naruto, Dragon Ball, Bleach, Attack on Titan
- My Hero Academia, Demon Slayer, Jujutsu Kaisen, Spy x Family
- Chainsaw Man, Tokyo Ghoul, Death Note, Fullmetal Alchemist
- And many more...

## API Endpoints

### Admin-Only Endpoints
All preload endpoints require admin authentication.

#### GET /preload/stats
Get preload statistics for the last N days.
- Query params: `days` (default: 7)
- Returns: Statistics grouped by source and job type

#### GET /preload/jobs
Get current preload jobs.
- Query params: `status`, `source`, `limit`
- Returns: List of jobs with status and details

#### POST /preload/create-daily
Create daily preload jobs for tomorrow.
- Returns: Number of jobs created

#### POST /preload/start-worker
Start the background preload worker.
- Returns: Success message

#### POST /preload/stop-worker
Stop the background preload worker.
- Returns: Success message

#### POST /preload/cleanup
Clean up old completed/failed jobs.
- Query params: `days` (default: 7)
- Returns: Cleanup confirmation

#### POST /preload/update-robots
Update robots.txt cache for all sources.
- Returns: Update confirmation

#### GET /preload/status
Get current preload system status.
- Returns: Worker status, job counts, today's statistics

## Usage

### 1. Setup Database
```bash
cd playwright_service
python setup_preload_tables.py
```

### 2. Test the System
```bash
python test_preload_system.py
```

### 3. Start the Backend
```bash
python app.py
```

### 4. Access Admin Interface
1. Navigate to the PreloadManager component in the frontend
2. Use admin credentials to access the interface
3. Monitor and manage the preload system

### 5. Monitor Performance
- Check the Statistics tab for success rates and response times
- Monitor the Jobs tab for job status and errors
- Use the Status tab for real-time system overview

## Best Practices

### Rate Limiting
- The system automatically respects robots.txt crawl delays
- Base delays are configured per source to be respectful
- Randomization prevents predictable request patterns

### Error Handling
- Failed jobs are retried up to 3 times
- Comprehensive error logging for debugging
- Graceful degradation when sources are unavailable

### Resource Management
- Old jobs are automatically cleaned up after 7 days
- Failed jobs are kept longer for debugging
- Database indexes optimize query performance

### Monitoring
- Track success rates to identify problematic sources
- Monitor response times to detect performance issues
- Use the admin interface to manage the system proactively

## Troubleshooting

### Common Issues

#### Worker Not Starting
- Check if another worker is already running
- Verify admin authentication
- Check server logs for errors

#### High Failure Rates
- Check source availability and robots.txt changes
- Review error messages in the jobs list
- Consider adjusting rate limits for problematic sources

#### Database Issues
- Ensure tables are created with `setup_preload_tables.py`
- Check database permissions and connectivity
- Verify SQLite file permissions

#### Performance Issues
- Monitor response times in statistics
- Consider reducing job frequency for slow sources
- Check server resources and network connectivity

### Debug Commands
```bash
# Test the preload system
python test_preload_system.py

# Check database tables
sqlite3 manga_cache.db ".tables"

# View recent jobs
sqlite3 manga_cache.db "SELECT * FROM preload_jobs ORDER BY created_at DESC LIMIT 10;"

# Check statistics
sqlite3 manga_cache.db "SELECT * FROM preload_stats ORDER BY date DESC LIMIT 5;"
```

## Security Considerations

- All preload endpoints require admin authentication
- User agent strings identify the application properly
- Rate limiting prevents abuse of external sources
- Error messages don't expose sensitive information
- Database queries use parameterized statements

## Future Enhancements

- **Machine Learning**: Predict popular content based on user behavior
- **Dynamic Scheduling**: Adjust preload frequency based on usage patterns
- **Multi-Server Support**: Distribute preload jobs across multiple workers
- **Advanced Analytics**: Detailed performance metrics and trend analysis
- **Source Health Monitoring**: Automatic detection of source availability issues 