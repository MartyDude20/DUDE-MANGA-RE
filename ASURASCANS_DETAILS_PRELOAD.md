# AsuraScans Manga Details Preload Strategy

## Current Implementation

### What We're Currently Preloading

The AsuraScans pagination preload system currently does two things:

1. **Basic Info Preload** (All Manga):
   ```python
   # From pagination crawl
   {
     'id': 'manga-slug-id',
     'title': 'Manga Title',
     'status': '',  # Empty in search results
     'chapter': '62',  # Latest chapter number
     'image': 'https://asuracomic.net/images/cover.jpg',
     'details_url': 'series/manga-slug-id',
     'source': 'asurascans'
   }
   ```

2. **Detailed Info Preload** (First 20 Manga):
   ```python
   # From get_details() function
   {
     'id': 'manga-slug-id',
     'title': 'Manga Title',
     'image': 'https://asuracomic.net/images/cover.jpg',
     'description': 'Full manga description...',
     'author': 'Author Name',
     'status': 'Ongoing/Completed',
     'url': 'https://asuracomic.net/series/manga-slug-id',
     'source': 'asurascans',
     'chapters': [
       {
         'title': 'Chapter 1',
         'url': 'https://asuracomic.net/series/manga-slug-id/chapter/1',
         'date': '2024-01-01'
       }
     ]
   }
   ```

### Current Preload Strategy

```python
def _preload_asurascans_pagination(self, max_pages: int = 50) -> bool:
    # 1. Get all manga from pagination (basic info)
    all_manga = asurascans.get_all_manga_from_pagination(page, max_pages)
    
    # 2. Cache all manga under special key
    cache_key = "asurascans_all_manga"
    self.cache_manager.cache_search_results(cache_key, 'asurascans', all_manga)
    
    # 3. Preload details for first 20 manga (most popular)
    popular_manga = all_manga[:20]
    for manga in popular_manga:
        details = asurascans.get_details(page, manga['id'])
        self.cache_manager.cache_manga_details(manga['id'], 'asurascans', details)
```

## Detailed Metadata Analysis

### What We Extract from AsuraScans Details

| Field | Extraction Method | Quality | Notes |
|-------|------------------|---------|-------|
| **Title** | `div.text-center.sm\\:text-left span.text-xl.font-bold` | ✅ High | Clean, reliable |
| **Image** | `div.relative.col-span-full.sm\\:col-span-3 img.rounded` | ✅ High | Good quality covers |
| **Description** | `span.font-medium.text-sm.text-\[\#A2A2A2\]` | ✅ High | Full descriptions |
| **Author** | `h3.text-\[\#D9D9D9\].font-medium.text-sm:text("Author")` | ✅ Medium | Sometimes missing |
| **Status** | `div.imptdt:has(i.fa-book)` | ✅ Medium | Ongoing/Completed |
| **Chapters** | `div.pl-4.pr-2.pb-4.overflow-y-auto` | ✅ High | Full list with dates |
| **Chapter Dates** | `h3` elements in chapter divs | ✅ High | Very reliable |

### Missing Metadata (Compared to WeebCentral)

| Field | Status | Reason |
|-------|--------|--------|
| **Tags/Genres** | ❌ Missing | AsuraScans doesn't display tags |
| **Type** | ❌ Missing | No manhwa/manhua/manga distinction |
| **Release Year** | ❌ Missing | Not shown on series pages |
| **Official Translation** | ❌ Missing | Not indicated |
| **Anime Adaptation** | ❌ Missing | Not shown |
| **Adult Content** | ❌ Missing | Not flagged |
| **Rating** | ❌ Missing | No rating system |

## Enhanced Preload Strategies

### Strategy 1: Smart Popularity-Based Preload

