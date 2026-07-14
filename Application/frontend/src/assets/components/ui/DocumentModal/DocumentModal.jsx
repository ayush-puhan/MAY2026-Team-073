import React, { useEffect } from 'react';
import styles from './DocumentModal.module.css';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';

const DOCS = {
  privacy: {
    title: 'Privacy Policy',
    content: (
      <>
        <h3>1. Data Collection</h3>
        <p>We collect your email, full name, and club affiliations to provide personalized campus experiences. We do not share this data with third-party advertisers.</p>
        <h3>2. Data Security</h3>
        <p>All passwords are encrypted and secure. Your session tokens are stored securely in HTTP-only cookies.</p>
        <h3>3. Your Rights</h3>
        <p>You may request deletion of your account at any time via the settings panel.</p>
        <h3>4. Analytics</h3>
        <p>We use anonymous usage data to improve our platform's responsiveness and discoverability for campus events.</p>
      </>
    )
  },
  terms: {
    title: 'Terms of Service',
    content: (
      <>
        <h3>1. Acceptance of Terms</h3>
        <p>By creating an account on ClubConnect, you agree to abide by these terms of service and our community guidelines.</p>
        <h3>2. User Responsibilities</h3>
        <p>You are responsible for maintaining the confidentiality of your account credentials.</p>
        <h3>3. Content Ownership</h3>
        <p>Clubs retain ownership of the content they post, but grant ClubConnect a license to display it on the platform.</p>
        <h3>4. Termination</h3>
        <p>We reserve the right to suspend accounts that repeatedly violate these terms or engage in malicious activity.</p>
      </>
    )
  },
  guidelines: {
    title: 'Community Guidelines',
    content: (
      <>
        <h3>1. Be Respectful</h3>
        <p>Treat all members of the campus community with respect. Harassment, hate speech, and bullying are strictly prohibited.</p>
        <h3>2. Authentic Identity</h3>
        <p>Use your real name and campus email to ensure accountability and trust within our platform.</p>
        <h3>3. Event Integrity</h3>
        <p>Only RSVP to events you genuinely intend to attend to respect the organizers' planning efforts.</p>
        <h3>4. Constructive Engagement</h3>
        <p>Keep discussions in club forums constructive and related to the club's purpose.</p>
      </>
    )
  }
};

export const DocumentModal = ({ isOpen, onClose, documentId }) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => { document.body.style.overflow = 'unset'; };
  }, [isOpen]);

  if (!documentId || !DOCS[documentId]) return null;

  const doc = DOCS[documentId];

  return (
    <AnimatePresence>
      {isOpen && (
        <div className={styles.overlay} onClick={onClose}>
          <motion.div 
            className={styles.modal} 
            onClick={e => e.stopPropagation()}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            <div className={styles.header}>
              <h2>{doc.title}</h2>
              <button className={styles.closeBtn} onClick={onClose}>
                <Icon icon="mdi:close" />
              </button>
            </div>
            <div className={styles.content}>
              {doc.content}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
