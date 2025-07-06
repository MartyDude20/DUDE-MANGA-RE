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

  useEffect(() => {
    const fetchMangaDetails = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await axios.get(`/api/manga/${source}/${id}`);
        setManga(response.data);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to fetch manga details');
      } finally {
        setLoading(false);
      }
    };

    if (id && source) {
      fetchMangaDetails();
    }
  }, [id, source]);

  const handleImageError = (e) => {
    e.target.style.display = 'none';
  };

  const handleChapterClick = async (e, chapter) => {
    e.preventDefault();
    setReaderLoading(true);
    setReaderOpen(true);
    setReaderTitle(chapter.title);
    try {
      // chapter.url is like 'bones-b58b6f2f/chapter/30', id is manga_id
      const resp = await axios.get(`/api/chapter-images/${source}/${id}/${chapter.url}`);
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
      <Link to="/" className="mb-6 px-4 py-2 bg-gray-700 text-gray-200 rounded-lg hover:bg-gray-600 transition-colors inline-block">
        ← Back to Search
      </Link>
      
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