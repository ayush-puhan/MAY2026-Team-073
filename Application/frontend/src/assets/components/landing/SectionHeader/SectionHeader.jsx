import React from 'react';
import styles from './SectionHeader.module.css';
import { Link } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { motion } from 'framer-motion';
import { uiIcons } from '../../../icons/registry';

export const SectionHeader = ({ label, title, titleAccent, subtitle, actionText, actionLink }) => (
  <motion.div 
    className={styles.headerRow}
    initial={{ opacity: 0, y: 20 }} 
    whileInView={{ opacity: 1, y: 0 }} 
    viewport={{ once: true }}
  >
    <div className={styles.headerContent}>
      {label && <span className={styles.label}>{label}</span>}
      <h2>{title} {titleAccent && <span className={styles.accent}>{titleAccent}</span>}</h2>
      {subtitle && <p>{subtitle}</p>}
    </div>
    {actionText && actionLink && (
      <div className={styles.headerAction}>
        <Link to={actionLink} className={styles.actionBtn}>
          {actionText} <Icon icon={uiIcons.arrowRight} />
        </Link>
      </div>
    )}
  </motion.div>
);
