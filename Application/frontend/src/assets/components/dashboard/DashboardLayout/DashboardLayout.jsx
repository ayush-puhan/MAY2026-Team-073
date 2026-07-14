import React, { useState, useEffect } from 'react';
import styles from './DashboardLayout.module.css';
import { Sidebar } from '../Sidebar/Sidebar';
import { DashboardHeader } from '../DashboardHeader/DashboardHeader';
import { authApi } from '../../../../api/auth.api';
import { useSession } from '../../../../context/SessionContext';

import { SidebarProvider, useSidebarContext } from '../../../../context/SidebarContext';

const DashboardLayoutContent = ({ children, title, user, sidebarLinks, isInitializing }) => {
  const { isSidebarOpen } = useSidebarContext();
  
  if (isInitializing) {
    return (
      <div className={styles.layout} data-colorblind={user?.color_blind_mode ? "true" : undefined}>
        <div className={styles.loadingScreen}>
          <div className={styles.spinner}></div>
          <p>Loading Dashboard Workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.layout} data-colorblind={user?.color_blind_mode ? "true" : undefined}>
      <Sidebar links={sidebarLinks} />
      <div className={`${styles.mainContent} ${!isSidebarOpen ? styles.collapsed : ''}`}>
        <DashboardHeader title={title} user={user} />
        <main className={styles.pageContent}>
          {children}
        </main>
      </div>
    </div>
  );
};

export const DashboardLayout = ({ children, title, user, sidebarLinks }) => {
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
        const fullUser = await authApi.getFullProfile(user.id);
        if (isMounted) {
          updateUser(fullUser);
          localStorage.setItem('user', JSON.stringify(fullUser));
        }
      } catch (err) {
        console.error("Failed to fetch full profile on dashboard mount", err);
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
