import React from 'react';
import { AuthLayout } from '../../assets/components/auth/AuthLayout/AuthLayout';
import { RegisterForm } from '../../assets/components/auth/RegisterForm/RegisterForm';

export const Register = () => {
  return (
    <AuthLayout 
      illustrationTitle="Your Campus Is Waiting"
      illustrationSubtitle="Join the largest student network and unlock endless opportunities."
    >
      <RegisterForm />
    </AuthLayout>
  );
};
