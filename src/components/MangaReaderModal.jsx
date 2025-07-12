import React, { useEffect, useState, useCallback } from 'react';

const MODES = ['single', 'double', 'vertical'];

const MangaReaderModal = ({ open, images, onClose, chapterTitle, chapters = [], currentChapterIndex = -1, onRequestChapter }) => {
  const [showControls, setShowControls] = useState(true);
  const [viewMode, setViewMode] = useState('vertical');
  const [currentPage, setCurrentPage] = useState(0);
  const [currentImageIndex, setCurrentImageIndex] = useState(0); // Track current image in vertical mode
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const [imagesError, setImagesError] = useState(false);
  const [loadedImages, setLoadedImages] = useState([]);

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
      <div className="pt-16 pb-8">
        {loadedImages.map((src, idx) => (
          <div key={src + idx} className="mb-4">
            <img
              src={src}
              alt={`chapter page ${idx + 1}`}
              className="manga-page-image max-w-full mx-auto"
              loading="lazy"
            />
          </div>
        ))}
      </div>
    );
  } else if (viewMode === 'single') {
    content = (
      <div className="pt-16 pb-8 flex justify-center">
        <img
          src={loadedImages[currentPage]}
          alt={`chapter page ${currentPage + 1}`}
          className="max-w-full"
          loading="lazy"
        />
      </div>
    );
  } else if (viewMode === 'double') {
    content = (
      <div className="pt-16 pb-8 flex justify-center gap-4">
        <img
          src={loadedImages[currentPage]}
          alt={`chapter page ${currentPage + 1}`}
          className="max-w-[50%]"
          loading="lazy"
        />
        {currentPage + 1 < loadedImages.length && (
          <img
            src={loadedImages[currentPage + 1]}
            alt={`chapter page ${currentPage + 2}`}
            className="max-w-[50%]"
            loading="lazy"
          />
        )}
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black z-50 overflow-auto">
      {/* Left Navigation Button */}
      <button
        onClick={() => {
          console.log('Left button clicked');
          prevVertical();
        }}
        className="fixed left-4 top-1/2 transform -translate-y-1/2 z-20 bg-black bg-opacity-50 hover:bg-opacity-70 text-white rounded-full p-3 transition-all duration-200 hover:scale-110 cursor-pointer"
        title="Previous Page (←)"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      {/* Right Navigation Button */}
      <button
        onClick={() => {
          console.log('Right button clicked');
          nextVertical();
        }}
        className="fixed right-4 top-1/2 transform -translate-y-1/2 z-20 bg-black bg-opacity-50 hover:bg-opacity-70 text-white rounded-full p-3 transition-all duration-200 hover:scale-110 cursor-pointer"
        title="Next Page (→ or Space)"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
        className="fixed right-4 bottom-4 z-30 bg-red-600 bg-opacity-90 hover:bg-opacity-100 text-white rounded-full p-3 transition-all duration-200 hover:scale-110 cursor-pointer shadow-lg"
        title="Back to Top"
      >
        <div className="flex flex-col items-center">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
          <span className="text-xs mt-1">TOP</span>
        </div>
      </button>

      {/* Show Controls Button (when controls are hidden) */}
      {!showControls && (
        <div className="fixed top-4 right-4 z-20">
          <button
            onClick={() => setShowControls(true)}
            className="px-3 py-2 bg-black bg-opacity-75 text-white rounded hover:bg-opacity-90 transition-all duration-200 cursor-pointer"
            title="Show Controls"
          >
            Show Controls
          </button>
        </div>
      )}

      {showControls && (
        <div className="fixed top-0 left-0 right-0 bg-black bg-opacity-75 text-white p-4 z-10">
          <div className="flex items-center justify-between mb-4">
            <button onClick={onClose} className="px-3 py-1 bg-gray-700 rounded hover:bg-gray-600">Close</button>
            <div className="flex items-center gap-2">
              {onRequestChapter && chapters.length > 0 && (
                <>
                  <button
                    className="px-3 py-1 bg-gray-700 rounded hover:bg-gray-600 disabled:opacity-50"
                    onClick={() => onRequestChapter(chapters[currentChapterIndex - 1], currentChapterIndex - 1)}
                    disabled={currentChapterIndex <= 0}
                  >
                    ← Previous Chapter
                  </button>
                  <span className="mx-2 text-gray-300">{chapterTitle}</span>
                  <button
                    className="px-3 py-1 bg-gray-700 rounded hover:bg-gray-600 disabled:opacity-50"
                    onClick={() => onRequestChapter(chapters[currentChapterIndex + 1], currentChapterIndex + 1)}
                    disabled={currentChapterIndex === -1 || currentChapterIndex >= chapters.length - 1}
                  >
                    Next Chapter →
                  </button>
                </>
              )}
            </div>
            <button onClick={() => setShowControls((prev) => !prev)} className="px-3 py-1 bg-gray-700 rounded hover:bg-gray-600">Hide UI (H)</button>
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
              className="px-3 py-1 bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors text-sm"
              onClick={() => setViewMode((prev) => {
                const idx = MODES.indexOf(prev);
                return MODES[(idx + 1) % MODES.length];
              })}
              title="Change View Mode (V)"
            >
              Change Mode
            </button>
          </div>
        </div>
      )}
      {content}
    </div>
  );
};

export default MangaReaderModal; 