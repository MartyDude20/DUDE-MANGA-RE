import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, PreloadedManga
from sources import weebcentral, asurascans, mangadex
from playwright.sync_api import sync_playwright
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PreloaderService:
    """Service for preloading manga data from various sources"""
    
    def __init__(self):
        self.sources = {
            'weebcentral': weebcentral,
            'asurascans': asurascans,
            'mangadex': mangadex
        }
        self.rate_limits = {
            'asurascans': 1.0,  # 1 second between requests
            'weebcentral': 1.5,  # 1.5 seconds between requests
            'mangadex': 2.0     # 2 seconds between requests
        }
        self.flask_app = None  # Will hold Flask app reference
    
    def set_app(self, app):
        """Set the Flask app reference for context management"""
        self.flask_app = app
    
    def preload_source(self, source: str, page_limit: int = 3) -> None:
        """Preload manga from a specific source"""
        if source not in self.sources:
            logger.error(f"Unknown source: {source}")
            return
        
        logger.info(f"Starting preload from {source}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Get the latest manga URL for the source
                latest_url = self._get_latest_url(source)
                if not latest_url:
                    logger.error(f"No latest URL found for {source}")
                    return
                
                # Navigate to the latest manga page
                page.goto(latest_url)
                page.wait_for_load_state('networkidle')
                
                manga_count = 0
                
                # Extract manga data from the page
                manga_list = self._extract_manga_list(page, source)
                
                for manga_data in manga_list[:page_limit * 20]:  # Assuming ~20 manga per page
                    try:
                        # Check if manga already exists
                        existing = PreloadedManga.query.filter_by(
                            source_url=manga_data.get('source_url')
                        ).first()
                        
                        if existing:
                            # Update existing manga
                            existing.last_updated = datetime.utcnow()
                            existing.chapters = manga_data.get('chapters', [])
                            existing.status = manga_data.get('status')
                        else:
                            # Create new manga entry
                            manga = PreloadedManga(
                                title=manga_data.get('title', 'Unknown'),
                                normalized_title=PreloadedManga.normalize_title(
                                    manga_data.get('title', '')
                                ),
                                source_url=manga_data.get('source_url'),
                                cover_url=manga_data.get('cover_url'),
                                description=manga_data.get('description'),
                                chapters=manga_data.get('chapters', []),
                                source=source,
                                author=manga_data.get('author'),
                                status=manga_data.get('status'),
                                last_updated=datetime.utcnow()
                            )
                            db.session.add(manga)
                        
                        manga_count += 1
                        
                        # Rate limiting
                        time.sleep(self.rate_limits.get(source, 1.0))
                        
                    except IntegrityError:
                        db.session.rollback()
                        logger.warning(f"Duplicate manga: {manga_data.get('title')}")
                        continue
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error saving manga: {e}")
                        continue
                
                db.session.commit()
                browser.close()
                
                logger.info(f"Preloaded {manga_count} manga from {source}")
                
        except Exception as e:
            logger.error(f"Preload failed for {source}: {e}")
    
    def _get_latest_url(self, source: str) -> Optional[str]:
        """Get the URL for latest manga based on source"""
        urls = {
            'weebcentral': 'https://weebcentral.com/search?sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display',
            'asurascans': 'https://asurascans.com/',
            'mangadex': 'https://mangadex.org/titles/latest'
        }
        return urls.get(source)
    
    def _extract_manga_list(self, page, source: str) -> List[Dict]:
        """Extract manga list from page based on source"""
        manga_list = []
        
        try:
            if source == 'weebcentral':
                # Use the existing weebcentral search function
                # We'll simulate a search for all manga
                results = weebcentral.search(page, '')
                for result in results:
                    manga_list.append({
                        'title': result.get('title'),
                        'source_url': result.get('details_url'),
                        'cover_url': result.get('image'),
                        'status': result.get('status'),
                        'chapters': []  # Will be populated later
                    })
            
            elif source == 'asurascans':
                # Extract from Asura Scans homepage
                manga_cards = page.query_selector_all('div.bs')
                for card in manga_cards[:50]:  # Limit to 50 manga
                    try:
                        link_elem = card.query_selector('a')
                        if link_elem:
                            manga_list.append({
                                'title': link_elem.get_attribute('title'),
                                'source_url': link_elem.get_attribute('href'),
                                'cover_url': card.query_selector('img').get_attribute('src'),
                                'status': 'Unknown',
                                'chapters': []
                            })
                    except:
                        continue
            
            elif source == 'mangadex':
                # Extract from MangaDex latest page
                manga_cards = page.query_selector_all('div.manga-card')
                for card in manga_cards[:50]:
                    try:
                        title_elem = card.query_selector('a.manga-title')
                        if title_elem:
                            manga_list.append({
                                'title': title_elem.inner_text(),
                                'source_url': f"https://mangadex.org{title_elem.get_attribute('href')}",
                                'cover_url': card.query_selector('img').get_attribute('src'),
                                'status': 'Unknown',
                                'chapters': []
                            })
                    except:
                        continue
        
        except Exception as e:
            logger.error(f"Error extracting manga list from {source}: {e}")
        
        return manga_list
    
    def update_popular_manga(self, limit: int = 100) -> None:
        """Update chapters for popular manga"""
        logger.info("Starting popular manga update")
        
        try:
            # Get most popular manga
            popular_manga = PreloadedManga.query.order_by(
                PreloadedManga.popularity.desc()
            ).limit(limit).all()
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                
                for manga in popular_manga:
                    try:
                        page = browser.new_page()
                        source_module = self.sources.get(manga.source)
                        
                        if not source_module:
                            continue
                        
                        # Extract manga ID from URL
                        manga_id = self._extract_manga_id(manga.source_url, manga.source)
                        if not manga_id:
                            continue
                        
                        # Get updated details
                        details = source_module.get_details(page, manga_id)
                        
                        # Update manga
                        manga.chapters = details.get('chapters', [])
                        manga.description = details.get('description', manga.description)
                        manga.author = details.get('author', manga.author)
                        manga.status = details.get('status', manga.status)
                        manga.last_updated = datetime.utcnow()
                        
                        db.session.commit()
                        page.close()
                        
                        # Rate limiting
                        time.sleep(self.rate_limits.get(manga.source, 1.0))
                        
                        logger.info(f"Updated {manga.title}")
                        
                    except Exception as e:
                        logger.error(f"Failed to update {manga.title}: {e}")
                        continue
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Popular manga update failed: {e}")
    
    def _extract_manga_id(self, url: str, source: str) -> Optional[str]:
        """Extract manga ID from URL based on source"""
        try:
            if source == 'weebcentral':
                # Extract from URL like /series/manga-id/
                parts = url.split('/')
                if 'series' in parts:
                    idx = parts.index('series')
                    return parts[idx + 1] if idx + 1 < len(parts) else None
            
            elif source == 'asurascans':
                # Extract from URL
                parts = url.split('/')
                return parts[-1] or parts[-2]
            
            elif source == 'mangadex':
                # Extract UUID from URL
                import re
                match = re.search(r'/title/([a-f0-9-]+)', url)
                return match.group(1) if match else None
                
        except Exception as e:
            logger.error(f"Failed to extract manga ID from {url}: {e}")
        
        return None
    
    def cleanup_old_entries(self, days: int = 30) -> None:
        """Remove manga entries that haven't been accessed in specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            old_entries = PreloadedManga.query.filter(
                or_(
                    PreloadedManga.last_accessed < cutoff_date,
                    PreloadedManga.last_accessed.is_(None)
                ),
                PreloadedManga.popularity < 5  # Keep popular manga
            ).all()
            
            for entry in old_entries:
                db.session.delete(entry)
            
            db.session.commit()
            logger.info(f"Cleaned up {len(old_entries)} old manga entries")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            db.session.rollback()
    
    def preload_popular_search_terms(self) -> None:
        """Preload manga for popular search terms"""
        logger.info("Starting popular search terms preload")
        
        # Popular search terms that users commonly search for
        popular_terms = [
            'one piece', 'naruto', 'dragon ball', 'bleach', 'attack on titan',
            'my hero academia', 'demon slayer', 'jujutsu kaisen', 'spy x family',
            'chainsaw man', 'tokyo ghoul', 'death note', 'fullmetal alchemist',
            'hunter x hunter', 'fairy tail', 'black clover', 'the promised neverland',
            'vinland saga', 'vagabond', 'berserk', 'kingdom', 'one punch man',
            'mob psycho', 'haikyuu', 'kuroko no basket', 'slam dunk', 'yuri on ice',
            'your name', 'weathering with you', 'a silent voice', 'i want to eat your pancreas'
        ]
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                
                for term in popular_terms:
                    try:
                        page = browser.new_page()
                        
                        # Search for the term on each source
                        for source_name, source_module in self.sources.items():
                            try:
                                logger.info(f"Preloading '{term}' from {source_name}")
                                
                                # Use the source's search function
                                results = source_module.search(page, term, fuzzy=False)
                                
                                # Cache the results
                                for result in results[:5]:  # Limit to top 5 results per term
                                    try:
                                        # Check if already exists
                                        existing = PreloadedManga.query.filter_by(
                                            source_url=result.get('details_url')
                                        ).first()
                                        
                                        if existing:
                                            # Update popularity
                                            existing.popularity += 1
                                            existing.last_updated = datetime.utcnow()
                                        else:
                                            # Create new entry
                                            manga = PreloadedManga(
                                                title=result.get('title', 'Unknown'),
                                                normalized_title=PreloadedManga.normalize_title(
                                                    result.get('title', '')
                                                ),
                                                source_url=result.get('details_url'),
                                                cover_url=result.get('image'),
                                                description=result.get('description', ''),
                                                chapters=result.get('chapters', []),
                                                source=source_name,
                                                author=result.get('author', ''),
                                                status=result.get('status', ''),
                                                popularity=1,
                                                last_updated=datetime.utcnow()
                                            )
                                            db.session.add(manga)
                                        
                                        db.session.commit()
                                        
                                    except IntegrityError:
                                        db.session.rollback()
                                        continue
                                    except Exception as e:
                                        logger.error(f"Error saving manga for term '{term}': {e}")
                                        db.session.rollback()
                                        continue
                                
                                # Rate limiting between sources
                                time.sleep(self.rate_limits.get(source_name, 1.0))
                                
                            except Exception as e:
                                logger.error(f"Error preloading '{term}' from {source_name}: {e}")
                                continue
                        
                        page.close()
                        
                        # Rate limiting between terms
                        time.sleep(2.0)
                        
                    except Exception as e:
                        logger.error(f"Error preloading term '{term}': {e}")
                        continue
                
                browser.close()
                logger.info("Popular search terms preload completed")
                
        except Exception as e:
            logger.error(f"Popular search terms preload failed: {e}")

# Create singleton instance
preloader_service = PreloaderService() 