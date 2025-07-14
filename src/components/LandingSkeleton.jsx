import React from 'react';
import Skeleton from './Skeleton';

const LandingSkeleton = () => {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Simple Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Skeleton width="120px" height="32px" />
            <div className="flex space-x-4">
              <Skeleton width="60px" height="20px" />
              <Skeleton width="60px" height="20px" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <Skeleton width="400px" height="48px" style={{ margin: '0 auto 1rem' }} />
            <Skeleton width="600px" height="24px" style={{ margin: '0 auto 1rem' }} />
            <Skeleton width="300px" height="16px" style={{ margin: '0 auto 2rem' }} />
            <div className="flex justify-center space-x-4">
              <Skeleton width="120px" height="40px" />
              <Skeleton width="120px" height="40px" />
            </div>
          </div>

          {/* Feature Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {[...Array(3)].map((_, index) => (
              <div key={index} className="text-center">
                <Skeleton width="64px" height="64px" style={{ margin: '0 auto 1rem', borderRadius: '50%' }} />
                <Skeleton width="200px" height="24px" style={{ margin: '0 auto 0.5rem' }} />
                <Skeleton width="100%" height="16px" style={{ marginBottom: '0.5rem' }} />
                <Skeleton width="90%" height="16px" />
              </div>
            ))}
          </div>

          {/* Content Section */}
          <div className="bg-gray-800 rounded-lg p-8">
            <Skeleton width="300px" height="32px" style={{ marginBottom: '1rem' }} />
            <Skeleton width="100%" height="16px" style={{ marginBottom: '0.5rem' }} />
            <Skeleton width="95%" height="16px" style={{ marginBottom: '0.5rem' }} />
            <Skeleton width="90%" height="16px" />
          </div>
        </div>
      </main>
    </div>
  );
};

export default LandingSkeleton; 