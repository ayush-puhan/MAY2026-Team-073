import React from 'react';
import { Link } from 'react-router-dom';
import styles from './CTASection.module.css';
import { Button } from '../../ui/Button/Button';
import { motion } from 'framer-motion';
import { useSession } from '../../../../context/SessionContext';
import { authApi } from '../../../../api/auth.api';

export const CTASection = () => {
  const { user } = useSession();
  
  return (
    <section className={styles.section}>
      <motion.div className={styles.card} initial={{ opacity: 0, scale: 0.95 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }}>
        <div className={styles.content}>
        <h2 className={styles.title}>Ready to Find Your Community?</h2>
        <p className={styles.subtitle}>
          Join thousands of students who have already discovered their passions and made lifelong friends.
        </p>
        <Link to={user ? authApi.getDashboardRoute(user.role) : "/register"}>
          <Button size="lg" className={styles.ctaBtn}>Get Started Today</Button>
        </Link>
        </div>
      </motion.div>
    </section>
  );
};
