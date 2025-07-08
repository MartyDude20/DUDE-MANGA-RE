import React, { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext.jsx';

const ResetPassword = () => {
  const { authFetch } = useAuth();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Get token from URL params or allow manual entry
  const tokenFromUrl = searchParams.get('token');
  const [token, setToken] = useState(tokenFromUrl || '');
  const [showTokenField, setShowTokenField] = useState(!tokenFromUrl);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!token.trim()) {
      setError('Please enter the reset token');
      return;
    }
    
    if (!password.trim()) {
      setError('Please enter a new password');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await authFetch('http://localhost:5000/password-reset/confirm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          token: token.trim(), 
          new_password: password 
        }),
      });

      if (response.ok) {
        setMessage('Password has been reset successfully! Redirecting to login...');
        setPassword('');
        setConfirmPassword('');
        setToken('');
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/auth');
        }, 3000);
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to reset password');
      }
    } catch (err) {
      setError('Failed to reset password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            Reset Password
          </h2>
          <p className="mt-2 text-center text-sm text-gray-400">
            Enter your reset token and new password.
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {tokenFromUrl && (
              <div className="rounded-md bg-blue-900 border border-blue-600 p-4">
                <div className="text-sm text-blue-200">
                  Reset token found in URL. You can proceed to set your new password.
                </div>
              </div>
            )}
            
            {showTokenField && (
              <div>
                <label htmlFor="token" className="block text-sm font-medium text-gray-300">
                  Reset Token
                </label>
                <input
                  id="token"
                  name="token"
                  type="text"
                  required
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  className="mt-1 appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-gray-800 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Enter reset token"
                  disabled={loading}
                />
              </div>
            )}

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300">
                New Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-gray-800 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="New password"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300">
                Confirm New Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="mt-1 appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-gray-800 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Confirm new password"
                disabled={loading}
              />
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-900 border border-red-600 p-4">
              <div className="text-sm text-red-200">{error}</div>
            </div>
          )}

          {message && (
            <div className="rounded-md bg-green-900 border border-green-600 p-4">
              <div className="text-sm text-green-200">{message}</div>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </div>

          <div className="text-center space-y-2">
            <div>
              <Link
                to="/login"
                className="font-medium text-blue-400 hover:text-blue-300"
              >
                Back to Login
              </Link>
            </div>
            <div>
              <Link
                to="/forgot-password"
                className="text-sm text-gray-400 hover:text-gray-300"
              >
                Need a new reset link?
              </Link>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword; 