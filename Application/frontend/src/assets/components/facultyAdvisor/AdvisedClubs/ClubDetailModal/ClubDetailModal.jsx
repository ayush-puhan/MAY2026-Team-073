import React, { useState, useEffect, useMemo } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import { StatusBadge } from '../../../ui/StatusBadge/StatusBadge';
import { facultyAdvisorApi } from '@api/facultyAdvisorApis/facultyAdvisor';
import { clubBudgetApi } from '@api/clubBudgetApis/clubBudgetApi';
import { useSession } from '../../../../../context/SessionContext';
import { BudgetStep } from './BudgetStep/BudgetStep';
import { MembersStep } from './MembersStep/MembersStep';
import { CommitteesStep } from './CommitteesStep/CommitteesStep';
import styles from './ClubDetailModal.module.css';
import { uiIcons, dashboardIcons } from '../../../../icons/registry';

const STEPS = [
  { id: 'budget', label: 'Budget', icon: dashboardIcons.cashMultiple },
  { id: 'members', label: 'Members', icon: dashboardIcons.accountGroupOutline },
  { id: 'committees', label: 'Committees', icon: dashboardIcons.committeeTasks },
];

export const ClubDetailModal = ({ clubId, onClose }) => {
  const { user } = useSession();
  const [club, setClub] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState(0);

  const [editingBudget, setEditingBudget] = useState(false);
  const [budgetAmount, setBudgetAmount] = useState('');
  const [savingBudget, setSavingBudget] = useState(false);

  const [memberSearch, setMemberSearch] = useState('');
  const [committeeSearch, setCommitteeSearch] = useState('');

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
    setSavingBudget(true);
    try {
      await clubBudgetApi.setClubBudget(clubId, budgetAmount, user.id);
      setEditingBudget(false);
      fetchClub();
    } catch (err) {
      console.error('[handleSaveBudget] error:', err);
      alert('Failed to save budget: ' + (err?.message || 'Unknown error'));
    } finally {
      setSavingBudget(false);
    }
  };

  const filteredMembers = useMemo(() => {
    const members = club?.members || [];
    if (!memberSearch) return members;
    const q = memberSearch.toLowerCase();
    return members.filter((m) => m.user_name?.toLowerCase().includes(q));
  }, [club, memberSearch]);

  const filteredCommittees = useMemo(() => {
    const committees = club?.committees || [];
    if (!committeeSearch) return committees;
    const q = committeeSearch.toLowerCase();
    return committees.filter((c) => c.name?.toLowerCase().includes(q));
  }, [club, committeeSearch]);

  const content = (
    <AnimatePresence>
      <div className={styles.overlay}>
        <motion.div
          className={styles.backdrop}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        />
        <motion.div
          className={styles.modal}
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          transition={{ duration: 0.2 }}
        >
          {loading || !club ? (
            <div className={styles.loading}>
              <Icon icon={uiIcons.loading} className="animate-spin" width="28" />
            </div>
          ) : (
            <>
              <div className={styles.header}>
                <div className={styles.headerInfo}>
                  <div className={styles.headerTitleRow}>
                    <h3>{club.name}</h3>
                    <StatusBadge status={club.status} />
                  </div>
                  <p className={styles.description}>{club.description}</p>
                </div>
                <button className={styles.closeBtn} onClick={onClose}>
                  <Icon icon={uiIcons.close} />
                </button>
              </div>

              <div className={styles.tabs}>
                {STEPS.map((step, idx) => (
                  <button
                    key={step.id}
                    className={`${styles.tabBtn} ${currentStep === idx ? styles.activeTab : ''}`}
                    onClick={() => setCurrentStep(idx)}
                  >
                    <span className={styles.stepNumber}>{idx + 1}</span>
                    <span>{step.label}</span>
                  </button>
                ))}
              </div>

              <div className={styles.content}>
                <AnimatePresence mode="wait">
                  {currentStep === 0 && (
                    <BudgetStep
                      club={club}
                      editingBudget={editingBudget}
                      setEditingBudget={setEditingBudget}
                      budgetAmount={budgetAmount}
                      setBudgetAmount={setBudgetAmount}
                      savingBudget={savingBudget}
                      onSaveBudget={handleSaveBudget}
                    />
                  )}
                  {currentStep === 1 && (
                    <MembersStep
                      club={club}
                      filteredMembers={filteredMembers}
                      onSearch={setMemberSearch}
                    />
                  )}
                  {currentStep === 2 && (
                    <CommitteesStep
                      club={club}
                      filteredCommittees={filteredCommittees}
                      onSearch={setCommitteeSearch}
                    />
                  )}
                </AnimatePresence>
              </div>
            </>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );

  return createPortal(content, document.body);
};
