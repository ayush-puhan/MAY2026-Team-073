import React from 'react';
import styles from './Button.module.css';
import { Icon } from '@iconify/react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  isLoading = false, 
  icon, 
  fullWidth = false,
  className,
  ...props 
}) => {
  return (
    <motion.button
      whileTap={{ scale: 0.98 }}
      className={clsx(
        styles.btn,
        styles[variant],
        styles[size],
        fullWidth && styles.fullWidth,
        isLoading && styles.loading,
        className
      )}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <Icon icon="mdi:loading" className={styles.spinner} />
      ) : icon ? (
        <Icon icon={icon} className={styles.icon} />
      ) : null}
      {children}
    </motion.button>
  );
};