```python
def _preload_asurascans_smart_details(self, all_manga: List[Dict], max_detailed: int = 50) -> bool:
    """Smart preload based on popularity indicators"""
    
    # Score manga based on popularity indicators
    scored_manga = []
    for manga in all_manga:
        score = 0
        
        # Higher chapter count = more popular
        if manga.get('chapter'):
            try:
                chapter_num = int(manga['chapter'])
                score += min(chapter_num, 100)  # Cap at 100
            except:
                pass
        
        # Recent manga (from first few pages) = more popular
        score += 10  # Base score for all manga
        
        scored_manga.append((score, manga))
    
    # Sort by score and take top manga
    scored_manga.sort(reverse=True)
    popular_manga = [manga for score, manga in scored_manga[:max_detailed]]
    
    return self._preload_manga_details_batch(popular_manga)
```

### Strategy 2: Tiered Preload System

```python
def _preload_asurascans_tiered(self, all_manga: List[Dict]) -> bool:
    """Tiered preload based on manga importance"""
    
    # Tier 1: First 10 manga (definitely popular)
    tier1_manga = all_manga[:10]
    
    # Tier 2: High chapter count manga (likely popular)
    tier2_manga = [m for m in all_manga[10:100] 
                   if m.get('chapter') and int(m['chapter']) > 50]
    
    # Tier 3: Recent manga (first 3 pages)
    tier3_manga = all_manga[:45]  # 3 pages * 15 manga per page
    
    # Combine and deduplicate
    all_tiered = list({m['id']: m for m in tier1_manga + tier2_manga + tier3_manga}.values())
    
    return self._preload_manga_details_batch(all_tiered[:50])
```

### Strategy 3: User Behavior-Based Preload

```python
def _preload_asurascans_behavior_based(self, all_manga: List[Dict]) -> bool:
    """Preload based on user search patterns"""
    
    # Get recent popular searches from cache
    recent_searches = self.get_recent_popular_searches()
    
    # Find manga that match recent search patterns
    behavior_manga = []
    for manga in all_manga:
        title_lower = manga['title'].lower()
        
        # Check if manga title contains popular search terms
        for search in recent_searches:
            if search['query'].lower() in title_lower:
                behavior_manga.append(manga)
                break
    
    # Combine with basic popularity
    popular_manga = all_manga[:30] + behavior_manga[:20]
    
    # Deduplicate
    unique_manga = list({m['id']: m for m in popular_manga}.values())
    
    return self._preload_manga_details_batch(unique_manga[:50])
```

## Implementation Recommendations

### 1. Enhanced Preload Manager Method

```python
def _preload_asurascans_enhanced(self, max_pages: int = 50, max_detailed: int = 50) -> bool:
    """Enhanced AsuraScans preload with smart details selection"""
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Set user agent
            page.set_extra_http_headers({
                'User-Agent': self.source_configs['asurascans']['user_agent']
            })
            
            # Step 1: Get all manga from pagination
            all_manga = asurascans.get_all_manga_from_pagination(page, max_pages)
            
            if not all_manga:
                logger.warning("No manga found during AsuraScans pagination preload")
                return False
            
            # Step 2: Cache all manga
            cache_key = "asurascans_all_manga"
            self.cache_manager.cache_search_results(cache_key, 'asurascans', all_manga, user_id=None)
            
            # Step 3: Smart selection for detailed preload
            detailed_manga = self._select_manga_for_details(all_manga, max_detailed)
            
            # Step 4: Preload details with progress tracking
            successful_details = 0
            for i, manga in enumerate(detailed_manga):
                try:
                    # Add delay between requests
                    time.sleep(self.get_respectful_delay('asurascans'))
                    
                    details = asurascans.get_details(page, manga['id'])
                    self.cache_manager.cache_manga_details(manga['id'], 'asurascans', details, user_id=None)
                    
                    successful_details += 1
                    logger.info(f"Preloaded details [{i+1}/{len(detailed_manga)}]: {manga['title']}")
                    
                except Exception as e:
                    logger.error(f"Error preloading details for {manga['id']}: {e}")
                    continue
            
            page.close()
            browser.close()
            
            logger.info(f"Enhanced AsuraScans preload: {len(all_manga)} total, {successful_details} detailed")
            return True
            
    except Exception as e:
        logger.error(f"Error in enhanced AsuraScans preload: {e}")
        return False

def _select_manga_for_details(self, all_manga: List[Dict], max_count: int) -> List[Dict]:
    """Smart selection of manga for detailed preload"""
    
    # Score each manga
    scored_manga = []
    for manga in all_manga:
        score = 0
        
        # Chapter count bonus
        if manga.get('chapter'):
            try:
                chapter_num = int(manga['chapter'])
                score += min(chapter_num * 2, 200)  # Higher chapters = more popular
            except:
                pass
        
        # Position bonus (earlier pages = more popular)
        score += 50  # Base score
        
        scored_manga.append((score, manga))
    
    # Sort by score and return top manga
    scored_manga.sort(reverse=True)
    return [manga for score, manga in scored_manga[:max_count]]
```

