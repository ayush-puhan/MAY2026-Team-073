import React, { useState } from 'react';
import { Icon } from '@iconify/react';
import { getRoleLabel, getRoleColor } from '../../../../../utils/clubPermissions';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import styles from './MembershipRequestsView.module.css';
import { useToast } from '../../../../../context/ToastContext';
import { uiIcons, authIcons } from '../../../../icons/registry';
import { Button } from '../../../ui/Button/Button';
import { Input } from '../../../ui/Input/Input';

const MembershipRequestsView = ({
  club,
  userRole,
  requests = [],
  onApprove,
  onReject,
  loading
}) => {
  const [rejectingId, setRejectingId] = useState(null);
  const [rejectReason, setRejectReason] = useState('');
  const [expandedId, setExpandedId] = useState(null);
  const { addToast } = useToast();

  const handleApprove = async (id) => {
    try {
      await onApprove(id);
      addToast('Request approved successfully', 'success');
    } catch (err) {
      addToast('Failed to approve request', 'error');
    }
  };

  const handleRejectClick = (id) => {
    setRejectingId(id);
    setRejectReason('');
  };

  const handleCancelReject = () => {
    setRejectingId(null);
    setRejectReason('');
  };

  const handleConfirmReject = async (id) => {
    try {
      await onReject(id, rejectReason);
      addToast('Request rejected', 'success');
      setRejectingId(null);
      setRejectReason('');
    } catch (err) {
      addToast('Failed to reject request', 'error');
    }
  };

  if (loading) {
    return (
      <div className={layoutStyles.workspaceArea}>
        <div className={layoutStyles.workspaceHeader}>
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Membership Requests</h2>
          </div>
        </div>
        <div className={layoutStyles.workspaceContent}>
          <div className={styles.skeletonContainer}>
            {[...Array(3)].map((_, i) => (
              <div key={i} className={styles.skeletonCard} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceHeader}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Membership Requests</h2>
          <span className={styles.badge}>{requests.length}</span>
        </div>
        <p style={{ color: 'var(--muted-foreground)', margin: 0 }}>
          Manage pending applications to join {club?.name}
        </p>
      </div>

      <div className={layoutStyles.workspaceContent}>
        {requests.length === 0 ? (
          <div className={styles.emptyState}>
            <Icon icon={uiIcons.checkCircleOutline} className={styles.emptyIcon} />
            <h3>No pending membership requests</h3>
            <p>You're all caught up!</p>
          </div>
        ) : (
          <div className={styles.requestsGrid}>
            {requests.map(req => {
              const user = req.user || {};
              const roleLabel = getRoleLabel(req.role_in_club);
              const roleColor = getRoleColor(req.role_in_club);
              const isRejecting = rejectingId === req.id;
              const appliedDate = new Date(req.applied_at).toLocaleDateString();

              return (
                <div key={req.id} className={styles.requestCard}>
                  <div className={styles.cardHeader}>
                    <div className={styles.userInfo}>
                      <img 
                        src={user.profile_photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.full_name || 'User')}&background=random`} 
                        alt={user.full_name} 
                        className={styles.avatar} 
                      />
                      <div className={styles.userDetails}>
                        <h4>{user.full_name}</h4>
                        <span>{user.email}</span>
                      </div>
                    </div>
                    <span 
                      className={styles.roleBadge} 
                      style={{ '--role-color': roleColor }}
                    >
                      {roleLabel}
                    </span>
                  </div>

                  <div className={styles.cardBody}>
                    <div className={styles.detailRow}>
                      <Icon icon={uiIcons.calendarBlank} />
                      <span>Applied on {appliedDate}</span>
                    </div>

                    <Button 
                      variant="outline"
                      onClick={() => setExpandedId(expandedId === req.id ? null : req.id)}
                    >
                      {expandedId === req.id ? 'Hide Details' : 'View Application Details'}
                      <Icon icon={expandedId === req.id ? uiIcons.chevronUp : uiIcons.chevronDown} />
                    </Button>

                    {expandedId === req.id && (
                      <div className={styles.expandedContent}>
                        {req.motivation && (
                          <div className={styles.infoBlock}>
                            <strong>Motivation</strong>
                            <p>{req.motivation}</p>
                          </div>
                        )}
                        {req.previous_experience && (
                          <div className={styles.infoBlock}>
                            <strong>Experience</strong>
                            <p>{req.previous_experience}</p>
                          </div>
                        )}
                        <div className={styles.infoGrid}>
                          {req.skills && (
                            <div className={styles.infoBlock}>
                              <strong>Skills</strong>
                              <p>{req.skills}</p>
                            </div>
                          )}
                          {req.weekly_availability && (
                            <div className={styles.infoBlock}>
                              <strong>Availability</strong>
                              <p>{req.weekly_availability}</p>
                            </div>
                          )}
                        </div>
                        {req.portfolio_url && (
                          <div className={styles.infoBlock}>
                            <strong>Portfolio</strong>
                            <a href={req.portfolio_url} target="_blank" rel="noreferrer" className={styles.link}>
                              {req.portfolio_url}
                            </a>
                          </div>
                        )}
                        {req.interests && req.interests.length > 0 && (
                          <div className={styles.infoBlock}>
                            <strong>Interests</strong>
                            <div className={styles.tagsContainer}>
                              {req.interests.map((tag, idx) => (
                                <span key={idx} className={styles.tag}>{tag}</span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  <div className={styles.cardActions}>
                    {isRejecting ? (
                      <div className={styles.rejectForm}>
                        <Input
                          placeholder="Reason for rejection (optional)"
                          value={rejectReason}
                          onChange={(e) => setRejectReason(e.target.value)}
                          autoFocus
                        />
                        <div className={styles.rejectActions}>
                          <Button 
                            variant="outline"
                            onClick={handleCancelReject}
                          >
                            Cancel
                          </Button>
                          <Button 
                            variant="danger"
                            onClick={() => handleConfirmReject(req.id)}
                          >
                            Confirm
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <Button 
                          variant="danger"
                          onClick={() => handleRejectClick(req.id)}
                        >
                          <Icon icon={uiIcons.close} /> Reject
                        </Button>
                        <Button 
                          variant="primary"
                          onClick={() => handleApprove(req.id)}
                        >
                          <Icon icon={authIcons.check} /> Approve
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export { MembershipRequestsView };

