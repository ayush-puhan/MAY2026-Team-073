import React, { useEffect, useRef } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSession } from '../../../../context/SessionContext';
import { authApi } from '@api/authApis/auth';
import { useToast } from '../../../../context/ToastContext';

export const PublicOnlyRoute = ({ children }) => {
  const { user, isAuthenticated } = useSession();
  const { showError } = useToast();
  const location = useLocation();
  const hasToasted = useRef(false);
  const initiallyAuthenticated = useRef(isAuthenticated);

  useEffect(() => {
    if (initiallyAuthenticated.current && isAuthenticated && user && !hasToasted.current) {
      hasToasted.current = true;
      let message = "Please logout first to access this page";
      if (location.pathname === '/login') {
        message = "Please logout to login with another account";
      } else if (location.pathname === '/register') {
        message = "Please logout to create a new account";
      } else if (location.pathname === '/forgot-password') {
        message = "Please logout to reset a password";
      }
      showError(message);
    }
  }, [isAuthenticated, user, showError, location.pathname]);

  if (isAuthenticated && user) {
    const correctRoute = authApi.getDashboardRoute(user.role);
    return <Navigate to={correctRoute} replace />;
  }

  return children;
};
