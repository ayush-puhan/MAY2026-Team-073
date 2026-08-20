import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';
import { eventsApi } from '../../../../api';
import { useToast } from '../../../../context/ToastContext';
import { Button } from '../../ui/Button/Button';
import { Input } from '../../ui/Input/Input';
import { EmptyState } from '../../ui/EmptyState/EmptyState';
import styles from './SessionsManager.module.css';

const SessionsManager = ({ eventId, clubId, isCompleted }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    venue: '',
    start_at: '',
    end_at: '',
    session_order: 1
  });
  
  const { addToast } = useToast();

  useEffect(() => {
    fetchSessions();
  }, [eventId]);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const data = await eventsApi.getEventSessions(eventId);
      setSessions(data || []);
    } catch (err) {
      console.error(err);
      addToast('Failed to load sessions', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const resetForm = () => {
    setEditingSessionId(null);
    setFormData({
      title: '',
      description: '',
      venue: '',
      start_at: '',
      end_at: '',
      session_order: sessions.length + 1
    });
  };

  const handleEditClick = (session) => {
    setEditingSessionId(session.id);
    setFormData({
      title: session.title || '',
      description: session.description || '',
      venue: session.venue || '',
      start_at: session.start_at ? new Date(session.start_at).toISOString().slice(0, 16) : '',
      end_at: session.end_at ? new Date(session.end_at).toISOString().slice(0, 16) : '',
      session_order: session.session_order || 1
    });
  };

  const handleSave = async () => {
    if (!formData.title || !formData.start_at || !formData.end_at) {
      addToast('Title, start time, and end time are required', 'warning');
      return;
    }

    try {
      if (editingSessionId) {
        await eventsApi.updateEventSession(editingSessionId, formData);
        addToast('Session updated successfully', 'success');
      } else {
        await eventsApi.createEventSessions(eventId, [formData]);
        addToast('Session added successfully', 'success');
      }
      resetForm();
      fetchSessions();
    } catch (err) {
      console.error(err);
      addToast('Failed to save session', 'error');
    }
  };

  const handleDelete = async (sessionId) => {
    if (!window.confirm('Are you sure you want to delete this session?')) return;
    
    try {
      await eventsApi.deleteEventSession(sessionId);
      addToast('Session deleted', 'success');
      fetchSessions();
    } catch (err) {
      console.error(err);
      addToast('Failed to delete session', 'error');
    }
  };

  if (loading) {
    return <div className={styles.loading}>Loading sessions...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.sessionsList}>
        {sessions.length === 0 ? (
          <EmptyState 
            icon={uiIcons.calendarOutline} 
            title="No sessions" 
            description="Add sessions to build out the event agenda." 
          />
        ) : (
          sessions.map((session, index) => (
            <div key={session.id || index} className={styles.sessionCard}>
              <div className={styles.sessionInfo}>
                <h4>{session.title}</h4>
                {session.venue && <p className={styles.venue}><Icon icon="mdi:map-marker" /> {session.venue}</p>}
                <p className={styles.time}>
                  {new Date(session.start_at).toLocaleString()} - {new Date(session.end_at).toLocaleString()}
                </p>
                {session.description && <p className={styles.description}>{session.description}</p>}
              </div>
              {!isCompleted && (
                <div className={styles.sessionActions}>
                  <Button variant="outline" size="small" onClick={() => handleEditClick(session)}>Edit</Button>
                  <Button variant="outline" size="small" style={{ borderColor: 'var(--destructive)', color: 'var(--destructive)' }} onClick={() => handleDelete(session.id)}>Delete</Button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {!isCompleted && (
        <div className={styles.formContainer}>
          <h3>{editingSessionId ? 'Edit Session' : 'Add New Session'}</h3>
          <div className={styles.formGrid}>
            <Input 
              label="Title *"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
            />
            <Input 
              label="Order"
              name="session_order"
              type="number"
              value={formData.session_order}
              onChange={handleInputChange}
            />
            <Input 
              label="Start Time *"
              name="start_at"
              type="datetime-local"
              value={formData.start_at}
              onChange={handleInputChange}
            />
            <Input 
              label="End Time *"
              name="end_at"
              type="datetime-local"
              value={formData.end_at}
              onChange={handleInputChange}
            />
            <div style={{ gridColumn: '1 / -1' }}>
              <Input 
                label="Venue"
                name="venue"
                value={formData.venue}
                onChange={handleInputChange}
              />
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <label className={styles.label}>Description</label>
              <textarea
                className={styles.textarea}
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={3}
              />
            </div>
          </div>
          <div className={styles.formActions}>
            {editingSessionId && (
              <Button variant="outline" onClick={resetForm}>Cancel</Button>
            )}
            <Button onClick={handleSave}>{editingSessionId ? 'Update Session' : 'Add Session'}</Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionsManager;
