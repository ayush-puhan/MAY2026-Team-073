import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import { StatusBadge } from '../../../ui/StatusBadge/StatusBadge';
import { facultyAdvisorApi } from '@api/facultyAdvisorApis/facultyAdvisor';
import { useSession } from '../../../../../context/SessionContext';
import styles from './ClubDetailModal.module.css';
import { uiIcons } from '../../../../icons/registry';

export const ClubDetailModal = ({ clubId, onClose }) => {
  const { user } = useSession();
  const [club, setClub] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editingBudget, setEditingBudget] = useState(false);
  const [budgetAmount, setBudgetAmount] = useState('');

  const fetchClub = () => {
    setLoading(true);
    facultyAdvisorApi.getClubDetail(clubId).then((data) => {
      setClub(data);
      if (data.mainBudget) {
        setBudgetAmount(data.mainBudget.allocated_amount);
      }
      setLoading(false);
    });
  };

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    fetchClub();
    return () => { document.body.style.overflow = 'auto'; };
  }, [clubId]);

  const handleSaveBudget = async (e) => {
    e.preventDefault();
    try {
      await facultyAdvisorApi.setClubBudget(clubId, budgetAmount, user.id);
      setEditingBudget(false);
      fetchClub();
    } catch (err) {
      alert("Failed to save budget");
    }
  };

  const content = (
    <AnimatePresence>
      <div className={styles.overlay} onClick={onClose}>
        <motion.div
          className={styles.modal}
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
        >
          <button className={styles.closeBtn} onClick={onClose}>
            <Icon icon={uiIcons.close} />
          </button>

          {loading || !club ? (
            <div className={styles.loading}>
              <Icon icon={uiIcons.loading} className="animate-spin" width="28" />
            </div>
          ) : (
            <>
              <div className={styles.header}>
                <h3 className={styles.title}>{club.name}</h3>
                <StatusBadge status={club.status} />
              </div>
              <p className={styles.description}>{club.description}</p>

              <div className={styles.section}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4 className={styles.sectionTitle}>Club Budget (Annual)</h4>
                  {!editingBudget && (
                    <button 
                      onClick={() => setEditingBudget(true)}
                      style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600 }}
                    >
                      {club.mainBudget ? 'Edit Budget' : 'Set Budget'}
                    </button>
                  )}
                </div>
                
                {editingBudget ? (
                  <form onSubmit={handleSaveBudget} style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                    <input 
                      type="number" 
                      step="0.01"
                      min="0"
                      value={budgetAmount}
                      onChange={e => setBudgetAmount(e.target.value)}
                      placeholder="Amount ($)"
                      required
                      style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--text)' }}
                    />
                    <button type="submit" style={{ padding: '0.5rem 1rem', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                      Save
                    </button>
                    <button type="button" onClick={() => setEditingBudget(false)} style={{ padding: '0.5rem 1rem', background: 'transparent', color: 'var(--text)', border: '1px solid var(--border)', borderRadius: '4px', cursor: 'pointer' }}>
                      Cancel
                    </button>
                  </form>
                ) : (
                  <div style={{ marginTop: '0.5rem', fontSize: '1.2rem', fontWeight: 600, color: club.mainBudget ? 'var(--text)' : 'var(--muted-foreground)' }}>
                    {club.mainBudget ? `$${parseFloat(club.mainBudget.allocated_amount).toFixed(2)}` : 'No budget allocated yet.'}
                  </div>
                )}
              </div>

              <div className={styles.section}>
                <h4 className={styles.sectionTitle}>Members ({club.members?.length || 0})</h4>
                <div className={styles.memberList}>
                  {(club.members || []).map((m) => (
                    <div key={m.id} className={styles.memberRow}>
                      <span>{m.user_name}</span>
                      <span className={styles.memberRole}>{m.role_in_club}</span>
                    </div>
                  ))}
                  {(!club.members || club.members.length === 0) && (
                    <p className={styles.emptyText}>No approved members yet.</p>
                  )}
                </div>
              </div>

              <div className={styles.section}>
                <h4 className={styles.sectionTitle}>Committees</h4>
                {(club.committees || []).length === 0 ? (
                  <p className={styles.emptyText}>No committees set up yet.</p>
                ) : (
                  club.committees.map((c) => (
                    <div key={c.id} className={styles.memberRow}>
                      <span>{c.name}</span>
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );

  return createPortal(content, document.body);
};
