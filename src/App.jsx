import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Header from './components/Header.jsx';
import Dashboard from './components/Dashboard.jsx';
import SearchPage from './components/SearchPage.jsx';
import MangaDetails from './components/MangaDetails.jsx';
import Sources from './components/Sources.jsx';
import SavedManga from './components/SavedManga.jsx';
import CacheManager from './components/CacheManager.jsx';
import AuthPage from './components/Auth/AuthPage.jsx';
import ForgotPassword from './components/Auth/ForgotPassword.jsx';
import ResetPassword from './components/Auth/ResetPassword.jsx';
import Profile from './components/Profile.jsx';
import ReadHistory from './components/ReadHistory.jsx';
import ReadingLists from './components/ReadingLists.jsx';
import Settings from './components/Settings.jsx';
import { AuthProvider, useAuth } from './components/Auth/AuthContext.jsx';
import LandingPage from './components/LandingPage.jsx';

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
  const { isAuthenticated } = useAuth();
  return (
    <div className="min-h-screen bg-gray-900">
      {isAuthenticated && <Header />}
      <main className="flex-1">
        <Routes>
          {!isAuthenticated ? (
            <>
              <Route path="/" element={<LandingPage />} />
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </>
          ) : (
            <>
              <Route path="/" element={<Dashboard />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/saved" element={<SavedManga />} />
              <Route path="/sources" element={<Sources />} />
              <Route path="/reading-lists" element={<ProtectedRoute><ReadingLists /></ProtectedRoute>} />
              <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
              <Route path="/cache" element={<ProtectedRoute><CacheManager /></ProtectedRoute>} />
              <Route path="/manga/:source/:id" element={<MangaDetails />} />
              <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
              <Route path="/read-history" element={<ProtectedRoute><ReadHistory /></ProtectedRoute>} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </>
          )}
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