### 2. Configuration Options

```python
# Add to source_configs
'asurascans': {
    'base_delay': 3.0,
    'crawl_delay': 2.0,
    'max_requests_per_hour': 50,
    'user_agent': 'MangaReader/1.0 (+https://github.com/your-repo)',
    'domain': 'asura.gg',
    'preload_config': {
        'max_pages': 50,
        'max_detailed': 50,
        'selection_strategy': 'smart',  # 'smart', 'tiered', 'behavior'
        'chapter_threshold': 30,  # Minimum chapters for detailed preload
        'position_weight': 0.3,  # Weight for page position
        'chapter_weight': 0.7   # Weight for chapter count
    }
}
```

### 3. Performance Monitoring

```python
def _track_asurascans_preload_performance(self, all_manga: List[Dict], detailed_manga: List[Dict]) -> Dict:
    """Track preload performance metrics"""
    
    return {
        'total_manga': len(all_manga),
        'detailed_manga': len(detailed_manga),
        'coverage_ratio': len(detailed_manga) / len(all_manga),
        'avg_chapters': sum(int(m.get('chapter', 0)) for m in detailed_manga) / len(detailed_manga),
        'popularity_distribution': {
            'high_chapters': len([m for m in detailed_manga if int(m.get('chapter', 0)) > 100]),
            'medium_chapters': len([m for m in detailed_manga if 50 <= int(m.get('chapter', 0)) <= 100]),
            'low_chapters': len([m for m in detailed_manga if int(m.get('chapter', 0)) < 50])
        }
    }
```

## Benefits of Enhanced Details Preload

### 1. Better User Experience
- **Faster Details Loading**: Preloaded details load instantly
- **More Complete Information**: Author, description, full chapter list
- **Chapter Dates**: Users can see when chapters were released

### 2. Improved Cache Performance
- **Higher Hit Rates**: More detailed info cached
- **Reduced Server Load**: Fewer real-time scraping requests
- **Better Search Results**: Rich metadata for filtering

### 3. Smart Resource Usage
- **Intelligent Selection**: Preload most popular manga
- **Respectful Crawling**: Proper delays and rate limiting
- **Scalable**: Can adjust based on server capacity

## Future Enhancements

### 1. Cross-Source Metadata Enrichment
```python
# Use MangaDex API to enrich AsuraScans data
def enrich_asurascans_metadata(self, asura_manga: Dict) -> Dict:
    """Enrich AsuraScans manga with MangaDex metadata"""
    
    # Search MangaDex for matching manga
    mangadex_info = self.search_mangadex_api(asura_manga['title'])
    
    if mangadex_info:
        # Merge metadata
        asura_manga['tags'] = mangadex_info.get('tags', [])
        asura_manga['type'] = mangadex_info.get('type', 'unknown')
        asura_manga['year'] = mangadex_info.get('year', 'unknown')
    
    return asura_manga
```

### 2. User Preference Learning
```python
# Learn from user behavior to improve preload selection
def update_preload_preferences(self, user_searches: List[str], user_clicks: List[str]):
    """Update preload strategy based on user behavior"""
    
    # Analyze user patterns
    popular_terms = self.analyze_search_patterns(user_searches)
    popular_manga = self.analyze_click_patterns(user_clicks)
    
    # Update preload selection weights
    self.update_selection_weights(popular_terms, popular_manga)
```

This enhanced details preload strategy will significantly improve the AsuraScans user experience while maintaining respectful crawling practices and efficient resource usage. 