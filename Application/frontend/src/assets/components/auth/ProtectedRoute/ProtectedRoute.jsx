import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSession } from '../../../../context/SessionContext';
import { authApi } from '../../../../api/auth.api';

export const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, isAuthenticated } = useSession();
  const location = useLocation();

  if (!isAuthenticated || !user) {
    // Not logged in
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Logged in, but role is not allowed
    // Route them to their proper dashboard
    const correctRoute = authApi.getDashboardRoute(user.role);
    return <Navigate to={correctRoute} replace />;
  }

  return children;
};
