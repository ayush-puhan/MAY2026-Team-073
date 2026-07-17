import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Icon } from '@iconify/react';
import styles from './Dropdown.module.css';

export const Dropdown = ({ name, value, onChange, options = [], placeholder = 'Select...', disabled, className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0, width: 0 });
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target) && !event.target.closest(`.${styles.menu}`)) {
        setIsOpen(false);
      }
    };
    const handleScroll = (e) => {
      if (!e.target.closest(`.${styles.menu}`)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    window.addEventListener('scroll', handleScroll, true);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      window.removeEventListener('scroll', handleScroll, true);
    };
  }, []);

  const selectedOption = options.find(opt => String(opt.value).toLowerCase() === String(value).toLowerCase());

  const handleSelect = (optValue) => {
    if (onChange) {
      onChange({ target: { name, value: optValue, type: 'select-one' } });
    }
    setIsOpen(false);
  };

  const toggleOpen = () => {
    if (disabled) return;
    if (!isOpen && dropdownRef.current) {
      const rect = dropdownRef.current.getBoundingClientRect();
      setCoords({
        left: rect.left,
        top: rect.bottom + 4,
        width: rect.width
      });
    }
    setIsOpen(!isOpen);
  };

  return (
    <div className={`${styles.dropdown} ${className || ''} ${disabled ? styles.disabled : ''}`} ref={dropdownRef}>
      <div 
        className={`${styles.header} ${!selectedOption ? styles.placeholder : ''}`}
        onClick={toggleOpen}
      >
        <span className={styles.value}>{selectedOption ? selectedOption.label : placeholder}</span>
        <Icon icon="mdi:chevron-down" className={`${styles.icon} ${isOpen ? styles.open : ''}`} />
      </div>
      
      {isOpen && typeof document !== 'undefined' && createPortal(
        <div className={styles.menu} style={{ top: coords.top, left: coords.left, width: coords.width }}>
          {options.length === 0 ? (
            <div className={styles.empty}>No options available</div>
          ) : (
            options.map((opt) => (
              <div
                key={opt.value}
                className={`${styles.option} ${String(value).toLowerCase() === String(opt.value).toLowerCase() ? styles.selected : ''}`}
                onClick={() => handleSelect(opt.value)}
              >
                {opt.label}
              </div>
            ))
          )}
        </div>,
        document.body
      )}
    </div>
  );
};
