import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import MangaCard from './MangaCard.jsx';

const SOURCE_OPTIONS = [
  { label: 'WeebCentral', value: 'weebcentral' },
  { label: 'Asura Scans', value: 'asurascans' },
];

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedSources, setSelectedSources] = useState(SOURCE_OPTIONS.map(s => s.value));

  const handleSourceChange = (source) => {
    setSelectedSources((prev) =>
      prev.includes(source)
        ? prev.filter((s) => s !== source)
        : [...prev, source]
    );
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    try {
      const params = { q: query };
      if (selectedSources.length > 0 && selectedSources.length < SOURCE_OPTIONS.length) {
        params.sources = selectedSources.join(',');
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

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-6">Search Manga</h1>
        
        <form onSubmit={handleSearch} className="space-y-4">
          {/* Source Selection */}
          <div className="flex flex-wrap gap-4 mb-4">
            {SOURCE_OPTIONS.map((source) => (
              <label key={source.value} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedSources.includes(source.value)}
                  onChange={() => handleSourceChange(source.value)}
                  className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                />
                <span className="text-gray-300">{source.label}</span>
              </label>
            ))}
          </div>
          
          {/* Search Form */}
          <div className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for manga..."
              className="flex-1 px-4 py-3 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-800 text-white placeholder-gray-400"
              disabled={loading}
            />
            <button 
              type="submit" 
              className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
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