import React from 'react';
import { Link } from 'react-router-dom';

const sourceLabels = {
  weebcentral: 'WeebCentral',
  asurascans: 'Asura Scans',
};

const MangaCard = ({ manga }) => {
  const handleImageError = (e) => {
    e.target.style.display = 'none';
  };

  return (
    <Link to={`/manga/${manga.source}/${manga.id}`} className="bg-gray-800 rounded-lg shadow-sm border border-gray-700 overflow-hidden hover:shadow-md hover:border-gray-600 transition-all cursor-pointer">
      <div className="relative">
        <img
          src={manga.image}
          alt={manga.title}
          className="w-full h-48 object-cover"
          onError={handleImageError}
        />
        <span className="absolute top-2 left-2 bg-blue-600 text-white px-2 py-1 rounded text-xs font-semibold">
          {sourceLabels[manga.source] || manga.source}
        </span>
      </div>
      <div className="p-4">
        <h3 className="font-medium text-white mb-2 line-clamp-2">{manga.title}</h3>
        {manga.status && (
          <div className="text-sm text-gray-300 mb-1">
            <span className="font-medium">Status:</span> {manga.status}
          </div>
        )}
        {manga.chapter && (
          <div className="text-sm text-gray-400">
            <span className="font-medium">Chapter:</span> {manga.chapter}
          </div>
        )}
      </div>
    </Link>
  );
};

export default MangaCard; 