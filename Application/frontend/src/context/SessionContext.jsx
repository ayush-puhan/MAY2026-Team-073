import { createContext, useContext, useState, useCallback, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@api/authApis/auth';
import { useTheme } from './ThemeContext';

const SESSION_KEY = 'session_user';

const SessionContext = createContext();

export const SessionProvider = ({ children }) => {
  const navigate = useNavigate();
  const { setTheme } = useTheme();

  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  // Apply on initial mount if user exists
  useEffect(() => {
    // Theme is now managed solely by ThemeContext + local storage
  }, []); // Only run once on mount

  const login = useCallback((userData) => {
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    authApi.logout();
    setUser(null);
    navigate('/');
  }, [navigate]);
  
  const updateUser = useCallback((updatedUserData) => {
    localStorage.setItem('user', JSON.stringify(updatedUserData));
    setUser(updatedUserData);
  }, []);

  const isAuthenticated = user !== null;

  const value = useMemo(
    () => ({ user, isAuthenticated, login, logout, updateUser }),
    [user, isAuthenticated, login, logout, updateUser]
  );

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};
