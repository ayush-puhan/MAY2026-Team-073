import { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';
import styles from './SearchInput.module.css';

export const SearchInput = ({ placeholder = "Search...", onChange, delay = 500, style }) => {
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const handler = setTimeout(() => {
      if (onChange) onChange(searchTerm);
    }, delay);

    return () => clearTimeout(handler);
  }, [searchTerm, delay, onChange]);

  return (
    <div className={styles.wrapper} style={style}>
      <Icon 
        icon={uiIcons.search} 
        className={styles.icon}
      />
      <input
        type="text"
        placeholder={placeholder}
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className={styles.input}
      />
    </div>
  );
};
