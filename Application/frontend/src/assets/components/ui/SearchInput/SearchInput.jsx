import React, { useState, useEffect, useRef } from 'react';
import { Icon } from '@iconify/react';
import styles from './SearchInput.module.css';

export const SearchInput = ({ placeholder = 'Search...', onChange, debounceMs = 500, style }) => {
  const [value, setValue] = useState('');
  const timeoutRef = useRef(null);

  useEffect(() => {
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => onChange?.(value), debounceMs);
    return () => clearTimeout(timeoutRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return (
    <div className={styles.wrapper} style={style}>
      <Icon icon="mdi:magnify" className={styles.icon} />
      <input
        type="text"
        className={styles.input}
        placeholder={placeholder}
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
    </div>
  );
};
