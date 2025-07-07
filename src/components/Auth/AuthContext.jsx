import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check for existing token on app load
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      setAccessToken(token);
      // Verify token and get user info
      verifyToken(token);
    } else {
      setIsLoading(false);
    }
  }, []);

  const verifyToken = async (token) => {
    try {
      const response = await fetch('http://localhost:5000/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        credentials: 'include',
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);
      } else {
        // Token is invalid, clear it
        logout();
      }
    } catch (error) {
      console.error('Token verification error:', error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (loginData) => {
    setUser(loginData.user);
    setAccessToken(loginData.accessToken);
    setIsAuthenticated(true);
  };

  const register = async (registerData) => {
    // After successful registration, user can login
    return registerData;
  };

  const logout = async () => {
    try {
      // Call logout endpoint to blacklist tokens
      if (accessToken) {
        await fetch('http://localhost:5000/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
          credentials: 'include',
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local state regardless of server response
      setUser(null);
      setAccessToken(null);
      setIsAuthenticated(false);
      localStorage.removeItem('accessToken');
    }
  };

  const refreshToken = async () => {
    try {
      const response = await fetch('http://localhost:5000/refresh', {
        method: 'POST',
        credentials: 'include',
      });

      if (response.ok) {
        const newAccessToken = response.headers.get('Authorization')?.replace('Bearer ', '');
        if (newAccessToken) {
          setAccessToken(newAccessToken);
          localStorage.setItem('accessToken', newAccessToken);
          return newAccessToken;
        }
      } else {
        // Refresh failed, logout user
        logout();
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
    }
    return null;
  };

  // Create authenticated fetch function
  const authFetch = async (url, options = {}) => {
    const token = accessToken || localStorage.getItem('accessToken');
    
    if (token) {
      options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
      };
    }

    let response = await fetch(url, {
      ...options,
      credentials: 'include',
    });

    // If token expired, try to refresh
    if (response.status === 401 && token) {
      const newToken = await refreshToken();
      if (newToken) {
        // Retry the request with new token
        options.headers = {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`,
        };
        response = await fetch(url, {
          ...options,
          credentials: 'include',
        });
      }
    }

    return response;
  };

  const value = {
    user,
    accessToken,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshToken,
    authFetch,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 