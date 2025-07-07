import React, { useState, useEffect } from 'react';
import { useAuth } from './Auth/AuthContext.jsx';

const CacheManager = () => {
  const { authFetch, user } = useAuth();
  const [cacheStats, setCacheStats] = useState(null);
  const [allUsersStats, setAllUsersStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);

  const fetchCacheStats = async () => {
    try {
      const response = await authFetch('http://localhost:5000/cache/stats');
      if (!response.ok) {
        const errorText = await response.text();
        setMessage(`Error: ${response.status} - ${errorText}`);
        console.error('Cache stats error:', response.status, errorText);
        setCacheStats(null);
        return;
      }
      const data = await response.json();
      setCacheStats(data);
    } catch (error) {
      console.error('Failed to fetch cache stats:', error);
      setMessage('Failed to fetch cache statistics');
      setCacheStats(null);
    }
  };

  const fetchAllUsersStats = async () => {
    try {
      const response = await authFetch('http://localhost:5000/admin/cache/stats');
      if (response.ok) {
        const data = await response.json();
        setAllUsersStats(data);
        setIsAdmin(true);
      }
    } catch (error) {
      console.error('Failed to fetch all users stats:', error);
      // Not an admin, that's fine
    }
  };

  const clearCache = async (type = 'all', source = null, query = null, mangaId = null) => {
    setLoading(true);
    try {
      const response = await authFetch('http://localhost:5000/cache/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type,
          source,
          query,
          manga_id: mangaId
        }),
      });
      const data = await response.json();
      setMessage(data.message || 'Cache cleared successfully');
      fetchCacheStats(); // Refresh stats
    } catch (error) {
      console.error('Failed to clear cache:', error);
      setMessage('Failed to clear cache');
    } finally {
      setLoading(false);
    }
  };

  const clearAllUsersCache = async (type = 'all', source = null, query = null, mangaId = null) => {
    setLoading(true);
    try {
      const response = await authFetch('http://localhost:5000/admin/cache/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type,
          source,
          query,
          manga_id: mangaId
        }),
      });
      const data = await response.json();
      setMessage(data.message || 'All users cache cleared successfully');
      fetchCacheStats(); // Refresh user stats
      fetchAllUsersStats(); // Refresh all users stats
    } catch (error) {
      console.error('Failed to clear all users cache:', error);
      setMessage('Failed to clear all users cache');
    } finally {
      setLoading(false);
    }
  };

  const cleanupCache = async () => {
    setLoading(true);
    try {
      const response = await authFetch('http://localhost:5000/cache/cleanup', {
        method: 'POST',
      });
      const data = await response.json();
      setMessage(data.message || 'Cache cleaned up successfully');
      fetchCacheStats(); // Refresh stats
    } catch (error) {
      console.error('Failed to cleanup cache:', error);
      setMessage('Failed to cleanup cache');
    } finally {
      setLoading(false);
    }
  };

  const cleanupAllUsersCache = async () => {
    setLoading(true);
    try {
      const response = await authFetch('http://localhost:5000/admin/cache/cleanup', {
        method: 'POST',
      });
      const data = await response.json();
      setMessage(data.message || 'All users cache cleaned up successfully');
      fetchCacheStats(); // Refresh user stats
      fetchAllUsersStats(); // Refresh all users stats
    } catch (error) {
      console.error('Failed to cleanup all users cache:', error);
      setMessage('Failed to cleanup all users cache');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCacheStats();
    fetchAllUsersStats();
  }, []);

  if (!cacheStats) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">Cache Manager</h1>
          <div className="animate-pulse">
            <div className="bg-gray-800 rounded-lg p-6 mb-4">
              <div className="h-4 bg-gray-700 rounded w-1/4 mb-4"></div>
              <div className="h-4 bg-gray-700 rounded w-1/2"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold">Cache Manager</h1>
            {user && (
              <p className="text-gray-400 mt-1">
                Managing cache for user: <span className="text-blue-400">{user.username}</span>
              </p>
            )}
          </div>
          <button
            onClick={() => {
              fetchCacheStats();
              if (isAdmin) fetchAllUsersStats();
            }}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors"
          >
            Refresh Stats
          </button>
        </div>

        {message && (
          <div className="bg-green-600 text-white p-4 rounded-lg mb-6">
            {message}
          </div>
        )}

        {/* User Cache Statistics */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Your Cache Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2">Search Cache</h3>
              <div className="space-y-2">
                <p>Total: {cacheStats.search_cache.total}</p>
                <p>Active: {cacheStats.search_cache.active}</p>
                <p>Expired: {cacheStats.search_cache.expired}</p>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2">Manga Cache</h3>
              <div className="space-y-2">
                <p>Total: {cacheStats.manga_cache.total}</p>
                {Object.entries(cacheStats.manga_cache.sources).map(([source, count]) => (
                  <p key={source} className="text-sm text-gray-300">
                    {source}: {count}
                  </p>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2">Chapter Cache</h3>
              <div className="space-y-2">
                <p>Total: {cacheStats.chapter_cache.total}</p>
              </div>
            </div>
          </div>
        </div>

        {/* All Users Cache Statistics (Admin Only) */}
        {isAdmin && allUsersStats && (
          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">All Users Cache Statistics (Admin)</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-red-900 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-2">Search Cache (All Users)</h3>
                <div className="space-y-2">
                  <p>Total: {allUsersStats.search_cache.total}</p>
                  <p>Active: {allUsersStats.search_cache.active}</p>
                  <p>Expired: {allUsersStats.search_cache.expired}</p>
                </div>
              </div>

              <div className="bg-red-900 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-2">Manga Cache (All Users)</h3>
                <div className="space-y-2">
                  <p>Total: {allUsersStats.manga_cache.total}</p>
                  {Object.entries(allUsersStats.manga_cache.sources).map(([source, count]) => (
                    <p key={source} className="text-sm text-gray-300">
                      {source}: {count}
                    </p>
                  ))}
                </div>
              </div>

              <div className="bg-red-900 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-2">Chapter Cache (All Users)</h3>
                <div className="space-y-2">
                  <p>Total: {allUsersStats.chapter_cache.total}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* User Cache Actions */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Your Cache Actions</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              onClick={() => clearCache('all')}
              disabled={loading}
              className="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
            >
              {loading ? 'Clearing...' : 'Clear All Cache'}
            </button>

            <button
              onClick={() => clearCache('search')}
              disabled={loading}
              className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
            >
              {loading ? 'Clearing...' : 'Clear Search Cache'}
            </button>

            <button
              onClick={() => clearCache('manga')}
              disabled={loading}
              className="bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
            >
              {loading ? 'Clearing...' : 'Clear Manga Cache'}
            </button>

            <button
              onClick={cleanupCache}
              disabled={loading}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
            >
              {loading ? 'Cleaning...' : 'Cleanup Expired'}
            </button>
          </div>
        </div>

        {/* Admin Cache Actions */}
        {isAdmin && (
          <div className="bg-red-900 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Admin Cache Actions (All Users)</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <button
                onClick={() => clearAllUsersCache('all')}
                disabled={loading}
                className="bg-red-800 hover:bg-red-900 disabled:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
              >
                {loading ? 'Clearing...' : 'Clear All Users Cache'}
              </button>

              <button
                onClick={() => clearAllUsersCache('search')}
                disabled={loading}
                className="bg-orange-800 hover:bg-orange-900 disabled:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
              >
                {loading ? 'Clearing...' : 'Clear All Search Cache'}
              </button>

              <button
                onClick={() => clearAllUsersCache('manga')}
                disabled={loading}
                className="bg-yellow-800 hover:bg-yellow-900 disabled:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
              >
                {loading ? 'Clearing...' : 'Clear All Manga Cache'}
              </button>

              <button
                onClick={cleanupAllUsersCache}
                disabled={loading}
                className="bg-green-800 hover:bg-green-900 disabled:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
              >
                {loading ? 'Cleaning...' : 'Cleanup All Expired'}
              </button>
            </div>
          </div>
        )}

        {/* Source-specific cache clearing */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Source-specific Actions</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h3 className="font-semibold">WeebCentral</h3>
              <div className="flex gap-2">
                <button
                  onClick={() => clearCache('search', 'weebcentral')}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-3 py-1 rounded text-sm transition-colors"
                >
                  Clear Search
                </button>
                <button
                  onClick={() => clearCache('manga', 'weebcentral')}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-3 py-1 rounded text-sm transition-colors"
                >
                  Clear Manga
                </button>
                {isAdmin && (
                  <button
                    onClick={() => clearAllUsersCache('search', 'weebcentral')}
                    disabled={loading}
                    className="bg-red-700 hover:bg-red-800 disabled:bg-gray-600 px-3 py-1 rounded text-sm transition-colors"
                  >
                    Clear All
                  </button>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold">AsuraScans</h3>
              <div className="flex gap-2">
                <button
                  onClick={() => clearCache('search', 'asurascans')}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-3 py-1 rounded text-sm transition-colors"
                >
                  Clear Search
                </button>
                <button
                  onClick={() => clearCache('manga', 'asurascans')}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-3 py-1 rounded text-sm transition-colors"
                >
                  Clear Manga
                </button>
                {isAdmin && (
                  <button
                    onClick={() => clearAllUsersCache('search', 'asurascans')}
                    disabled={loading}
                    className="bg-red-700 hover:bg-red-800 disabled:bg-gray-600 px-3 py-1 rounded text-sm transition-colors"
                  >
                    Clear All
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CacheManager; 