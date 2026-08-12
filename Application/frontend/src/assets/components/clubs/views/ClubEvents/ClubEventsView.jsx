import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { useToast } from '../../../../../context/ToastContext';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/backendApis/clubsApis/clubs';
import { eventsApi } from '../../../../../api';
import { canManageEvents, canApproveEvents, canManageAttendance } from '../../../../../utils/clubPermissions';
import styles from './ClubEventsView.module.css';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import { Button } from '../../../ui/Button/Button';
import { EmptyState } from '../../../ui/EmptyState/EmptyState';
import { Input } from '../../../ui/Input/Input';
import { EventSessionManager } from '../../../../components/events/EventSessionManager/EventSessionManager';
import AttendanceManager from '../../../events/AttendanceManager/AttendanceManager';
import SessionsManager from '../../../events/SessionsManager/SessionsManager';
import EventFormWizard from '../../../events/EventForm/EventFormWizard';
import { uiIcons, dashboardIcons } from '../../../../icons/registry';

const ClubEventsView = () => {
  const { club, userRole, currentUserId } = useOutletContext();
  const { showSuccess, showError } = useToast();

  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingEventId, setEditingEventId] = useState(null);
  const [newEvent, setNewEvent] = useState({
    title: '',
    description: '',
    sponsors: '',
    banner: '',
    venue: '',
    is_public: false,
    requires_external_participants: false,
    start_at: '',
    end_at: '',
    registration_deadline: ''
  });

  const [sessions, setSessions] = useState([]);
  const [manageEventId, setManageEventId] = useState(null);
  const [manageTab, setManageTab] = useState('attendance');

  useEffect(() => {
    fetchEvents();
  }, [club.id]);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const data = await clubsApi.getClubEvents(club.id);
      setEvents(data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to load events.');
      showError('Failed to load events.');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (eventId) => {
    try {
      await clubsApi.approveEvent(eventId, currentUserId);
      await fetchEvents();
      showSuccess('Event approved');
    } catch (err) {
      showError(err.message || 'Failed to approve event');
    }
  };

  const handleReject = async (eventId) => {
    try {
      await clubsApi.rejectEvent(eventId, currentUserId);
      await fetchEvents();
      showSuccess('Event rejected');
    } catch (err) {
      showError(err.message || 'Failed to reject event');
    }
  };

  const formatForDatetimeLocal = (value) => {
    if (!value) return '';
    const date = new Date(value);
    const pad = (n) => String(n).padStart(2, '0');
    const yyyy = date.getFullYear();
    const mm = pad(date.getMonth() + 1);
    const dd = pad(date.getDate());
    const hh = pad(date.getHours());
    const min = pad(date.getMinutes());
    return `${yyyy}-${mm}-${dd}T${hh}:${min}`;
  };

  const openForm = async (event = null) => {
    if (event) {
      setEditingEventId(event.id);
      setNewEvent({
        title: event.title || '',
        description: event.description || '',
        sponsors: event.mapped_sponsors ? event.mapped_sponsors.map(s => s.organization_name).join(', ') : '',
        banner: event.banner || '',
        venue: event.venue || '',
        is_public: event.is_public || false,
        requires_external_participants: event.requires_external_participants || false,
        start_at: formatForDatetimeLocal(event.start_at),
        end_at: formatForDatetimeLocal(event.end_at),
        registration_deadline: formatForDatetimeLocal(event.registration_deadline)
      });

      try {
        const evData = await eventsApi.getEventDetails(event.id);
        setSessions(evData.event_sessions || evData.sessions || []);
      } catch (e) {
        console.error('Failed to load sessions', e);
        setSessions([]);
      }
    } else {
      setEditingEventId(null);
      setNewEvent({
        title: '',
        description: '',
        sponsors: '',
        banner: '',
        venue: '',
        is_public: false,
        requires_external_participants: false,
        start_at: '',
        end_at: '',
        registration_deadline: ''
      });
      setSessions([]);
    }
    setShowCreateForm(true);
  };

  const handleCreateSubmit = async (formData, formSessions) => {
    if (!formData.title || !formData.start_at || !formData.end_at) {
      showError('Title, start time, and end time are required.');
      return;
    }

    const payload = {
      title: formData.title,
      description: formData.description,
      sponsors: formData.sponsors,
      banner: formData.banner,
      venue: formData.venue,
      is_public: formData.is_public,
      requires_external_participants: formData.requires_external_participants,
      start_at: formData.start_at,
      end_at: formData.end_at,
      registration_deadline: formData.registration_deadline || null
    };

    try {
      let eventId = editingEventId;

      if (editingEventId) {
        await clubsApi.updateEvent(
          editingEventId,
          payload,
          currentUserId
        );
        eventId = editingEventId;
      } else {
        const createdEvent = await clubsApi.createEvent(payload, club.id);
        eventId = createdEvent?.id;
      }

      if (formSessions && formSessions.length > 0 && eventId) {
        const cleanSessions = formSessions.map(({ id, isNew, ...rest }) => rest);
        await eventsApi.createEventSessions(eventId, cleanSessions);
      }

      setShowCreateForm(false);
      setEditingEventId(null);
      setNewEvent({
        title: '',
        description: '',
        sponsors: '',
        banner: '',
        venue: '',
        is_public: false,
        requires_external_participants: false,
        start_at: '',
        end_at: '',
        registration_deadline: ''
      });
      setSessions([]);
      showSuccess(editingEventId ? 'Event updated successfully' : 'Event created successfully');

      await fetchEvents();
    } catch (err) {
      console.error(err);
      showError(err.message || 'Failed to save event');
    }
  };

  if (loading) {
    return (
      <div className={layoutStyles.workspaceArea}>
        <div className={layoutStyles.workspaceContent}>
          <div className={styles.loading}>Loading events...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={layoutStyles.workspaceArea}>
        <div className={layoutStyles.workspaceContent}>
          <div className={styles.error}>{error}</div>
        </div>
      </div>
    );
  }

  const visibleEvents = events.filter(e => {
    if (e.status === 'pending_approval' && !canManageEvents(userRole) && !canApproveEvents(userRole)) {
      return false;
    }
    return true;
  });

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent}>
        <header className={styles.header}>
          <div>
            <h2>Club Events</h2>
            <p>Discover and manage events for {club.name}</p>
          </div>
          {canManageEvents(userRole) && (
            <Button
              icon={showCreateForm ? 'mdi:close' : 'mdi:calendar-plus'}
              onClick={() => showCreateForm ? setShowCreateForm(false) : openForm()}
              variant="primary"
            >
              {showCreateForm ? 'Cancel' : 'Create Event'}
            </Button>
          )}
        </header>

        {showCreateForm && (
          <EventFormWizard
            initialData={newEvent}
            onSubmit={handleCreateSubmit}
            onCancel={() => {
              setShowCreateForm(false);
              setEditingEventId(null);
            }}
            isEditing={!!editingEventId}
          />
        )}

        {visibleEvents.length === 0 ? (
          <EmptyState
            icon={uiIcons.calendarBlank}
            title="No events found"
            description="There are currently no events matching your criteria."
          />
        ) : (
          <div className={styles.eventsGrid}>
            {visibleEvents.map(event => (
              <div key={event.id} className={styles.eventCard}>
                <div className={styles.eventHeader}>
                  <h3>{event.title}</h3>
                  <span className={`${styles.statusBadge} ${styles[event.status]}`}>
                    {String(event.status || '').replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                <p className={styles.description}>{event.description}</p>

                {event.mapped_sponsors && event.mapped_sponsors.length > 0 && (
                  <div className={styles.sponsorsSection}>
                    <Icon icon={uiIcons.handshakeOutline} /> <strong>Sponsors:</strong> {event.mapped_sponsors.map(s => s.organization_name).join(', ')}
                  </div>
                )}

                <div className={styles.actions}>
                  {event.status === 'pending_approval' && canApproveEvents(userRole) && (
                    <div className={styles.approvalActions}>
                      <Button variant="outline" style={{ borderColor: '#10b981', color: '#10b981' }} onClick={() => handleApprove(event.id)}>
                        Approve
                      </Button>
                      <Button variant="outline" style={{ borderColor: '#ef4444', color: '#ef4444' }} onClick={() => handleReject(event.id)}>
                        Reject
                      </Button>
                    </div>
                  )}

                  {canManageEvents(userRole) && event.status === 'scheduled' && (
                    <Button variant="outline" icon="mdi:pencil" onClick={() => openForm(event)}>
                      Edit Event
                    </Button>
                  )}

                  {(event.status === 'scheduled' || event.status === 'ongoing' || event.status === 'completed') && canManageAttendance(userRole) && (
                    <Button
                      variant="outline"
                      fullWidth
                      icon={dashboardIcons.clipboardCheckOutline}
                      onClick={() => {
                        setManageEventId(event.id);
                        setManageTab('attendance');
                      }}
                    >
                      Manage Event
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {manageEventId && (
          <div className={styles.modalOverlay} onClick={() => setManageEventId(null)}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()} style={{ maxWidth: '900px', width: '95%', padding: '0' }}>
              <div className={styles.manageEventHeader}>
                <h3>Manage Event</h3>
                <div className={styles.manageTabs}>
                  <button
                    className={`${styles.tabBtn} ${manageTab === 'attendance' ? styles.activeTab : ''}`}
                    onClick={() => setManageTab('attendance')}
                  >
                    Attendance
                  </button>
                  <button
                    className={`${styles.tabBtn} ${manageTab === 'sessions' ? styles.activeTab : ''}`}
                    onClick={() => setManageTab('sessions')}
                  >
                    Sessions
                  </button>
                  <button
                    className={`${styles.tabBtn} ${manageTab === 'participation' ? styles.activeTab : ''}`}
                    onClick={() => setManageTab('participation')}
                  >
                    Registrations & Participation
                  </button>
                </div>
              </div>

              <div className={styles.manageEventBody}>
                {manageTab === 'attendance' && (
                  <AttendanceManager
                    eventId={manageEventId}
                    clubId={club.id}
                    onClose={() => setManageEventId(null)}
                  />
                )}
                {manageTab === 'sessions' && (
                  <SessionsManager
                    eventId={manageEventId}
                    clubId={club.id}
                    isCompleted={events.find(e => e.id === manageEventId)?.status === 'completed'}
                  />
                )}
                {manageTab === 'participation' && (
                  <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--muted-foreground)' }}>
                    <Icon icon="mdi:account-group-outline" style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.5 }} />
                    <h3>Participation Tracking</h3>
                    <p>Participation and registration data will be displayed here.</p>
                  </div>
                )}
              </div>

              <div className={styles.manageEventFooter}>
                <Button variant="outline" onClick={() => setManageEventId(null)}>Close</Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClubEventsView;