import { useState, useEffect } from 'react';
import { api } from '../../../../api/api';
import { emergencyApi } from '../../../../api';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { Icon } from '@iconify/react';
import { uiIcons, emergencyIcons } from '../../../icons/registry';
import { Button } from '../../ui/Button/Button';
import { Dropdown } from '../../ui/Dropdown/Dropdown';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { createPortal } from 'react-dom';
import styles from './EmergencyDashboard.module.css';
import contextStyles from "../../ui/ContextLayout/ContextLayout.module.css";

export const EmergencyDashboard = () => {
  const { user } = useSession();
  const { showSuccess, showError } = useToast();
  
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('All');
  const [selectedReport, setSelectedReport] = useState(null);
  
  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const data = await emergencyApi.getEmergencyReports();
      setReports(data);
    } catch (err) {
      console.error(err);
      showError("Failed to load emergency reports");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (status) => {
    if (!selectedReport) return;
    try {
      await emergencyApi.updateEmergencyStatus(selectedReport.id, status, user.id);
      showSuccess(`Status updated to ${status}`);
      setSelectedReport(null);
      fetchReports();
    } catch (err) {
      console.error(err);
      showError("Failed to update status");
    }
  };

  const filteredReports = activeTab === 'All' 
    ? reports 
    : reports.filter(r => r.status.toLowerCase().replace('_', ' ') === activeTab.toLowerCase());

  const stats = {
    total: reports.length,
    active: reports.filter(r => r.status !== 'resolved').length,
    acknowledged: reports.filter(r => r.status === 'acknowledged').length,
    resolved: reports.filter(r => r.status === 'resolved').length
  };

  const columns = [
    { header: 'ID', cell: (row) => <span>#{row.id}</span>, width: '80px' },
    { header: 'Reporter', accessor: 'reporter_name' },
    { header: 'Category', cell: (row) => <span style={{ textTransform: 'capitalize' }}>{row.category.replace('_', ' ')}</span> },
    { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
    { header: 'Handler', accessor: 'handler_name' },
    { header: 'Created', cell: (row) => new Date(row.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) }
  ];

  const TABS = ['All', 'Reported', 'Acknowledged', 'In Progress', 'Resolved'];

  return (
    <div className={contextStyles.pageContainer}>
      <div className={contextStyles.header}>
        <div>
          <h1 className={contextStyles.title}>Emergency Dashboard</h1>
          <p className={contextStyles.subtitle}>Manage and respond to emergency reports</p>
        </div>
        <Button onClick={fetchReports} icon={uiIcons.refresh} variant="outline">Refresh</Button>
      </div>

      <div className={styles.statsContainer}>
        <div className={styles.statCard}>
          <div className={styles.statIcon}><Icon icon={emergencyIcons.alert} /></div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Total Reports</span>
            <span className={styles.statValue}>{stats.total}</span>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ color: 'var(--destructive)' }}><Icon icon={emergencyIcons.medical} /></div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Active</span>
            <span className={styles.statValue}>{stats.active}</span>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ color: 'var(--warning)' }}><Icon icon={uiIcons.eye} /></div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Acknowledged</span>
            <span className={styles.statValue}>{stats.acknowledged}</span>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ color: 'var(--success)' }}><Icon icon={uiIcons.checkCircle} /></div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Resolved</span>
            <span className={styles.statValue}>{stats.resolved}</span>
          </div>
        </div>
      </div>

      <div className={styles.tabs}>
        {TABS.map(tab => (
          <button 
            key={tab}
            className={`${styles.tab} ${activeTab === tab ? styles.activeTab : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className={contextStyles.contentCard}>
        {loading ? (
          <div className={styles.loading}><Icon icon={uiIcons.loading} className="spin" width="32" /></div>
        ) : (
          <DataTable 
            columns={columns} 
            data={filteredReports} 
            emptyTitle="No reports found"
            emptyDesc="There are no emergency reports in this category."
            onRowClick={setSelectedReport}
          />
        )}
      </div>

      {selectedReport && typeof document !== 'undefined' && createPortal(
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <div className={styles.modalHeader}>
              <h3>Emergency #{selectedReport.id}</h3>
              <button className={styles.closeBtn} onClick={() => setSelectedReport(null)}>
                <Icon icon={uiIcons.close} />
              </button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.detailRow}>
                <strong>Reporter:</strong> {selectedReport.reporter_name}
              </div>
              <div className={styles.detailRow}>
                <strong>Category:</strong> <span style={{ textTransform: 'capitalize' }}>{selectedReport.category.replace('_', ' ')}</span>
              </div>
              <div className={styles.detailRow}>
                <strong>Status:</strong> <StatusBadge status={selectedReport.status} />
              </div>
              <div className={styles.detailRow}>
                <strong>Created At:</strong> {new Date(selectedReport.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}
              </div>
              <div className={styles.detailRow}>
                <strong>Description:</strong>
                <p className={styles.descriptionBox}>{selectedReport.description}</p>
              </div>
            </div>
            
            <div className={styles.modalFooter}>
              {selectedReport.status === 'reported' && (
                <Button onClick={() => handleUpdateStatus('acknowledged')} style={{ backgroundColor: 'var(--warning)', color: 'white', border: 'none' }}>Acknowledge</Button>
              )}
              {(selectedReport.status === 'reported' || selectedReport.status === 'acknowledged') && (
                <Button onClick={() => handleUpdateStatus('in_progress')} variant="primary">Mark In Progress</Button>
              )}
              {selectedReport.status !== 'resolved' && (
                <Button onClick={() => handleUpdateStatus('resolved')} style={{ backgroundColor: 'var(--success)', color: 'white', border: 'none' }}>Resolve</Button>
              )}
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};


