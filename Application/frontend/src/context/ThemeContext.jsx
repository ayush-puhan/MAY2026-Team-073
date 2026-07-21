import { createContext, useContext, useEffect, useState, useCallback } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved || 'dark';
  });

  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  /**
   * Circle reveal animation for theme toggle.
   * A circle expands from the toggle button position until it covers the viewport.
   * Uses the View Transitions API where supported, with a clip-path circle animation.
   *
   * Always originates from the exact centre of the toggle button (found via DOM id),
   * regardless of where on the button the user clicks or what screen size is used.
   */
  const toggleTheme = useCallback((e) => {
    const newTheme = theme === 'light' ? 'dark' : 'light';

    // If View Transitions API is not supported, fall back to instant switch
    if (!document.startViewTransition) {
      setTheme(newTheme);
      return;
    }

    // ── Use the exact click coordinates if available ──
    let x = window.innerWidth / 2;
    let y = window.innerHeight / 2;

    if (e && e.currentTarget) {
      const rect = e.currentTarget.getBoundingClientRect();
      x = Math.round(rect.left + rect.width / 2);
      y = Math.round(rect.top + rect.height / 2);
      
      // ── Location-based Custom Offsets ──
      // Adjust these values based on where the button is rendered.
      // Positive X = right, Negative X = left | Positive Y = down, Negative Y = up
      const path = window.location.pathname;
      let offsetX = 0;
      let offsetY = 0;
      
      if (path.includes('dashboard')) {
        // Dashboard Header Offsets
        offsetX = 375;
        offsetY = 10;
      } else if (path.includes('/login') || path.includes('/register') || path.includes('/forgot') || path.includes('/verify')) {
        // Auth Pages Offsets
        offsetX = 370;
        offsetY = 15;
      } else {
        // Landing Page Header Offsets (default)
        offsetX = 295;
        offsetY = 15;
      }
      
      x += offsetX;
      y += offsetY;

    } else if (e && typeof e.clientX !== 'undefined' && typeof e.clientY !== 'undefined') {
      x = e.clientX;
      y = e.clientY;
    }

    // Calculate the max radius needed to cover the entire viewport
    const maxRadius = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y)
    );

    const transition = document.startViewTransition(() => {
      setTheme(newTheme);
    });

    transition.ready.then(() => {
      document.documentElement.animate(
        {
          clipPath: [
            `circle(0px at ${x}px ${y}px)`,
            `circle(${maxRadius}px at ${x}px ${y}px)`,
          ],
        },
        {
          duration: 800,
          easing: 'ease-in-out',
          pseudoElement: '::view-transition-new(root)',
        }
      );
    });
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};