import { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { calendarIcons, uiIcons } from '../../../icons/registry';
import { calendarApi } from '../../../../api';
import { useToast } from '../../../../context/ToastContext';
import { Dropdown } from '../../ui/Dropdown/Dropdown';
import { ContextPanel } from '../../ui/ContextPanel/ContextPanel';
import styles from './CalendarContextPanel.module.css';

const CalendarContextPanel = ({ filters, setFilters, user }) => {
  const [syncing, setSyncing] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  const { showSuccess, showError, showInfo } = useToast();

  const isGoogleAuth = user?.auth_provider === 'google' || user?.google_signed_in;

  const handleSync = async () => {
    if (!isGoogleAuth) {
      showInfo("Feature coming soon!");
      return;
    }

    setSyncing(true);
    try {
      await calendarApi.syncToGoogleCalendar(user.id);
      showSuccess("Calendar synced with Google successfully!");
    } catch (err) {
      showError("Failed to sync with Google Calendar.");
    } finally {
      setSyncing(false);
    }
  };

  const handleSearchChange = (e) => {
    setFilters(prev => ({ ...prev, searchQuery: e.target.value }));
  };

  const handlePublicToggle = (e) => {
    setFilters(prev => ({ ...prev, show_public: e.target.checked }));
  };

  const handleUniversityChange = (e) => {
    setFilters(prev => ({ ...prev, university_id: e.target.value }));
  };

  const handleClubChange = (e) => {
    setFilters(prev => ({ ...prev, club_id: e.target.value }));
  };

  return (
    <ContextPanel>
      <div className={styles.panelHeader}>
        <h2>Calendar</h2>
        {isGoogleAuth ? (
          <button 
            className={`${styles.syncBtn} ${syncing ? styles.syncing : ''}`} 
            onClick={handleSync}
            title="Sync with Google Calendar"
          >
            <Icon icon={calendarIcons.googleSync} width="20" height="20" />
          </button>
        ) : (
          <button 
            className={styles.syncBtnWithText}
            onClick={handleSync}
            title="Sign in with Google to enable Sync"
          >
            <Icon icon={calendarIcons.googleSync} width="16" height="16" />
            <span>Sign in to Sync</span>
          </button>
        )}
      </div>

      <div className={styles.controlsWrapper}>
        <div className={styles.searchBox}>
          <Icon icon={uiIcons.search} className={styles.searchIcon} width="20" />
          <input 
            type="text" 
            placeholder="Search events, clubs..." 
            value={filters.searchQuery}
            onChange={handleSearchChange}
          />
        </div>

        <div className={styles.filterSection}>
          <h3 className={styles.filterHeading}>Filters</h3>
          
          <div className={styles.filterControls}>
            {(() => {
              const hasUniversity = !!user?.university_id;

              return (
                <>
                  <div className={styles.toggleRow}>
                    <span className={styles.toggleLabel}>Show Public Events</span>
                <label className={styles.switch}>
                  <input 
                    type="checkbox" 
                    checked={filters.show_public} 
                    onChange={handlePublicToggle} 
                  />
                  <span className={styles.slider}></span>
                </label>
              </div>

              {/* University filter is ONLY shown to users with a university when exploring public events */}
              {hasUniversity && filters.show_public && (
                <div className={styles.selectGroup}>
                  <label>University</label>
                  <Dropdown 
                    value={filters.university_id} 
                    onChange={handleUniversityChange}
                    options={[
                      { value: '', label: 'All Universities' },
                      { value: '1', label: 'IIT Delhi' },
                      { value: '2', label: 'BITS Pilani' }
                    ]}
                    placeholder="All Universities"
                  />
                </div>
              )}

              {/* Club filter is ONLY shown to users with a university */}
              {hasUniversity && (
                <div className={styles.selectGroup}>
                  <label>Club</label>
                  {(() => {
                    const allClubs = [
                      { value: '1', label: 'Robotics Club', university_id: '1' },
                      { value: '2', label: 'Photography Club', university_id: '1' },
                      { value: '3', label: 'Music Society', university_id: '2' }
                    ];

                    const filteredClubs = filters.university_id 
                      ? allClubs.filter(c => c.university_id === filters.university_id)
                      : allClubs;

                    const clubOptions = [
                      { value: '', label: 'All Clubs' },
                      ...filteredClubs.map(c => ({ value: c.value, label: c.label }))
                    ];

                    return (
                      <Dropdown 
                        value={filters.club_id} 
                        onChange={handleClubChange}
                        options={clubOptions}
                        placeholder="All Clubs"
                        disabled={filters.show_public && !filters.university_id}
                      />
                    );
                  })()}
                </div>
              )}

              <div className={`${styles.selectGroup} ${styles.mobileViewSelector}`}>
                <label>View Mode</label>
                <Dropdown 
                  value={filters.calendarView || 'month'}
                  onChange={(e) => setFilters(prev => ({ ...prev, calendarView: e.target.value }))}
                  options={[
                    { value: 'month', label: 'Month' },
                    { value: 'week', label: 'Week' },
                    { value: 'day', label: 'Day' },
                    { value: 'agenda', label: 'Agenda' }
                  ].filter(opt => !isMobile || (opt.value === 'day' || opt.value === 'agenda'))}
                  placeholder="Select view"
                />
              </div>
            </>
          );
        })()}
          </div>
        </div>
      </div>
    </ContextPanel>
  );
};

export default CalendarContextPanel;

