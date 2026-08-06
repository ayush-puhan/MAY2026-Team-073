import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { EventCard } from '../../ui/EventCard/EventCard';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { FilterTabs } from '../../ui/FilterTabs/FilterTabs';
import { facultyAdvisorApi } from '@api/facultyAdvisorApis/facultyAdvisor';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { EventDecisionModal } from './EventDecisionModal/EventDecisionModal';
import styles from './EventApprovals.module.css';
import { uiIcons, dashboardIcons } from '../../../icons/registry';

export const EventApprovals = () => {
  const { user } = useSession();
  const { showSuccess, showError } = useToast();
  const [events, setEvents] = useState([]);
  const [activeTab, setActiveTab] = useState('pending');
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState(null);

  const loadEvents = async () => {
    setLoading(true);
    const data = await facultyAdvisorApi.getEvents(user.id);
    setEvents(data);
    setLoading(false);
  };

  useEffect(() => { loadEvents(); }, [user.id]);

  const STATUS_BY_TAB = { pending: 'pending_approval', approved: 'scheduled', rejected: 'rejected' };
  const LABEL_BY_STATUS = { pending_approval: 'Pending', scheduled: 'Approved', rejected: 'Rejected' };

  const filtered = events.filter((e) => e.status === STATUS_BY_TAB[activeTab]);
  const tabs = [
    { id: 'pending', label: 'Pending', count: events.filter((e) => e.status === STATUS_BY_TAB.pending).length },
    { id: 'approved', label: 'Approved', count: events.filter((e) => e.status === STATUS_BY_TAB.approved).length },
    { id: 'rejected', label: 'Rejected', count: events.filter((e) => e.status === STATUS_BY_TAB.rejected).length },
  ];

  const handleDecide = async (eventId, approval_status, review_comments) => {
    try {
      await facultyAdvisorApi.decideEvent(eventId, { approval_status, review_comments, reviewed_by: user.id });
      showSuccess(`Event ${approval_status}.`);
      setSelectedEvent(null);
      loadEvents();
    } catch (err) {
      showError(err.message || 'Failed to update event.');
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <Icon icon={uiIcons.loading} className="animate-spin" width="32" />
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Event Approvals</h2>
        <p className={styles.subtitle}>Review, approve, or reject events submitted by your advised clubs.</p>
      </div>

      <FilterTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem', marginTop: '1.5rem' }}>
        {filtered.length === 0 ? (
          <div className={styles.emptyState} style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', color: 'var(--muted-foreground)' }}>
            <Icon icon={dashboardIcons.calendarCheckOutline} width="48" style={{ marginBottom: '1rem', opacity: 0.5 }} />
            <h3>No {activeTab} events</h3>
          </div>
        ) : (
          filtered.map(ev => (
            <EventCard
              key={ev.id}
              title={ev.title}
              subtitle={`${ev.club_name} • ${new Date(ev.start_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' })}`}
              icon={uiIcons.calendarText}
              bannerKeyword={ev.bannerKeyword}
              color={activeTab === 'pending' ? 'var(--campus-orange)' : activeTab === 'approved' ? 'var(--success)' : 'var(--destructive)'}
              onClick={() => ev.status === STATUS_BY_TAB.pending && setSelectedEvent(ev)}
              rightElement={
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', alignItems: 'flex-end' }}>
                  <StatusBadge status={LABEL_BY_STATUS[ev.status] || ev.status} />
                  {ev.status === STATUS_BY_TAB.pending && (
                    <Icon icon={uiIcons.chevronRight} style={{ color: 'var(--muted-foreground)' }} />
                  )}
                </div>
              }
            />
          ))
        )}
      </div>

      {selectedEvent && (
        <EventDecisionModal
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
          onDecide={handleDecide}
        />
      )}
    </div>
  );
};
