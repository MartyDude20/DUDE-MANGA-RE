import React from 'react';
import './Skeleton.css';

const Skeleton = ({ width = '100%', height = '1.5rem', style = {} }) => (
  <div
    className="skeleton"
    style={{
      width,
      height,
      borderRadius: '4px',
      background: 'linear-gradient(90deg, #374151 25%, #4B5563 50%, #374151 75%)',
      backgroundSize: '200% 100%',
      animation: 'skeleton-loading 1.2s infinite linear',
      ...style,
    }}
  />
);

export default Skeleton; 