import React, { useState, useEffect } from 'react';
import styles from './DashboardLayout.module.css';
import { Sidebar } from '../Sidebar/Sidebar';
import { DashboardHeader } from '../DashboardHeader/DashboardHeader';
import { authApi } from '../../../../api/auth.api';
import { useSession } from '../../../../context/SessionContext';

import { SidebarProvider, useSidebarContext } from '../../../../context/SidebarContext';

const DashboardLayoutContent = ({ children, title, user, sidebarLinks, isInitializing }) => {
  const { isSidebarOpen } = useSidebarContext();
  
  return (
    <div className={styles.layout} data-colorblind={user?.color_blind_mode ? "true" : undefined}>
      <Sidebar links={sidebarLinks} />
      <div className={`${styles.mainContent} ${!isSidebarOpen ? styles.collapsed : ''}`}>
        <DashboardHeader title={title} user={user} />
        <main className={styles.pageContent}>
          {children}
        </main>
      </div>

      {isInitializing && (
        <div className={styles.loadingScreen}>
          <div className={styles.spinner}></div>
          <p>Loading Dashboard Workspace...</p>
        </div>
      )}
    </div>
  );
};

/**
 * DashboardLayout — wraps every dashboard page.
 * 
 * @param {Function} onLoadData - Optional async callback for page-specific data fetching.
 *   Called in parallel with getFullProfile. The loading screen stays visible until ALL 
 *   data (profile + page-specific) finishes loading. Future dashboard pages can pass 
 *   their own fetch logic here (clubs, events, stats, etc.) and it will all be covered 
 *   by one unified loading state.
 */
export const DashboardLayout = ({ children, title, user, sidebarLinks, onLoadData }) => {
  const { updateUser } = useSession();
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const initializeDashboard = async () => {
      if (!user?.id) {
        setIsInitializing(false);
        return;
      }
      try {
        // Run profile fetch + any page-specific data loading in parallel
        const tasks = [authApi.getFullProfile(user.id)];
        if (onLoadData) tasks.push(onLoadData());
        
        const [fullUser] = await Promise.all(tasks);

        if (isMounted && fullUser) {
          updateUser(fullUser);
          localStorage.setItem('user', JSON.stringify(fullUser));
        }
      } catch (err) {
        console.error("Failed to initialize dashboard", err);
      } finally {
        if (isMounted) setIsInitializing(false);
      }
    };
    
    initializeDashboard();
    return () => { isMounted = false; };
  }, [user?.id, updateUser]);

  return (
    <SidebarProvider>
      <DashboardLayoutContent 
        title={title} 
        user={user} 
        sidebarLinks={sidebarLinks} 
        isInitializing={isInitializing}
      >
        {children}
      </DashboardLayoutContent>
    </SidebarProvider>
  );
};
