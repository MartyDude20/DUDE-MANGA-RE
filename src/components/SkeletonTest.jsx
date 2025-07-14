import React, { useState } from 'react';
import LoadingSkeleton from './LoadingSkeleton';
import LandingSkeleton from './LandingSkeleton';

const SkeletonTest = () => {
  const [showLoading, setShowLoading] = useState(false);
  const [showLanding, setShowLanding] = useState(false);

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Skeleton UI Test</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold text-white mb-4">Loading Skeleton (Authenticated)</h2>
            <button
              onClick={() => setShowLoading(!showLoading)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
            >
              {showLoading ? 'Hide' : 'Show'} Loading Skeleton
            </button>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold text-white mb-4">Landing Skeleton (Unauthenticated)</h2>
            <button
              onClick={() => setShowLanding(!showLanding)}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
            >
              {showLanding ? 'Hide' : 'Show'} Landing Skeleton
            </button>
          </div>
        </div>

        {showLoading && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-white mb-4">Loading Skeleton Preview:</h3>
            <div className="border-2 border-blue-500 rounded-lg overflow-hidden">
              <LoadingSkeleton />
            </div>
          </div>
        )}

        {showLanding && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-white mb-4">Landing Skeleton Preview:</h3>
            <div className="border-2 border-green-500 rounded-lg overflow-hidden">
              <LandingSkeleton />
            </div>
          </div>
        )}

        <div className="bg-gray-800 p-6 rounded-lg">
          <h2 className="text-xl font-semibold text-white mb-4">Instructions</h2>
          <ul className="text-gray-300 space-y-2">
            <li>• Click the buttons above to preview each skeleton component</li>
            <li>• The Loading Skeleton mimics the authenticated app layout</li>
            <li>• The Landing Skeleton mimics the landing page layout</li>
            <li>• These will automatically show during authentication loading</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SkeletonTest; 