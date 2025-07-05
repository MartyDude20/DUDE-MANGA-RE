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
    <div>
      <div className="search-container">
        <form onSubmit={handleSearch} className="search-form" style={{ flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.5rem' }}>
            {SOURCE_OPTIONS.map((source) => (
              <label key={source.value} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={selectedSources.includes(source.value)}
                  onChange={() => handleSourceChange(source.value)}
                />
                {source.label}
              </label>
            ))}
          </div>
          <div style={{ display: 'flex', gap: '1rem', width: '100%' }}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for manga..."
              className="search-input"
              disabled={loading}
            />
            <button type="submit" className="search-button" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>
      </div>

      {error && <div className="error">{error}</div>}

      {loading && <div className="loading">Searching for manga...</div>}

      {!loading && results.length > 0 && (
        <div className="manga-grid">
          {results.map((manga) => (
            <MangaCard key={manga.id + manga.source} manga={manga} />
          ))}
        </div>
      )}

      {!loading && !error && results.length === 0 && query && (
        <div className="loading">No manga found for "{query}"</div>
      )}
    </div>
  );
};

export default SearchPage; 