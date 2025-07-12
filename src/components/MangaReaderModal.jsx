import React, { useEffect, useState, useCallback, useRef } from 'react';

const MODES = ['single', 'double', 'vertical'];

const MangaReaderModal = ({ open, images, onClose, chapterTitle, chapters = [], currentChapterIndex = -1, onRequestChapter }) => {
  const [showControls, setShowControls] = useState(true);
  const [viewMode, setViewMode] = useState('vertical');
  const [currentPage, setCurrentPage] = useState(0);
  const [currentImageIndex, setCurrentImageIndex] = useState(0); // Track current image in vertical mode
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const [imagesError, setImagesError] = useState(false);
  const [loadedImages, setLoadedImages] = useState([]);
  const [isMobile, setIsMobile] = useState(false);
  const [isChapterLoading, setIsChapterLoading] = useState(false);
  const touchStartRef = useRef(null);
  const touchEndRef = useRef(null);

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
    if (!open) return;
    setCurrentPage(0);
    setCurrentImageIndex(0);
    setViewMode('vertical');
    setImagesLoaded(false);
    setImagesError(false);
    setLoadedImages([]);
  }, [open, images]);

  // Image loading with timeout
  useEffect(() => {
    if (!open || !images || images.length === 0) return;

    const timeout = setTimeout(() => {
      setImagesError(true);
      setImagesLoaded(true);
    }, 60000); // 60 seconds timeout

    let loadedCount = 0;
    const imagePromises = images.map((src, index) => {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
          loadedCount++;
          setLoadedImages(prev => [...prev, src]);
          if (loadedCount === images.length) {
            clearTimeout(timeout);
            setImagesLoaded(true);
          }
          resolve(src);
        };
        img.onerror = () => {
          loadedCount++;
          if (loadedCount === images.length) {
            clearTimeout(timeout);
            setImagesLoaded(true);
          }
          reject(src);
        };
        img.src = src;
      });
    });

    return () => {
      clearTimeout(timeout);
    };
  }, [open, images]);

  // Progress calculation
  const totalPages = images ? images.length : 0;
  const progress = totalPages > 0 ? ((viewMode === 'double' ? currentPage + 2 : currentPage + 1) / totalPages) * 100 : 0;

  // Navigation
  const nextPage = useCallback(() => {
    if (!images) return;
    const increment = viewMode === 'double' ? 2 : 1;
    setCurrentPage((prev) => Math.min(prev + increment, totalPages - 1));
  }, [images, viewMode, totalPages]);

  const prevPage = useCallback(() => {
    const decrement = viewMode === 'double' ? 2 : 1;
    setCurrentPage((prev) => Math.max(prev - decrement, 0));
  }, [viewMode]);

  // Navigation for vertical mode - scroll to next/previous image
  const nextVertical = useCallback(() => {
    console.log('Next button clicked, viewMode:', viewMode, 'currentImageIndex:', currentImageIndex);
    if (viewMode === 'vertical') {
      if (currentImageIndex < loadedImages.length - 1) {
        const newIndex = currentImageIndex + 1;
        setCurrentImageIndex(newIndex);
        
        // Scroll to the specific image
        setTimeout(() => {
          const imageElements = document.querySelectorAll('.manga-page-image');
          if (imageElements[newIndex]) {
            imageElements[newIndex].scrollIntoView({ 
              behavior: 'smooth', 
              block: 'start' 
            });
          }
        }, 100);
      }
    } else {
      nextPage();
    }
  }, [viewMode, nextPage, currentImageIndex, loadedImages.length]);

  const prevVertical = useCallback(() => {
    console.log('Previous button clicked, viewMode:', viewMode, 'currentImageIndex:', currentImageIndex);
    if (viewMode === 'vertical') {
      if (currentImageIndex > 0) {
        const newIndex = currentImageIndex - 1;
        setCurrentImageIndex(newIndex);
        
        // Scroll to the specific image
        setTimeout(() => {
          const imageElements = document.querySelectorAll('.manga-page-image');
          if (imageElements[newIndex]) {
            imageElements[newIndex].scrollIntoView({ 
              behavior: 'smooth', 
              block: 'start' 
            });
          }
        }, 100);
      }
    } else {
      prevPage();
    }
  }, [viewMode, prevPage, currentImageIndex]);

  // Touch gesture handling
  const handleTouchStart = useCallback((e) => {
    touchStartRef.current = e.touches[0].clientX;
  }, []);

  const handleTouchEnd = useCallback((e) => {
    if (!touchStartRef.current) return;
    
    touchEndRef.current = e.changedTouches[0].clientX;
    const diff = touchStartRef.current - touchEndRef.current;
    const minSwipeDistance = 50;

    if (Math.abs(diff) > minSwipeDistance) {
      if (diff > 0) {
        // Swipe left - next page
        nextVertical();
      } else {
        // Swipe right - previous page
        prevVertical();
      }
    }
    
    touchStartRef.current = null;
    touchEndRef.current = null;
  }, [nextVertical, prevVertical]);

  // Handle image click to toggle controls on mobile
  const handleImageClick = useCallback(() => {
    if (isMobile) {
      setShowControls(prev => !prev);
    }
  }, [isMobile]);

  // Keyboard navigation
  const handleKeyPress = useCallback(
    (e) => {
      if (!open) return;
      switch (e.key) {
        case 'Escape':
          onClose();
          break;
        case 'h':
        case 'H':
          setShowControls((prev) => !prev);
          break;
        case 'v':
        case 'V':
          setViewMode((prev) => {
            const idx = MODES.indexOf(prev);
            return MODES[(idx + 1) % MODES.length];
          });
          break;
        case 'ArrowRight':
        case ' ':
          nextVertical();
          break;
        case 'ArrowLeft':
          prevVertical();
          break;
        default:
          break;
      }
    },
    [open, onClose, viewMode, nextVertical, prevVertical]
  );

  useEffect(() => {
    if (!open) return;
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [open, handleKeyPress]);

  // Track current image when scrolling manually in vertical mode
  useEffect(() => {
    if (!open || viewMode !== 'vertical' || !loadedImages.length) return;

    const handleScroll = () => {
      const imageElements = document.querySelectorAll('.manga-page-image');
      const scrollTop = window.scrollY;
      const windowHeight = window.innerHeight;
      
      let currentIndex = 0;
      for (let i = 0; i < imageElements.length; i++) {
        const rect = imageElements[i].getBoundingClientRect();
        if (rect.top <= windowHeight / 2) {
          currentIndex = i;
        }
      }
      
      if (currentIndex !== currentImageIndex) {
        setCurrentImageIndex(currentIndex);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [open, viewMode, loadedImages.length, currentImageIndex]);

  // Handle chapter navigation with loading state
  const handleChapterNavigation = useCallback(async (direction) => {
    if (!onRequestChapter || chapters.length === 0) return;
    
    let targetIndex;
    let targetChapter;
    
    if (direction === 'next') {
      if (currentChapterIndex >= chapters.length - 1) return;
      targetIndex = currentChapterIndex + 1;
      targetChapter = chapters[targetIndex];
    } else {
      if (currentChapterIndex <= 0) return;
      targetIndex = currentChapterIndex - 1;
      targetChapter = chapters[targetIndex];
    }
    
    setIsChapterLoading(true);
    
    try {
      await onRequestChapter(targetChapter, targetIndex);
    } catch (error) {
      console.error('Error loading chapter:', error);
    } finally {
      // Keep loading state for a minimum time to show the transition
      setTimeout(() => {
        setIsChapterLoading(false);
      }, 500);
    }
  }, [onRequestChapter, chapters, currentChapterIndex]);

  if (!open) return null;

  // Render images for current mode
  let content = null;
  
  if (!imagesLoaded) {
    // Loading state
    content = (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4">Loading manga pages...</p>
        </div>
      </div>
    );
  } else if (imagesError || !images || images.length === 0) {
    // Error or no images state
    content = (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-white">
          <p className="text-xl mb-2">No manga found</p>
          <p className="text-gray-400">Images failed to load or no pages available</p>
        </div>
      </div>
    );
  } else if (viewMode === 'vertical') {
    content = (
      <div className={`${isMobile ? 'pt-20 pb-16' : 'pt-16 pb-8'}`}>
        {loadedImages.map((src, idx) => (
          <div key={src + idx} className={`${isMobile ? 'mb-2' : 'mb-4'}`}>
            <img
              src={src}
              alt={`chapter page ${idx + 1}`}
              className="manga-page-image max-w-full mx-auto cursor-pointer"
              loading="lazy"
              onClick={handleImageClick}
            />
          </div>
        ))}
      </div>
    );
  } else if (viewMode === 'single') {
    content = (
      <div className={`${isMobile ? 'pt-20 pb-16' : 'pt-16 pb-8'} flex justify-center`}>
        <img
          src={loadedImages[currentPage]}
          alt={`chapter page ${currentPage + 1}`}
          className="max-w-full cursor-pointer"
          loading="lazy"
          onClick={handleImageClick}
        />
      </div>
    );
  } else if (viewMode === 'double') {
    content = (
      <div className={`${isMobile ? 'pt-20 pb-16' : 'pt-16 pb-8'} flex justify-center ${isMobile ? 'flex-col gap-2' : 'gap-4'}`}>
        <img
          src={loadedImages[currentPage]}
          alt={`chapter page ${currentPage + 1}`}
          className={`${isMobile ? 'max-w-full' : 'max-w-[50%]'} cursor-pointer`}
          loading="lazy"
          onClick={handleImageClick}
        />
        {currentPage + 1 < loadedImages.length && (
          <img
            src={loadedImages[currentPage + 1]}
            alt={`chapter page ${currentPage + 2}`}
            className={`${isMobile ? 'max-w-full' : 'max-w-[50%]'} cursor-pointer`}
            loading="lazy"
            onClick={handleImageClick}
          />
        )}
      </div>
    );
  }

  return (
    <div 
      className="fixed inset-0 bg-black z-50 overflow-auto"
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      {/* Chapter Loading Modal */}
      {isChapterLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center">
          <div className="text-center text-white">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-lg font-medium">Loading chapter...</p>
            <p className="text-gray-400 text-sm mt-2">Please wait while the images load</p>
          </div>
        </div>
      )}

      {/* Left Navigation Button */}
      <button
        onClick={() => {
          console.log('Left button clicked');
          prevVertical();
        }}
        className={`fixed top-1/2 transform -translate-y-1/2 z-20 bg-black bg-opacity-50 hover:bg-opacity-70 text-white rounded-full transition-all duration-200 hover:scale-110 cursor-pointer ${
          isMobile 
            ? 'left-2 p-4 w-12 h-12' 
            : 'left-4 p-3 w-10 h-10'
        }`}
        title="Previous Page (←)"
      >
        <svg className={`${isMobile ? 'w-8 h-8' : 'w-6 h-6'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      {/* Right Navigation Button */}
      <button
        onClick={() => {
          console.log('Right button clicked');
          nextVertical();
        }}
        className={`fixed top-1/2 transform -translate-y-1/2 z-20 bg-black bg-opacity-50 hover:bg-opacity-70 text-white rounded-full transition-all duration-200 hover:scale-110 cursor-pointer ${
          isMobile 
            ? 'right-2 p-4 w-12 h-12' 
            : 'right-4 p-3 w-10 h-10'
        }`}
        title="Next Page (→ or Space)"
      >
        <svg className={`${isMobile ? 'w-8 h-8' : 'w-6 h-6'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>

      {/* Back to Top Button */}
      <button
        onClick={() => {
          console.log('Back to top clicked');
          console.log('Current scroll position:', window.scrollY);
          console.log('View mode:', viewMode);
          
          // Try multiple scroll methods
          try {
            // Method 1: Scroll to top of window
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Method 2: Also try scrolling the container
            const container = document.querySelector('.fixed.inset-0.bg-black.z-50.overflow-auto');
            if (container) {
              container.scrollTo({ top: 0, behavior: 'smooth' });
            }
            
            // Reset image index
            setCurrentImageIndex(0);
            console.log('Back to top executed');
          } catch (error) {
            console.error('Back to top error:', error);
            // Fallback: instant scroll
            window.scrollTo(0, 0);
          }
        }}
        className={`fixed z-30 bg-red-600 bg-opacity-90 hover:bg-opacity-100 text-white rounded-full transition-all duration-200 hover:scale-110 cursor-pointer shadow-lg ${
          isMobile 
            ? 'right-3 bottom-3 p-3 w-12 h-12' 
            : 'right-4 bottom-4 p-3 w-10 h-10'
        }`}
        title="Back to Top"
      >
        <div className="flex flex-col items-center">
          <svg className={`${isMobile ? 'w-6 h-6' : 'w-5 h-5'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
          {!isMobile && <span className="text-xs mt-1">TOP</span>}
        </div>
      </button>

      {/* Show Controls Button (when controls are hidden) */}
      {!showControls && (
        <div className={`fixed z-20 ${isMobile ? 'top-3 right-3' : 'top-4 right-4'}`}>
          <button
            onClick={() => setShowControls(true)}
            className={`bg-black bg-opacity-75 text-white rounded hover:bg-opacity-90 transition-all duration-200 cursor-pointer ${
              isMobile ? 'px-4 py-2 text-sm' : 'px-3 py-2'
            }`}
            title="Show Controls"
          >
            {isMobile ? 'Show' : 'Show Controls'}
          </button>
        </div>
      )}

      {showControls && (
        <div className={`fixed top-0 left-0 right-0 bg-black bg-opacity-75 text-white z-10 ${
          isMobile ? 'p-3' : 'p-4'
        }`}>
          <div className={`flex items-center justify-between mb-4 ${
            isMobile ? 'flex-col gap-3' : ''
          }`}>
            <button 
              onClick={onClose} 
              className={`bg-gray-700 rounded hover:bg-gray-600 ${
                isMobile ? 'px-4 py-2 text-sm w-full' : 'px-3 py-1'
              }`}
            >
              Close
            </button>
            
            <div className={`flex items-center gap-2 ${
              isMobile ? 'w-full' : ''
            }`}>
              {onRequestChapter && chapters.length > 0 && (
                <>
                  <button
                    className={`bg-gray-700 rounded hover:bg-gray-600 disabled:opacity-50 transition-colors ${
                      isMobile ? 'px-3 py-2 text-sm flex-1' : 'px-3 py-1'
                    } ${isChapterLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    onClick={() => handleChapterNavigation('prev')}
                    disabled={currentChapterIndex <= 0 || isChapterLoading}
                  >
                    {isMobile ? '← Previous' : '← Previous Chapter'}
                  </button>
                  <span className={`mx-2 text-gray-300 ${
                    isMobile ? 'text-center text-sm px-2' : ''
                  }`}>
                    {isMobile ? chapterTitle.substring(0, 15) + '...' : chapterTitle}
                  </span>
                  <button
                    className={`bg-gray-700 rounded hover:bg-gray-600 disabled:opacity-50 transition-colors ${
                      isMobile ? 'px-3 py-2 text-sm flex-1' : 'px-3 py-1'
                    } ${isChapterLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    onClick={() => handleChapterNavigation('next')}
                    disabled={currentChapterIndex === -1 || currentChapterIndex >= chapters.length - 1 || isChapterLoading}
                  >
                    {isMobile ? 'Next →' : 'Next Chapter →'}
                  </button>
                </>
              )}
            </div>
            
            <button 
              onClick={() => setShowControls((prev) => !prev)} 
              className={`bg-gray-700 rounded hover:bg-gray-600 ${
                isMobile ? 'px-4 py-2 text-sm w-full' : 'px-3 py-1'
              }`}
            >
              {isMobile ? 'Hide UI' : 'Hide UI (H)'}
            </button>
          </div>
          
          {/* Progress bar */}
          <div className="w-full bg-gray-700 rounded-full h-2 mb-4">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          
          <div className="flex items-center justify-center">
            <button
              className={`bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors ${
                isMobile ? 'px-4 py-2 text-sm w-full' : 'px-3 py-1 text-sm'
              }`}
              onClick={() => setViewMode((prev) => {
                const idx = MODES.indexOf(prev);
                return MODES[(idx + 1) % MODES.length];
              })}
              title="Change View Mode (V)"
            >
              {isMobile ? 'Change Mode' : 'Change Mode (V)'}
            </button>
          </div>
        </div>
      )}
      {content}
    </div>
  );
};

export default MangaReaderModal; 