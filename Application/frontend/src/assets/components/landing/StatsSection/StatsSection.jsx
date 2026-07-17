import React from 'react';
import styles from './StatsSection.module.css';
import { motion } from 'framer-motion';
import { SectionHeader } from '../SectionHeader/SectionHeader';

const stats = [
  { value: '500+', label: 'Partner Campuses' },
  { value: '10k+', label: 'Active Clubs' },
  { value: '1M+', label: 'Student Members' },
  { value: '2M+', label: 'Yearly Events' },
];

export const StatsSection = () => (
  <section className={styles.section} id="about">
    <div className={styles.container}>
      <SectionHeader 
        label="ABOUT US"
        title="By the"
        titleAccent="numbers."
        subtitle="ClubConnect is growing rapidly across campuses nationwide."
      />
      <div className={styles.grid}>
      {stats.map((s, i) => (
        <motion.div key={i} className={styles.stat} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
          <h3 className={styles.value}>{s.value}</h3>
          <p>{s.label}</p>
        </motion.div>
      ))}
      </div>
    </div>
  </section>
);
