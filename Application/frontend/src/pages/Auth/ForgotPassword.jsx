import React from 'react';
import { AuthLayout } from '../../assets/components/auth/AuthLayout/AuthLayout';
import { ForgotPasswordForm } from '../../assets/components/auth/ForgotPasswordForm/ForgotPasswordForm';

export const ForgotPassword = () => {
  return (
    <AuthLayout 
      illustrationTitle="Secure Your Account"
      illustrationSubtitle="We'll help you get back to your campus network securely."
    >
      <ForgotPasswordForm />
    </AuthLayout>
  );
};
