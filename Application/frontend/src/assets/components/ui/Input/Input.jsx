import React, { forwardRef, useState } from 'react';
import styles from './Input.module.css';
import { Icon } from '@iconify/react';
import clsx from 'clsx';

export const Input = forwardRef(({ 
  label, 
  error, 
  icon, 
  type = 'text', 
  className,
  wrapperClassName,
  as: Component = 'input',
  ...props 
}, ref) => {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === 'password';
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;

  return (
    <div className={clsx(styles.wrapper, wrapperClassName)}>
      {label && <label className={styles.label}>{label}</label>}
      <div className={styles.inputContainer}>
        {icon && <Icon icon={icon} className={styles.leadingIcon} />}
        <Component
          ref={ref}
          type={Component === 'input' ? inputType : undefined}
          className={clsx(
            styles.input,
            Component === 'textarea' && styles.textarea,
            icon && styles.hasLeadingIcon,
            isPassword && styles.hasTrailingIcon,
            error && styles.hasError,
            className
          )}
          {...props}
        />
        {isPassword && (
          <button
            type="button"
            className={styles.trailingIconBtn}
            onClick={() => setShowPassword(!showPassword)}
          >
            <Icon icon={showPassword ? "mdi:eye-off" : "mdi:eye"} />
          </button>
        )}
      </div>
      {error && <span className={styles.errorMessage}>{error}</span>}
    </div>
  );
});

Input.displayName = 'Input';
