import React, { useState, useEffect } from 'react';
import styles from './Header.module.css';
import { Logo } from '../../ui/Logo/Logo';
import { ThemeToggle } from '../../ui/ThemeToggle/ThemeToggle';
import { Button } from '../../ui/Button/Button';
import { Link } from 'react-router-dom';
import { useSession, getDashboardLink } from '../../../../context/SessionContext';

export const Header = () => {
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const { user } = useSession();

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      
      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        setIsVisible(false);
      } else {
        setIsVisible(true);
      }
      
      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  return (
    <header className={`${styles.header} ${isVisible ? '' : styles.hidden}`}>
      <div className={styles.container}>
        <Logo size="lg" />
        <nav className={styles.nav}>
          <a href="#clubs" onClick={(e) => { e.preventDefault(); document.getElementById('clubs')?.scrollIntoView({ behavior: 'smooth' }); }} className={styles.navLink}>Clubs</a>
          <a href="#events" onClick={(e) => { e.preventDefault(); document.getElementById('events')?.scrollIntoView({ behavior: 'smooth' }); }} className={styles.navLink}>Events</a>
          <a href="#community" onClick={(e) => { e.preventDefault(); document.getElementById('community')?.scrollIntoView({ behavior: 'smooth' }); }} className={styles.navLink}>Community</a>
          <a href="#about" onClick={(e) => { e.preventDefault(); document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' }); }} className={styles.navLink}>About</a>
        </nav>
        <div className={styles.actions}>
          <ThemeToggle />
          {user ? (
            <Link to={getDashboardLink(user.role)}><Button variant="primary" size="sm" className={styles.joinBtn}>Go to Dashboard</Button></Link>
          ) : (
            <>
              <Link to="/login" className={styles.loginLink}>Sign in</Link>
              <Link to="/register"><Button variant="primary" size="sm" className={styles.joinBtn}>Join</Button></Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
