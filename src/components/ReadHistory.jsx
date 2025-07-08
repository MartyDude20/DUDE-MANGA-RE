import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './Auth/AuthContext.jsx';

const ReadHistory = () => {
  const { authFetch } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterSource, setFilterSource] = useState('all');

  useEffect(() => {
    fetchReadHistory();
  }, []);

  const fetchReadHistory = async () => {
    try {
      const response = await authFetch('http://localhost:5000/read-history');
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      } else {
        setError('Failed to load read history');
      }
    } catch (err) {
      setError('Failed to load read history');
    } finally {
      setLoading(false);
    }
  };

  // Filter and search history
  const filteredHistory = history.filter(item => {
    const matchesSearch = item.manga_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.chapter_title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSource = filterSource === 'all' || item.source === filterSource;
    return matchesSearch && matchesSource;
  });

  // Get unique sources for filter dropdown
  const sources = ['all', ...new Set(history.map(item => item.source))];

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-400 mt-4">Loading read history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <Link to="/" className="text-blue-400 hover:text-blue-300">
          ← Back to Home
        </Link>
        <h1 className="text-3xl font-bold text-white mt-4">Read History</h1>
        <p className="text-gray-400 mt-2">
          Track of all the manga chapters you've read
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900 border border-red-600 text-red-200 rounded-lg">
          {error}
        </div>
      )}

      {/* Search and Filter Controls */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search manga or chapter titles..."
            className="w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="sm:w-48">
          <select
            value={filterSource}
            onChange={(e) => setFilterSource(e.target.value)}
            className="w-full px-4 py-2 border border-gray-600 rounded-lg bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {sources.map(source => (
              <option key={source} value={source}>
                {source === 'all' ? 'All Sources' : source.charAt(0).toUpperCase() + source.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-white">{history.length}</div>
          <div className="text-gray-400">Total Chapters Read</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-white">
            {new Set(history.map(item => item.manga_title)).size}
          </div>
          <div className="text-gray-400">Unique Manga</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="text-2xl font-bold text-white">
            {new Set(history.map(item => item.source)).size}
          </div>
          <div className="text-gray-400">Sources Used</div>
        </div>
      </div>

      {/* History List */}
      {filteredHistory.length === 0 ? (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <h3 className="text-lg font-medium text-gray-400 mb-2">
            {searchQuery || filterSource !== 'all' ? 'No matching history found' : 'No read history yet'}
          </h3>
          <p className="text-gray-500">
            {searchQuery || filterSource !== 'all' 
              ? 'Try adjusting your search or filter criteria'
              : 'Start reading manga to build your history!'
            }
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredHistory.map((item, index) => (
            <div
              key={`${item.manga_title}-${item.chapter_title}-${item.read_at}`}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors"
            >
              <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-xl font-semibold text-white">
                      {item.manga_title}
                    </h3>
                    <span className="px-2 py-1 bg-blue-900 text-blue-200 text-xs rounded-full">
                      {item.source}
                    </span>
                  </div>
                  <p className="text-gray-300 mb-2">{item.chapter_title}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-400">
                    <span className="flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {formatDate(item.read_at)}
                    </span>
                  </div>
                </div>
                <div className="mt-4 md:mt-0 md:ml-4">
                  <Link
                    to={`/manga/${item.source}/${item.manga_id}`}
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    View Manga
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      {filteredHistory.length > 0 && (
        <div className="mt-8 text-center text-gray-400">
          Showing {filteredHistory.length} of {history.length} entries
        </div>
      )}
    </div>
  );
};

export default ReadHistory; 