import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import SearchPage from './components/SearchPage';
import MangaDetails from './components/MangaDetails';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route path="/manga/:id" element={<MangaDetails />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 