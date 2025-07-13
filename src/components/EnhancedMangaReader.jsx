import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from './Auth/AuthContext.jsx';
import { 
  FaZoomIn, 
  FaZoomOut, 
  FaExpand, 
  FaCompress, 
  FaArrowLeft, 
  FaArrowRight,
  FaPlay,
  FaPause,
  FaMoon,
  FaSun,
  FaEye,
  FaEyeSlash,
  FaBookmark,
  FaShare,
  FaCog,
  FaTimes
} from 'react-icons/fa';
import { motion, AnimatePresence } from 'framer-motion';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import { useSwipeable } from 'react-swipeable';

const EnhancedMangaReader = () => {
  const { source, id, chapterId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  // State management
  const [images, setImages] = useState([]);
  const [currentPage, setCurrentPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mangaInfo, setMangaInfo] = useState(null);
  
  // Reader settings
  const [zoom, setZoom] = useState(1);
  const [readingDirection, setReadingDirection] = useState('ltr'); // ltr or rtl
  const [nightMode, setNightMode] = useState(false);
  const [autoScroll, setAutoScroll] = useState(false);
  const [autoScrollSpeed, setAutoScrollSpeed] = useState(1);
  const [showUI, setShowUI] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);
  
  // Reading progress
  const [readingStartTime, setReadingStartTime] = useState(null);
  const [totalReadingTime, setTotalReadingTime] = useState(0);
  const [pageReadingTimes, setPageReadingTimes] = useState({});
  
  // Refs
  const containerRef = useRef(null);
  const autoScrollRef = useRef(null);
  const lastPageTimeRef = useRef(null);
  
  // Fetch chapter images
  useEffect(() => {
    fetchChapterImages();
  }, [source, id, chapterId]);
  
  // Track reading time
  useEffect(() => {
    if (isAuthenticated && images.length > 0) {
      setReadingStartTime(Date.now());
      lastPageTimeRef.current = Date.now();
    }
  }, [isAuthenticated, images]);
  
  // Auto-scroll functionality
  useEffect(() => {
    if (autoScroll && images.length > 0) {
      const interval = setInterval(() => {
        if (currentPage < images.length - 1) {
          handleNextPage();
        } else {
          setAutoScroll(false);
        }
      }, 3000 / autoScrollSpeed); // 3 seconds base time divided by speed
      
      autoScrollRef.current = interval;
      return () => clearInterval(interval);
    }
  }, [autoScroll, currentPage, images.length, autoScrollSpeed]);
  
  // Save reading progress when page changes
  useEffect(() => {
    if (isAuthenticated && currentPage > 0) {
      saveReadingProgress();
    }
  }, [currentPage, isAuthenticated]);
  
  // Hide UI after inactivity
  useEffect(() => {
    if (!showUI) return;
    
    const timer = setTimeout(() => {
      setShowUI(false);
    }, 3000);
    
    return () => clearTimeout(timer);
  }, [showUI, currentPage]);
  
  const fetchChapterImages = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/chapter-images/${source}/${id}/${chapterId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch chapter images');
      }
      
      const data = await response.json();
      setImages(data.images || []);
      
      // Fetch manga info for progress tracking
      const mangaResponse = await fetch(`/api/manga/${source}/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (mangaResponse.ok) {
        const mangaData = await mangaResponse.json();
        setMangaInfo(mangaData);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const handleNextPage = () => {
    if (currentPage < images.length - 1) {
      trackPageReadingTime();
      setCurrentPage(prev => prev + 1);
    }
  };
  
  const handlePrevPage = () => {
    if (currentPage > 0) {
      trackPageReadingTime();
      setCurrentPage(prev => prev - 1);
    }
  };
  
  const trackPageReadingTime = () => {
    if (lastPageTimeRef.current) {
      const timeSpent = Date.now() - lastPageTimeRef.current;
      setPageReadingTimes(prev => ({
        ...prev,
        [currentPage]: timeSpent
      }));
      setTotalReadingTime(prev => prev + timeSpent);
    }
    lastPageTimeRef.current = Date.now();
  };
  
  const saveReadingProgress = async () => {
    if (!isAuthenticated || !mangaInfo) return;
    
    try {
      await fetch('/api/reading-progress', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          manga_id: id,
          source: source,
          manga_title: mangaInfo.title,
          current_chapter: chapterId,
          current_page: currentPage + 1,
          total_pages_in_chapter: images.length,
          chapters_read: 0, // This would need to be calculated based on completed chapters
          total_chapters: mangaInfo.chapters?.length || 0,
          reading_time: totalReadingTime / 1000 // Convert to seconds
        })
      });
    } catch (error) {
      console.error('Failed to save reading progress:', error);
    }
  };
  
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setFullscreen(true);
    } else {
      document.exitFullscreen();
      setFullscreen(false);
    }
  };
  
  const toggleAutoScroll = () => {
    setAutoScroll(!autoScroll);
  };
  
  const toggleNightMode = () => {
    setNightMode(!nightMode);
  };
  
  const toggleUI = () => {
    setShowUI(!showUI);
  };
  
  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.25, 3));
  };
  
  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.25, 0.5));
  };
  
  const resetZoom = () => {
    setZoom(1);
  };
  
  const toggleReadingDirection = () => {
    setReadingDirection(prev => prev === 'ltr' ? 'rtl' : 'ltr');
  };
  
  // Swipe handlers for mobile
  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => readingDirection === 'ltr' ? handleNextPage() : handlePrevPage(),
    onSwipedRight: () => readingDirection === 'ltr' ? handlePrevPage() : handleNextPage(),
    preventDefaultTouchmoveEvent: true,
    trackMouse: true
  });
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      switch (e.key) {
        case 'ArrowRight':
          e.preventDefault();
          readingDirection === 'ltr' ? handleNextPage() : handlePrevPage();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          readingDirection === 'ltr' ? handlePrevPage() : handleNextPage();
          break;
        case ' ':
          e.preventDefault();
          toggleAutoScroll();
          break;
        case 'f':
          e.preventDefault();
          toggleFullscreen();
          break;
        case 'z':
          e.preventDefault();
          toggleNightMode();
          break;
        case 'h':
          e.preventDefault();
          toggleUI();
          break;
        case 'Escape':
          if (fullscreen) {
            toggleFullscreen();
          }
          break;
      }
    };
    
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [readingDirection, fullscreen]);
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading chapter...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-red-500 text-xl">Error: {error}</div>
      </div>
    );
  }
  
  return (
    <div 
      ref={containerRef}
      className={`min-h-screen ${nightMode ? 'bg-gray-900' : 'bg-white'} transition-colors duration-300`}
      {...swipeHandlers}
      onMouseMove={() => setShowUI(true)}
    >
      {/* Main Reader */}
      <div className="relative w-full h-screen overflow-hidden">
        <TransformWrapper
          initialScale={zoom}
          minScale={0.5}
          maxScale={3}
          centerOnInit={true}
          wheel={{ step: 0.1 }}
        >
          <TransformComponent>
            <div className="flex flex-col items-center justify-center min-h-screen p-4">
              <AnimatePresence mode="wait">
                <motion.img
                  key={currentPage}
                  src={images[currentPage]}
                  alt={`Page ${currentPage + 1}`}
                  className={`max-w-full max-h-full object-contain ${
                    nightMode ? 'filter brightness-75 contrast-125' : ''
                  }`}
                  initial={{ opacity: 0, x: readingDirection === 'ltr' ? 100 : -100 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: readingDirection === 'ltr' ? -100 : 100 }}
                  transition={{ duration: 0.3 }}
                  onError={(e) => {
                    e.target.src = '/placeholder-manga.jpg';
                  }}
                />
              </AnimatePresence>
            </div>
          </TransformComponent>
        </TransformWrapper>
        
        {/* Page Navigation Overlay */}
        <div className="absolute inset-0 pointer-events-none">
          <div 
            className="absolute left-0 top-0 bottom-0 w-1/3 cursor-pointer"
            onClick={readingDirection === 'ltr' ? handlePrevPage : handleNextPage}
          />
          <div 
            className="absolute right-0 top-0 bottom-0 w-1/3 cursor-pointer"
            onClick={readingDirection === 'ltr' ? handleNextPage : handlePrevPage}
          />
        </div>
      </div>
      
      {/* UI Controls */}
      <AnimatePresence>
        {showUI && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="absolute top-0 left-0 right-0 z-50"
          >
            {/* Top Bar */}
            <div className={`p-4 ${nightMode ? 'bg-gray-800/90' : 'bg-white/90'} backdrop-blur-sm`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => navigate(-1)}
                    className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors"
                  >
                    <FaTimes className="w-5 h-5" />
                  </button>
                  <div>
                    <h1 className="font-bold text-lg">{mangaInfo?.title}</h1>
                    <p className="text-sm text-gray-600">Chapter {chapterId}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={toggleUI}
                    className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors"
                    title="Hide UI (H)"
                  >
                    <FaEyeSlash className="w-5 h-5" />
                  </button>
                  <button
                    onClick={toggleFullscreen}
                    className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors"
                    title="Fullscreen (F)"
                  >
                    {fullscreen ? <FaCompress className="w-5 h-5" /> : <FaExpand className="w-5 h-5" />}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Bottom Controls */}
      <AnimatePresence>
        {showUI && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="absolute bottom-0 left-0 right-0 z-50"
          >
            <div className={`p-4 ${nightMode ? 'bg-gray-800/90' : 'bg-white/90'} backdrop-blur-sm`}>
              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span>Page {currentPage + 1} of {images.length}</span>
                  <span>{Math.round(((currentPage + 1) / images.length) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-300 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentPage + 1) / images.length) * 100}%` }}
                  />
                </div>
              </div>
              
              {/* Control Buttons */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handlePrevPage}
                    disabled={currentPage === 0}
                    className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 disabled:opacity-50 transition-colors"
                    title="Previous Page (←)"
                  >
                    <FaArrowLeft className="w-5 h-5" />
                  </button>
                  
                  <button
                    onClick={toggleAutoScroll}
                    className={`p-2 rounded-full transition-colors ${
                      autoScroll ? 'bg-red-500 text-white' : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                    title="Auto Scroll (Space)"
                  >
                    {autoScroll ? <FaPause className="w-5 h-5" /> : <FaPlay className="w-5 h-5" />}
                  </button>
                  
                  <button
                    onClick={handleNextPage}
                    disabled={currentPage === images.length - 1}
                    className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 disabled:opacity-50 transition-colors"
                    title="Next Page (→)"
                  >
                    <FaArrowRight className="w-5 h-5" />
                  </button>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleZoomOut}
                    className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors"
                    title="Zoom Out"
                  >
                    <FaZoomOut className="w-5 h-5" />
                  </button>
                  
                  <button
                    onClick={resetZoom}
                    className="px-3 py-2 rounded bg-gray-200 hover:bg-gray-300 transition-colors text-sm"
                    title="Reset Zoom"
                  >
                    {Math.round(zoom * 100)}%
                  </button>
                  
                  <button
                    onClick={handleZoomIn}
                    className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors"
                    title="Zoom In"
                  >
                    <FaZoomIn className="w-5 h-5" />
                  </button>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={toggleReadingDirection}
                    className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors"
                    title="Toggle Reading Direction"
                  >
                    <span className="text-sm font-bold">{readingDirection.toUpperCase()}</span>
                  </button>
                  
                  <button
                    onClick={toggleNightMode}
                    className={`p-2 rounded-full transition-colors ${
                      nightMode ? 'bg-yellow-500 text-white' : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                    title="Night Mode (Z)"
                  >
                    {nightMode ? <FaSun className="w-5 h-5" /> : <FaMoon className="w-5 h-5" />}
                  </button>
                  
                  <button
                    className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors"
                    title="Bookmark"
                  >
                    <FaBookmark className="w-5 h-5" />
                  </button>
                  
                  <button
                    className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors"
                    title="Settings"
                  >
                    <FaCog className="w-5 h-5" />
                  </button>
                </div>
              </div>
              
              {/* Auto-scroll speed control */}
              {autoScroll && (
                <div className="mt-4 flex items-center space-x-2">
                  <span className="text-sm">Speed:</span>
                  <input
                    type="range"
                    min="0.5"
                    max="3"
                    step="0.5"
                    value={autoScrollSpeed}
                    onChange={(e) => setAutoScrollSpeed(parseFloat(e.target.value))}
                    className="flex-1"
                  />
                  <span className="text-sm">{autoScrollSpeed}x</span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Keyboard Shortcuts Help */}
      {showUI && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute top-20 right-4 z-50"
        >
          <div className={`p-4 rounded-lg ${nightMode ? 'bg-gray-800/90' : 'bg-white/90'} backdrop-blur-sm text-sm`}>
            <h3 className="font-bold mb-2">Keyboard Shortcuts</h3>
            <div className="space-y-1">
              <div>← → : Navigate pages</div>
              <div>Space : Auto-scroll</div>
              <div>F : Fullscreen</div>
              <div>Z : Night mode</div>
              <div>H : Hide UI</div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default EnhancedMangaReader; 