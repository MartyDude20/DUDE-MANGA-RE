import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import MangaReaderModal from './MangaReaderModal.jsx';
import { useAuth } from './Auth/AuthContext.jsx';

// Helper function to format date
function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  if (isNaN(date)) return dateStr;
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

// Helper to extract date from title
function extractDateFromTitle(title) {
  if (!title) return { cleanTitle: title, date: null };
  // Match formats like ' - May 1, 2024', ' - 2024-05-01', ' Sep 7, 2024', or 'March 24th 2025' at the end
  const datePattern = /(?:\s*[-:]?\s*|\s+)((?:\w+ \d{1,2}(?:st|nd|rd|th)?,? \d{4})|(?:\d{4}-\d{2}-\d{2}))$/i;
  const match = title.match(datePattern);
  if (match) {
    const cleanTitle = title.replace(datePattern, '').trim();
    return { cleanTitle, date: match[1] };
  }
  return { cleanTitle: title, date: null };
}

// Helper to normalize date string (remove ordinal suffixes)
function normalizeDateString(dateStr) {
  if (!dateStr) return dateStr;
  // Remove st, nd, rd, th from day
  return dateStr.replace(/(\d{1,2})(st|nd|rd|th)/gi, '$1');
}

const MangaDetails = () => {
  const { id, source } = useParams();
  const navigate = useNavigate();
  const { authFetch, isAuthenticated } = useAuth();
  const [manga, setManga] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [readerOpen, setReaderOpen] = useState(false);
  const [readerImages, setReaderImages] = useState([]);
  const [readerLoading, setReaderLoading] = useState(false);
  const [readerTitle, setReaderTitle] = useState('');
  const [isSaved, setIsSaved] = useState(false);
  const [forceRefresh, setForceRefresh] = useState(false);
  const [cacheInfo, setCacheInfo] = useState(null);
  const [chapterSortOrder, setChapterSortOrder] = useState('newest'); // 'newest', 'oldest'
  const [readChapters, setReadChapters] = useState(new Set()); // Track read chapters
  const [isMobile, setIsMobile] = useState(false);

  // Detect mobile device
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    const fetchMangaDetails = async () => {
      try {
        setLoading(true);
        setError('');
        const params = {};
        if (forceRefresh) {
          params.refresh = 'true';
        }
        const response = await axios.get(`/api/manga/${source}/${id}`, { params });
        setManga(response.data);
        setCacheInfo(response.data.cached);
        
        // Check if manga is saved
        const savedManga = JSON.parse(localStorage.getItem('savedManga') || '[]');
        const isMangaSaved = savedManga.some(saved => 
          saved.id === id && saved.source === source
        );
        setIsSaved(isMangaSaved);
        
        // Load read chapters for this manga
        loadReadChapters();
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to fetch manga details');
      } finally {
        setLoading(false);
      }
    };

    if (id && source) {
      fetchMangaDetails();
    }
  }, [id, source, forceRefresh]);

  // Load read chapters from localStorage
  const loadReadChapters = () => {
    const readChaptersData = JSON.parse(localStorage.getItem('readChapters') || '{}');
    const mangaKey = `${source}-${id}`;
    const chapters = readChaptersData[mangaKey] || [];
    setReadChapters(new Set(chapters));
  };

  // Save read chapter to localStorage
  const saveReadChapter = (chapterUrl) => {
    const readChaptersData = JSON.parse(localStorage.getItem('readChapters') || '{}');
    const mangaKey = `${source}-${id}`;
    const chapters = readChaptersData[mangaKey] || [];
    
    if (!chapters.includes(chapterUrl)) {
      chapters.push(chapterUrl);
      readChaptersData[mangaKey] = chapters;
      localStorage.setItem('readChapters', JSON.stringify(readChaptersData));
      setReadChapters(new Set(chapters));
    }
  };

  const handleImageError = (e) => {
    e.target.style.display = 'none';
  };

  const handleSaveToggle = () => {
    const savedManga = JSON.parse(localStorage.getItem('savedManga') || '[]');
    
    if (isSaved) {
      // Remove from saved list
      const updatedList = savedManga.filter(saved => 
        !(saved.id === id && saved.source === source)
      );
      localStorage.setItem('savedManga', JSON.stringify(updatedList));
      setIsSaved(false);
    } else {
      // Add to saved list
      const mangaToSave = {
        id: id,
        title: manga.title,
        image: manga.image,
        source: source,
        status: manga.status,
        author: manga.author,
        savedAt: new Date().toISOString()
      };
      savedManga.push(mangaToSave);
      localStorage.setItem('savedManga', JSON.stringify(savedManga));
      setIsSaved(true);
    }
  };

  const recordReadHistory = async (chapter) => {
    if (!isAuthenticated) return;
    
    try {
              await authFetch('http://localhost:5000/read-history', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          manga_title: manga.title,
          chapter_title: chapter.title,
          source: source,
          manga_id: id,
          chapter_url: chapter.url,
        }),
      });
    } catch (err) {
      console.error('Failed to record read history:', err);
    }
  };

  const handleChapterClick = async (e, chapter) => {
    e.preventDefault();
    setReaderLoading(true);
    setReaderOpen(true);
    setReaderTitle(chapter.title);
    
    // Save chapter as read
    saveReadChapter(chapter.url);
    
    // Record read history when chapter is opened
    await recordReadHistory(chapter);
    
    try {
      let chapterId = chapter.url;
      if (source === 'mangadex') {
        // Extract UUID from the end of the URL
        chapterId = chapter.url.split('/').pop();
      }
      const resp = await axios.get(`/api/chapter-images/${source}/${id}/${chapterId}`);
      setReaderImages(resp.data.images || []);
    } catch (err) {
      setReaderImages([]);
    } finally {
      setReaderLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-400 mt-4">Loading manga details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Link to="/" className={`mb-6 bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors inline-block ${
          isMobile ? 'p-2' : 'px-4 py-2'
        }`}>
          {isMobile ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          ) : (
            '← Back to Search'
          )}
        </Link>
        <div className="p-4 bg-red-900 border border-red-600 text-red-200 rounded-lg">
          {error}
        </div>
      </div>
    );
  }

  if (!manga) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Link to="/" className={`mb-6 bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors inline-block ${
          isMobile ? 'p-2' : 'px-4 py-2'
        }`}>
          {isMobile ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          ) : (
            '← Back to Search'
          )}
        </Link>
        <div className="p-4 bg-red-900 border border-red-600 text-red-200 rounded-lg">
          Manga not found
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <Link to="/" className={`bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors inline-block ${
          isMobile ? 'p-2' : 'px-4 py-2'
        }`}>
          {isMobile ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          ) : (
            '← Back to Search'
          )}
        </Link>
        
        <div className="flex items-center space-x-4">
          {/* Cache Refresh Toggle */}
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={forceRefresh}
              onChange={(e) => setForceRefresh(e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
            />
            <span className="text-gray-300 text-sm">Force refresh</span>
          </label>
          
          <button
            onClick={handleSaveToggle}
            className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
              isSaved 
                ? 'bg-red-600 hover:bg-red-700 text-white' 
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isSaved ? (
              <>
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                </svg>
                <span>Saved</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                <span>Save Manga</span>
              </>
            )}
          </button>
        </div>
      </div>
      
      {cacheInfo !== null && (
        <div className={`mb-6 p-4 rounded-lg border ${
          cacheInfo 
            ? 'bg-green-900 border-green-600 text-green-200' 
            : 'bg-blue-900 border-blue-600 text-blue-200'
        }`}>
          <div className="flex items-center space-x-2">
            {cacheInfo ? (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
              </svg>
            )}
            <span>
              {cacheInfo ? 'Manga details loaded from cache' : 'Fresh manga details loaded'}
            </span>
          </div>
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-6 mb-8 bg-gray-800 p-6 rounded-lg shadow-lg">
        <img
          src={manga.image}
          alt={manga.title}
          className="w-64 h-96 object-cover rounded-lg shadow-lg"
          onError={handleImageError}
        />
        <div className="flex-1">
          <h1 className="text-4xl font-bold text-white mb-4">{manga.title}</h1>
          <p className="text-gray-300 mb-2">
            <span className="font-medium">Author:</span> {manga.author}
          </p>
          {manga.url && (
            <p className="text-gray-300">
              <span className="font-medium">Source:</span>{' '}
              <a 
                href={manga.url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="text-blue-400 hover:text-blue-300 underline"
              >
                View on {manga.source ? manga.source.charAt(0).toUpperCase() + manga.source.slice(1) : 'Source'}
              </a>
            </p>
          )}
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">Description</h2>
        <p className="text-gray-300 leading-relaxed whitespace-pre-line">{manga.description}</p>
      </div>
      
      {manga.chapters && manga.chapters.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Chapters</h2>
          <div className="flex gap-2 mb-4">
            <button
              type="button"
              className={`px-3 py-1 rounded text-sm font-medium border focus:outline-none transition-colors ${chapterSortOrder === 'newest' ? 'bg-blue-600 text-white border-blue-700' : 'bg-gray-700 text-gray-200 border-gray-600 hover:bg-gray-600'}`}
              onClick={() => setChapterSortOrder('newest')}
            >
              Newest Added
            </button>
            <button
              type="button"
              className={`px-3 py-1 rounded text-sm font-medium border focus:outline-none transition-colors ${chapterSortOrder === 'oldest' ? 'bg-blue-600 text-white border-blue-700' : 'bg-gray-700 text-gray-200 border-gray-600 hover:bg-gray-600'}`}
              onClick={() => setChapterSortOrder('oldest')}
            >
              Oldest Added
            </button>
          </div>
          <div className="space-y-2">
            {(() => {
              let sortedChapters = [...manga.chapters];
              sortedChapters = sortedChapters.map(chapter => {
                const { cleanTitle, date: extractedDate } = extractDateFromTitle(chapter.title);
                return { ...chapter, cleanTitle, extractedDate };
              });
              // Always sort by the value shown in the date column
              sortedChapters.sort((a, b) => {
                let dateA = a.date || a.extractedDate;
                let dateB = b.date || b.extractedDate;
                dateA = normalizeDateString(dateA);
                dateB = normalizeDateString(dateB);
                const parsedA = dateA ? Date.parse(dateA) : NaN;
                const parsedB = dateB ? Date.parse(dateB) : NaN;
                if (!isNaN(parsedA) && !isNaN(parsedB)) {
                  if (chapterSortOrder === 'newest') {
                    return parsedB - parsedA;
                  } else {
                    return parsedA - parsedB;
                  }
                } else if (!isNaN(parsedA)) {
                  // a has a date, b does not
                  return -1;
                } else if (!isNaN(parsedB)) {
                  // b has a date, a does not
                  return 1;
                } else {
                  // neither has a date
                  return 0;
                }
              });
              return sortedChapters.map((chapter, idx) => {
                const displayDate = chapter.date || chapter.extractedDate;
                const isRead = readChapters.has(chapter.url);
                return (
                  <div 
                    key={`${chapter.url}-${idx}`} 
                    className={`flex items-center justify-between p-4 rounded-lg border cursor-pointer transition-colors ${
                      isRead 
                        ? 'bg-gray-900 border-gray-600 hover:bg-gray-800 opacity-60' 
                        : 'bg-gray-800 border-gray-700 hover:bg-gray-700'
                    }`}
                    onClick={e => handleChapterClick(e, chapter)}
                  >
                    <div className="flex items-center">
                      {isRead && (
                        <svg className="w-4 h-4 mr-2 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      )}
                      <div>
                        <h3 className={`font-medium mb-1 ${isRead ? 'text-gray-400' : 'text-white'}`}>
                          {chapter.cleanTitle}
                        </h3>
                        <p className={`text-sm ${isRead ? 'text-gray-500' : 'text-gray-400'}`}>
                          {chapter.number}
                        </p>
                      </div>
                    </div>
                    <span className={`flex items-center min-w-[140px] justify-end text-sm ${
                      isRead ? 'text-gray-500' : 'text-gray-500'
                    }`}>
                      <svg className={`w-4 h-4 mr-1 ${isRead ? 'text-gray-500' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <rect x="3" y="4" width="18" height="18" rx="2" strokeWidth="2" stroke="currentColor" fill="none" />
                        <line x1="16" y1="2" x2="16" y2="6" strokeWidth="2" stroke="currentColor" />
                        <line x1="8" y1="2" x2="8" y2="6" strokeWidth="2" stroke="currentColor" />
                        <line x1="3" y1="10" x2="21" y2="10" strokeWidth="2" stroke="currentColor" />
                      </svg>
                      {formatDate(normalizeDateString(displayDate))}
                    </span>
                  </div>
                );
              });
            })()}
          </div>
        </div>
      )}
      
      <MangaReaderModal
        open={readerOpen}
        images={readerImages}
        onClose={() => setReaderOpen(false)}
        chapterTitle={readerTitle}
        chapters={manga.chapters}
        currentChapterIndex={manga.chapters ? manga.chapters.findIndex(ch => ch.title === readerTitle) : -1}
        onRequestChapter={async (chapter, idx) => {
          setReaderLoading(true);
          setReaderOpen(true);
          setReaderTitle(chapter.title);
          
          // Save chapter as read
          saveReadChapter(chapter.url);
          
          // Record read history when chapter is opened
          await recordReadHistory(chapter);
          
          try {
            let chapterId = chapter.url;
            if (source === 'mangadex') {
              chapterId = chapter.url.split('/').pop();
            }
            const resp = await axios.get(`/api/chapter-images/${source}/${id}/${chapterId}`);
            setReaderImages(resp.data.images || []);
          } catch (err) {
            setReaderImages([]);
          } finally {
            setReaderLoading(false);
          }
        }}
      />
      

    </div>
  );
};

export default MangaDetails; 