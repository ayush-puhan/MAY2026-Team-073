import { useState, useEffect } from 'react';
import { adminApi } from '@api/adminApis/admin';
import { DataTable } from '../../ui/DataTable/DataTable';
import { FilterTabs } from '../../ui/FilterTabs/FilterTabs';
import { SearchInput } from '../../ui/SearchInput/SearchInput';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';
import styles from './AuditLogs.module.css';

export const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const tabs = [
    { id: 'all', label: 'All Activities' },
    { id: 'CREATE', label: 'Creations' },
    { id: 'UPDATE', label: 'Updates' },
    { id: 'DELETE', label: 'Deletions' }
  ];

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await adminApi.getAuditLogs(100); // Fetch latest 100 for admin
        setLogs(data);
        setFilteredLogs(data);
      } catch (error) {
        console.error("Failed to load audit logs", error);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  useEffect(() => {
    let result = logs;
    
    // Filter by Tab
    if (activeTab !== 'all') {
      result = result.filter(log => log.action?.toUpperCase() === activeTab);
    }
    
    // Filter by Search
    if (searchTerm) {
      const lowerSearch = searchTerm.toLowerCase();
      result = result.filter(log => 
        log.entity_type?.toLowerCase().includes(lowerSearch) || 
        log.details?.toLowerCase().includes(lowerSearch) ||
        String(log.user_id).includes(lowerSearch)
      );
    }

    setFilteredLogs(result);
  }, [logs, activeTab, searchTerm]);

  const columns = [
    { 
      header: 'Action', 
      cell: (row) => {
        const action = row.action?.toUpperCase();
        let color = 'var(--foreground)';
        let icon = 'mdi:help-circle';
        if (action === 'CREATE') { color = '#10b981'; icon = 'mdi:plus-circle'; }
        if (action === 'UPDATE') { color = '#3b82f6'; icon = 'mdi:pencil-circle'; }
        if (action === 'DELETE') { color = '#ef4444'; icon = 'mdi:minus-circle'; }
        return (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color, fontWeight: 600 }}>
            <Icon icon={icon} width="20" />
            {action}
          </div>
        );
      } 
    },
    { header: 'Entity Type', accessor: 'entity_type' },
    { header: 'Entity ID', accessor: 'entity_id' },
    { header: 'User ID', accessor: 'user_id' },
    { header: 'Details', cell: (row) => <span className={styles.detailsCell} title={row.details}>{row.details}</span> },
    { header: 'Timestamp', cell: (row) => new Date(row.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) }
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Audit Logs</h2>
        <p className={styles.subtitle}>Track and review all significant actions performed within the platform.</p>
      </div>

      <div className={styles.controls}>
        <FilterTabs 
          tabs={tabs} 
          activeTab={activeTab} 
          onTabChange={setActiveTab} 
        />
        <SearchInput 
          placeholder="Search logs..." 
          onChange={setSearchTerm} 
          style={{ width: '300px' }}
        />
      </div>

      {loading ? (
        <div className={styles.loading}><Icon icon={uiIcons.loading} className="spin" width="32" /></div>
      ) : (
        <DataTable 
          columns={columns} 
          data={filteredLogs} 
          emptyTitle="No logs found"
          emptyDesc="No activities match your current search and filters."
        />
      )}
    </div>
  );
};
