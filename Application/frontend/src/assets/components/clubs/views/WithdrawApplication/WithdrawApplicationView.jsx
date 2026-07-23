import React, { useState, useEffect } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/mockbackendApis/clubsApis/clubs';
import styles from './WithdrawApplicationView.module.css';
import { uiIcons } from '../../../../icons/registry';

const WithdrawApplicationView = () => {
  const { club, currentUserId, currentMembershipId } = useOutletContext();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [membership, setMembership] = useState(null);

  useEffect(() => {
    fetchStatus();
  }, [club.id]);

  const fetchStatus = async () => {
    try {
      const allPending = await clubsApi.getPendingMemberships(currentUserId);
      const specific = allPending.find(m => String(m.club_id) === String(club.id));
      setMembership(specific);
    } catch (err) {
      console.error(err);
    }
  };

  const handleWithdraw = async () => {
    if (!window.confirm("Are you sure you want to withdraw your application?")) return;
    
    setLoading(true);
    try {
      await clubsApi.withdrawApplication(currentMembershipId, currentUserId);
      alert(`Your application to ${club.name} has been withdrawn.`);
      navigate('/clubs/explore'); // Redirect to explore page
    } catch (err) {
      alert("Failed to withdraw application");
      setLoading(false);
    }
  };

  if (!membership && !loading) {
    return (
      <div className={styles.container}>
        <div className={styles.warningBox}>
          <Icon icon={uiIcons.alertCircleOutline} className={styles.warningIcon} />
          <div className={styles.warningText}>
            <h3>No Pending Application</h3>
            <p>You don't have an active application to withdraw for this club.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h2>Withdraw Application</h2>
          <p>Cancel your request to join {club.name}</p>
        </div>
      </header>

      <div className={styles.content}>
        <div className={styles.warningBox}>
          <Icon icon={uiIcons.closeCircleOutline} className={styles.warningIcon} />
          <div className={styles.warningText}>
            <h3>Withdraw your application?</h3>
            <p>
              By withdrawing your application, it will be removed from the club's review queue. 
              If you change your mind later, you will need to submit a new application from scratch.
            </p>
          </div>
        </div>

        <div className={styles.actions}>
          <button 
            className={styles.withdrawBtn} 
            onClick={handleWithdraw} 
            disabled={loading}
          >
            {loading ? 'Withdrawing...' : 'Withdraw Application'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default WithdrawApplicationView;
