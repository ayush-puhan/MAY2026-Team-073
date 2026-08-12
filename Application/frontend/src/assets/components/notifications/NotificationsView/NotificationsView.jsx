import React, { useState, useEffect } from 'react';
import { notificationApi } from '../../../../api';
import { useSession } from '../../../../context/SessionContext';
import { SecondaryHeader } from '../../ui/SecondaryHeader/SecondaryHeader';
import { SearchInput } from '../../ui/SearchInput/SearchInput';
import { Button } from '../../ui/Button/Button';
import { DataTable } from '../../ui/DataTable/DataTable';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';
import styles from './NotificationsView.module.css';

export const NotificationsView = () => {
  const { user } = useSession();
  const [notifications, setNotifications] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const data = await notificationApi.getNotifications(user.id);
      setNotifications(data || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching notifications:', err);
      setError('Failed to load notifications.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.id) {
      fetchNotifications();
    }
  }, [user?.id]);

  const handleMarkAsRead = async (notifId) => {
    try {
      await notificationApi.markAsRead(notifId);
      setNotifications(prev => prev.map(n => n.id === notifId ? { ...n, is_read: true } : n));
    } catch (err) {
      console.error('Error marking as read:', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationApi.markAllAsRead(user.id);
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      console.error('Error marking all as read:', err);
    }
  };

  const filteredNotifications = notifications.filter(n => {
    if (!searchQuery) return true;
    const lowerQ = searchQuery.toLowerCase();
    return (n.title && n.title.toLowerCase().includes(lowerQ)) || (n.body && n.body.toLowerCase().includes(lowerQ));
  });

  const columns = [
    { 
      header: 'Notification', 
      cell: (row) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <strong style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {!row.is_read && <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--primary)' }} />}
            {row.title}
          </strong>
          <span style={{ color: 'var(--text-secondary)' }}>{row.body}</span>
        </div>
      )
    },
    { 
      header: 'Date', 
      cell: (row) => new Date(row.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
      width: '200px'
    },
    {
      header: 'Actions',
      cell: (row) => (
        !row.is_read ? (
          <Button variant="secondary" size="sm" onClick={() => handleMarkAsRead(row.id)}>
            Mark as Read
          </Button>
        ) : (
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Read</span>
        )
      ),
      width: '150px'
    }
  ];

  return (
    <div className={styles.container}>
      <SecondaryHeader 
        title="Your Notifications" 
        description="View and manage your alerts and updates."
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        rightControls={
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <Button onClick={handleMarkAllAsRead} variant="secondary">Mark All as Read</Button>
          </div>
        }
      />
      
      <div className={styles.content} style={{ marginTop: '1.5rem' }}>
        {loading ? (
          <p className={styles.message}>Loading notifications...</p>
        ) : error ? (
          <p className={styles.error}>{error}</p>
        ) : (
          <DataTable 
            columns={columns}
            data={filteredNotifications}
            emptyTitle="No notifications found"
            emptyDesc="You're all caught up!"
          />
        )}
      </div>
    </div>
  );
};
