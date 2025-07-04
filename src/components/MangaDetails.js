import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import MangaReaderModal from './MangaReaderModal';

const MangaDetails = () => {
  const { id, source } = useParams();
  const [manga, setManga] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [readerOpen, setReaderOpen] = useState(false);
  const [readerImages, setReaderImages] = useState([]);
  const [readerLoading, setReaderLoading] = useState(false);
  const [readerTitle, setReaderTitle] = useState('');

  useEffect(() => {
    const fetchMangaDetails = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await axios.get(`/api/manga/${source}/${id}`);
        setManga(response.data);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to fetch manga details');
      } finally {
        setLoading(false);
      }
    };

    if (id && source) {
      fetchMangaDetails();
    }
  }, [id, source]);

  const handleImageError = (e) => {
    e.target.style.display = 'none';
  };

  const handleChapterClick = async (e, chapter) => {
    e.preventDefault();
    setReaderLoading(true);
    setReaderOpen(true);
    setReaderTitle(chapter.title);
    try {
      // chapter.url is like 'bones-b58b6f2f/chapter/30', id is manga_id
      const resp = await axios.get(`/api/chapter-images/${source}/${id}/${chapter.url}`);
      setReaderImages(resp.data.images || []);
    } catch (err) {
      setReaderImages([]);
    } finally {
      setReaderLoading(false);
    }
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
                View on {manga.source ? manga.source.charAt(0).toUpperCase() + manga.source.slice(1) : 'Source'}
              </a>
            </p>
          )}
        </div>
      </div>

      <div className="manga-description">
        <h2>Description</h2>
        <p>{manga.description}</p>
      </div>
      {manga.chapters && manga.chapters.length > 0 && (
        <div className="manga-chapters" style={{ marginTop: '2rem' }}>
          <h2>Chapters</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {manga.chapters.map((chapter, idx) => (
              <li key={`${chapter.url}-${idx}`} style={{ marginBottom: '0.5rem' }}>
                <a
                  href={chapter.url}
                  style={{ color: 'var(--accent-color)', textDecoration: 'underline', cursor: 'pointer' }}
                  onClick={e => handleChapterClick(e, chapter)}
                >
                  {chapter.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
      <MangaReaderModal
        open={readerOpen}
        images={readerImages}
        onClose={() => setReaderOpen(false)}
        chapterTitle={readerTitle}
      />
      {readerOpen && readerLoading && (
        <div className="manga-reader-loading">Loading pages...</div>
      )}
    </div>
  );
};

export default MangaDetails; 