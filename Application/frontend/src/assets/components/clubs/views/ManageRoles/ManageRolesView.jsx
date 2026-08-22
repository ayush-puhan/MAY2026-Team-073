import React, { useState, useEffect } from 'react';
import { useOutletContext, useNavigate, Navigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/backendApis/clubsApis/clubs';
import { getRoleLabel, getRoleRank, canManageRoles, canAssignRoleTo } from '../../../../../utils/clubPermissions';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import styles from './ManageRolesView.module.css';
import { uiIcons } from '../../../../icons/registry';
import { Button } from '../../../ui/Button/Button';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import { DataTable } from '../../../ui/DataTable/DataTable';

const ManageRolesView = () => {
  const { club, currentUserId, userRole } = useOutletContext();
  const navigate = useNavigate();
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  if (!canManageRoles(userRole) && userRole !== 'system_admin') {
    return <Navigate to={`/clubs/${club?.id || ''}`} replace />;
  }

  // Transfer Presidency state
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [selectedSuccessor, setSelectedSuccessor] = useState('');
  
  // To avoid circular or redundant imports, define local array
  const ASSIGNABLE_ROLES = [
    'vice_president',
    'treasurer',
    'secretary',
    'event_coordinator',
    'volunteer_coordinator',
    'member'
  ];

  useEffect(() => {
    fetchMembers();
  }, [club.id]);

  const fetchMembers = async () => {
    try {
      setLoading(true);
      const data = await clubsApi.getClubMembers(club.id);
      // Sort by role rank, then name
      const sorted = data.sort((a, b) => {
        const rankDiff = getRoleRank(a.role_in_club) - getRoleRank(b.role_in_club);
        if (rankDiff !== 0) return rankDiff;
        return a.user.full_name.localeCompare(b.user.full_name);
      });
      setMembers(sorted);
    } catch (err) {
      console.error(err);
      setError('Failed to load members.');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (membershipId, newRole) => {
    try {
      await clubsApi.updateMemberRole(club.id, membershipId, newRole, currentUserId);
      fetchMembers();
    } catch (err) {
      alert("Failed to update role");
    }
  };

  const handleTransferPresidency = async () => {
    if (!selectedSuccessor) return;
    
    // In a real app with "faculty approval" this would just create a pending request.
    // For our mock, we'll simulate the request/approval process or just do it immediately
    // but inform the user about the policy.
    
    const confirmMsg = "Transferring presidency requires Faculty Advisor approval in the real system.\n\nFor this demo, do you want to instantly transfer presidency to the selected user and step down?";
    if (!window.confirm(confirmMsg)) return;

    try {
      const currentPresMembership = members.find(m => String(m.user_id) === String(currentUserId));
      await clubsApi.transferPresidency(club.id, currentPresMembership.id, selectedSuccessor);
      
      alert("Presidency transferred successfully. You are now the Vice President.");
      setShowTransferModal(false);
      
      // Since they are no longer president, redirect to dashboard
      navigate(`/clubs/${club.id}/dashboard`);
    } catch (err) {
      alert("Failed to transfer presidency.");
    }
  };

  if (loading) return <div className={styles.loading}>Loading members...</div>;
  if (error) return <div className={styles.error}>{error}</div>;

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent}>
        <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h2>Manage Roles</h2>
          <p>Assign responsibilities and build your leadership team</p>
        </div>
        {userRole === 'president' && (
          <Button onClick={() => setShowTransferModal(true)} icon={uiIcons.crownOutline}>
            Transfer Presidency
          </Button>
        )}
      </header>

      {showTransferModal && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>Transfer Presidency</h3>
            <p className={styles.warningText}>
              <Icon icon={uiIcons.alert} />
              Warning: This action will demote you from President. The new President will have full control over the club. This action typically requires Faculty Advisor approval.
            </p>
            
            <div className={styles.formGroup}>
              <Dropdown
                label="Select Successor:"
                value={selectedSuccessor} 
                onChange={(val) => setSelectedSuccessor(val)}
                options={[
                  { value: "", label: "-- Choose a member --" },
                  ...members
                    .filter(m => String(m.user_id) !== String(currentUserId))
                    .map(m => ({
                      value: m.id,
                      label: `${m.user.full_name} (Current: ${getRoleLabel(m.role_in_club)})`
                    }))
                ]}
              />
            </div>
            
            <div className={styles.modalActions}>
              <Button variant="outline" onClick={() => setShowTransferModal(false)}>Cancel</Button>
              <Button 
                variant="primary" 
                onClick={handleTransferPresidency}
                disabled={!selectedSuccessor}
              >
                Submit Transfer
              </Button>
            </div>
          </div>
        </div>
      )}

      <div className={styles.tableContainer}>
        <DataTable
          columns={[
            {
              header: 'Member Name',
              cell: (row) => {
                const isCurrentUser = String(row.user_id) === String(currentUserId);
                return (
                  <div className={styles.memberInfo}>
                    <span className={styles.memberName}>{row.user?.full_name}</span>
                    {isCurrentUser && <span className={styles.youBadge}>You</span>}
                  </div>
                );
              }
            },
            {
              header: 'Current Role',
              cell: (row) => <span className={styles.roleLabel}>{getRoleLabel(row.role_in_club)}</span>
            },
            {
              header: 'Assign New Role',
              cell: (row) => {
                const isCurrentUser = String(row.user_id) === String(currentUserId);
                if (isCurrentUser) {
                  return <span className={styles.mutedText}>Cannot change own role</span>;
                }
                if (row.role_in_club === 'president') {
                  return <span className={styles.mutedText}>President</span>;
                }
                if (!canAssignRoleTo(userRole, row.role_in_club, 'member')) {
                  return <span className={styles.mutedText}>Not Authorized</span>;
                }
                
                return (
                  <Dropdown
                    value={row.role_in_club}
                    onChange={(val) => handleRoleChange(row.id, val)}
                    options={ASSIGNABLE_ROLES.filter(role => canAssignRoleTo(userRole, row.role_in_club, role)).map(role => ({
                      value: role,
                      label: getRoleLabel(role)
                    }))}
                    className={styles.roleSelectWrapper}
                  />
                );
              }
            }
          ]}
          data={members}
        />
        </div>
      </div>
    </div>
  </div>
  );
};

export default ManageRolesView;
