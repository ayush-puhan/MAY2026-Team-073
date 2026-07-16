import React, { useState, useEffect } from 'react';
import { adminApi } from '../../../../../api/admin.api';
import { api } from '../../../../../api/api';
import { Icon } from '@iconify/react';
import { uiIcons, adminIcons } from '../../../../icons/registry';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import { StatusBadge } from '../../../ui/StatusBadge/StatusBadge';
import { PriorityBadge } from '../../../ui/PriorityBadge/PriorityBadge';
import { Input } from '../../../ui/Input/Input';
import { TICKET_STATUS_OPTIONS, TICKET_PRIORITY_OPTIONS } from '../../../../../config/enums';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';
import { Button } from '../../../ui/Button/Button';
import { useToast } from '../../../../../context/ToastContext';
import styles from './SupportTicketModal.module.css';

export const SupportTicketModal = ({ ticket, onClose, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [responseMsg, setResponseMsg] = useState('');
  const [responses, setResponses] = useState([]);
  const { showInfo } = useToast();

  if (!ticket) return null;

  useEffect(() => {
    if (ticket && (ticket.status === 'New' || ticket.status === 'Unread')) {
      adminApi.updateTicket(ticket.id, { status: 'Open' }).then(() => onUpdate());
    }
    
    // Fetch responses for this ticket
    if (ticket) {
      api.get(`/ticket_responses?ticket_id=${ticket.id}`).then(res => {
        setResponses(res || []);
      }).catch(err => console.error("Failed to fetch responses", err));
    }
  }, [ticket, onUpdate]);

  const handleStatusChange = async (e) => {
    const newStatus = e.target.value;
    if (newStatus === ticket.status) return;
    
    setLoading(true);
    try {
      await adminApi.updateTicket(ticket.id, { status: newStatus });
      onUpdate();
    } catch (error) {
      console.error("Failed to update status", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePriorityChange = async (e) => {
    const newPriority = e.target.value;
    if (newPriority === ticket.priority) return;
    
    setLoading(true);
    try {
      await adminApi.updateTicket(ticket.id, { priority: newPriority });
      onUpdate();
    } catch (error) {
      console.error("Failed to update priority", error);
    } finally {
      setLoading(false);
    }
  };

  const handleResponseSubmit = async (e) => {
    e.preventDefault();
    if (ticket.status === 'Closed') {
      showInfo('This ticket is closed. Reopen it before responding.');
      return;
    }
    if (!responseMsg.trim()) {
      showInfo('Please type a help message before sending.');
      return;
    }

    setLoading(true);
    try {
      await adminApi.respondToTicket(ticket.id, responseMsg);
      // Auto-mark as Closed when admin responds
      if (ticket.status !== 'Closed') {
        await adminApi.updateTicket(ticket.id, { status: 'Closed' });
      }
      // Re-fetch responses to show the newly sent one immediately
      const newResps = await api.get(`/ticket_responses?ticket_id=${ticket.id}`);
      setResponses(newResps || []);
      
      onUpdate();
    } catch (error) {
      console.error("Failed to send response", error);
    } finally {
      setLoading(false);
      setResponseMsg('');
    }
  };

  const modalContent = (
    <AnimatePresence>
      {ticket && (
        <div className={styles.overlay} onClick={onClose}>
          <motion.div 
            className={styles.modal} 
            onClick={e => e.stopPropagation()}
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
          >
            <div className={styles.header}>
          <div className={styles.headerTitle}>
            <span className={styles.ticketId}>#{ticket.id}</span>
            <h3>{ticket.title}</h3>
          </div>
          <button className={styles.closeBtn} onClick={onClose}>
            <Icon icon={uiIcons.close} width="24" />
          </button>
        </div>

        <div className={styles.body}>
          <div className={styles.infoBar}>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Status</span>
              <Dropdown 
                name="status"
                value={ticket.status} 
                onChange={handleStatusChange}
                disabled={loading}
                options={TICKET_STATUS_OPTIONS}
              />
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Priority</span>
              <Dropdown 
                name="priority"
                value={ticket.priority || 'Medium'} 
                onChange={handlePriorityChange} 
                disabled={loading}
                options={TICKET_PRIORITY_OPTIONS}
              />
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Type</span>
              <span className={styles.infoValue}>{ticket.ticket_type}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Created</span>
              <span className={styles.infoValue}>{new Date(ticket.created_at).toLocaleString()}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Raised By</span>
              <span className={styles.infoValue}>
                {ticket.raised_by_user ? `${ticket.raised_by_user.full_name} (${ticket.raised_by_user.email})` : `#${ticket.raised_by}`}
              </span>
            </div>
          </div>

          <div className={styles.descriptionBox}>
            <h4>Description</h4>
            <p>{ticket.description}</p>
          </div>
          
          <div className={styles.responsesHistory}>
            <h4>Responses</h4>
            {responses.length === 0 ? (
              <p className={styles.noResponses}>No responses yet.</p>
            ) : (
              <div className={styles.responsesList}>
                {responses.map(resp => (
                  <div key={resp.id} className={styles.responseCard}>
                    <div className={styles.responseHeader}>
                      <span>{resp.responder_id === 7 ? 'Admin' : 'Support'}</span>
                      <small>{new Date(resp.created_at).toLocaleString()}</small>
                    </div>
                    <div className={styles.responseBody}>{resp.message}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className={styles.responseSection}>
            <h4>Respond to User</h4>
            <form onSubmit={handleResponseSubmit} className={styles.responseForm}>
              <Input 
                as="textarea"
                placeholder="Type your response here..." 
                value={responseMsg}
                onChange={(e) => setResponseMsg(e.target.value)}
                disabled={loading || ticket.status === 'Closed'}
                rows="4"
              />
              <div className={styles.formActions}>
                <Button 
                  type="submit" 
                  variant="primary"
                >
                  {loading ? <Icon icon={uiIcons.loading} className="spin" /> : <Icon icon={adminIcons.send} />}
                  Send Response
                </Button>
              </div>
            </form>
          </div>
        </div>
        </motion.div>
      </div>
      )}
    </AnimatePresence>
  );

  return typeof document !== 'undefined' ? createPortal(modalContent, document.body) : null;
};
