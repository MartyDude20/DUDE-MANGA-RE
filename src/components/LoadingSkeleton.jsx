import React from 'react';
import Skeleton from './Skeleton';

const LoadingSkeleton = () => {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header Skeleton */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo/Brand */}
            <div className="flex items-center">
              <Skeleton width="120px" height="32px" />
            </div>
            
            {/* Navigation */}
            <nav className="hidden md:flex space-x-8">
              <Skeleton width="60px" height="20px" />
              <Skeleton width="60px" height="20px" />
              <Skeleton width="60px" height="20px" />
              <Skeleton width="60px" height="20px" />
            </nav>
            
            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <Skeleton width="32px" height="32px" style={{ borderRadius: '50%' }} />
              <Skeleton width="80px" height="20px" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Skeleton */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Page Title */}
          <div className="mb-8">
            <Skeleton width="200px" height="32px" style={{ marginBottom: '0.5rem' }} />
            <Skeleton width="300px" height="16px" />
          </div>

          {/* Content Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {/* Manga Cards */}
            {[...Array(8)].map((_, index) => (
              <div key={index} className="bg-gray-800 rounded-lg overflow-hidden">
                {/* Manga Cover */}
                <Skeleton width="100%" height="200px" />
                
                {/* Manga Info */}
                <div className="p-4">
                  <Skeleton width="80%" height="20px" style={{ marginBottom: '0.5rem' }} />
                  <Skeleton width="60%" height="16px" style={{ marginBottom: '0.5rem' }} />
                  <Skeleton width="40%" height="14px" />
                </div>
              </div>
            ))}
          </div>

          {/* Sidebar/Additional Content */}
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Main Content Area */}
            <div className="lg:col-span-3">
              <div className="bg-gray-800 rounded-lg p-6">
                <Skeleton width="100%" height="24px" style={{ marginBottom: '1rem' }} />
                <Skeleton width="100%" height="16px" style={{ marginBottom: '0.5rem' }} />
                <Skeleton width="90%" height="16px" style={{ marginBottom: '0.5rem' }} />
                <Skeleton width="95%" height="16px" style={{ marginBottom: '0.5rem' }} />
                <Skeleton width="85%" height="16px" />
              </div>
            </div>
            
            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-gray-800 rounded-lg p-6">
                <Skeleton width="100%" height="24px" style={{ marginBottom: '1rem' }} />
                <Skeleton width="100%" height="16px" style={{ marginBottom: '0.5rem' }} />
                <Skeleton width="100%" height="16px" style={{ marginBottom: '0.5rem' }} />
                <Skeleton width="100%" height="16px" />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default LoadingSkeleton; 