import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import MangaCard from './MangaCard.jsx';

const SavedManga = () => {
  const [savedManga, setSavedManga] = useState([]);
  const [sortBy, setSortBy] = useState('savedAt'); // 'savedAt', 'title', 'source', 'lastRead'
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc', 'desc'
  const [filterSource, setFilterSource] = useState('all');

  // Load saved manga from localStorage
  useEffect(() => {
    const loadSavedManga = () => {
      const saved = JSON.parse(localStorage.getItem('savedManga') || '[]');
      setSavedManga(saved);
    };

    loadSavedManga();
    
    // Listen for storage changes (when manga is saved/unsaved from other pages)
    const handleStorageChange = (e) => {
      if (e.key === 'savedManga') {
        loadSavedManga();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Sort and filter manga
  const sortedAndFilteredManga = savedManga
    .filter(manga => filterSource === 'all' || manga.source === filterSource)
    .sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'title':
          comparison = a.title.localeCompare(b.title);
          break;
        case 'source':
          comparison = a.source.localeCompare(b.source);
          break;
        case 'lastRead':
          // Get last read time from localStorage or use savedAt as fallback
          const aLastRead = localStorage.getItem(`lastRead_${a.source}_${a.id}`) || a.savedAt;
          const bLastRead = localStorage.getItem(`lastRead_${b.source}_${b.id}`) || b.savedAt;
          comparison = new Date(aLastRead) - new Date(bLastRead);
          break;
        case 'savedAt':
        default:
          comparison = new Date(a.savedAt) - new Date(b.savedAt);
          break;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const handleRemoveAll = () => {
    if (window.confirm('Are you sure you want to remove all saved manga?')) {
      localStorage.removeItem('savedManga');
      setSavedManga([]);
    }
  };

  const handleRemoveFiltered = () => {
    if (window.confirm(`Are you sure you want to remove all ${filterSource === 'all' ? 'saved manga' : `${filterSource} manga`}?`)) {
      const updatedList = savedManga.filter(manga => 
        filterSource === 'all' ? false : manga.source !== filterSource
      );
      localStorage.setItem('savedManga', JSON.stringify(updatedList));
      setSavedManga(updatedList);
    }
  };

  const getSourceCounts = () => {
    const counts = {};
    savedManga.forEach(manga => {
      counts[manga.source] = (counts[manga.source] || 0) + 1;
    });
    return counts;
  };

  const sourceCounts = getSourceCounts();

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Saved Manga</h1>
            <p className="text-gray-300">
              {savedManga.length} manga saved • {Object.keys(sourceCounts).length} sources
            </p>
          </div>
          
          {savedManga.length > 0 && (
            <div className="flex space-x-2">
              <button
                onClick={handleRemoveFiltered}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Remove {filterSource === 'all' ? 'All' : filterSource}
              </button>
            </div>
          )}
        </div>

        {savedManga.length === 0 ? (
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-400 mb-2">No saved manga yet</h3>
            <p className="text-gray-500 mb-4">Start searching for manga and save your favorites!</p>
            <Link 
              to="/" 
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Search Manga
            </Link>
          </div>
        ) : (
          <>
            {/* Filters and Sorting */}
            <div className="flex flex-wrap items-center gap-4 mb-6 p-4 bg-gray-800 rounded-lg">
              {/* Source Filter */}
              <div className="flex items-center space-x-2">
                <label className="text-gray-300 text-sm">Source:</label>
                <select
                  value={filterSource}
                  onChange={(e) => setFilterSource(e.target.value)}
                  className="px-3 py-1 bg-gray-700 text-white rounded border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Sources ({savedManga.length})</option>
                  {Object.entries(sourceCounts).map(([source, count]) => (
                    <option key={source} value={source}>
                      {source.charAt(0).toUpperCase() + source.slice(1)} ({count})
                    </option>
                  ))}
                </select>
              </div>

              {/* Sort By */}
              <div className="flex items-center space-x-2">
                <label className="text-gray-300 text-sm">Sort by:</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="px-3 py-1 bg-gray-700 text-white rounded border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="savedAt">Date Saved</option>
                  <option value="lastRead">Last Read</option>
                  <option value="title">Title</option>
                  <option value="source">Source</option>
                </select>
              </div>

              {/* Sort Order */}
              <div className="flex items-center space-x-2">
                <label className="text-gray-300 text-sm">Order:</label>
                <button
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="px-3 py-1 bg-gray-700 text-white rounded border border-gray-600 hover:bg-gray-600 transition-colors"
                >
                  {sortOrder === 'asc' ? '↑ Ascending' : '↓ Descending'}
                </button>
              </div>
            </div>

            {/* Source Statistics */}
            <div className="flex flex-wrap gap-2 mb-6">
              {Object.entries(sourceCounts).map(([source, count]) => (
                <span
                  key={source}
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    filterSource === source
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600 cursor-pointer'
                  }`}
                  onClick={() => setFilterSource(filterSource === source ? 'all' : source)}
                >
                  {source.charAt(0).toUpperCase() + source.slice(1)}: {count}
                </span>
              ))}
            </div>

            {/* Manga Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {sortedAndFilteredManga.map((manga) => (
                <MangaCard key={`${manga.source}-${manga.id}`} manga={manga} />
              ))}
            </div>

            {sortedAndFilteredManga.length === 0 && filterSource !== 'all' && (
              <div className="text-center py-12">
                <p className="text-gray-400">No saved manga from {filterSource}</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default SavedManga; 