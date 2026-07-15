import React, { useState, useRef, useEffect } from 'react';
import { Icon } from '@iconify/react';
import clsx from 'clsx';
import styles from './Dropdown.module.css';

// options: [{ value, label }]
export const Dropdown = ({ options = [], value, onChange, placeholder = 'Select...', label }) => {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setIsOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selected = options.find((o) => o.value === value);

  return (
    <div className={styles.wrapper} ref={ref}>
      {label && <label className={styles.label}>{label}</label>}
      <button
        type="button"
        className={styles.trigger}
        onClick={() => setIsOpen((prev) => !prev)}
      >
        <span className={clsx(!selected && styles.placeholder)}>
          {selected ? selected.label : placeholder}
        </span>
        <Icon icon="mdi:chevron-down" className={clsx(styles.chevron, isOpen && styles.chevronOpen)} />
      </button>
      {isOpen && (
        <div className={styles.menu}>
          {options.map((option) => (
            <button
              type="button"
              key={option.value}
              className={clsx(styles.option, option.value === value && styles.optionActive)}
              onClick={() => { onChange(option.value); setIsOpen(false); }}
            >
              {option.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
