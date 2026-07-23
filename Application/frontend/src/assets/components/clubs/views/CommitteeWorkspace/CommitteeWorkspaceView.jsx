import React, { useState, useEffect } from 'react';
import { useOutletContext, useParams, useNavigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/mockbackendApis/clubsApis/clubs';
import { hasCommitteePermission, canManageCommittees } from '../../../../../utils/clubPermissions';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import styles from './CommitteeWorkspaceView.module.css';
import { Button } from '../../../ui/Button/Button';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import { SecondaryHeader } from '../../../ui/SecondaryHeader/SecondaryHeader';
import { EmptyState } from '../../../ui/EmptyState/EmptyState';
import { DataTable } from '../../../ui/DataTable/DataTable';
import { dashboardIcons, uiIcons, rewardsIcons } from '../../../../icons/registry';

// Subcomponents for tabs
const CommitteeOverview = ({ committee }) => (
  <div style={{ marginTop: '1.5rem' }}>
    <p style={{ fontSize: '1.1rem', color: 'var(--text)', lineHeight: 1.6 }}>{committee?.description || 'No description provided.'}</p>
  </div>
);

const CommitteeMembers = ({ 
  committee, 
  members, 
  clubMembers, 
  onAddMember, 
  onRemoveMember, 
  onUpdateRole, 
  canManage 
}) => {
  const [newMemberId, setNewMemberId] = useState('');

  const handleAdd = () => {
    if (newMemberId) {
      onAddMember(newMemberId);
      setNewMemberId('');
    }
  };

  return (
    <div style={{ marginTop: '1.5rem' }}>
      {canManage && (
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', alignItems: 'center' }}>
          <div style={{ flex: 1, maxWidth: '300px' }}>
            <Dropdown 
              value={newMemberId}
              onChange={setNewMemberId}
              options={[
                { value: "", label: "-- Select Member --" },
                ...clubMembers
                  .filter(cm => cm.status === 'approved' && !members.find(m => String(m.membership_id) === String(cm.id)))
                  .map(cm => ({
                    value: cm.id,
                    label: cm.user?.full_name || 'Unknown User'
                  }))
              ]}
            />
          </div>
          <Button variant="primary" onClick={handleAdd} disabled={!newMemberId}>Add Member</Button>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {members.length > 0 ? (
          members.map(m => (
            <div key={m.id} style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '1rem', backgroundColor: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '8px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Icon icon={rewardsIcons.account} style={{ color: 'var(--muted-foreground)', fontSize: '1.5rem' }} />
                <span style={{ fontWeight: 500 }}>{m.user?.first_name || 'Member'} {m.user?.last_name || ''}</span>
              </div>
              
              {canManage ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <Dropdown 
                    value={m.role}
                    onChange={(val) => onUpdateRole(m.id, val)}
                    options={[
                      { value: 'head', label: 'Head' },
                      { value: 'co_head', label: 'Co-Head' },
                      { value: 'member', label: 'Member' }
                    ]}
                  />
                  <Button variant="ghost" icon={uiIcons.deleteOutline} onClick={() => onRemoveMember(m.id)} style={{ color: 'var(--destructive)', padding: '0.5rem' }} />
                </div>
              ) : (
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--muted-foreground)' }}>
                  {m.role?.replace('_', ' ').toUpperCase() || 'MEMBER'}
                </span>
              )}
            </div>
          ))
        ) : (
          <EmptyState icon={dashboardIcons.accountGroupOutline} title="No Members" description="This committee has no members." />
        )}
      </div>
    </div>
  );
};

const CommitteeTasks = ({ tasks }) => (
  <div style={{ marginTop: '1.5rem' }}>
    {tasks.length > 0 ? (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {tasks.map(t => (
          <div key={t.id} style={{ padding: '1rem', border: '1px solid var(--border)', borderRadius: '8px', background: 'var(--surface)' }}>
            <h4 style={{ margin: '0 0 0.5rem 0' }}>{t.task_description}</h4>
            <span style={{ fontSize: '0.85rem', color: 'var(--muted-foreground)' }}>Status: {t.status}</span>
          </div>
        ))}
      </div>
    ) : (
      <EmptyState icon={uiIcons.clipboardCheckOutline} title="No Tasks" description="No tasks assigned to this committee." />
    )}
  </div>
);

const CommitteeResources = ({ resources }) => (
  <div style={{ marginTop: '1.5rem' }}>
    {resources.length > 0 ? (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {resources.map(r => (
          <div key={r.id} style={{ padding: '1rem', border: '1px solid var(--border)', borderRadius: '8px', background: 'var(--surface)' }}>
            <h4 style={{ margin: '0 0 0.5rem 0' }}>{r.title}</h4>
            <a href={r.file_url} target="_blank" rel="noreferrer" style={{ fontSize: '0.9rem', color: 'var(--primary)' }}>View Document</a>
          </div>
        ))}
      </div>
    ) : (
      <EmptyState icon={uiIcons.folderOutline} title="No Resources" description="No resources uploaded for this committee." />
    )}
  </div>
);

const CommitteeBudgets = ({ committeeId, clubId, currentUserId, canManageThis }) => {
  const [budgets, setBudgets] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newDesc, setNewDesc] = useState('');
  const [newAmount, setNewAmount] = useState('');

  const fetchData = async () => {
    try {
      const [fetchedBudgets, fetchedExpenses] = await Promise.all([
        clubsApi.getCommitteeBudgets(clubId, committeeId),
        clubsApi.getClubExpenses(clubId)
      ]);
      setBudgets(fetchedBudgets);
      
      const bIds = fetchedBudgets.map(b => String(b.id));
      setExpenses(fetchedExpenses.filter(e => bIds.includes(String(e.budget_id))));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [clubId, committeeId]);

  const handleCreateExpense = async (e) => {
    e.preventDefault();
    if (!newDesc || !newAmount) return;
    
    if (budgets.length === 0) {
      alert("No active budget assigned to this committee.");
      return;
    }

    try {
      await clubsApi.createExpense(budgets[0].id, {
        description: newDesc,
        amount: parseFloat(newAmount),
        category: 'Committee Expense'
      }, currentUserId);
      setNewDesc('');
      setNewAmount('');
      fetchData();
    } catch (err) {
      alert("Failed to create expense request");
    }
  };

  if (loading) return <div>Loading budget...</div>;

  const totalAllocated = budgets.reduce((sum, b) => sum + parseFloat(b.allocated_amount || 0), 0);
  const totalSpent = expenses.filter(e => (e.status || '').toLowerCase() === 'approved').reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
  const remaining = totalAllocated - totalSpent;

  return (
    <div style={{ marginTop: '1.5rem' }}>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ flex: 1, padding: '1.5rem', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '8px' }}>
          <h4 style={{ color: 'var(--muted-foreground)', margin: '0 0 0.5rem 0', fontSize: '0.9rem', textTransform: 'uppercase' }}>Allocated</h4>
          <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>${totalAllocated.toFixed(2)}</div>
        </div>
        <div style={{ flex: 1, padding: '1.5rem', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '8px' }}>
          <h4 style={{ color: 'var(--muted-foreground)', margin: '0 0 0.5rem 0', fontSize: '0.9rem', textTransform: 'uppercase' }}>Spent</h4>
          <div style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#ef4444' }}>${totalSpent.toFixed(2)}</div>
        </div>
        <div style={{ flex: 1, padding: '1.5rem', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '8px' }}>
          <h4 style={{ color: 'var(--muted-foreground)', margin: '0 0 0.5rem 0', fontSize: '0.9rem', textTransform: 'uppercase' }}>Remaining</h4>
          <div style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#10b981' }}>${remaining.toFixed(2)}</div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '2rem' }}>
        <div style={{ flex: 2 }}>
          <h3 style={{ marginBottom: '1rem' }}>Expense History</h3>
          <DataTable
            columns={[
              {
                header: 'Date',
                cell: (row) => new Date(row.created_at).toLocaleDateString()
              },
              { header: 'Description', accessor: 'description' },
              {
                header: 'Amount',
                cell: (row) => `$${parseFloat(row.amount).toFixed(2)}`
              },
              {
                header: 'Status',
                cell: (row) => {
                  const st = (row.status || '').toLowerCase();
                  const bg = st === 'approved' ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)';
                  const color = st === 'approved' ? '#10b981' : '#f59e0b';
                  return (
                    <span style={{ 
                      fontSize: '0.75rem', fontWeight: 'bold', padding: '0.25rem 0.5rem', borderRadius: '100px',
                      background: bg, color: color
                    }}>
                      {st.toUpperCase()}
                    </span>
                  );
                }
              }
            ]}
            data={expenses}
            emptyIcon={uiIcons.cashMinus}
            emptyTitle="No Expenses"
            emptyDesc="No expenses recorded for this committee yet."
          />
        </div>

        {canManageThis && (
          <div style={{ flex: 1 }}>
            <h3 style={{ marginBottom: '1rem' }}>Request Expense</h3>
            <form onSubmit={handleCreateExpense} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', padding: '1.5rem', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '8px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <label style={{ fontSize: '0.85rem', fontWeight: '500' }}>Description</label>
                <input 
                  type="text" 
                  value={newDesc} 
                  onChange={e => setNewDesc(e.target.value)} 
                  required 
                  style={{ padding: '0.75rem', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--text)' }}
                />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <label style={{ fontSize: '0.85rem', fontWeight: '500' }}>Amount ($)</label>
                <input 
                  type="number" 
                  step="0.01" 
                  min="0"
                  max={remaining}
                  value={newAmount} 
                  onChange={e => setNewAmount(e.target.value)} 
                  required 
                  style={{ padding: '0.75rem', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--background)', color: 'var(--text)' }}
                />
              </div>
              <Button type="submit" variant="primary" style={{ marginTop: '0.5rem' }}>Submit Request</Button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

const CommitteeWorkspaceView = () => {
  const { club, userRole, currentUserId } = useOutletContext();
  const { committeeId } = useParams();
  const navigate = useNavigate();

  const [committee, setCommittee] = useState(null);
  const [members, setMembers] = useState([]);
  const [clubMembers, setClubMembers] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  const myCommRole = (members || []).find(m => String(m.user?.id) === String(currentUserId))?.role || null;
  const canManageThis = canManageCommittees(userRole) || hasCommitteePermission('manage_members', myCommRole);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [comms, mems, cMems, tsks, res] = await Promise.all([
          clubsApi.getClubCommittees(club.id),
          clubsApi.getCommitteeMembers(committeeId),
          clubsApi.getClubMembers(club.id),
          clubsApi.getCommitteeTasks(club.id, committeeId),
          clubsApi.getCommitteeResources(club.id, committeeId)
        ]);

        const currentComm = comms.find(c => String(c.id) === String(committeeId));
        if (!currentComm) {
          navigate(`../../committees`, { replace: true });
          return;
        }
        
        setCommittee(currentComm);
        setMembers(mems || []);
        setClubMembers(cMems || []);
        setTasks(tsks || []);
        setResources(res || []);
      } catch (err) {
        console.error("Failed to load workspace:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [club.id, committeeId, navigate]);

  const handleAddMember = async (membershipId) => {
    try {
      await clubsApi.addCommitteeMember(committeeId, membershipId, 'member');
      const updated = await clubsApi.getCommitteeMembers(committeeId);
      setMembers(updated);
    } catch (err) {
      alert('Failed to add member');
    }
  };

  const handleRemoveMember = async (committeeMemberId) => {
    try {
      await clubsApi.removeCommitteeMember(committeeMemberId);
      const updated = await clubsApi.getCommitteeMembers(committeeId);
      setMembers(updated);
    } catch (err) {
      alert('Failed to remove member');
    }
  };

  const handleUpdateRole = async (committeeMemberId, newRole) => {
    try {
      await clubsApi.updateCommitteeMemberRole(committeeMemberId, newRole);
      const updated = await clubsApi.getCommitteeMembers(committeeId);
      setMembers(updated);
    } catch (err) {
      alert('Failed to update role');
    }
  };

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading workspace...</div>;
  if (!committee) return null;

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent}>
        <div className={styles.workspaceContainer}>
      <div className={styles.workspaceHeader}>
        <div className={styles.breadcrumb}>
          <button className={styles.backBtn} onClick={() => navigate('../committees')}>
            <Icon icon="mdi:arrow-left" /> Back to Committees
          </button>
        </div>
        <div className={styles.titleArea}>
          <h2>{committee.name} Workspace</h2>
          <p>Collaborate and manage tasks specifically for this working group.</p>
        </div>
      </div>

      <SecondaryHeader 
        tabs={[
          { id: 'overview', label: 'Overview', icon: 'mdi:information-outline' },
          { id: 'tasks', label: 'Tasks', icon: 'mdi:clipboard-check-outline' },
          { id: 'resources', label: 'Resources', icon: 'mdi:folder-outline' },
          { id: 'members', label: 'Members', icon: 'mdi:account-group-outline' },
          { id: 'budgets', label: 'Budget & Expenses', icon: 'mdi:cash-multiple' }
        ]}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <div className={styles.tabContent}>
        {activeTab === 'overview' && <CommitteeOverview committee={committee} />}
        {activeTab === 'members' && (
          <CommitteeMembers 
            committee={committee} 
            members={members} 
            clubMembers={clubMembers}
            onAddMember={handleAddMember}
            onRemoveMember={handleRemoveMember}
            onUpdateRole={handleUpdateRole}
            canManage={canManageThis}
          />
        )}
        {activeTab === 'tasks' && <CommitteeTasks tasks={tasks} />}
        {activeTab === 'resources' && <CommitteeResources resources={resources} />}
        {activeTab === 'budgets' && (
          <CommitteeBudgets 
            committeeId={committeeId} 
            clubId={club.id} 
            currentUserId={currentUserId}
            canManageThis={canManageThis}
          />
        )}
      </div>
    </div>
  </div>
</div>
  );
};

export default CommitteeWorkspaceView;
