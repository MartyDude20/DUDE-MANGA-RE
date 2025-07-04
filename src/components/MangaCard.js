import React from 'react';
import { Link } from 'react-router-dom';

const sourceLabels = {
  weebcentral: 'WeebCentral',
  asurascans: 'Asura Scans',
};

const MangaCard = ({ manga }) => {
  const handleImageError = (e) => {
    e.target.style.display = 'none';
  };

  return (
    <Link to={`/manga/${manga.source}/${manga.id}`} className="manga-card">
      <div style={{ position: 'relative' }}>
        <img
          src={manga.image}
          alt={manga.title}
          className="manga-image"
          onError={handleImageError}
        />
        <span
          style={{
            position: 'absolute',
            top: 8,
            left: 8,
            background: 'var(--accent-color)',
            color: 'white',
            padding: '2px 8px',
            borderRadius: '6px',
            fontSize: '0.8rem',
            fontWeight: 600,
            zIndex: 2,
          }}
        >
          {sourceLabels[manga.source] || manga.source}
        </span>
      </div>
      <div className="manga-info">
        <h3 className="manga-title">{manga.title}</h3>
        {manga.status && (
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <strong>Status:</strong> {manga.status}
          </div>
        )}
        {manga.chapter && (
          <div className="manga-chapter">
            <strong>Chapter:</strong> {manga.chapter}
          </div>
        )}
      </div>
    </Link>
  );
};

export default MangaCard; 