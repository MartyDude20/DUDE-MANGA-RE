import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './Auth/AuthContext.jsx';
import MangaCard from './MangaCard.jsx';

const DEFAULT_SOURCES = [
  { id: 'weebcentral', name: 'WeebCentral', enabled: true },
  { id: 'asurascans', name: 'Asura Scans', enabled: true },
  { id: 'mangadex', name: 'MangaDex', enabled: true },
];

const SearchPage = () => {
  const { authFetch } = useAuth();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sources, setSources] = useState(DEFAULT_SOURCES);
  const [forceRefresh, setForceRefresh] = useState(false);
  const [cacheInfo, setCacheInfo] = useState(null);
  const [openAccordions, setOpenAccordions] = useState({});

  // Load and merge saved sources from localStorage on component mount
  useEffect(() => {
    const savedSources = localStorage.getItem('mangaSources');
    if (savedSources) {
      const saved = JSON.parse(savedSources);
      // Merge: add any new sources from DEFAULT_SOURCES
      const merged = DEFAULT_SOURCES.map(def => {
        const found = saved.find(s => s.id === def.id);
        return found ? { ...def, ...found } : def;
      });
      setSources(merged);
      // Optionally, update localStorage with merged sources
      localStorage.setItem('mangaSources', JSON.stringify(merged));
    } else {
      setSources(DEFAULT_SOURCES);
      localStorage.setItem('mangaSources', JSON.stringify(DEFAULT_SOURCES));
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
      if (forceRefresh) {
        params.refresh = 'true';
      }
      const queryString = new URLSearchParams(params).toString();
      const response = await authFetch(`/api/search?${queryString}`);
      const data = await response.json();
      setResults(data.results || []);
      setCacheInfo(data.cached);
    } catch (err) {
      setError('Failed to search manga');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const enabledCount = sources.filter(source => source.enabled).length;

  const groupedResults = results.reduce((acc, manga) => {
    acc[manga.source] = acc[manga.source] || [];
    acc[manga.source].push(manga);
    return acc;
  }, {});

  const handleAccordionToggle = (sourceId) => {
    setOpenAccordions((prev) => ({ ...prev, [sourceId]: !prev[sourceId] }));
  };

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
          <div className="flex flex-col sm:flex-row gap-4">
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
          
          {/* Cache Options */}
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={forceRefresh}
                onChange={(e) => setForceRefresh(e.target.checked)}
                className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
              />
              <span className="text-gray-300 text-sm">Force refresh (bypass cache)</span>
            </label>
          </div>
        </form>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900 border border-red-600 text-red-200 rounded-lg">
          {error}
        </div>
      )}

      {cacheInfo !== null && (
        <div className={`mb-6 p-4 rounded-lg border ${
          cacheInfo 
            ? 'bg-green-900 border-green-600 text-green-200' 
            : 'bg-blue-900 border-blue-600 text-blue-200'
        }`}>
          <div className="flex items-center space-x-2">
            {cacheInfo ? (
              <>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
                <span>Results loaded from cache</span>
                {results.some(r => r.cached === true) && results.some(r => r.cached === false) && (
                  <span className="text-sm ml-2">(mixed: some from preloader, some fresh)</span>
                )}
              </>
            ) : (
              <>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
              </svg>
                <span>Fresh results loaded</span>
              </>
            )}
          </div>
          {results.length > 0 && results[0].last_updated && (
            <div className="text-xs mt-1 opacity-75">
              Data last updated: {new Date(results[0].last_updated).toLocaleString()}
            </div>
          )}
        </div>
      )}

      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-400 mt-4">Searching for manga...</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="space-y-4">
          {Object.keys(groupedResults).map((sourceId) => {
            const source = sources.find(s => s.id === sourceId) || { name: sourceId };
            const isOpen = openAccordions[sourceId] ?? true;
            return (
              <div key={sourceId} className="border border-gray-700 rounded-lg bg-gray-800">
                <button
                  className="w-full flex justify-between items-center px-6 py-4 text-left focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onClick={() => handleAccordionToggle(sourceId)}
                >
                  <span className="text-lg font-semibold text-white">{source.name}</span>
                  <svg
                    className={`w-5 h-5 transform transition-transform ${isOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {isOpen && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 px-6 pb-6">
                    {groupedResults[sourceId].map((manga) => (
                      <MangaCard key={manga.id + manga.source} manga={manga} />
                    ))}
                  </div>
                )}
              </div>
            );
          })}
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