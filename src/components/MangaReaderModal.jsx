import React, { useEffect, useState, useCallback } from 'react';
import './MangaReaderModal.css';

const MODES = ['single', 'double', 'vertical'];

const MangaReaderModal = ({ open, images, onClose, chapterTitle }) => {
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
      <div className="manga-reader-loading-container">
        <div className="manga-reader-loading-circle"></div>
        <p>Loading manga pages...</p>
      </div>
    );
  } else if (imagesError || !images || images.length === 0) {
    // Error or no images state
    content = (
      <div className="manga-reader-no-pages">
        <p>No manga found</p>
        <p>Images failed to load or no pages available</p>
      </div>
    );
  } else if (viewMode === 'vertical') {
    content = (
      <div className="manga-reader-images manga-reader-vertical-images">
        {loadedImages.map((src, idx) => (
          <div key={src + idx} className="manga-reader-image-wrapper">
            <img
              src={src}
              alt={`chapter page ${idx + 1}`}
              className="manga-reader-image"
              loading="lazy"
            />
          </div>
        ))}
      </div>
    );
  } else if (viewMode === 'single') {
    content = (
      <div className="manga-reader-images manga-reader-single-image">
        <div className="manga-reader-image-wrapper">
          <img
            src={loadedImages[currentPage]}
            alt={`chapter page ${currentPage + 1}`}
            className="manga-reader-image"
            loading="lazy"
          />
        </div>
      </div>
    );
  } else if (viewMode === 'double') {
    content = (
      <div className="manga-reader-images manga-reader-double-images">
        <div className="manga-reader-image-wrapper">
          <img
            src={loadedImages[currentPage]}
            alt={`chapter page ${currentPage + 1}`}
            className="manga-reader-image"
            loading="lazy"
          />
          {currentPage + 1 < loadedImages.length && (
            <img
              src={loadedImages[currentPage + 1]}
              alt={`chapter page ${currentPage + 2}`}
              className="manga-reader-image"
              loading="lazy"
            />
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="manga-reader-modal-overlay">
      <div className={`manga-reader-modal-content manga-reader-${viewMode}`}>
        {showControls && (
          <div className="manga-reader-header">
            <button className="manga-reader-close" onClick={onClose}>&times;</button>
            <h2 className="manga-reader-title">{chapterTitle}</h2>
            {/* Progress bar */}
            <div className="manga-reader-progress-bar">
              <div
                className="manga-reader-progress"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="manga-reader-controls">
              <span className="manga-reader-mode">{viewMode.charAt(0).toUpperCase() + viewMode.slice(1)} Mode</span>
              <span className="manga-reader-page-info">
                {viewMode === 'double'
                  ? `${currentPage + 1}-${Math.min(currentPage + 2, totalPages)} / ${totalPages}`
                  : `${currentPage + 1} / ${totalPages}`}
              </span>
              <button
                className="manga-reader-toggle-controls"
                onClick={() => setShowControls((prev) => !prev)}
                title="Toggle Controls (H)"
              >
                Hide Controls
              </button>
              <button
                className="manga-reader-toggle-mode"
                onClick={() => setViewMode((prev) => {
                  const idx = MODES.indexOf(prev);
                  return MODES[(idx + 1) % MODES.length];
                })}
                title="Change View Mode (V)"
              >
                Change Mode
              </button>
            </div>
            <div className="manga-reader-nav-buttons">
              <button
                className="manga-reader-nav-btn"
                onClick={prevPage}
                disabled={currentPage === 0}
                title="Previous Page (←)"
              >
                &#8592;
              </button>
              <button
                className="manga-reader-nav-btn"
                onClick={nextPage}
                disabled={currentPage >= totalPages - (viewMode === 'double' ? 2 : 1)}
                title="Next Page (→ or Space)"
              >
                &#8594;
              </button>
            </div>
          </div>
        )}
        {content}
      </div>
    </div>
  );
};

export default MangaReaderModal; 