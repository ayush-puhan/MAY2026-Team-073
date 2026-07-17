import React, { useState } from 'react';
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

  const addSession = () => {
    const newSession = {
      id: Date.now(), // temporary ID for frontend keying
      title: '',
      description: '',
      venue: '',
      start_at: '',
      end_at: '',
      session_order: sessions.length + 1
    };
    setSessions([...sessions, newSession]);
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

  const handleSessionChange = (id, field, value) => {
    setSessions(sessions.map(s => s.id === id ? { ...s, [field]: value } : s));
  };

  return (
    <div className={styles.managerContainer}>
      <div className={styles.header}>
        <h3>Event Sessions</h3>
        <button type="button" className={styles.addBtn} onClick={addSession}>
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
                <span className={styles.sessionOrder}>Session {session.session_order}</span>
                <div className={styles.actions}>
                  <button 
                    type="button"
                    className={styles.iconBtn} 
                    onClick={() => moveSession(index, -1)}
                    disabled={index === 0}
                    title="Move Up"
                  >
                    <Icon icon="mdi:arrow-up" width="18" />
                  </button>
                  <button 
                    type="button"
                    className={styles.iconBtn} 
                    onClick={() => moveSession(index, 1)}
                    disabled={index === sessions.length - 1}
                    title="Move Down"
                  >
                    <Icon icon="mdi:arrow-down" width="18" />
                  </button>
                  <button 
                    type="button"
                    className={`${styles.iconBtn} ${styles.deleteBtn}`} 
                    onClick={() => removeSession(session.id)}
                    title="Delete Session"
                  >
                    <Icon icon="mdi:delete-outline" width="18" />
                  </button>
                </div>
              </div>

              <div className={styles.formGrid}>
                <div className={`${styles.formGroup} ${styles.fullWidth}`}>
                  <label>Session Title *</label>
                  <input 
                    type="text" 
                    value={session.title} 
                    onChange={e => handleSessionChange(session.id, 'title', e.target.value)} 
                    placeholder="e.g. Opening Keynote"
                    required
                  />
                </div>
                
                <div className={styles.formGroup}>
                  <label>Start Date & Time *</label>
                  <input 
                    type="datetime-local" 
                    value={session.start_at} 
                    onChange={e => handleSessionChange(session.id, 'start_at', e.target.value)} 
                    min={eventStart}
                    max={session.end_at || eventEnd}
                    required
                  />
                </div>

                <div className={styles.formGroup}>
                  <label>End Date & Time *</label>
                  <input 
                    type="datetime-local" 
                    value={session.end_at} 
                    onChange={e => handleSessionChange(session.id, 'end_at', e.target.value)} 
                    min={session.start_at || eventStart}
                    max={eventEnd}
                    required
                  />
                </div>

                <div className={`${styles.formGroup} ${styles.fullWidth}`}>
                  <label>Venue / Location</label>
                  <input 
                    type="text" 
                    value={session.venue} 
                    onChange={e => handleSessionChange(session.id, 'venue', e.target.value)} 
                    placeholder="e.g. Main Auditorium (Leave blank to use parent event venue)"
                  />
                </div>

                <div className={`${styles.formGroup} ${styles.fullWidth}`}>
                  <label>Description</label>
                  <textarea 
                    value={session.description} 
                    onChange={e => handleSessionChange(session.id, 'description', e.target.value)} 
                    placeholder="Details about this specific session..."
                  />
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
