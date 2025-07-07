import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Header from './components/Header.jsx';
import SearchPage from './components/SearchPage.jsx';
import MangaDetails from './components/MangaDetails.jsx';
import Sources from './components/Sources.jsx';
import SavedManga from './components/SavedManga.jsx';
import CacheManager from './components/CacheManager.jsx';
import AuthPage from './components/Auth/AuthPage.jsx';
import { AuthProvider, useAuth } from './components/Auth/AuthContext.jsx';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  return children;
};

// Public Route Component (redirects to home if already authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
};

// Main App Content
const AppContent = () => {
  return (
    <div className="min-h-screen bg-gray-900">
      <Header />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/saved" element={<SavedManga />} />
          <Route path="/sources" element={<Sources />} />
          <Route path="/cache" element={
            <ProtectedRoute>
              <CacheManager />
            </ProtectedRoute>
          } />
          <Route path="/manga/:source/:id" element={<MangaDetails />} />
          <Route path="/auth" element={
            <PublicRoute>
              <AuthPage />
            </PublicRoute>
          } />
        </Routes>
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App; 