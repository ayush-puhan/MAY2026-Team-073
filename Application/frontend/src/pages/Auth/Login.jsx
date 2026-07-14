import React from 'react';
import { AuthLayout } from '../../assets/components/auth/AuthLayout/AuthLayout';
import { LoginForm } from '../../assets/components/auth/LoginForm/LoginForm';

export const Login = () => {
  return (
    <AuthLayout 
      illustrationTitle="Welcome Back to Campus"
      illustrationSubtitle="Sign in to access your clubs, events, and campus network."
    >
      <LoginForm />
    </AuthLayout>
  );
};
