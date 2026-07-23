import { useState, useEffect } from 'react';
import { api } from '../../../../api/api';
import { logAudit, istNow } from '../../../../api/mockbackendApis/auditHelper';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { Icon } from '@iconify/react';
import { uiIcons, emergencyIcons } from '../../../icons/registry';
import { emergencyApi } from '../../../../api';
import { Button } from '../../ui/Button/Button';
import { Dropdown } from '../../ui/Dropdown/Dropdown';
import { Input } from '../../ui/Input/Input';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { PriorityBadge } from '../../ui/PriorityBadge/PriorityBadge';
import { checkIsVerified } from '../../../../utils/verification';
import { TICKET_PRIORITY_OPTIONS, TICKET_TYPE_OPTIONS } from '../../../../config/enums';
import { createPortal } from 'react-dom';
import styles from './Helpdesk.module.css';

const SUPPORT_ROLES = [
  { id: 'system_admin', label: 'System Administrator', type: 'system' },
  { id: 'dean_student_welfare', label: 'Dean of Student Welfare', type: 'university' },
  { id: 'student_affairs_office', label: 'Student Affairs Office', type: 'university' },
  { id: 'president', label: 'Club President', type: 'club' },
  { id: 'vice_president', label: 'Club Vice President', type: 'club' },
  { id: 'secretary', label: 'Club Secretary', type: 'club' },
  { id: 'treasurer', label: 'Club Treasurer', type: 'club' },
  { id: 'event_coordinator', label: 'Event Coordinator', type: 'club' },
  { id: 'faculty_advisor', label: 'Faculty Advisor', type: 'club' }
];

