import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getProxiedImageUrl } from '../utils/imageProxy.js';

const sourceLabels = {
  weebcentral: 'WeebCentral',
  asurascans: 'Asura Scans',
};

const MangaCard = ({ manga }) => {
  const [isSaved, setIsSaved] = useState(false);

  // Check if manga is saved on component mount
  useEffect(() => {
    const savedManga = JSON.parse(localStorage.getItem('savedManga') || '[]');
    const isMangaSaved = savedManga.some(saved => 
      saved.id === manga.id && saved.source === manga.source
    );
    setIsSaved(isMangaSaved);
    
    // Debug: Log image URL
    console.log('MangaCard - Title:', manga.title, 'Image URL:', manga.image, 'Source:', manga.source);
  }, [manga.id, manga.source]);

  const handleImageError = (e) => {
    console.log('Image failed to load:', e.target.src);
    console.log('Manga:', manga.title, 'Source:', manga.source);
    // Show a placeholder image instead of hiding the image
    e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIwIiBoZWlnaHQ9IjMyMCIgdmlld0JveD0iMCAwIDMyMCAzMjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMjAiIGhlaWdodD0iMzIwIiBmaWxsPSIjMzc0MTUxIi8+CjxwYXRoIGQ9Ik0xNjAgODBDMTI4IDgwIDEwMiAxMDYgMTAyIDEzOEMxMDIgMTcwIDEyOCAxOTYgMTYwIDE5NkMxOTIgMTk2IDIxOCAxNzAgMjE4IDEzOEMyMTggMTA2IDE5MiA4MCAxNjAgODBaIiBmaWxsPSIjNkI3MjgwIi8+CjxwYXRoIGQ9Ik0xNjAgMjE2QzE5MiAyMTYgMjE4IDI0MiAyMTggMjc0QzIxOCAzMDYgMTkyIDMzMiAxNjAgMzMyQzEyOCAzMzIgMTAyIDMwNiAxMDIgMjc0QzEwMiAyNDIgMTI4IDIxNiAxNjAgMjE2WiIgZmlsbD0iIzZCNzI4MCIvPgo8L3N2Zz4K';
    e.target.alt = 'Image not available';
    e.target.className = 'w-full h-80 object-cover opacity-50';
  };

  const handleSaveToggle = (e) => {
    e.preventDefault(); // Prevent navigation
    e.stopPropagation(); // Prevent event bubbling
    
    const savedManga = JSON.parse(localStorage.getItem('savedManga') || '[]');
    
    if (isSaved) {
      // Remove from saved list
      const updatedList = savedManga.filter(saved => 
        !(saved.id === manga.id && saved.source === manga.source)
      );
      localStorage.setItem('savedManga', JSON.stringify(updatedList));
      setIsSaved(false);
    } else {
      // Add to saved list
      const mangaToSave = {
        id: manga.id,
        title: manga.title,
        image: manga.image,
        source: manga.source,
        status: manga.status,
        chapter: manga.chapter,
        savedAt: new Date().toISOString()
      };
      savedManga.push(mangaToSave);
      localStorage.setItem('savedManga', JSON.stringify(savedManga));
      setIsSaved(true);
    }
  };

  return (
    <Link to={`/manga/${manga.source}/${manga.id}`} className="bg-gray-800 rounded-lg shadow-sm border border-gray-700 overflow-hidden hover:shadow-md hover:border-gray-600 transition-all cursor-pointer group">
      <div className="relative">
        <img
          src={getProxiedImageUrl(manga.image)}
          alt={manga.title}
          className="w-full h-80 object-cover"
          onError={handleImageError}
        />
        <span className="absolute top-2 left-2 bg-blue-600 text-white px-2 py-1 rounded text-xs font-semibold">
          {sourceLabels[manga.source] || manga.source}
        </span>
        
        {/* Save Button */}
        <button
          onClick={handleSaveToggle}
          className={`absolute top-2 right-2 p-2 rounded-full transition-all ${
            isSaved 
              ? 'bg-red-600 hover:bg-red-700 text-white' 
              : 'bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white'
          }`}
          title={isSaved ? 'Remove from saved' : 'Save manga'}
        >
          {isSaved ? (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          )}
        </button>
      </div>
      <div className="p-4">
        <h3 className="text-xl font-semibold text-white text-center">{manga.title}</h3>
      </div>
    </Link>
  );
};

export default MangaCard; 