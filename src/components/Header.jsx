import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          Dude Manga
        </Link>
      </div>
    </header>
  );
};

export default Header; 