import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSession } from '../../../../context/SessionContext';
import { authApi } from '@api/authApis/auth';

export const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, isAuthenticated } = useSession();
  const location = useLocation();

  React.useEffect(() => {
    if (user?.color_blind_mode) {
      document.documentElement.setAttribute('data-colorblind', 'true');
    } else {
      document.documentElement.removeAttribute('data-colorblind');
    }
    return () => {
      document.documentElement.removeAttribute('data-colorblind');
    };
  }, [user?.color_blind_mode]);

  if (!isAuthenticated || !user) {
    // Not logged in
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role?.toLowerCase())) {
    // Logged in, but role is not allowed
    // Route them to their proper dashboard
    const correctRoute = authApi.getDashboardRoute(user.role);
    return <Navigate to={correctRoute} replace />;
  }

  return children;
};
