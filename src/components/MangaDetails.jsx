import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import MangaReaderModal from './MangaReaderModal.jsx';

const MangaDetails = () => {
  const { id, source } = useParams();
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

  const handleChapterClick = async (e, chapter) => {
    e.preventDefault();
    setReaderLoading(true);
    setReaderOpen(true);
    setReaderTitle(chapter.title);
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
        <Link to="/" className="mb-6 px-4 py-2 bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors inline-block">
          ← Back to Search
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
        <Link to="/" className="mb-6 px-4 py-2 bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors inline-block">
          ← Back to Search
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
        <Link to="/" className="px-4 py-2 bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors inline-block">
          ← Back to Search
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
          <div className="space-y-2">
            {manga.chapters.map((chapter, idx) => (
              <div 
                key={`${chapter.url}-${idx}`} 
                className="flex items-center justify-between p-4 bg-gray-800 rounded-lg border border-gray-700 hover:bg-gray-700 cursor-pointer transition-colors"
                  onClick={e => handleChapterClick(e, chapter)}
                >
                <div>
                  <h3 className="font-medium text-white mb-1">{chapter.title}</h3>
                  <p className="text-sm text-gray-400">{chapter.number}</p>
                </div>
                <span className="text-sm text-gray-500">{chapter.date}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <MangaReaderModal
        open={readerOpen}
        images={readerImages}
        onClose={() => setReaderOpen(false)}
        chapterTitle={readerTitle}
      />
      
      {readerOpen && readerLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="text-center text-white">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4">Loading pages...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MangaDetails; 