import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { EventCard } from '../../ui/EventCard/EventCard';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { SearchInput } from '../../ui/SearchInput/SearchInput';
import { universityAdminApi } from '@api/universityAdminApis/universityAdmin';
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

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem', marginTop: '1.5rem' }}>
        {filtered.length === 0 ? (
          <div className={styles.emptyState} style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', color: 'var(--muted-foreground)' }}>
            <Icon icon="mdi:calendar-blank-outline" width="48" style={{ marginBottom: '1rem', opacity: 0.5 }} />
            <h3>No events found</h3>
          </div>
        ) : (
          filtered.map(ev => (
            <EventCard
              key={ev.id}
              title={ev.title}
              subtitle={`${ev.club_name} • ${ev.venue} • ${new Date(ev.start_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' })}`}
              bannerKeyword={ev.bannerKeyword}
              icon="mdi:calendar-star"
              color="var(--innovation)"
              rightElement={
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', alignItems: 'flex-end' }}>
                  <StatusBadge status={ev.approval_status} />
                </div>
              }
            />
          ))
        )}
      </div>
    </div>
  );
};
