import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './Auth/AuthContext.jsx';

const Header = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const dropdownRef = useRef(null);
  const mobileMenuRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
      if (mobileMenuRef.current && !mobileMenuRef.current.contains(event.target)) {
        setIsMobileMenuOpen(false);
      }
    };

    if (isDropdownOpen || isMobileMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen, isMobileMenuOpen]);

  const handleLogout = async () => {
    await logout();
    setIsDropdownOpen(false);
    setIsMobileMenuOpen(false);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <header className="bg-gray-800 shadow-sm border-b border-gray-700">
      <div className="max-w-6xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold text-blue-500 hover:text-blue-400 transition-colors">
            Dude Manga
          </Link>
          
          {/* Desktop Navigation */}
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
          </nav>

          {/* Desktop Authentication Section */}
          <div className="hidden md:flex items-center space-x-4">
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
                  <span className="hidden sm:block">{user?.username}</span>
                  <svg
                    className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Desktop Dropdown Menu */}
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
                      {user?.hasAdmin && (
                        <Link
                          to="/cache"
                          onClick={() => setIsDropdownOpen(false)}
                          className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                        >
                          Cache
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

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {user?.username?.charAt(0).toUpperCase()}
                </span>
              </div>
            ) : (
              <Link
                to="/auth"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded-md text-sm font-medium transition-colors"
              >
                Sign in
              </Link>
            )}
            
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-gray-300 hover:text-white transition-colors"
              aria-label="Toggle mobile menu"
            >
              <svg
                className={`w-6 h-6 transition-transform ${isMobileMenuOpen ? 'rotate-90' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {isMobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      {/* Mobile Dropdown Menu */}
      <div 
        ref={mobileMenuRef}
        className={`md:hidden bg-gray-800 border-t border-gray-700 transition-all duration-300 ease-in-out overflow-hidden ${
          isMobileMenuOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="px-6 py-4 space-y-2">
          <Link 
            to="/" 
            onClick={closeMobileMenu}
            className="block text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
          >
            Search
          </Link>
          <Link 
            to="/saved" 
            onClick={closeMobileMenu}
            className="block text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
          >
            Saved
          </Link>
          <Link 
            to="/sources" 
            onClick={closeMobileMenu}
            className="block text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
          >
            Sources
          </Link>
          {isAuthenticated && (
            <>
              <Link 
                to="/read-history" 
                onClick={closeMobileMenu}
                className="block text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
              >
                History
              </Link>
              <div className="border-t border-gray-700 pt-2 mt-2">
                <div className="px-3 py-2 text-sm text-gray-400">
                  Signed in as <span className="text-white">{user?.username}</span>
                </div>
                <Link 
                  to="/profile" 
                  onClick={closeMobileMenu}
                  className="block text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
                >
                  Profile
                </Link>
                {user?.hasAdmin && (
                  <Link 
                    to="/cache" 
                    onClick={closeMobileMenu}
                    className="block text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
                  >
                    Cache
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="block w-full text-left text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
                >
                  Sign out
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header; 