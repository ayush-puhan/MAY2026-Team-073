import React from 'react';
import { AuthLayout } from '../../assets/components/auth/AuthLayout/AuthLayout';
import { ResetPasswordForm } from '../../assets/components/auth/ResetPasswordForm/ResetPasswordForm';

export const ResetPassword = () => {
  return (
    <AuthLayout>
      <ResetPasswordForm />
    </AuthLayout>
  );
};
