import { useState, useEffect } from 'react';
import { adminApi } from '@api/adminApis/admin';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { PriorityBadge } from '../../ui/PriorityBadge/PriorityBadge';
import { FilterTabs } from '../../ui/FilterTabs/FilterTabs';
import { Dropdown } from '../../ui/Dropdown/Dropdown';
import { SearchInput } from '../../ui/SearchInput/SearchInput';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';
import { SupportTicketModal } from './SupportTicketModal/SupportTicketModal';
import { TICKET_PRIORITY_OPTIONS } from '../../../../config/enums';
import { useSession } from '../../../../context/SessionContext';
import styles from './SupportManagement.module.css';

export const SupportManagement = () => {
  const [tickets, setTickets] = useState([]);
  const [filteredTickets, setFilteredTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [activeTab, setActiveTab] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTicket, setSelectedTicket] = useState(null);

  const tabs = [
    { id: 'all', label: 'All Tickets' },
    { id: 'open', label: 'Open' },
    { id: 'closed', label: 'Closed' },
    { id: 'in_progress', label: 'In Progress' },
    { id: 'resolved', label: 'Resolved' }
  ];
  const { user } = useSession();
  const fetchTickets = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getSupportTickets();
      
      let authorizedTickets = data;
      if (user?.role !== 'system_admin') {
        authorizedTickets = authorizedTickets.filter(t => String(t.assigned_agent_id) === String(user?.id));
      }
      
      setTickets(authorizedTickets);
      setFilteredTickets(authorizedTickets);
    } catch (error) {
      console.error("Failed to load tickets", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  useEffect(() => {
    let result = tickets;
    
    // Filter by Tab
    if (activeTab === 'open') result = result.filter(t => t.status?.toLowerCase() === 'open');
    if (activeTab === 'closed') result = result.filter(t => t.status?.toLowerCase() === 'closed');
    if (activeTab === 'in_progress') result = result.filter(t => t.status?.toLowerCase() === 'in progress');
    if (activeTab === 'resolved') result = result.filter(t => t.status?.toLowerCase() === 'resolved');
    
    // Filter by Priority
    if (priorityFilter !== 'all') {
      result = result.filter(t => (t.priority || 'Medium').toLowerCase() === priorityFilter.toLowerCase());
    }
    
    // Filter by Search
    if (searchTerm) {
      const lowerSearch = searchTerm.toLowerCase();
      result = result.filter(t => 
        t.title?.toLowerCase().includes(lowerSearch) || 
        t.ticket_type?.toLowerCase().includes(lowerSearch)
      );
    }

    setFilteredTickets(result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
  }, [tickets, activeTab, priorityFilter, searchTerm]);

  const handleRowClick = async (ticket) => {
    try {
      const fullTicket = await adminApi.getTicketById(ticket.id);
      setSelectedTicket(fullTicket);
    } catch (error) {
      console.error("Failed to load full ticket details", error);
    }
  };

  const handleTicketUpdate = () => {
    fetchTickets();
    setSelectedTicket(null);
  };

  const columns = [
    { header: 'ID', cell: (row) => <span className={styles.ticketId}>#{row.id}</span>, width: '80px' },
    { 
      header: 'Subject', 
      cell: (row) => (
        <div className={styles.subjectCell}>
          <span className={styles.subject}>{row.title}</span>
          <span className={styles.type}>{row.ticket_type}</span>
        </div>
      )
    },
    { 
      header: 'Raised By', 
      cell: (row) => row.raised_by_user?.full_name || `#${row.raised_by}`
    },
    { header: 'Priority', cell: (row) => <PriorityBadge priority={row.priority} /> },
    { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
    { header: 'Created', cell: (row) => new Date(row.created_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' }) },
    { header: '', cell: () => <Icon icon={uiIcons.chevronRight} color="var(--muted-foreground)" width="20" /> }
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Support Management</h2>
        <p className={styles.subtitle}>Manage user help requests, bug reports, and platform inquiries.</p>
      </div>

      <div className={styles.controls}>
        <FilterTabs 
          tabs={tabs} 
          activeTab={activeTab} 
          onTabChange={setActiveTab} 
        />
        <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
          <Dropdown
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            options={[
              { value: 'all', label: 'All Priorities' },
              ...TICKET_PRIORITY_OPTIONS
            ]}
          />
          <SearchInput 
            placeholder="Search ticket by subject..." 
            onChange={setSearchTerm} 
            style={{ width: '450px' }}
          />
        </div>
      </div>

      {loading ? (
        <div className={styles.loading}><Icon icon={uiIcons.loading} className="spin" width="32" /></div>
      ) : (
        <DataTable 
          columns={columns} 
          data={filteredTickets} 
          onRowClick={handleRowClick}
          emptyTitle="No tickets found"
          emptyDesc="There are no support tickets matching your criteria."
        />
      )}

      {selectedTicket && (
        <SupportTicketModal 
          ticket={selectedTicket} 
          onClose={() => setSelectedTicket(null)} 
          onUpdate={handleTicketUpdate}
        />
      )}
    </div>
  );
};
