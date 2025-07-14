import React from 'react';

const ProgressIndicator = ({ step, progress, message }) => {
  // Color coding based on progress
  const getProgressColor = (progress) => {
    if (progress < 0.3) return 'bg-red-500'; // Red for early stages
    if (progress < 0.7) return 'bg-yellow-500'; // Yellow for middle stages
    return 'bg-green-500'; // Green for completion
  };

  // Icon based on step
  const getStepIcon = (step) => {
    switch (step.toLowerCase()) {
      case 'details':
        return '📖';
      case 'chapters':
        return '📚';
      case 'images':
        return '🖼️';
      case 'search':
        return '🔍';
      default:
        return '⚡';
    }
  };

  // Format step name
  const formatStepName = (step) => {
    return step.charAt(0).toUpperCase() + step.slice(1);
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-lg">{getStepIcon(step)}</span>
          <span className="font-semibold text-gray-200">{formatStepName(step)}</span>
        </div>
        <span className="text-sm text-gray-400 font-mono">
          {Math.round(progress * 100)}%
        </span>
      </div>
      
      {/* Progress Bar */}
      <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ease-out ${getProgressColor(progress)}`}
          style={{ width: `${progress * 100}%` }}
        />
      </div>
      
      {/* Message */}
      {message && (
        <p className="text-sm text-gray-300 mt-1">
          {message}
        </p>
      )}
      
      {/* Progress Details */}
      <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
        <span>Progress: {progress.toFixed(3)}</span>
        <span>
          {progress === 1.0 ? '✅ Complete' : progress > 0.5 ? '🔄 In Progress' : '⏳ Starting'}
        </span>
      </div>
    </div>
  );
};

export default ProgressIndicator; 