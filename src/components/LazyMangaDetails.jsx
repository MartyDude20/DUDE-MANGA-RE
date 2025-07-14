import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { FaArrowLeft, FaSpinner, FaEye, FaEyeSlash, FaBookmark, FaShare } from 'react-icons/fa';
import ProgressIndicator from './ProgressIndicator';
import LazyChapterList from './LazyChapterList';
import MangaReaderModal from './MangaReaderModal';

const LazyMangaDetails = () => {
  const { source, id } = useParams();
  const [manga, setManga] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState({});
  const [sessionId] = useState(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [readerOpen, setReaderOpen] = useState(false);
  const [readerImages, setReaderImages] = useState([]);
  const [readerLoading, setReaderLoading] = useState(false);
  const [readerTitle, setReaderTitle] = useState('');
  const [isSaved, setIsSaved] = useState(false);
  const [forceRefresh, setForceRefresh] = useState(false);

  // Progress polling
  const [progressPolling, setProgressPolling] = useState(null);

  // Fetch manga details with progress tracking
  const fetchMangaDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      setProgress({});

      // Start progress polling
      startProgressPolling();

      const params = {
        session_id: sessionId,
        ...(forceRefresh && { refresh: 'true' })
      };

      const response = await axios.get(`/api/lazy/manga/${id}/details`, { params });
      setManga(response.data);
      
      // Check if manga is saved
      const savedManga = JSON.parse(localStorage.getItem('savedManga') || '[]');
      const isMangaSaved = savedManga.some(saved => 
        saved.id === id && saved.source === source
      );
      setIsSaved(isMangaSaved);
      
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch manga details');
    } finally {
      setLoading(false);
      stopProgressPolling();
    }
  }, [id, source, sessionId, forceRefresh]);

  // Progress polling functions
  const startProgressPolling = useCallback(() => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`/api/lazy/progress/${sessionId}`);
        setProgress(response.data);
      } catch (err) {
        // Progress endpoint might not exist yet or session expired
        console.debug('Progress polling error:', err.message);
      }
    }, 500); // Poll every 500ms

    setProgressPolling(pollInterval);
  }, [sessionId]);

  const stopProgressPolling = useCallback(() => {
    if (progressPolling) {
      clearInterval(progressPolling);
      setProgressPolling(null);
    }
  }, [progressPolling]);

  // Load manga details on mount
  useEffect(() => {
    if (id && source) {
      fetchMangaDetails();
    }

    return () => {
      stopProgressPolling();
    };
  }, [id, source, fetchMangaDetails, stopProgressPolling]);

  // Handle chapter click
  const handleChapterClick = async (chapter) => {
    setReaderLoading(true);
    setReaderOpen(true);
    setReaderTitle(chapter.title);
    
    try {
      const params = { session_id: sessionId };
      const response = await axios.get(`/api/lazy/chapter-images/${encodeURIComponent(chapter.url)}`, { params });
      setReaderImages(response.data.images || []);
    } catch (err) {
      setReaderImages([]);
      console.error('Failed to load chapter images:', err);
    } finally {
      setReaderLoading(false);
    }
  };

  // Save/unsave manga
  const toggleSaved = () => {
    const savedManga = JSON.parse(localStorage.getItem('savedManga') || '[]');
    const mangaKey = `${source}-${id}`;
    
    if (isSaved) {
      const updated = savedManga.filter(saved => 
        !(saved.id === id && saved.source === source)
      );
      localStorage.setItem('savedManga', JSON.stringify(updated));
      setIsSaved(false);
    } else {
      const newSaved = {
        id,
        source,
        title: manga?.title || 'Unknown',
        image: manga?.image || '',
        addedAt: new Date().toISOString()
      };
      savedManga.push(newSaved);
      localStorage.setItem('savedManga', JSON.stringify(savedManga));
      setIsSaved(true);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Link to="/" className="mb-6 bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors inline-block px-4 py-2">
          <FaArrowLeft className="inline mr-2" />
          Back to Search
        </Link>
        
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-400 mt-4">Loading manga details...</p>
          
          {/* Progress Indicators */}
          {Object.keys(progress).length > 0 && (
            <div className="mt-6 space-y-4">
              {Object.entries(progress).map(([step, data]) => (
                <ProgressIndicator
                  key={step}
                  step={step}
                  progress={data.progress}
                  message={data.message}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Link to="/" className="mb-6 bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors inline-block px-4 py-2">
          <FaArrowLeft className="inline mr-2" />
          Back to Search
        </Link>
        <div className="p-4 bg-red-900 border border-red-600 text-red-200 rounded-lg">
          {error}
        </div>
      </div>
    );
  }

  // Main content
  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Link to="/" className="bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors inline-block px-4 py-2">
          <FaArrowLeft className="inline mr-2" />
          Back to Search
        </Link>
        
        <div className="flex space-x-2">
          <button
            onClick={() => setForceRefresh(!forceRefresh)}
            className="bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors px-4 py-2"
          >
            <FaSpinner className="inline mr-2" />
            Refresh
          </button>
          
          <button
            onClick={toggleSaved}
            className={`rounded-lg transition-colors px-4 py-2 ${
              isSaved 
                ? 'bg-green-600 text-white hover:bg-green-700' 
                : 'bg-gray-600 text-gray-200 hover:bg-gray-700'
            }`}
          >
            {isSaved ? <FaEyeSlash className="inline mr-2" /> : <FaEye className="inline mr-2" />}
            {isSaved ? 'Saved' : 'Save'}
          </button>
          
          <button className="bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors px-4 py-2">
            <FaShare className="inline mr-2" />
            Share
          </button>
        </div>
      </div>

      {/* Manga Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Cover Image */}
        <div className="md:col-span-1">
          <div className="relative">
            {manga?.image ? (
              <img
                src={manga.image}
                alt={manga.title}
                className="w-full h-96 object-cover rounded-lg shadow-lg"
                onError={(e) => {
                  e.target.src = '/placeholder-manga.jpg';
                }}
              />
            ) : (
              <div className="w-full h-96 bg-gray-300 rounded-lg shadow-lg flex items-center justify-center">
                <span className="text-gray-500">No Image</span>
              </div>
            )}
          </div>
        </div>

        {/* Manga Details */}
        <div className="md:col-span-2">
          <h1 className="text-3xl font-bold text-gray-100 mb-4">{manga?.title}</h1>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <span className="text-gray-400">Author:</span>
              <p className="text-gray-200">{manga?.author || 'Unknown'}</p>
            </div>
            <div>
              <span className="text-gray-400">Status:</span>
              <p className="text-gray-200">{manga?.status || 'Unknown'}</p>
            </div>
            <div>
              <span className="text-gray-400">Total Chapters:</span>
              <p className="text-gray-200">{manga?.total_chapters || manga?.chapters?.length || 0}</p>
            </div>
            <div>
              <span className="text-gray-400">Source:</span>
              <p className="text-gray-200 capitalize">{manga?.source}</p>
            </div>
          </div>

          <div className="mb-6">
            <span className="text-gray-400">Description:</span>
            <p className="text-gray-200 mt-2 leading-relaxed">
              {manga?.description || 'No description available.'}
            </p>
          </div>

          {/* Progress Indicators */}
          {Object.keys(progress).length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-200 mb-3">Loading Progress</h3>
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
        </div>
      </div>

      {/* Chapters Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-100">Chapters</h2>
          <div className="text-gray-400">
            {manga?.chapters?.length || 0} of {manga?.total_chapters || 0} chapters
          </div>
        </div>
        
        <LazyChapterList
          mangaId={id}
          source={source}
          initialChapters={manga?.chapters || []}
          totalChapters={manga?.total_chapters || 0}
          hasMoreChapters={manga?.has_more_chapters || false}
          sessionId={sessionId}
          onChapterClick={handleChapterClick}
        />
      </div>

      {/* Reader Modal */}
      <MangaReaderModal
        open={readerOpen}
        images={readerImages}
        onClose={() => setReaderOpen(false)}
        chapterTitle={readerTitle}
        loading={readerLoading}
      />
    </div>
  );
};

export default LazyMangaDetails; 