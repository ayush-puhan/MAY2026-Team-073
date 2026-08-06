import React, { useState, useEffect } from 'react';
import { useOutletContext, Navigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/backendApis/clubsApis/clubs';
import { canManageBudget, canApproveExpenses, canViewBudget } from '../../../../../utils/clubPermissions';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import styles from './ClubBudgetView.module.css';
import { Input } from '../../../ui/Input/Input';
import { Button } from '../../../ui/Button/Button';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import { DataTable } from '../../../ui/DataTable/DataTable';
import { uiIcons } from '../../../../icons/registry';

const ClubBudgetView = () => {
  const { club, userRole, currentUserId } = useOutletContext();
  const [budgets, setBudgets] = useState([]);
  const [committees, setCommittees] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  if (!canViewBudget(userRole) && userRole !== 'system_admin') {
    return <Navigate to={`/clubs/${club?.id || ''}`} replace />;
  }

  // Forms
  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [showAllocateForm, setShowAllocateForm] = useState(false);
  
  const [newDesc, setNewDesc] = useState('');
  const [newAmount, setNewAmount] = useState('');
  const [newCategory, setNewCategory] = useState('');
  
  const [allocCommittee, setAllocCommittee] = useState('');
  const [allocAmount, setAllocAmount] = useState('');
  const [allocTitle, setAllocTitle] = useState('');

  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  useEffect(() => {
    fetchData();
  }, [club.id]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [fetchedBudgets, fetchedExpenses, fetchedCommittees] = await Promise.all([
        clubsApi.getClubBudgets(club.id),
        clubsApi.getClubExpenses(club.id),
        clubsApi.getClubCommittees(club.id)
      ]);
      setBudgets(fetchedBudgets);
      setExpenses(fetchedExpenses);
      setCommittees(fetchedCommittees);
    } catch (err) {
      console.error(err);
      setError('Failed to load budget data.');
    } finally {
      setLoading(false);
    }
  };

  const mainBudget = budgets.find(b => !b.committee_id && !b.parent_budget_id) || budgets[0];
  const subBudgets = budgets.filter(b => b.committee_id);

  const handleCreateExpense = async (e) => {
    e.preventDefault();
    if (!newDesc || !newAmount) return;
    
    if (!mainBudget) {
      alert("No active main budget found for this club.");
      return;
    }

    try {
      await clubsApi.createExpense({
        budget_id: mainBudget.id,
        description: newDesc,
        amount: parseFloat(newAmount),
        category: newCategory
      });
      setShowExpenseForm(false);
      setNewDesc('');
      setNewAmount('');
      setNewCategory('');
      fetchData();
    } catch (err) {
      alert("Failed to create expense request");
    }
  };

  const handleAllocateBudget = async (e) => {
    e.preventDefault();
    if (!allocCommittee || !allocAmount || !allocTitle) return;
    
    if (!mainBudget) {
      alert("No active main budget found to allocate from.");
      return;
    }

    try {
      await clubsApi.allocateCommitteeBudget(
        club.id,
        allocCommittee,
        {
          title: allocTitle,
          allocated_amount: parseFloat(allocAmount),
          created_by: currentUserId,
          parent_budget_id: mainBudget.id,
        }
      );
      setShowAllocateForm(false);
      setAllocCommittee('');
      setAllocAmount('');
      setAllocTitle('');
      fetchData();
    } catch (err) {
      alert("Failed to allocate budget");
    }
  };

  const handleApprove = async (expenseId) => {
    if (!window.confirm(`Approve this expense as ${userRole}?`)) return;
    try {
      await clubsApi.approveExpense(expenseId, currentUserId, userRole);
      fetchData();
    } catch (err) {
      alert(err.message || "Failed to approve expense");
    }
  };

  if (loading) return <div className={styles.loading}>Loading budget...</div>;
  if (error) return <div className={styles.error}>{error}</div>;

  const totalAllocated = mainBudget ? parseFloat(mainBudget.allocated_amount || 0) : 0;
  
  const mainExpenses = expenses.filter(e => e.budget_id === mainBudget?.id);
  const totalClubSpent = mainExpenses
    .filter(e => (e.status || '').toLowerCase() === 'approved')
    .reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
    
  const totalAllocatedToCommittees = subBudgets.reduce((sum, b) => sum + parseFloat(b.allocated_amount || 0), 0);
  
  const remaining = totalAllocated - totalClubSpent - totalAllocatedToCommittees;

  const showAdvancedFilters = ['treasurer', 'vice_president', 'president'].includes(userRole);

  const filteredExpenses = expenses.filter(e => {
    if (statusFilter && (e.status || '').toLowerCase() !== statusFilter.toLowerCase()) return false;
    if (categoryFilter && (e.category || '').toLowerCase() !== categoryFilter.toLowerCase()) return false;
    return true;
  });

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent}>
        <div className={styles.container}>
          <header className={styles.header}>
            <div>
              <h2>Budget & Finance</h2>
              <p>Track allocated funds and manage expenses for {club.name}</p>
            </div>
            <div style={{display: 'flex', gap: '1rem'}}>
              {canManageBudget(userRole) && (
                <Button variant="outline" onClick={() => setShowAllocateForm(true)}>
                  <Icon icon="mdi:bank-transfer" />
                  Allocate to Committee
                </Button>
              )}
              {canManageBudget(userRole) && (
                <Button onClick={() => setShowExpenseForm(true)}>
                  <Icon icon="mdi:receipt-text-plus" />
                  Submit Club Expense
                </Button>
              )}
            </div>
          </header>

          <div className={styles.summaryCards}>
            <div className={styles.card}>
              <div className={styles.cardIcon} style={{color: 'var(--primary)', backgroundColor: 'rgba(var(--primary-rgb), 0.1)'}}>
                <Icon icon={uiIcons.bankOutline} />
              </div>
              <div className={styles.cardContent}>
                <h4>Total Club Budget</h4>
                <div className={styles.cardValue}>${totalAllocated.toFixed(2)}</div>
              </div>
            </div>
            <div className={styles.card}>
              <div className={styles.cardIcon} style={{color: '#8b5cf6', backgroundColor: 'rgba(139, 92, 246, 0.1)'}}>
                <Icon icon="mdi:bank-transfer" />
              </div>
              <div className={styles.cardContent}>
                <h4>Allocated to Committees</h4>
                <div className={styles.cardValue}>${totalAllocatedToCommittees.toFixed(2)}</div>
              </div>
            </div>
            <div className={styles.card}>
              <div className={styles.cardIcon} style={{color: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)'}}>
                <Icon icon={uiIcons.cashMinus} />
              </div>
              <div className={styles.cardContent}>
                <h4>Spent (Direct)</h4>
                <div className={styles.cardValue}>${totalClubSpent.toFixed(2)}</div>
              </div>
            </div>
            <div className={styles.card}>
              <div className={styles.cardIcon} style={{color: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)'}}>
                <Icon icon={uiIcons.cashCheck} />
              </div>
              <div className={styles.cardContent}>
                <h4>Remaining Club Balance</h4>
                <div className={styles.cardValue}>${remaining.toFixed(2)}</div>
              </div>
            </div>
          </div>

          {showExpenseForm && (
            <div className={styles.modalOverlay}>
              <div className={styles.modal}>
                <form className={styles.createForm} onSubmit={handleCreateExpense}>
                  <h3>Submit Club Expense</h3>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                      <Input 
                        label="Amount ($)" 
                        type="number" 
                        step="0.01" 
                        min="0" 
                        value={newAmount} 
                        onChange={e => setNewAmount(e.target.value)} 
                        required 
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <Dropdown 
                        label="Category" 
                        value={newCategory} 
                        onChange={val => setNewCategory(val)} 
                        options={[
                          { value: "", label: "Select..." },
                          { value: "Food & Beverages", label: "Food & Beverages" },
                          { value: "Event Supplies", label: "Event Supplies" },
                          { value: "Marketing", label: "Marketing" },
                          { value: "Travel", label: "Travel" },
                          { value: "Other", label: "Other" }
                        ]}
                      />
                    </div>
                    <div className={styles.formGroup} style={{gridColumn: '1 / -1'}}>
                      <Input 
                        label="Description / Justification" 
                        type="text" 
                        value={newDesc} 
                        onChange={e => setNewDesc(e.target.value)} 
                        required 
                      />
                    </div>
                  </div>
                  <div className={styles.formActions}>
                    <Button variant="outline" onClick={() => setShowExpenseForm(false)} type="button">Cancel</Button>
                    <Button type="submit" variant="primary">Submit Request</Button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {showAllocateForm && (
            <div className={styles.modalOverlay}>
              <div className={styles.modal}>
                <form className={styles.createForm} onSubmit={handleAllocateBudget}>
                  <h3>Allocate Budget to Committee</h3>
                  <div className={styles.formGrid}>
                    <div className={styles.formGroup} style={{gridColumn: '1 / -1'}}>
                      <Dropdown 
                        label="Select Committee" 
                        value={allocCommittee} 
                        onChange={val => setAllocCommittee(val)} 
                        options={[
                          { value: "", label: "Select..." },
                          ...committees.map(c => ({ value: c.id, label: c.name }))
                        ]}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <Input 
                        label="Allocation Title" 
                        type="text" 
                        value={allocTitle} 
                        onChange={e => setAllocTitle(e.target.value)} 
                        required 
                        placeholder="e.g. Fall Event Budget"
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <Input 
                        label="Amount ($)" 
                        type="number" 
                        step="0.01" 
                        min="0" 
                        max={remaining}
                        value={allocAmount} 
                        onChange={e => setAllocAmount(e.target.value)} 
                        required 
                      />
                    </div>
                  </div>
                  <div className={styles.formActions}>
                    <Button variant="outline" onClick={() => setShowAllocateForm(false)} type="button">Cancel</Button>
                    <Button type="submit" variant="primary">Allocate Budget</Button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {subBudgets.length > 0 && (
            <div className={styles.tableContainer} style={{ marginBottom: '2rem' }}>
              <div className={styles.tableHeader}>
                <h3>Allocated Sub-Budgets</h3>
              </div>
              <DataTable
                columns={[
                  {
                    header: 'Date Allocated',
                    cell: (row) => new Date(row.created_at).toLocaleDateString()
                  },
                  {
                    header: 'Committee',
                    cell: (row) => {
                      const committee = committees.find(c => String(c.id) === String(row.committee_id));
                      return <span className={styles.committeeBadge}>{committee ? committee.name : 'Unknown'}</span>;
                    }
                  },
                  { header: 'Title', accessor: 'title' },
                  {
                    header: 'Amount',
                    cell: (row) => `$${parseFloat(row.allocated_amount).toFixed(2)}`
                  }
                ]}
                data={subBudgets}
                emptyIcon="mdi:bank-transfer"
                emptyTitle="No Allocations"
                emptyDesc="No budget has been allocated to committees yet."
              />
            </div>
          )}

          <div className={styles.tableContainer}>
            <div className={styles.tableHeader}>
              <h3>All Expenses (Club & Committees)</h3>
              {showAdvancedFilters && (
                <div className={styles.filters}>
                  <Dropdown 
                    value={statusFilter} 
                    onChange={val => setStatusFilter(val.toString())} 
                    options={[
                      { value: "", label: "All Statuses" },
                      { value: "pending", label: "Pending" },
                      { value: "approved", label: "Approved" },
                      { value: "rejected", label: "Rejected" }
                    ]}
                  />
                  <Dropdown 
                    value={categoryFilter} 
                    onChange={val => setCategoryFilter(val.toString())} 
                    options={[
                      { value: "", label: "All Categories" },
                      { value: "Food & Beverages", label: "Food & Beverages" },
                      { value: "Event Supplies", label: "Event Supplies" },
                      { value: "Marketing", label: "Marketing" },
                      { value: "Travel", label: "Travel" },
                      { value: "Other", label: "Other" }
                    ]}
                  />
                </div>
              )}
            </div>
            
            <DataTable
              columns={[
                {
                  header: 'Date',
                  cell: (row) => new Date(row.created_at).toLocaleDateString()
                },
                {
                  header: 'Source',
                  cell: (row) => {
                    const committee = committees.find(c => String(c.id) === String(row.budget?.committee_id));
                    return committee ? (
                      <span className={styles.committeeBadge}>{committee.name}</span>
                    ) : (
                      <span className={styles.clubBadge}>Club Main</span>
                    );
                  }
                },
                { header: 'Description', accessor: 'description' },
                { header: 'Category', accessor: 'category' },
                {
                  header: 'Amount',
                  cell: (row) => `$${parseFloat(row.amount).toFixed(2)}`
                },
                {
                  header: 'Status',
                  cell: (row) => {
                    const st = (row.status || '').toLowerCase();
                    if (st === 'pending') {
                      return (
                        <div style={{display: 'flex', gap: '4px', flexDirection: 'column'}}>
                          <span className={`${styles.statusBadge} ${row.treasurer_approved ? styles.approved : styles.pending}`}>
                            Treasurer: {row.treasurer_approved ? 'Yes' : 'No'}
                          </span>
                          <span className={`${styles.statusBadge} ${row.president_approved ? styles.approved : styles.pending}`}>
                            President: {row.president_approved ? 'Yes' : 'No'}
                          </span>
                        </div>
                      );
                    }
                    return (
                      <span className={`${styles.statusBadge} ${styles[st]}`}>
                        {st.toUpperCase()}
                      </span>
                    );
                  }
                },
                ...(canApproveExpenses(userRole) ? [{
                  header: 'Actions',
                  cell: (row) => {
                    const st = (row.status || '').toLowerCase();
                    if (st === 'pending') {
                      if ((userRole === 'treasurer' && !row.treasurer_approved) || 
                          (userRole === 'president' && !row.president_approved)) {
                        return (
                          <Button variant="primary" size="small" icon={uiIcons.checkCircle} onClick={() => handleApprove(row.id)}>
                            Approve
                          </Button>
                        );
                      }
                      return (
                        <span className={styles.approvedText}>
                          Waiting on {userRole === 'treasurer' ? 'President' : 'Treasurer'}
                        </span>
                      );
                    }
                    return <span className={styles.approvedText}>Approved</span>;
                  }
                }] : [])
              ]}
              data={filteredExpenses}
              emptyIcon="mdi:receipt-text-outline"
              emptyTitle="No Expenses"
              emptyDesc="No expenses have been recorded yet."
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClubBudgetView;
