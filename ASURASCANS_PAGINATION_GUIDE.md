# AsuraScans Pagination Preload System

## Overview

The AsuraScans preload system has been enhanced to use **pagination-based crawling** instead of search terms. This approach is much more efficient and comprehensive, as it crawls through all manga pages to build a complete catalog.

## How It Works

### Traditional Search Approach (Old)
- Used popular search terms like "one piece", "naruto", etc.
- Limited to only popular manga
- Required multiple search queries
- Incomplete coverage

### New Pagination Approach
- Crawls `https://asuracomic.net/series?page=1` and increments pages
- Gets **ALL** manga from the site
- Single comprehensive crawl
- Complete catalog coverage

## Implementation Details

### 1. Pagination Function
```python
def get_all_manga_from_pagination(page: Page, max_pages: int = 100):
    """
    Get all manga from AsuraScans by crawling through pagination
    Returns a list of all manga found across all pages
    """
```

**Key Features:**
- Increments page numbers: `?page=1`, `?page=2`, etc.
- Stops when no more manga found or max_pages reached
- Extracts manga ID, title, chapter, image from each card
- Handles errors gracefully and continues crawling
- Duplicate detection and validation

### 2. Preload Manager Integration
```python
def _preload_asurascans_pagination(self, max_pages: int = 50) -> bool:
    """Preload all AsuraScans manga using pagination"""
```

**Process:**
1. Crawls all pages up to `max_pages`
2. Caches all manga under special key: `"asurascans_all_manga"`
3. Preloads details for first 20 manga (most popular)
4. Respects rate limits with delays between requests

### 3. Job System Integration
- New job type: `asurascans_pagination`
- Target ID contains max_pages (e.g., "50")
- Automatically scheduled in daily preload jobs
- Replaces search jobs for AsuraScans

## Performance Results

### Test Results (5 pages)
- **Duration:** 56.09 seconds
- **Pages crawled:** 5
- **Total manga found:** 75
- **Average manga per page:** 15.0
- **Manga per second:** 1.3

### Performance Characteristics
- **1 page:** 5.44s, 15 manga (2.8 manga/sec)
- **3 pages:** 59.01s, 30 manga (0.5 manga/sec)
- **5 pages:** 56.09s, 75 manga (1.3 manga/sec)

### Rate Limiting
- **Base delay:** 3.0 seconds between requests
- **Crawl delay:** 2.0 seconds (from robots.txt)
- **User agent:** `MangaReader/1.0 (+https://github.com/your-repo)`
- **Max requests per hour:** 50

## Benefits

### 1. Complete Coverage
- Gets ALL manga, not just popular ones
- Better cache hit rates for user searches
- Comprehensive catalog for browsing

### 2. Efficiency
- Single crawl vs multiple search queries
- More predictable performance
- Better resource utilization

### 3. User Experience
- Faster search results (cached)
- More comprehensive search results
- Better discovery of obscure manga

### 4. Scalability
- Can adjust max_pages based on needs
- Incremental updates possible
- Respectful crawling with delays

## Configuration

### Environment Variables
```bash
# AsuraScans specific settings
ASURASCANS_MAX_PAGES=50
ASURASCANS_BASE_DELAY=3.0
ASURASCANS_CRAWL_DELAY=2.0
```

### Preload Manager Settings
```python
'asurascans': {
    'base_delay': 3.0,
    'crawl_delay': 2.0,
    'max_requests_per_hour': 50,
    'user_agent': 'MangaReader/1.0 (+https://github.com/your-repo)',
    'domain': 'asura.gg'
}
```

## Usage Examples

### Manual Preload
```python
from backend.services.preload.preload_manager import PreloadManager

# Create preload manager
preload_manager = PreloadManager(cache_manager)

# Run pagination preload
success = preload_manager._preload_asurascans_pagination(max_pages=50)
```

### Scheduled Jobs
```python
# Daily preload automatically creates pagination jobs
preload_manager.create_daily_preload_jobs()

# Job will be created with:
# - job_type: 'asurascans_pagination'
# - target_id: '50' (max pages)
# - scheduled_at: tomorrow 2-6 AM
```

### Cache Access
```python
# Get all cached manga
all_manga = cache_manager.get_search_results("asurascans_all_manga", "asurascans")

# Get specific manga details
details = cache_manager.get_manga_details(manga_id, "asurascans")
```

## Monitoring and Maintenance

### Logs to Watch
```
INFO: Preloaded AsuraScans pagination: 750 total manga, 20 detailed
INFO: Processing job: asurascans_pagination for asurascans - 50
```

### Performance Metrics
- Total manga found per crawl
- Pages crawled successfully
- Duration and manga per second
- Cache hit rates for user searches

### Error Handling
- Timeout errors (increase delays)
- Network errors (retry logic)
- Rate limiting (adjust delays)
- Empty pages (stop crawling)

## Recommendations

### Production Settings
- **Max pages:** 50-100 for comprehensive coverage
- **Schedule:** 2-6 AM (off-peak hours)
- **Cache duration:** 24-48 hours
- **Retry attempts:** 3 for failed pages

### Optimization
- Monitor cache hit rates
- Adjust max_pages based on site growth
- Consider incremental updates
- Track performance metrics

### Future Enhancements
- Incremental crawling (only new pages)
- Parallel processing for multiple sources
- Smart scheduling based on site activity
- Advanced error recovery

## Comparison with Other Sources

| Source | Approach | Coverage | Efficiency |
|--------|----------|----------|------------|
| AsuraScans | Pagination | Complete | High |
| WeebCentral | Search Terms | Partial | Medium |
| MangaDex | API | Complete | Very High |

## Conclusion

The pagination-based preload system for AsuraScans provides:
- **Complete catalog coverage**
- **Better performance**
- **More efficient resource usage**
- **Improved user experience**

This approach can be extended to other sources that support pagination, providing a more comprehensive and efficient preload system across all manga sources. 