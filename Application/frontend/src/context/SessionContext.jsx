import { createContext, useContext, useState, useCallback, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/auth.api';

const SESSION_KEY = 'session_user';

const SessionContext = createContext();

export const SessionProvider = ({ children }) => {
  const navigate = useNavigate();

  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const login = useCallback((userData) => {
    // In auth.api.js we already set localStorage. Here we just update React state
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    authApi.logout();
    setUser(null);
    navigate('/');
  }, [navigate]);
  
  const updateUser = useCallback((updatedUserData) => {
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
