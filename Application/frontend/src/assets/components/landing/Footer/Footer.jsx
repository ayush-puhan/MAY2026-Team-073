import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './Footer.module.css';
import { Logo } from '../../ui/Logo/Logo';
import { DocumentModal } from '../../ui/DocumentModal/DocumentModal';

export const Footer = () => {
  const [activeDoc, setActiveDoc] = useState(null);

  return (
    <footer className={styles.footer}>
      <div className={styles.content}>
        <div className={styles.brand}>
          <Logo size="md" />
          <p>Empowering student communities.</p>
        </div>
        <div className={styles.links}>
          <button onClick={() => setActiveDoc('privacy')} className={styles.linkBtn}>Privacy Policy</button>
          <button onClick={() => setActiveDoc('terms')} className={styles.linkBtn}>Terms of Service</button>
          <Link to="#">Support Helpdesk</Link>
        </div>
      </div>
      <div className={styles.bottom}>
        <p>&copy; 2026 ClubConnect. All rights reserved.</p>
      </div>
      
      <DocumentModal isOpen={!!activeDoc} onClose={() => setActiveDoc(null)} documentId={activeDoc} />
    </footer>
  );
};
