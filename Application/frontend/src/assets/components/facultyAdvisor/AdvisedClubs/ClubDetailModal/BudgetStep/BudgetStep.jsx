import React from 'react';
import { motion } from 'framer-motion';
import styles from '../ClubDetailModal.module.css';

export const BudgetStep = ({
  club,
  editingBudget,
  setEditingBudget,
  budgetAmount,
  setBudgetAmount,
  savingBudget,
  onSaveBudget,
}) => {
  return (
    <motion.div
      key="budget"
      initial={{ opacity: 0, x: 8 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -8 }}
      transition={{ duration: 0.15 }}
      className={styles.section}
    >
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
        <form onSubmit={onSaveBudget} style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="number"
            step="0.01"
            min="0"
            value={budgetAmount}
            onChange={(e) => setBudgetAmount(e.target.value)}
            placeholder="Amount (₹)"
            required
            style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--text)' }}
          />
          <button type="submit" disabled={savingBudget} style={{ padding: '0.5rem 1rem', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            {savingBudget ? 'Saving...' : 'Save'}
          </button>
          <button type="button" onClick={() => setEditingBudget(false)} style={{ padding: '0.5rem 1rem', background: 'transparent', color: 'var(--text)', border: '1px solid var(--border)', borderRadius: '4px', cursor: 'pointer' }}>
            Cancel
          </button>
        </form>
      ) : (
        <div style={{ fontSize: '1.2rem', fontWeight: 600, color: club.mainBudget ? 'var(--text)' : 'var(--muted-foreground)' }}>
          {club.mainBudget ? `₹${parseFloat(club.mainBudget.allocated_amount).toFixed(2)}` : 'No budget allocated yet.'}
        </div>
      )}

      <div className={styles.statLine}>
        <span className={styles.statValue}>{club.members?.length || 0}</span>
        <span className={styles.statLabel}>approved members</span>
      </div>
    </motion.div>
  );
};
