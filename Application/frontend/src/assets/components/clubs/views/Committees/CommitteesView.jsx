import React, { useState, useEffect } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/mockbackendApis/clubsApis/clubs';
import { canManageCommittees, hasCommitteePermission } from '../../../../../utils/clubPermissions';
import { useToast } from '../../../../../context/ToastContext';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import styles from './CommitteesView.module.css';
import { Button } from '../../../ui/Button/Button';
import { EmptyState } from '../../../ui/EmptyState/EmptyState';
import { Input } from '../../../ui/Input/Input';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import { dashboardIcons, uiIcons, rewardsIcons } from '../../../../icons/registry';

const CommitteesView = () => {
  const { club, userRole, currentUserId } = useOutletContext();
  const { showSuccess, showError } = useToast();
  const [committees, setCommittees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const navigate = useNavigate();
  const [committeeMembers, setCommitteeMembers] = useState({});
  const [clubMembers, setClubMembers] = useState([]);

  const [showForm, setShowForm] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [requestedCommittees, setRequestedCommittees] = useState(new Set());
  const [requesting, setRequesting] = useState(false);

  // Added a quick helper to check if the current user has a specific committee role
  const getMyCommitteeRole = (committeeId) => {
    const myMembership = (committeeMembers[committeeId] || []).find(m => String(m.user?.id) === String(currentUserId));
    return myMembership?.role || null;
  };

  useEffect(() => {
    fetchCommittees();
  }, [club.id]);

  const fetchCommittees = async () => {
    try {
      setLoading(true);
      const data = await clubsApi.getClubCommittees(club.id);
      setCommittees(data || []);
      
      // Auto-fetch my committee roles to allow permission checks without expanding
      const membershipsPromises = (data || []).map(c => clubsApi.getCommitteeMembers(c.id));
      const membersData = await Promise.all(membershipsPromises);
      
      const newCommitteeMembers = {};
      (data || []).forEach((c, idx) => {
        newCommitteeMembers[c.id] = membersData[idx];
      });
      setCommitteeMembers(newCommitteeMembers);

    } catch (err) {
      console.error(err);
      setError('Failed to load committees.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCommittee = async (e) => {
    e.preventDefault();
    if (!newName) return;

    try {
      const newCommittee = await clubsApi.createCommittee(club.id, {
        name: newName,
        description: newDesc,
        status: 'active'
      }, currentUserId);
      setShowForm(false);
      setNewName('');
      setNewDesc('');
      // Silently refetch data to ensure 100% accuracy without loading screen flash
      const data = await clubsApi.getClubCommittees(club.id);
      setCommittees(data || []);
      
      const membersPromises = (data || []).map(c => clubsApi.getCommitteeMembers(c.id));
      const membersData = await Promise.all(membersPromises);
      
      const newCommitteeMembers = {};
      (data || []).forEach((c, idx) => {
        newCommitteeMembers[c.id] = membersData[idx];
      });
      setCommitteeMembers(newCommitteeMembers);
    } catch (err) {
      alert('Failed to create committee');
    }
  };





  if (loading) return <div className={styles.loading}>Loading committees...</div>;
  if (error) return <div className={styles.error}>{error}</div>;

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent}>
        <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h2>Committees</h2>
          <p>Specialized working groups within {club.name}</p>
        </div>
        {canManageCommittees(userRole) && (
          <Button icon={showForm ? "mdi:close" : "mdi:plus-circle-outline"} onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : 'Create Committee'}
          </Button>
        )}
      </header>

      {showForm && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <form className={styles.createForm} onSubmit={handleCreateCommittee}>
              <h3>New Committee</h3>
              <div className={styles.formGrid}>
                <Input
                  label="Committee Name"
                  type="text" 
                  value={newName} 
                  onChange={e => setNewName(e.target.value)} 
                  required 
                />
                <div className={styles.formGroup} style={{gridColumn: '1 / -1'}}>
                  <Input
                    label="Description"
                    as="textarea"
                    value={newDesc} 
                    onChange={e => setNewDesc(e.target.value)} 
                    rows="3"
                  />
                </div>
              </div>
              <div className={styles.formActions}>
                <Button variant="outline" onClick={() => setShowForm(false)} type="button">
                  Cancel
                </Button>
                <Button type="submit" variant="primary">Create</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {committees.length === 0 ? (
        <EmptyState 
          icon={dashboardIcons.accountGroupOutline} 
          title="No committees established" 
          description="No committees have been established yet." 
        />
      ) : (
        <div className={styles.grid}>
          {committees.map(c => {
            const myCommRole = getMyCommitteeRole(c.id);
            const canManageThis = canManageCommittees(userRole) || hasCommitteePermission('manage_members', myCommRole);
            const canViewThis = canManageCommittees(userRole) || hasCommitteePermission('view_committee', myCommRole) || userRole === 'system_admin';

            return (
              <div key={c.id} className={styles.card}>
                <div className={styles.cardHeader}>
                  <h3>{c.name}</h3>
                  {myCommRole && <span className={styles.myRoleBadge}>{myCommRole.replace('_', ' ').toUpperCase()}</span>}
                </div>
                <p className={styles.desc}>{c.description}</p>
                
                <div className={styles.actions}>
                  {canViewThis ? (
                    <Button variant="outline" icon={uiIcons.accountSearchOutline} onClick={() => {
                      navigate(`${c.id}`);
                    }}>
                      View Workspace
                    </Button>
                  ) : (
                    <div className={styles.privateActions}>
                      <span className={styles.mutedText}>Private working group</span>
                      <Button 
                        variant="secondary" 
                        size="small"
                        icon={requestedCommittees.has(c.id) ? "mdi:check" : "mdi:account-plus-outline"} 
                        disabled={requesting || requestedCommittees.has(c.id)}
                        onClick={async () => {
                          setRequesting(true);
                          try {
                            await clubsApi.requestJoinCommittee(c.id, currentUserId);
                            setRequestedCommittees(prev => new Set(prev).add(c.id));
                            showSuccess('Request to join committee sent!');
                          } catch (e) {
                            showError('Failed to send request.');
                          } finally {
                            setRequesting(false);
                          }
                        }}
                      >
                        {requestedCommittees.has(c.id) ? 'Requested' : 'Request to Join'}
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
        </div>
      </div>
    </div>
  );
};

export default CommitteesView;
