import React, { useState, useMemo } from 'react';
import { Icon } from '@iconify/react';
import { useToast } from '../../../../../context/ToastContext';
import { 
  canManageMembers, 
  canManageRoles, 
  getRoleLabel, 
  getRoleColor, 
  getRoleIcon 
} from '../../../../../utils/clubPermissions';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import styles from './ClubMembersView.module.css';
import { uiIcons, dashboardIcons } from '../../../../icons/registry';
import { Input } from '../../../ui/Input/Input';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import { Button } from '../../../ui/Button/Button';

const ROLES = [
  { value: 'member', label: 'Member' },
  { value: 'volunteer_coordinator', label: 'Volunteer Coordinator' },
  { value: 'event_coordinator', label: 'Event Coordinator' },
  { value: 'secretary', label: 'Secretary' },
  { value: 'treasurer', label: 'Treasurer' },
  { value: 'vice_president', label: 'Vice President' }
];

const ClubMembersView = ({ 
  club, 
  userRole, 
  members = [], 
  onRoleChange, 
  onRemoveMember,
  currentUserId 
}) => {
  const { addToast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');

  const allowManageMembers = canManageMembers(userRole);
  const allowManageRoles = canManageRoles(userRole);

  const filteredMembers = useMemo(() => {
    if (!searchQuery.trim()) return members;
    const query = searchQuery.toLowerCase();
    return members.filter(m => {
      const name = m.user?.full_name?.toLowerCase() || '';
      const email = m.user?.email?.toLowerCase() || '';
      return name.includes(query) || email.includes(query);
    });
  }, [members, searchQuery]);

  const handleRoleChange = async (membershipId, newRole) => {
    try {
      if (onRoleChange) {
        await onRoleChange(membershipId, newRole);
      }
    } catch (error) {
      // Toast is handled by parent component (ClubsHub)
      console.error(error);
    }
  };

  const handleRemoveMember = async (membershipId) => {
    if (!window.confirm('Are you sure you want to remove this member?')) return;
    try {
      if (onRemoveMember) {
        await onRemoveMember(membershipId);
      }
    } catch (error) {
      // Toast is handled by parent component (ClubsHub)
      console.error(error);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getInitials = (name) => {
    if (!name) return '?';
    return name.charAt(0).toUpperCase();
  };

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent}>
        <div className={styles.container}>
          <div className={styles.header}>
            <div className={styles.searchContainer}>
              <Input
                icon={uiIcons.magnify}
                placeholder="Search members by name or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                wrapperClassName={styles.searchInputWrapper}
              />
            </div>
          </div>

      {filteredMembers.length === 0 ? (
        <div className={styles.emptyState}>
          <Icon icon={dashboardIcons.accountGroupOutline} className={styles.emptyIcon} />
          <h3>No members found</h3>
          <p>We couldn't find any members matching your search.</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {filteredMembers.map((member) => {
            const isCurrentUser = currentUserId ? member.user_id === currentUserId : false;
            // Prevent removing self or president
            const canRemove = allowManageMembers && !isCurrentUser && member.role_in_club !== 'president';
            // Prevent changing role of self or president
            const canEditRole = allowManageRoles && !isCurrentUser && member.role_in_club !== 'president';
            
            const roleColor = getRoleColor ? getRoleColor(member.role_in_club) : '#666';
            
            return (
              <div key={member.id} className={styles.memberCard}>
                <div className={styles.cardHeader}>
                  {member.user?.profile_photo_url ? (
                    <>
                      <img 
                        src={member.user.profile_photo_url} 
                        alt={member.user?.full_name} 
                        className={styles.avatar} 
                        onError={(e) => {
                          e.target.style.display = 'none';
                          if (e.target.nextSibling) {
                            e.target.nextSibling.style.display = 'flex';
                          }
                        }}
                      />
                      <div className={styles.avatar} style={{ display: 'none' }}>
                        {getInitials(member.user?.full_name)}
                      </div>
                    </>
                  ) : (
                    <div className={styles.avatar}>
                      {getInitials(member.user?.full_name)}
                    </div>
                  )}
                  
                  <div className={styles.memberInfo}>
                    <h3 className={styles.name}>{member.user?.full_name || 'Unknown User'}</h3>
                    <p className={styles.email}>{member.user?.email || 'No email provided'}</p>
                    <div 
                      className={styles.roleBadge} 
                      style={{ 
                        backgroundColor: `${roleColor}15`, 
                        color: roleColor,
                        border: `1px solid ${roleColor}30`
                      }}
                    >
                      {getRoleIcon && <Icon icon={getRoleIcon(member.role_in_club)} />}
                      {getRoleLabel ? getRoleLabel(member.role_in_club) : member.role_in_club}
                    </div>
                  </div>
                </div>
                
                <div className={styles.cardFooter}>
                  <div className={styles.joinedDate}>
                    Joined {formatDate(member.applied_at || member.created_at)}
                  </div>
                  
                  <div className={styles.actions}>
                    {canEditRole && (
                      <Dropdown
                        options={ROLES}
                        value={member.role_in_club}
                        onChange={(val) => handleRoleChange(member.id, val)}
                        className={styles.roleSelectWrapper}
                      />
                    )}
                    
                    {canRemove && (
                      <Button 
                        variant="ghost"
                        color="error"
                        size="sm"
                        icon={uiIcons.accountRemoveOutline}
                        onClick={() => handleRemoveMember(member.id)}
                        title="Remove member"
                      >
                        Remove
                      </Button>
                    )}
                  </div>
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

export { ClubMembersView };

