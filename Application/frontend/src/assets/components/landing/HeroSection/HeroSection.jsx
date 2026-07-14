import React from 'react';
import { Link } from 'react-router-dom';
import styles from './HeroSection.module.css';
import { Button } from '../../ui/Button/Button';
import { motion } from 'framer-motion';
import { landingIcons } from '../../../icons/registry';
import { Icon } from '@iconify/react';
import roboticsBanner from '../../../images/robotics_banner.png';
import { useSession, getDashboardLink } from '../../../../context/SessionContext';

export const HeroSection = () => {
  const { user } = useSession();
  return (
    <section className={styles.hero}>
      <div className={styles.orb1} />
      <div className={styles.orb2} />
      <div className={styles.orb3} />

      {/* Visual column moved to cardsSide to act as floating bubbles around the cards */}

      <div className={styles.heroInner}>
        {/* LEFT — Text content */}
        <div className={styles.textSide}>
          <motion.div className={styles.liveBadge} initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <span className={styles.liveDot} /> Your campus is live with new activities today
          </motion.div>

          <motion.h1 className={styles.title} initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
            Where every <span className={styles.accent}>passion</span> finds its club.
          </motion.h1>

          <motion.p className={styles.subtitle} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.2 }}>
            Discover communities, build friendships, organize events and create unforgettable campus experiences.
          </motion.p>

          <motion.div className={styles.actions} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.4 }}>
            <div className={styles.ctaGroup}>
              <Link to={user ? getDashboardLink(user.role) : "/register"}>
                <Button size="lg" icon={landingIcons.compass} className={styles.glowBtn}>Explore campus</Button>
              </Link>
              <Link to={user ? getDashboardLink(user.role) : "/register"}>
                <Button variant="outline" size="lg">Join ClubConnect <Icon icon={landingIcons.arrowRight} /></Button>
              </Link>
            </div>
          </motion.div>
        </div>

        {/* RIGHT — Floating glass cards stack */}
        <div className={styles.cardsSide}>
          {/* Floating Bubble Icons */}
          <div className={`${styles.floater} ${styles.f1}`}><Icon icon={landingIcons.heroCamera} /></div>
          <div className={`${styles.floater} ${styles.f2}`}><Icon icon={landingIcons.heroMusic} /></div>
          <div className={`${styles.floater} ${styles.f3}`}><Icon icon={landingIcons.heroCode} /></div>
          <div className={`${styles.floater} ${styles.f4}`}><Icon icon={landingIcons.heroRobot} /></div>

          <motion.div className={styles.floatCard} style={{ top: '0px', right: '15%', zIndex: 3 }} initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0, y: [0, -10, 0] }} transition={{ duration: 0.8, delay: 0.5, y: { duration: 5, repeat: Infinity, ease: 'easeInOut' } }}>
            <div className={styles.fcItem}>
              <Icon icon={landingIcons.heroLightning} className={styles.fcIcon} style={{ color: 'var(--campus-orange)' }} />
              <span>Shaastra Hackathon</span>
            </div>
            <p className={styles.fcSub}>36-hour build sprint</p>
            <div className={styles.fcMeta}>
              <div className={styles.avatarGroup}>
                <span className={styles.dot} style={{ background: '#e74c3c' }} />
                <span className={styles.dot} style={{ background: '#f39c12' }} />
                <span className={styles.dot} style={{ background: '#3498db' }} />
              </div>
              <span>340 registered</span>
            </div>
            <div className={styles.fcTimer}>
              <span>Starts in</span>
              <div className={styles.countdown}><span>02</span>:<span>14</span></div>
            </div>
          </motion.div>

          <motion.div className={styles.floatCard} style={{ top: '180px', right: '0', zIndex: 5 }} initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0, y: [0, -8, 0] }} transition={{ duration: 0.8, delay: 0.7, y: { duration: 4.5, repeat: Infinity, ease: 'easeInOut', delay: 1 } }}>
            <div className={styles.fcLabel}>Trending club</div>
            <h4>Robotics Club</h4>
            <div className={styles.fcGradientBar} style={{ backgroundImage: `url(${roboticsBanner})`, backgroundSize: 'cover', backgroundPosition: 'center' }} />
            <span className={styles.fcSmall}>+124 this week</span>
          </motion.div>

          <motion.div className={styles.floatCard} style={{ top: '340px', right: '8%', zIndex: 4 }} initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0, y: [0, -6, 0] }} transition={{ duration: 0.8, delay: 0.9, y: { duration: 5.5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 } }}>
            <div className={styles.fcItem}>
              <Icon icon={landingIcons.heroMusicCircle} className={styles.fcIcon} style={{ color: 'var(--soft-purple)' }} />
              <div>
                <strong>Open Mic Night</strong>
                <p className={styles.fcSub}>Music Club · Friday, 7pm</p>
              </div>
            </div>
            <div className={styles.fcSeats}>
              <div className={styles.seatBar}><div className={styles.seatFill} /></div>
              <span>37 OF 50 SEATS</span>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
