import React from 'react';
import { Link } from 'react-router-dom';
import styles from './CTASection.module.css';
import { Button } from '../../ui/Button/Button';
import { motion } from 'framer-motion';
import { useSession, getDashboardLink } from '../../../../context/SessionContext';

export const CTASection = () => {
  const { user } = useSession();
  
  return (
    <section className={styles.section}>
      <motion.div className={styles.card} initial={{ opacity: 0, scale: 0.95 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }}>
        <h2>Your campus is <span className={styles.accent}>waiting.</span></h2>
        <p>Don't miss out on the best part of your university life.</p>
        <Link to={user ? getDashboardLink(user.role) : "/register"}>
          <Button size="lg" className={styles.ctaBtn}>Get Started Today</Button>
        </Link>
      </motion.div>
    </section>
  );
};
