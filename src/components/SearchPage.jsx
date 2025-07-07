import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import MangaCard from './MangaCard.jsx';

const DEFAULT_SOURCES = [
  { id: 'weebcentral', name: 'WeebCentral', enabled: true },
  { id: 'asurascans', name: 'Asura Scans', enabled: true },
];

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sources, setSources] = useState(DEFAULT_SOURCES);

  // Load saved sources from localStorage on component mount
  useEffect(() => {
    const savedSources = localStorage.getItem('mangaSources');
    if (savedSources) {
      setSources(JSON.parse(savedSources));
    }
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    const enabledSources = sources.filter(source => source.enabled);
    if (enabledSources.length === 0) {
      setError('No manga sources are enabled. Please enable at least one source in the Sources page.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const params = { q: query };
      if (enabledSources.length > 0 && enabledSources.length < sources.length) {
        params.sources = enabledSources.map(s => s.id).join(',');
      }
      const response = await axios.get('/api/search', { params });
      setResults(response.data.results || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to search manga');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const enabledCount = sources.filter(source => source.enabled).length;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-6">Search Manga</h1>
        
        {enabledCount === 0 && (
          <div className="mb-6 p-4 bg-yellow-900 border border-yellow-600 rounded-lg">
            <div className="flex items-center space-x-3">
              <svg className="w-6 h-6 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <h3 className="text-lg font-medium text-yellow-200">No Sources Enabled</h3>
                <p className="text-yellow-100 mt-1">
                  You need to enable at least one manga source to search. 
                  <Link to="/sources" className="text-blue-400 hover:text-blue-300 underline ml-1">
                    Go to Sources
                  </Link>
                </p>
              </div>
            </div>
          </div>
        )}
        
        <form onSubmit={handleSearch} className="space-y-4">
          {/* Source Selection */}
          <div className="flex flex-wrap gap-4 mb-4">
            {sources.map((source) => (
              <div key={source.id} className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${source.enabled ? 'bg-green-500' : 'bg-gray-500'}`}></div>
                <span className={`text-sm ${source.enabled ? 'text-gray-300' : 'text-gray-500'}`}>
                  {source.name}
                </span>
              </div>
            ))}
            <Link 
              to="/sources" 
              className="text-sm text-blue-400 hover:text-blue-300 underline"
            >
              Manage Sources
            </Link>
          </div>
          
          {/* Search Form */}
          <div className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for manga..."
              className="flex-1 px-4 py-3 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-800 text-white placeholder-gray-400"
              disabled={loading || enabledCount === 0}
            />
            <button 
              type="submit" 
              className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading || enabledCount === 0}
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900 border border-red-600 text-red-200 rounded-lg">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-400 mt-4">Searching for manga...</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {results.map((manga) => (
            <MangaCard key={manga.id + manga.source} manga={manga} />
          ))}
        </div>
      )}

      {!loading && !error && results.length === 0 && query && (
        <div className="text-center py-12 text-gray-400">
          No manga found for "{query}"
        </div>
      )}
    </div>
  );
};

export default SearchPage; 