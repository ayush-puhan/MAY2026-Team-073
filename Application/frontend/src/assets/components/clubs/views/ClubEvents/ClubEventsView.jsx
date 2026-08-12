import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { useToast } from '../../../../../context/ToastContext';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/backendApis/clubsApis/clubs';
import { eventsRealApi } from '../../../../../api/backendApis/eventsApis/events';
import { canManageEvents, canApproveEvents, canManageAttendance } from '../../../../../utils/clubPermissions';
import styles from './ClubEventsView.module.css';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import { Button } from '../../../ui/Button/Button';
import { EmptyState } from '../../../ui/EmptyState/EmptyState';
import { Input } from '../../../ui/Input/Input';
import { EventSessionManager } from '../../../../components/events/EventSessionManager/EventSessionManager';
import AttendanceManager from '../../../../components/events/AttendanceManager/AttendanceManager';
import { uiIcons, dashboardIcons } from '../../../../icons/registry';
import ParticipationManager from "../../../../components/events/ParticipationManager/ParticipationManager";

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
        const evData = await eventsRealApi.getEventDetails(event.id);
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

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    if (!newEvent.title || !newEvent.start_at || !newEvent.end_at) {
      showError('Title, start time, and end time are required.');
      return;
    }

    const payload = {
      title: newEvent.title,
      description: newEvent.description,
      sponsors: newEvent.sponsors,
      banner: newEvent.banner,
      venue: newEvent.venue,
      is_public: newEvent.is_public,
      requires_external_participants: newEvent.requires_external_participants,
      start_at: newEvent.start_at,
      end_at: newEvent.end_at,
      registration_deadline: newEvent.registration_deadline || null
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

      if (sessions.length > 0 && eventId) {
        const cleanSessions = sessions.map(({ id, isNew, ...rest }) => rest);
        await eventsRealApi.createEventSessions(eventId, cleanSessions);
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
          <div className={styles.modalOverlay} onClick={() => setShowCreateForm(false)}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <form onSubmit={handleCreateSubmit}>
                <h3>{editingEventId ? 'Edit Event' : 'Schedule New Event'}</h3>

                <Input
                  label="Event Title *"
                  type="text"
                  value={newEvent.title}
                  onChange={e => setNewEvent({ ...newEvent, title: e.target.value })}
                  required
                />

                <Input
                  label="Venue (Optional)"
                  type="text"
                  value={newEvent.venue}
                  onChange={e => setNewEvent({ ...newEvent, venue: e.target.value })}
                />

                <Input
                  label="Description"
                  as="textarea"
                  rows="3"
                  value={newEvent.description}
                  onChange={e => setNewEvent({ ...newEvent, description: e.target.value })}
                />

                <Input
                  label="Sponsors (Optional, comma separated)"
                  type="text"
                  placeholder="e.g. Google, GitHub, Local Pizza Shop"
                  value={newEvent.sponsors}
                  onChange={e => setNewEvent({ ...newEvent, sponsors: e.target.value })}
                />

                <Input
                  label="Banner URL (Optional)"
                  type="text"
                  placeholder="https://example.com/banner.png"
                  value={newEvent.banner}
                  onChange={e => setNewEvent({ ...newEvent, banner: e.target.value })}
                />

                <Input
                  label="Start Time *"
                  type="datetime-local"
                  value={newEvent.start_at}
                  onChange={e => setNewEvent({ ...newEvent, start_at: e.target.value })}
                  required
                />

                <Input
                  label="End Time *"
                  type="datetime-local"
                  value={newEvent.end_at}
                  onChange={e => setNewEvent({ ...newEvent, end_at: e.target.value })}
                  required
                />

                <Input
                  label="Registration Deadline (Optional)"
                  type="datetime-local"
                  value={newEvent.registration_deadline}
                  onChange={e => setNewEvent({ ...newEvent, registration_deadline: e.target.value })}
                />

                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '0.5rem', marginBottom: '1rem' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={newEvent.requires_external_participants}
                      onChange={e => setNewEvent({ ...newEvent, requires_external_participants: e.target.checked })}
                    />
                    Public Event (Requires External Participants)
                  </label>

                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={newEvent.is_public}
                      onChange={e => setNewEvent({ ...newEvent, is_public: e.target.checked })}
                    />
                    Open Club Event (Open to any University Student)
                  </label>
                </div>

                <EventSessionManager
                  sessions={sessions}
                  setSessions={setSessions}
                />

                <div className={styles.formActions}>
                  <Button variant="outline" type="button" onClick={() => setShowCreateForm(false)}>
                    Cancel
                  </Button>
                  <Button variant="primary" type="submit">
                    {editingEventId ? 'Save Changes' : 'Submit Event'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
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

                  {canManageEvents(userRole) && (
                    <Button variant="outline" icon="mdi:pencil" onClick={() => openForm(event)}>
                      Edit Event
                    </Button>
                  )}

                  {(event.status === 'scheduled' || event.status === 'ongoing') && canManageAttendance(userRole) && (
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
                {manageTab === 'participation' && (
                  <ParticipationManager
                    eventId={manageEventId}
                    onClose={() => setManageEventId(null)}
                  />
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