export const Helpdesk = () => {
  const { user } = useSession();
  const { showInfo } = useToast();
  const [tickets, setTickets] = useState([]);
  const [clubs, setClubs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [responses, setResponses] = useState([]);
  
  // Form State
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'Medium',
    ticket_type: 'Support',
    target_category: '', // 'system', 'university', 'club'
    assigned_role: '',
    assigned_club_id: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState('tickets');
  const [emergencies, setEmergencies] = useState([]);
  const [isEmergencyModalOpen, setIsEmergencyModalOpen] = useState(false);
  const [emergencyForm, setEmergencyForm] = useState({ category: 'medical', description: '', event_id: '' });


  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ticketsData, clubsData, memberships, emergencyData] = await Promise.all([
          api.get(`/support_tickets`),
          api.get('/clubs'),
          api.get(`/club_memberships?user_id=${user.id}`),
          emergencyApi.getEmergencyReports({ reported_by: user.id })
        ]);
        const userTickets = ticketsData.filter(t => String(t.raised_by) === String(user.id));
        setTickets(userTickets);
        setEmergencies(emergencyData);
        
        const userClubIds = memberships.map(m => String(m.club_id));
        const userClubs = clubsData.filter(c => userClubIds.includes(String(c.id)));
        setClubs(userClubs);
      } catch (err) {
        console.error("Failed to fetch helpdesk data", err);
      } finally {
        setLoading(false);
      }
    };
    if (user?.id) fetchData();
  }, [user?.id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const newTicket = {
        title: formData.title,
        description: formData.description,
        raised_by: user.id,
        club_id: formData.assigned_club_id ? parseInt(formData.assigned_club_id) : null,
        university_id: user.university_id || null,
        status: 'Open',
        priority: formData.priority,
        ticket_type: formData.ticket_type,
        assigned_agent_id: null,
        created_at: istNow()
      };
      
      const savedTicket = await api.post('/support_tickets', newTicket);
      
      await logAudit({
        userId: user.id,
        action: 'CREATE',
        entityType: 'SupportTicket',
        entityId: savedTicket.id,
        details: `Student created support ticket: ${formData.title}`,
      });
      
      setTickets(prev => [...prev, savedTicket]);
      setIsModalOpen(false);
      setFormData({ title: '', description: '', priority: 'Medium', ticket_type: 'Support', target_category: '', assigned_role: '', assigned_club_id: '' });
    } catch (err) {
      console.error("Failed to create ticket", err);
    } finally {
      setSubmitting(false);
    }
  };

  
  const handleEmergencySubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const data = {
        reported_by: user.id,
        category: emergencyForm.category,
        description: emergencyForm.description,
        event_id: emergencyForm.event_id || null
      };
      const res = await emergencyApi.submitEmergencyReport(data);
      setEmergencies(prev => [res, ...prev]);
      setIsEmergencyModalOpen(false);
      setEmergencyForm({ category: 'medical', description: '', event_id: '' });
      showInfo("Emergency report submitted successfully.");
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRowClick = async (ticket) => {
    setSelectedTicket(ticket);
    try {
      const resp = await api.get(`/ticket_responses?ticket_id=${ticket.id}`);
      setResponses(resp || []);
    } catch (error) {
      console.error("Failed to fetch responses", error);
    }
  };

  const columns = [
    { header: 'ID', cell: (row) => <span>#{row.id}</span>, width: '80px' },
    { header: 'Type', accessor: 'ticket_type' },
    { header: 'Title', accessor: 'title' },
    { header: 'Priority', cell: (row) => <PriorityBadge priority={row.priority || 'Medium'} /> },
    { header: 'Status', cell: (row) => <StatusBadge status={row.status || 'Open'} /> },
    { header: 'Created', cell: (row) => new Date(row.created_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' }) }
  ];

  const isVerified = checkIsVerified(user);

  const getFilteredRoles = () => {
    if (!formData.target_category) return [];
    let roles = SUPPORT_ROLES.filter(r => r.type === formData.target_category);
    if (!isVerified && formData.target_category !== 'system') {
      return [];
    }
    return roles;
  };
  const availableRoles = getFilteredRoles();

  const handleOpenModal = () => {
    setIsModalOpen(true);
    if (!isVerified) {
      showInfo("Please verify your university email in Profile Settings to contact university staff and club officers.");
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Support Helpdesk</h2>
          <p className={styles.subtitle}>Submit and track your support tickets.</p>
        </div>
        <Button className={styles.createBtn} onClick={handleOpenModal} icon={uiIcons.plus}>
          New Ticket
        </Button>
      </div>

      <div className={styles.content}>
        {loading ? (
          <div className={styles.loading}><Icon icon={uiIcons.loading} className="spin" width="32" /></div>
        ) : (
          <DataTable 
            columns={columns} 
            data={tickets} 
            emptyTitle="No tickets found"
            emptyDesc="You haven't submitted any support tickets yet."
            onRowClick={handleRowClick}
          />
        )}
      </div>

      {isModalOpen && typeof document !== 'undefined' && createPortal(
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <div className={styles.modalHeader}>
              <h3>Create Support Ticket</h3>
              <button className={styles.closeBtn} onClick={() => setIsModalOpen(false)}>
                <Icon icon={uiIcons.close} />
              </button>
            </div>
            <form onSubmit={handleSubmit} className={styles.form}>
              <div className={styles.field}>
                <label>Subject</label>
                <Input 
                  name="title"
                  value={formData.title} 
                  onChange={(e) => setFormData({...formData, title: e.target.value})} 
                  required 
                  className={styles.input}
                  placeholder="Brief description of the issue"
                />
              </div>

              <div className={styles.row}>
                <div className={styles.field}>
                  <label>Type</label>
                  <Dropdown 
                    name="ticket_type"
                    value={formData.ticket_type}
                    onChange={(e) => setFormData({...formData, ticket_type: e.target.value})}
                    options={TICKET_TYPE_OPTIONS}
                  />
                </div>
                <div className={styles.field}>
                  <label>Priority</label>
                  <Dropdown 
                    name="priority"
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: e.target.value})}
                    options={TICKET_PRIORITY_OPTIONS}
                  />
                </div>
              </div>

              <div className={styles.row}>
                <div className={styles.field}>
                  <label>Support Category</label>
                  <Dropdown 
                    name="target_category"
                    value={formData.target_category}
                    onChange={(e) => setFormData({...formData, target_category: e.target.value, assigned_role: '', assigned_club_id: ''})}
                    placeholder="-- Select Category --"
                    options={[
                      { value: 'system', label: 'System Admin' },
                      ...(isVerified ? [
                        { value: 'university', label: 'University Staff' },
                        { value: 'club', label: 'Club Officer' }
                      ] : [])
                    ]}
                  />
                </div>

                {formData.target_category === 'club' && (
                  <div className={styles.field}>
                    <label>Select Club</label>
                    <Dropdown 
                      name="assigned_club_id"
                      value={formData.assigned_club_id}
                      onChange={(e) => setFormData({...formData, assigned_club_id: e.target.value, assigned_role: ''})}
                      placeholder="-- Select Club --"
                      options={clubs.map(c => ({ value: c.id, label: c.name }))}
                    />
                  </div>
                )}
              </div>

              {formData.target_category && (formData.target_category !== 'club' || formData.assigned_club_id) && (
                <div className={styles.field}>
                  <label>Assign To (Role)</label>
                  <Dropdown 
                    name="assigned_role"
                    value={formData.assigned_role}
                    onChange={(e) => setFormData({...formData, assigned_role: e.target.value})}
                    placeholder="-- Select Role --"
                    options={availableRoles.map(r => ({ value: r.id, label: r.label }))}
                  />
                  {!isVerified && formData.target_category !== 'system' && (
                    <small style={{ color: 'var(--destructive)', marginTop: '4px', display: 'block', fontSize: '0.8rem' }}>
                      You must verify your email in Profile Settings to contact this role.
                    </small>
                  )}
                </div>
              )}

              <div className={styles.field}>
                <label>Description</label>
                <textarea 
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  required
                  className={styles.textarea}
                  rows={4}
                  placeholder="Please provide details about your issue..."
                />
              </div>

              <div className={styles.footer}>
                <Button variant="outline" type="button" className={styles.cancelBtn} onClick={() => setIsModalOpen(false)}>Cancel</Button>
                <Button type="submit" className={styles.submitBtn} disabled={submitting} isLoading={submitting}>
                  Submit Ticket
                </Button>
              </div>
            </form>
          </div>
        </div>,
        document.body
      )}

      {selectedTicket && typeof document !== 'undefined' && createPortal(
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <div className={styles.modalHeader}>
              <h3>Ticket #{selectedTicket.id}</h3>
              <button className={styles.closeBtn} onClick={() => setSelectedTicket(null)}>
                <Icon icon={uiIcons.close} />
              </button>
            </div>
            <div className={styles.ticketDetails}>
              <div className={styles.detailRow}>
                <strong>Subject:</strong> {selectedTicket.title}
              </div>
              <div className={styles.detailRow}>
                <strong>Status:</strong> <StatusBadge status={selectedTicket.status} />
              </div>
              <div className={styles.detailRow}>
                <strong>Priority:</strong> <PriorityBadge priority={selectedTicket.priority} />
              </div>
              <div className={styles.detailRow}>
                <strong>Description:</strong> 
                <p>{selectedTicket.description}</p>
              </div>
            </div>

            <div className={styles.responsesSection}>
              <h4>Responses</h4>
              {responses.length === 0 ? (
                <p className={styles.noResponses}>No responses yet.</p>
              ) : (
                <div className={styles.responsesList}>
                  {responses.map(resp => (
                    <div key={resp.id} className={styles.responseCard}>
                      <div className={styles.responseHeader}>
                        <span>Admin</span>
                        <small>{new Date(resp.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</small>
                      </div>
                      <div className={styles.responseBody}>{resp.message}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};
