import React, { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import { useAuth } from './AuthContext';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const { login, register } = useAuth();

  const handleLogin = async (loginData) => {
    setIsLoading(true);
    setSuccessMessage('');
    try {
      await login(loginData);
      // Login successful - user will be redirected by the app
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (registerData) => {
    setIsLoading(true);
    setSuccessMessage('');
    try {
      await register(registerData);
      // Registration successful, switch to login
      setIsLogin(true);
      setSuccessMessage('Account created successfully! Please sign in.');
      // Show success message (you could add a toast notification here)
    } catch (error) {
      console.error('Registration error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const switchToLogin = () => {
    setIsLogin(true);
    setSuccessMessage('');
  };

  const switchToRegister = () => {
    setIsLogin(false);
    setSuccessMessage('');
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {successMessage && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50">
          <div className="bg-green-600 text-white px-6 py-3 rounded-md shadow-lg">
            {successMessage}
          </div>
        </div>
      )}
      
      {isLogin ? (
        <LoginForm
          onLogin={handleLogin}
          onSwitchToRegister={switchToRegister}
          isLoading={isLoading}
        />
      ) : (
        <RegisterForm
          onRegister={handleRegister}
          onSwitchToLogin={switchToLogin}
          isLoading={isLoading}
        />
      )}
    </div>
  );
};

export default AuthPage; 