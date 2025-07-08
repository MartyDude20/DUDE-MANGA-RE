import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage = () => (
  <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white px-4">
    <h1 className="text-5xl font-extrabold text-blue-500 mb-4">Dude Manga</h1>
    <h2 className="text-2xl font-semibold mb-6">your favorite manga reader</h2>
    <p className="text-lg mb-8 text-gray-300 max-w-xl text-center">
      You need to create an account to use Dude Manga. Sign up to start reading and tracking your favorite manga!
    </p>
    <Link
      to="/auth"
      className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-md text-lg font-bold shadow-lg transition-colors"
    >
      Sign Up / Log In
    </Link>
    <div className="mt-8 text-gray-400 text-sm">
      Already have an account? Click the <span className="text-indigo-400 font-semibold">Sign Up / Log In</span> button at the top right.
    </div>
  </div>
);

export default LandingPage; 