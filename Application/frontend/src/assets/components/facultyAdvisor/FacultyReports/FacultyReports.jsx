import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { FilterTabs } from '../../ui/FilterTabs/FilterTabs';
import { Button } from '../../ui/Button/Button';
import { facultyAdvisorApi } from '../../../../api/facultyAdvisor.api';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import styles from './FacultyReports.module.css';

export const FacultyReports = () => {
  const { user } = useSession();
  const { showSuccess, showError } = useToast();
  const [expenses, setExpenses] = useState([]);
  const [activeTab, setActiveTab] = useState('pending');
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);

  const loadExpenses = async () => {
    setLoading(true);
    const data = await facultyAdvisorApi.getExpenses(user.id);
    setExpenses(data);
    setLoading(false);
  };

  useEffect(() => { loadExpenses(); }, [user.id]);

  const filtered = expenses.filter((e) => e.approval_status === activeTab);
  const tabs = [
    { value: 'pending', label: 'Pending', count: expenses.filter((e) => e.approval_status === 'pending').length },
    { value: 'approved', label: 'Approved', count: expenses.filter((e) => e.approval_status === 'approved').length },
    { value: 'rejected', label: 'Rejected', count: expenses.filter((e) => e.approval_status === 'rejected').length },
  ];

  const decide = async (id, approval_status) => {
    setBusyId(id);
    try {
      await facultyAdvisorApi.decideExpense(id, {
        approval_status,
        approval_remarks: approval_status === 'approved' ? 'Approved by faculty advisor.' : 'Rejected by faculty advisor.',
        approved_by: user.id,
      });
      showSuccess(`Expense ${approval_status}.`);
      loadExpenses();
    } catch (err) {
      showError(err.message || 'Failed to update expense.');
    } finally {
      setBusyId(null);
    }
  };

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
        <h2 className={styles.title}>Financial Oversight</h2>
        <p className={styles.subtitle}>Review budgets and expenses submitted by your advised clubs.</p>
      </div>

      <FilterTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      <DataTable
        columns={[
          { header: 'Description', accessor: 'description' },
          { header: 'Budget', accessor: 'budget_title' },
          { header: 'Category', accessor: 'category' },
          { header: 'Amount', cell: (row) => `₹${row.amount}` },
          { header: 'Status', cell: (row) => <StatusBadge status={row.approval_status} /> },
          {
            header: '',
            cell: (row) => row.approval_status === 'pending' ? (
              <div className={styles.rowActions}>
                <Button size="sm" variant="outline" isLoading={busyId === row.id} onClick={() => decide(row.id, 'rejected')}>Reject</Button>
                <Button size="sm" variant="primary" isLoading={busyId === row.id} onClick={() => decide(row.id, 'approved')}>Approve</Button>
              </div>
            ) : null,
          },
        ]}
        data={filtered}
        emptyIcon="mdi:cash-multiple"
        emptyTitle={`No ${activeTab} expenses`}
      />
    </div>
  );
};
