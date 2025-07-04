import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const MangaDetails = () => {
  const { id } = useParams();
  const [manga, setManga] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMangaDetails = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await axios.get(`/api/manga/${id}`);
        setManga(response.data);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to fetch manga details');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchMangaDetails();
    }
  }, [id]);

  const handleImageError = (e) => {
    e.target.style.display = 'none';
  };

  if (loading) {
    return <div className="loading">Loading manga details...</div>;
  }

  if (error) {
    return (
      <div>
        <Link to="/" className="back-button">← Back to Search</Link>
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!manga) {
    return (
      <div>
        <Link to="/" className="back-button">← Back to Search</Link>
        <div className="error">Manga not found</div>
      </div>
    );
  }

  return (
    <div className="manga-details">
      <Link to="/" className="back-button">← Back to Search</Link>
      
      <div className="manga-details-header">
        <img
          src={manga.image}
          alt={manga.title}
          className="manga-details-image"
          onError={handleImageError}
        />
        <div className="manga-details-info">
          <h1>{manga.title}</h1>
          <p><strong>Author:</strong> {manga.author}</p>
          {manga.url && (
            <p>
              <strong>Source:</strong>{' '}
              <a href={manga.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-color)' }}>
                View on WeebCentral
              </a>
            </p>
          )}
        </div>
      </div>

      <div className="manga-description">
        <h2>Description</h2>
        <p>{manga.description}</p>
      </div>
    </div>
  );
};

export default MangaDetails; 