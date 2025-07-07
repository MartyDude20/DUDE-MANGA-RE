import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
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
            <Link to="/sources" className="text-gray-300 hover:text-white font-medium transition-colors">
              Sources
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header; 