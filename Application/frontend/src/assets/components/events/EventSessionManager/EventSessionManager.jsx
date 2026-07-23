import React, { useState } from 'react';
import { Button } from '../../ui/Button/Button';
import { Input } from '../../ui/Input/Input';
import { Icon } from '@iconify/react';
import { uiIcons, calendarIcons } from '../../../icons/registry';
import styles from './EventSessionManager.module.css';

/**
 * EventSessionManager
 * 
 * Component to manage Event Sessions within an Event Creation or Edit form.
 * It passes the sessions array up to the parent form to be submitted along with the main Event data.
 * 
 * @param {Array} sessions - The list of session objects
 * @param {Function} setSessions - State setter for the sessions array
 * @param {Date} eventStart - Minimum start date allowed (based on parent event)
 * @param {Date} eventEnd - Maximum end date allowed (based on parent event)
 */
export const EventSessionManager = ({ sessions = [], setSessions, eventStart, eventEnd }) => {

  const [editingSession, setEditingSession] = useState(null);

  const openNewSessionModal = () => {
    setEditingSession({
      id: Date.now(), // temporary ID for frontend keying
      title: '',
      description: '',
      venue: '',
      start_at: '',
      end_at: '',
      session_order: sessions.length + 1,
      isNew: true
    });
  };

  const removeSession = (id) => {
    setSessions(sessions.filter(s => s.id !== id).map((s, index) => ({
      ...s,
      session_order: index + 1 // Recompute order
    })));
  };

  const moveSession = (index, direction) => {
    if ((direction === -1 && index === 0) || (direction === 1 && index === sessions.length - 1)) return;
    
    const newSessions = [...sessions];
    const temp = newSessions[index];
    newSessions[index] = newSessions[index + direction];
    newSessions[index + direction] = temp;
    
    // Update orders
    setSessions(newSessions.map((s, i) => ({ ...s, session_order: i + 1 })));
  };

  const handleSaveSession = (e) => {
    e.preventDefault();
    if (editingSession.isNew) {
      const { isNew, ...sessionData } = editingSession;
      setSessions([...sessions, sessionData]);
    } else {
      setSessions(sessions.map(s => s.id === editingSession.id ? editingSession : s));
    }
    setEditingSession(null);
  };

  return (
    <div className={styles.managerContainer}>
      <div className={styles.header}>
        <h3>Event Sessions</h3>
        <button type="button" className={styles.addBtn} onClick={openNewSessionModal}>
          <Icon icon={calendarIcons.addSession} width="18" />
          Add Session
        </button>
      </div>

      <div className={styles.sessionList}>
        {sessions.length === 0 ? (
          <div className={styles.emptyState}>
            No sessions added yet. An event must have at least one session.
          </div>
        ) : (
          sessions.map((session, index) => (
            <div key={session.id} className={styles.sessionCard}>
              <div className={styles.sessionHeader}>
                <div className={styles.sessionTitleGroup}>
                  <span className={styles.sessionOrder}>Session {session.session_order}</span>
                  <span className={styles.sessionTitle}>{session.title}</span>
                </div>
                <div className={styles.actions}>
                  <button 
                    type="button"
                    className={styles.iconBtn} 
                    onClick={() => moveSession(index, -1)}
                    disabled={index === 0}
                    title="Move Up"
                  >
                    <Icon icon={uiIcons.arrowUp} width="18" />
                  </button>
                  <button 
                    type="button"
                    className={styles.iconBtn} 
                    onClick={() => moveSession(index, 1)}
                    disabled={index === sessions.length - 1}
                    title="Move Down"
                  >
                    <Icon icon={uiIcons.arrowDown} width="18" />
                  </button>
                  <button 
                    type="button"
                    className={styles.iconBtn} 
                    onClick={() => setEditingSession(session)}
                    title="Edit Session"
                  >
                    <Icon icon="mdi:pencil" width="18" />
                  </button>
                  <button 
                    type="button"
                    className={`${styles.iconBtn} ${styles.deleteBtn}`} 
                    onClick={() => removeSession(session.id)}
                    title="Delete Session"
                  >
                    <Icon icon={uiIcons.deleteOutline} width="18" />
                  </button>
                </div>
              </div>
              <div className={styles.sessionSummary}>
                <div className={styles.summaryRow}>
                  <Icon icon="mdi:calendar-clock" />
                  <span>{new Date(session.start_at).toLocaleString()} - {new Date(session.end_at).toLocaleString()}</span>
                </div>
                {session.venue && (
                  <div className={styles.summaryRow}>
                    <Icon icon="mdi:map-marker" />
                    <span>{session.venue}</span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {editingSession && (
        <div className={styles.modalOverlay} onClick={() => setEditingSession(null)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.nestedFormDiv}>
              <div className={styles.modalHeader}>
                <h3>{editingSession.isNew ? 'Add Session' : 'Edit Session'}</h3>
                <button type="button" className={styles.closeBtn} onClick={() => setEditingSession(null)}>
                  <Icon icon={uiIcons.close} />
                </button>
              </div>

              <div className={styles.modalBody}>
                <Input
                  label="Session Title *"
                  type="text" 
                  value={editingSession.title} 
                  onChange={e => setEditingSession({...editingSession, title: e.target.value})} 
                  placeholder="e.g. Opening Keynote"
                  required
                />
                
                <div className={styles.formGrid}>
                  <Input
                    label="Start Date & Time *"
                    type="datetime-local" 
                    value={editingSession.start_at} 
                    onChange={e => setEditingSession({...editingSession, start_at: e.target.value})} 
                    min={eventStart}
                    max={editingSession.end_at || eventEnd}
                    required
                  />
                  <Input
                    label="End Date & Time *"
                    type="datetime-local" 
                    value={editingSession.end_at} 
                    onChange={e => setEditingSession({...editingSession, end_at: e.target.value})} 
                    min={editingSession.start_at || eventStart}
                    max={eventEnd}
                    required
                  />
                </div>

                <Input
                  label="Venue / Location"
                  type="text" 
                  value={editingSession.venue} 
                  onChange={e => setEditingSession({...editingSession, venue: e.target.value})} 
                  placeholder="e.g. Main Auditorium (Leave blank to use parent event venue)"
                />

                <Input
                  label="Description"
                  as="textarea"
                  rows="3"
                  value={editingSession.description} 
                  onChange={e => setEditingSession({...editingSession, description: e.target.value})} 
                  placeholder="Details about this specific session..."
                />
              </div>

              <div className={styles.modalActions}>
                <Button variant="outline" onClick={() => setEditingSession(null)}>Cancel</Button>
                <Button variant="primary" onClick={handleSaveSession}>
                  {editingSession.isNew ? 'Add Session' : 'Save Session'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
