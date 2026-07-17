import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import styles from './AuthLayout.module.css';
import { motion } from 'framer-motion';
import { Icon } from '@iconify/react';
import { Logo } from '../../ui/Logo/Logo';
import { ThemeToggle } from '../../ui/ThemeToggle/ThemeToggle';
import { uiIcons } from '../../../icons/registry';

const floatingCards = [
  { icon: 'mdi:trophy-outline', color: 'var(--primary)', title: 'Shaastra Hackathon', sub: '340 registered • starts Fri 9AM' },
  { icon: 'mdi:account-group', color: 'var(--campus-orange)', title: 'Robotics recruiting', sub: 'Round 1 open • 124 applied' },
  { icon: 'mdi:medal', color: 'var(--achievement)', title: 'Ananya K. — SIH Winner', sub: 'Represented in National Hackathon' },
  { icon: 'mdi:music-note', color: 'var(--campus-orange)', title: 'Open Mic Night', sub: '37 / 50 seats • Friday' },
];

export const AuthLayout = ({ children }) => {
  const [glowPos, setGlowPos] = useState({ x: 0, y: 0, visible: false });

  const handleMouseMove = useCallback((e) => {
    setGlowPos({ x: e.clientX, y: e.clientY, visible: true });
  }, []);

  const handleMouseLeave = useCallback(() => {
    setGlowPos(prev => ({ ...prev, visible: false }));
  }, []);

  return (
    <div className={styles.container}>
      <div className={styles.leftPane}>
        <div className={styles.orbPrimary} />
        <div className={styles.orbGold} />
        <div className={styles.orbBlue} />

        <div className={styles.logoWrapper}>
          <Logo size="md" />
        </div>

        <div className={styles.leftContent}>

          <motion.div className={styles.heroText} initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
            <h1>Step into a<br /><span className={styles.heroAccent}>living campus.</span></h1>
            <p className={styles.heroSub}>Discover all the clubs, events, and friends you haven't met yet — all one login away.</p>
          </motion.div>

          <motion.div className={styles.cardsGrid} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.3 }}>
            {floatingCards.map((card, i) => (
              <motion.div key={i} className={styles.glassCard} whileHover={{ y: -3, scale: 1.02 }} transition={{ type: 'spring', stiffness: 300 }}>
                <div className={styles.cardIcon} style={{ backgroundColor: `color-mix(in oklab, ${card.color} 20%, transparent)`, color: card.color }}>
                  <Icon icon={card.icon} />
                </div>
                <div className={styles.cardText}>
                  <span className={styles.cardTitle}>{card.title}</span>
                  <span className={styles.cardSub}>{card.sub}</span>
                </div>
              </motion.div>
            ))}
          </motion.div>

          <motion.p className={styles.testimonial} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
            "ClubConnect made my first semester feel like home." — Meera, EE'27
          </motion.p>
        </div>
      </div>

      <div className={styles.rightPane} onMouseMove={handleMouseMove} onMouseLeave={handleMouseLeave}>
        <div
          className={`${styles.cursorGlow} ${glowPos.visible ? styles.visible : ''}`}
          style={{ left: glowPos.x, top: glowPos.y }}
        />
        <div className={styles.topBar}>
          <Link to="/" className={styles.backLink}>
            <Icon icon={uiIcons.arrowLeft} className={styles.backIcon} />
            Back to campus
          </Link>
          <ThemeToggle />
        </div>
        <div className={styles.formArea}>
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }} className={styles.formWrapper}>
            {children}
          </motion.div>
        </div>
      </div>
    </div>
  );
};
