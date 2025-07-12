import React, { useEffect, useState, useCallback } from 'react';

const MODES = ['single', 'double', 'vertical'];

const MangaReaderModal = ({ open, images, onClose, chapterTitle, chapters = [], currentChapterIndex = -1, onRequestChapter }) => {
  const [showControls, setShowControls] = useState(true);
  const [viewMode, setViewMode] = useState('vertical');
  const [currentPage, setCurrentPage] = useState(0);
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const [imagesError, setImagesError] = useState(false);
  const [loadedImages, setLoadedImages] = useState([]);

  useEffect(() => {
    if (!open) return;
    setCurrentPage(0);
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
          if (viewMode === 'vertical') {
            window.scrollBy(0, window.innerHeight * 0.8);
          } else {
            nextPage();
          }
          break;
        case 'ArrowLeft':
          if (viewMode === 'vertical') {
            window.scrollBy(0, -window.innerHeight * 0.8);
          } else {
            prevPage();
          }
          break;
        default:
          break;
      }
    },
    [open, onClose, viewMode, nextPage, prevPage]
  );

  useEffect(() => {
    if (!open) return;
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [open, handleKeyPress]);

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
              className="max-w-full mx-auto"
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
          
          <div className="flex items-center justify-between">
            <div className="flex space-x-2">
              <button
                className="px-3 py-1 bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors text-sm"
                onClick={() => setShowControls((prev) => !prev)}
                title="Toggle Controls (H)"
              >
                Hide Controls
              </button>
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
            
            <div className="flex space-x-2">
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={prevPage}
                disabled={currentPage === 0}
                title="Previous Page (←)"
              >
                &#8592;
              </button>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={nextPage}
                disabled={currentPage >= totalPages - (viewMode === 'double' ? 2 : 1)}
                title="Next Page (→ or Space)"
              >
                &#8594;
              </button>
            </div>
            </div>
          </div>
        )}
        {content}
    </div>
  );
};

export default MangaReaderModal; 