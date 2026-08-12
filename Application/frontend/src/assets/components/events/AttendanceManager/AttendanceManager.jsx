import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';
import { eventsApi } from '../../../../api';
import { useToast } from '../../../../context/ToastContext';
import { useSession } from '../../../../context/SessionContext';
import { Button } from '../../ui/Button/Button';
import { EmptyState } from '../../ui/EmptyState/EmptyState';
import styles from './AttendanceManager.module.css';

const AttendanceManager = ({ eventId, clubId, onClose }) => {
  const [registrations, setRegistrations] = useState([]);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const { user } = useSession();
  const currentUserId = user?.id;
  const { addToast } = useToast();

  useEffect(() => {
    fetchData(true);
  }, [eventId]);

  const fetchData = async (showLoader = true) => {
    try {
      if (showLoader) setLoading(true);
      // Fetch registrations
      const [regsRaw, externalRegsRaw] = await Promise.all([
        eventsApi.getEventRegistrations(eventId),
        eventsApi.getExternalParticipants(eventId)
      ]);
      
      const regs = Array.isArray(regsRaw) ? regsRaw : [];
      const externalRegs = Array.isArray(externalRegsRaw) ? externalRegsRaw : [];

      // Normalize user objects — backend may return first_name/last_name instead of full_name
      const normalizeUser = (u) => {
        if (!u) return u;
        if (!u.full_name && (u.first_name || u.last_name)) {
          u.full_name = `${u.first_name || ''} ${u.last_name || ''}`.trim();
        }
        return u;
      };

      // Combine internal and external registrations
      const combinedRegs = [
        ...regs.map(r => ({ ...r, user: normalizeUser(r.user), isExternal: false })),
        ...externalRegs.map(r => ({ ...r, isExternal: true, user: { id: `ext_${r.id}`, full_name: r.name || 'External', email: r.email } }))
      ];
      
      setRegistrations(combinedRegs);

      // Fetch attendance records
      const recordsRaw = await eventsApi.getEventAttendance(eventId);
      setAttendanceRecords(Array.isArray(recordsRaw) ? recordsRaw : []);
    } catch (err) {
      console.error(err);
      addToast('Failed to load attendance data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async (userId) => {
    try {
      await eventsApi.checkInUser(eventId, userId, currentUserId);
      addToast('User checked in successfully', 'success');
      await fetchData(false); // Refresh without full loader
    } catch (err) {
      console.error(err);
      addToast('Failed to check in user', 'error');
    }
  };

  const handleUndoCheckIn = async (recordId) => {
    try {
      await eventsApi.undoCheckIn(recordId);
      addToast('Check-in removed', 'success');
      await fetchData(false);
    } catch (err) {
      console.error(err);
      addToast('Failed to remove check-in', 'error');
    }
  };

  const checkedInCount = attendanceRecords.length;
  const totalCount = registrations.length;

  if (loading) {
    return <div className={styles.loading}>Loading attendance data...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h3>Manage Attendance</h3>
          <div className={styles.stats}>
            {checkedInCount} / {totalCount} Checked In
          </div>
        </div>
        <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
          <Icon icon={uiIcons.close} />
        </button>
      </div>

      {registrations.length === 0 ? (
        <EmptyState 
          icon={uiIcons.groupOutline} 
          title="No registrations yet" 
          description="There are no users registered for this event." 
        />
      ) : (
        <div className={styles.rosterList}>
          {registrations.map(reg => {
            const user = reg.user;
            if (!user) return null; // Safety check

            const record = attendanceRecords.find(r => String(r.user_id) === String(user.id));
            const isCheckedIn = !!record;

            return (
              <div key={user.id} className={styles.rosterItem}>
                <div className={styles.userInfo}>
                  <div className={styles.avatar}>
                    {user.avatar ? (
                      <img src={user.avatar} alt={user.full_name || ''} />
                    ) : (
                      (user.full_name || '?').charAt(0).toUpperCase()
                    )}
                  </div>
                  <div className={styles.userDetails}>
                    <span className={styles.userName}>
                      {user.full_name || 'Unknown'} {reg.isExternal && '(External)'}
                    </span>
                    <span className={styles.userEmail}>{user.email}</span>
                  </div>
                </div>
                
                <div className={styles.actionArea}>
                  {isCheckedIn ? (
                    <div className={styles.checkInStatus}>
                      <Icon icon={uiIcons.checkCircle} width="20" />
                      Checked In
                      <button 
                        className={styles.undoBtn}
                        onClick={() => handleUndoCheckIn(record.id)}
                      >
                        Undo
                      </button>
                    </div>
                  ) : (
                    <Button 
                      variant="primary" 
                      onClick={() => handleCheckIn(user.id)}
                    >
                      Check In
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default AttendanceManager;
