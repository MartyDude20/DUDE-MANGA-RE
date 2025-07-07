import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Header from './components/Header.jsx';
import SearchPage from './components/SearchPage.jsx';
import MangaDetails from './components/MangaDetails.jsx';
import Sources from './components/Sources.jsx';
import SavedManga from './components/SavedManga.jsx';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900">
        <Header />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route path="/saved" element={<SavedManga />} />
            <Route path="/sources" element={<Sources />} />
            <Route path="/manga/:source/:id" element={<MangaDetails />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 