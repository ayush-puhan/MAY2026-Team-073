import React from 'react';
import styles from './Testimonials.module.css';
import { motion } from 'framer-motion';
import { Icon } from '@iconify/react';
import { SectionHeader } from '../SectionHeader/SectionHeader';

const testimonials = [
  { name: 'Priya S.', role: 'Robotics Club President', quote: 'ClubConnect transformed how we recruit and manage our team. Everything is in one place now.', avatar: 'mdi:account-circle' },
  { name: 'Arjun M.', role: 'CS Student, Batch \'27', quote: 'I discovered 5 clubs in my first week that I never knew existed. The event calendar is a lifesaver.', avatar: 'mdi:account-circle' },
  { name: 'Meera K.', role: 'Cultural Fest Coordinator', quote: 'Managing 200+ volunteers for our cultural fest was seamless. The analytics dashboard gave us real insights.', avatar: 'mdi:account-circle' },
];

export const Testimonials = () => (
  <section className={styles.section} id="community">
    <div className={styles.container}>
      <SectionHeader 
        label="COMMUNITY"
        title="What students"
        titleAccent="are saying."
        subtitle="Hear from leaders and members who found their community on ClubConnect."
      />
      <div className={styles.grid}>
        {testimonials.map((t, i) => (
          <motion.div key={i} className={styles.card} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.12 }} whileHover={{ y: -4 }}>
            <p className={styles.quote}>"{t.quote}"</p>
            <div className={styles.author}>
              <Icon icon={t.avatar} className={styles.avatar} />
              <div>
                <strong>{t.name}</strong>
                <span>{t.role}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
);
