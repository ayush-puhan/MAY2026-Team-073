import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { DataTable, RowChevron } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { FilterTabs } from '../../ui/FilterTabs/FilterTabs';
import { facultyAdvisorApi } from '../../../../api/facultyAdvisor.api';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { EventDecisionModal } from './EventDecisionModal/EventDecisionModal';
import styles from './EventApprovals.module.css';

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

  const filtered = events.filter((e) => e.approval_status === activeTab);
  const tabs = [
    { value: 'pending', label: 'Pending', count: events.filter((e) => e.approval_status === 'pending').length },
    { value: 'approved', label: 'Approved', count: events.filter((e) => e.approval_status === 'approved').length },
    { value: 'rejected', label: 'Rejected', count: events.filter((e) => e.approval_status === 'rejected').length },
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
        <Icon icon="mdi:loading" className="animate-spin" width="32" />
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

      <DataTable
        columns={[
          { header: 'Event', accessor: 'title' },
          { header: 'Club', accessor: 'club_name' },
          { header: 'Date', cell: (row) => new Date(row.start_at).toLocaleDateString() },
          { header: 'Status', cell: (row) => <StatusBadge status={row.approval_status} /> },
          { header: '', cell: (row) => row.approval_status === 'pending' ? <RowChevron /> : null },
        ]}
        data={filtered}
        onRowClick={(row) => row.approval_status === 'pending' && setSelectedEvent(row)}
        emptyIcon="mdi:calendar-check-outline"
        emptyTitle={`No ${activeTab} events`}
      />

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
