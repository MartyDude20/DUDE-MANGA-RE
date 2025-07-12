import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './Auth/AuthContext.jsx';

const Header = () => {
  const { user, isAuthenticated, logout, authFetch } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const dropdownRef = useRef(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }

    };

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen]);

  const handleLogout = async () => {
    await logout();
    setIsDropdownOpen(false);
  };

  const handleQuickPreloadAction = async (action) => {
    if (!user?.hasAdmin) return;
    
    try {
      let endpoint = '';
      
      switch (action) {
        case 'start':
          endpoint = 'http://localhost:5000/preload/start-worker';
          break;
        case 'stop':
          endpoint = 'http://localhost:5000/preload/stop-worker';
          break;
        case 'create-daily':
          endpoint = 'http://localhost:5000/preload/create-daily';
          break;
        case 'update-robots':
          endpoint = 'http://localhost:5000/preload/update-robots';
          break;
        default:
          return;
      }
      
      const response = await authFetch(endpoint, { method: 'POST' });
      if (response.ok) {
        const result = await response.json();
        alert(result.message);
      } else {
        const errorData = await response.json();
        alert(errorData.error || `Failed to ${action}`);
      }
    } catch (error) {
      console.error(`Failed to ${action}:`, error);
      alert(`Failed to ${action}`);
    }
  };

  return (
    <header className="bg-gray-800 shadow-sm border-b border-gray-700">
      <div className="max-w-6xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold text-blue-500 hover:text-blue-400 transition-colors">
            Dude Manga
          </Link>
          
          <nav className="hidden md:flex space-x-8">
            <Link to="/" className="text-gray-300 hover:text-white font-medium transition-colors">
              Search
            </Link>
            <Link to="/saved" className="text-gray-300 hover:text-white font-medium transition-colors">
              Saved
            </Link>
            <Link to="/sources" className="text-gray-300 hover:text-white font-medium transition-colors">
              Sources
            </Link>
            {isAuthenticated && (
              <Link to="/read-history" className="text-gray-300 hover:text-white font-medium transition-colors">
                History
              </Link>
            )}
            {isAuthenticated && user?.hasAdmin && (
              <Link to="/preload" className="text-gray-300 hover:text-white font-medium transition-colors">
                Preload
              </Link>
            )}
            {/* Debug: Show user info for admin users */}
            {isAuthenticated && user && (
              <div className="text-xs text-gray-500">
                Debug: {user.username} - hasAdmin: {user.hasAdmin ? 'true' : 'false'}
              </div>
            )}
          </nav>

          {/* Authentication Section */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors"
                >
                  <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-white">
                      {user?.username?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <span className="hidden sm:block">
                    {user?.username}
                    {user?.hasAdmin && (
                      <span className="ml-2 px-2 py-1 text-xs bg-purple-600 text-white rounded-full">
                        Admin
                      </span>
                    )}
                  </span>
                  <svg
                    className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Dropdown Menu */}
                {isDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-gray-800 rounded-md shadow-lg border border-gray-700 z-50">
                    <div className="py-1">
                      <div className="px-4 py-2 text-sm text-gray-400 border-b border-gray-700">
                        Signed in as <span className="text-white">{user?.username}</span>
                      </div>
                      <Link
                        to="/profile"
                        onClick={() => setIsDropdownOpen(false)}
                        className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                      >
                        Profile
                      </Link>
                      <Link
                        to="/cache"
                        onClick={() => setIsDropdownOpen(false)}
                        className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                      >
                        Cache
                      </Link>
                      {user?.hasAdmin && (
                        <Link
                          to="/preload"
                          onClick={() => setIsDropdownOpen(false)}
                          className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                        >
                          Preload Manager
                        </Link>
                      )}
                      <button
                        onClick={handleLogout}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                      >
                        Sign out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <Link
                to="/auth"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign in
              </Link>
            )}
          </div>
        </div>
      </div>
      
      {/* Mobile Menu */}
      <div className="md:hidden">
        <div className="px-6 py-2 space-y-1">
          <Link to="/" className="block text-gray-300 hover:text-white py-2 transition-colors">
            Search
          </Link>
          <Link to="/saved" className="block text-gray-300 hover:text-white py-2 transition-colors">
            Saved
          </Link>
          <Link to="/sources" className="block text-gray-300 hover:text-white py-2 transition-colors">
            Sources
          </Link>
          {isAuthenticated && (
            <>
              <Link to="/read-history" className="block text-gray-300 hover:text-white py-2 transition-colors">
                History
              </Link>
              <Link to="/profile" className="block text-gray-300 hover:text-white py-2 transition-colors">
                Profile
              </Link>
              <Link to="/cache" className="block text-gray-300 hover:text-white py-2 transition-colors">
                Cache
              </Link>
              {user?.hasAdmin && (
                <Link to="/preload" className="block text-gray-300 hover:text-white py-2 transition-colors">
                  Preload
                </Link>
              )}
              <button
                onClick={handleLogout}
                className="block w-full text-left text-gray-300 hover:text-white py-2 transition-colors"
              >
                Sign out
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header; 