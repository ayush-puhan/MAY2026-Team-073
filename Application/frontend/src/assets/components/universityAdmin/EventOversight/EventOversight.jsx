import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { SearchInput } from '../../ui/SearchInput/SearchInput';
import { universityAdminApi } from '../../../../api/universityAdmin.api';
import styles from './EventOversight.module.css';

export const EventOversight = () => {
  const [events, setEvents] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    universityAdminApi.getAllEvents().then((data) => {
      if (isMounted) {
        setEvents(data);
        setLoading(false);
      }
    });
    return () => { isMounted = false; };
  }, []);

  useEffect(() => {
    setFiltered(
      events.filter((e) =>
        e.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        e.club_name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [events, searchTerm]);

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
        <h2 className={styles.title}>Event Oversight</h2>
        <p className={styles.subtitle}>University-wide view of every club event.</p>
      </div>

      <div className={styles.controls}>
        <SearchInput placeholder="Search events or clubs..." onChange={setSearchTerm} />
      </div>

      <DataTable
        columns={[
          { header: 'Event', accessor: 'title' },
          { header: 'Club', accessor: 'club_name' },
          { header: 'Venue', accessor: 'venue' },
          { header: 'Date', cell: (row) => new Date(row.start_at).toLocaleDateString() },
          { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
          { header: 'Approval', cell: (row) => <StatusBadge status={row.approval_status} /> },
        ]}
        data={filtered}
        emptyIcon="mdi:calendar-blank-outline"
        emptyTitle="No events found"
      />
    </div>
  );
};
