import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Logo.module.css';
import { Icon } from '@iconify/react';
import clsx from 'clsx';
import { uiIcons } from '../../../icons/registry';

export const Logo = ({ size = 'md', linkTo = '/', className }) => {
  return (
    <Link to={linkTo} className={clsx(styles.logo, styles[size], className)}>
      <Icon icon={uiIcons.starFourPoints} className={styles.icon} />
      <span className={styles.wordmark}>
        <span className={styles.text}>Club</span>
        <span className={styles.accent}>Connect</span>
      </span>
    </Link>
  );
};
