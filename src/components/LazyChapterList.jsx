import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { FaChevronDown, FaChevronUp, FaSpinner, FaEye } from 'react-icons/fa';
import ProgressIndicator from './ProgressIndicator';

const LazyChapterList = ({ 
  mangaId, 
  source, 
  initialChapters, 
  totalChapters, 
  hasMoreChapters, 
  sessionId, 
  onChapterClick 
}) => {
  const [chapters, setChapters] = useState(initialChapters);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState({});
  const [offset, setOffset] = useState(initialChapters.length);
  const [hasMore, setHasMore] = useState(hasMoreChapters);
  const [expanded, setExpanded] = useState(false);

  // Progress polling
  const [progressPolling, setProgressPolling] = useState(null);

  // Load more chapters
  const loadMoreChapters = useCallback(async () => {
    if (loadingMore || !hasMore) return;

    try {
      setLoadingMore(true);
      setError('');
      setProgress({});

      // Start progress polling
      startProgressPolling();

      const params = {
        offset,
        limit: 10,
        session_id: sessionId
      };

      const response = await axios.get(`/api/lazy/manga/${mangaId}/chapters`, { params });
      
      const newChapters = response.data.chapters || [];
      setChapters(prev => [...prev, ...newChapters]);
      setOffset(prev => prev + newChapters.length);
      setHasMore(response.data.has_more);

    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load more chapters');
    } finally {
      setLoadingMore(false);
      stopProgressPolling();
    }
  }, [mangaId, offset, hasMore, loadingMore, sessionId]);

  // Progress polling functions
  const startProgressPolling = useCallback(() => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`/api/lazy/progress/${sessionId}`);
        setProgress(response.data);
      } catch (err) {
        console.debug('Progress polling error:', err.message);
      }
    }, 500);

    setProgressPolling(pollInterval);
  }, [sessionId]);

  const stopProgressPolling = useCallback(() => {
    if (progressPolling) {
      clearInterval(progressPolling);
      setProgressPolling(null);
    }
  }, [progressPolling]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopProgressPolling();
    };
  }, [stopProgressPolling]);

  // Handle chapter click
  const handleChapterClick = (chapter) => {
    onChapterClick(chapter);
  };

  // Format chapter number
  const formatChapterNumber = (title) => {
    const match = title.match(/Chapter\s+(\d+(?:\.\d+)?)/i);
    return match ? match[1] : title;
  };

  // Sort chapters by number (descending - newest first)
  const sortedChapters = [...chapters].sort((a, b) => {
    const aNum = parseFloat(formatChapterNumber(a.title)) || 0;
    const bNum = parseFloat(formatChapterNumber(b.title)) || 0;
    return bNum - aNum;
  });

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      {/* Header */}
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-700 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center space-x-3">
          <span className="text-lg">📚</span>
          <div>
            <h3 className="font-semibold text-gray-200">Chapters</h3>
            <p className="text-sm text-gray-400">
              {chapters.length} of {totalChapters} chapters loaded
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {expanded ? <FaChevronUp className="text-gray-400" /> : <FaChevronDown className="text-gray-400" />}
        </div>
      </div>

      {/* Progress Indicators */}
      {Object.keys(progress).length > 0 && (
        <div className="px-4 pb-4">
          <div className="space-y-3">
            {Object.entries(progress).map(([step, data]) => (
              <ProgressIndicator
                key={step}
                step={step}
                progress={data.progress}
                message={data.message}
              />
            ))}
          </div>
        </div>
      )}

      {/* Chapters List */}
      {expanded && (
        <div className="border-t border-gray-700">
          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-900 border border-red-600 text-red-200 rounded-lg m-4">
              {error}
            </div>
          )}

          {/* Chapters */}
          <div className="max-h-96 overflow-y-auto">
            {sortedChapters.length > 0 ? (
              <div className="divide-y divide-gray-700">
                {sortedChapters.map((chapter, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 hover:bg-gray-700 transition-colors cursor-pointer"
                    onClick={() => handleChapterClick(chapter)}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-sm text-gray-400 font-mono">
                        {formatChapterNumber(chapter.title)}
                      </span>
                      <span className="text-gray-200">{chapter.title}</span>
                    </div>
                    <FaEye className="text-gray-400 hover:text-blue-400 transition-colors" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-gray-400">
                No chapters available
              </div>
            )}
          </div>

          {/* Load More Button */}
          {hasMore && (
            <div className="p-4 border-t border-gray-700">
              <button
                onClick={loadMoreChapters}
                disabled={loadingMore}
                className="w-full bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors py-2 px-4 flex items-center justify-center space-x-2"
              >
                {loadingMore ? (
                  <>
                    <FaSpinner className="animate-spin" />
                    <span>Loading more chapters...</span>
                  </>
                ) : (
                  <>
                    <FaChevronDown />
                    <span>Load More Chapters</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* End of chapters */}
          {!hasMore && chapters.length > 0 && (
            <div className="p-4 border-t border-gray-700 text-center text-gray-400 text-sm">
              All chapters loaded ({chapters.length} total)
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LazyChapterList; 