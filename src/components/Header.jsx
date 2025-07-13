import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './Auth/AuthContext.jsx';
import { FaBell, FaCog, FaUser, FaSignOutAlt, FaBookmark, FaHistory, FaSearch, FaHome, FaList, FaBook } from 'react-icons/fa';

const Header = () => {
  const { user, isAuthenticated, logout, authFetch } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const dropdownRef = useRef(null);
  const mobileMenuRef = useRef(null);
  const notificationsRef = useRef(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
      if (mobileMenuRef.current && !mobileMenuRef.current.contains(event.target)) {
        setIsMobileMenuOpen(false);
      }
      if (notificationsRef.current && !notificationsRef.current.contains(event.target)) {
        setIsNotificationsOpen(false);
      }
    };

    if (isDropdownOpen || isMobileMenuOpen || isNotificationsOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen, isMobileMenuOpen, isNotificationsOpen]);

  // Fetch notifications
  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications();
    }
  }, [isAuthenticated]);

  const fetchNotifications = async () => {
    try {
      const response = await authFetch('/api/notifications');
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const handleLogout = async () => {
    await logout();
    setIsDropdownOpen(false);
    setIsMobileMenuOpen(false);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const markNotificationAsRead = async (notificationId) => {
    try {
      await authFetch(`/api/notifications/${notificationId}/read`, {
        method: 'PUT'
      });
      fetchNotifications(); // Refresh notifications
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const navigationItems = [
    { to: "/", label: "Dashboard", icon: FaHome },
    { to: "/search", label: "Search", icon: FaSearch },
    { to: "/reading-lists", label: "Reading Lists", icon: FaBook },
    { to: "/saved", label: "Saved", icon: FaBookmark },
    { to: "/sources", label: "Sources", icon: FaList },
    { to: "/read-history", label: "History", icon: FaHistory },
  ];

  return (
    <header className="bg-gray-800 shadow-sm border-b border-gray-700">
      <div className="max-w-6xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold text-blue-500 hover:text-blue-400 transition-colors">
            Dude Manga
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link 
                  key={item.to}
                  to={item.to} 
                  className="flex items-center space-x-2 text-gray-300 hover:text-white font-medium transition-colors"
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Desktop Authentication Section */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                {/* Notifications */}
                <div className="relative" ref={notificationsRef}>
                  <button
                    onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                    className="relative p-2 text-gray-300 hover:text-white transition-colors"
                  >
                    <FaBell className="w-5 h-5" />
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                        {unreadCount > 99 ? '99+' : unreadCount}
                      </span>
                    )}
                  </button>

                  {/* Notifications Dropdown */}
                  {isNotificationsOpen && (
                    <div className="absolute right-0 mt-2 w-80 bg-gray-800 rounded-md shadow-lg border border-gray-700 z-50 max-h-96 overflow-y-auto">
                      <div className="py-2">
                        <div className="px-4 py-2 text-sm text-gray-400 border-b border-gray-700">
                          Notifications
                        </div>
                        {notifications.length === 0 ? (
                          <div className="px-4 py-8 text-center text-gray-400">
                            No notifications
                          </div>
                        ) : (
                          notifications.map((notification) => (
                            <div
                              key={notification.id}
                              className={`px-4 py-3 hover:bg-gray-700 transition-colors cursor-pointer ${
                                !notification.read ? 'bg-gray-700/50' : ''
                              }`}
                              onClick={() => markNotificationAsRead(notification.id)}
                            >
                              <div className="text-sm font-medium text-white">
                                {notification.title}
                              </div>
                              <div className="text-xs text-gray-400 mt-1">
                                {notification.message}
                              </div>
                              <div className="text-xs text-gray-500 mt-2">
                                {new Date(notification.created_at).toLocaleDateString()}
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* User Dropdown */}
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
                          className="flex items-center px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                        >
                          <FaUser className="w-4 h-4 mr-2" />
                          Profile
                        </Link>
                        <Link
                          to="/settings"
                          onClick={() => setIsDropdownOpen(false)}
                          className="flex items-center px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                        >
                          <FaCog className="w-4 h-4 mr-2" />
                          Settings
                        </Link>
                        {user?.hasAdmin && (
                          <Link
                            to="/cache"
                            onClick={() => setIsDropdownOpen(false)}
                            className="flex items-center px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                          >
                            <FaCog className="w-4 h-4 mr-2" />
                            Cache
                          </Link>
                        )}
                        <button
                          onClick={handleLogout}
                          className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                        >
                          <FaSignOutAlt className="w-4 h-4 mr-2" />
                          Sign out
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </>
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
              <>
                {/* Mobile Notifications */}
                <div className="relative">
                  <button
                    onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                    className="relative p-2 text-gray-300 hover:text-white transition-colors"
                  >
                    <FaBell className="w-5 h-5" />
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                        {unreadCount > 99 ? '99+' : unreadCount}
                      </span>
                    )}
                  </button>
                </div>
                
                <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-white">
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
              </>
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
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link 
                key={item.to}
                to={item.to} 
                onClick={closeMobileMenu}
                className="flex items-center space-x-3 text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
          
          {isAuthenticated && (
            <>
              <div className="border-t border-gray-700 pt-2 mt-2">
                <div className="px-3 py-2 text-sm text-gray-400">
                  Signed in as <span className="text-white">{user?.username}</span>
                </div>
                <Link 
                  to="/profile" 
                  onClick={closeMobileMenu}
                  className="flex items-center space-x-3 text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
                >
                  <FaUser className="w-5 h-5" />
                  <span>Profile</span>
                </Link>
                <Link 
                  to="/settings" 
                  onClick={closeMobileMenu}
                  className="flex items-center space-x-3 text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
                >
                  <FaCog className="w-5 h-5" />
                  <span>Settings</span>
                </Link>
                {user?.hasAdmin && (
                  <Link 
                    to="/cache" 
                    onClick={closeMobileMenu}
                    className="flex items-center space-x-3 text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
                  >
                    <FaCog className="w-5 h-5" />
                    <span>Cache</span>
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-3 w-full text-left text-gray-300 hover:text-white py-3 px-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
                >
                  <FaSignOutAlt className="w-5 h-5" />
                  <span>Sign out</span>
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