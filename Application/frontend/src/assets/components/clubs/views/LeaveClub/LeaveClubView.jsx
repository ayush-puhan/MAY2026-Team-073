import React, { useState } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/backendApis/clubsApis/clubs';
import styles from './LeaveClubView.module.css';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import { Input } from '../../../ui/Input/Input';
import { Button } from '../../../ui/Button/Button';
import { uiIcons } from '../../../../icons/registry';

const LeaveClubView = () => {
  const { club, currentUserId } = useOutletContext();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [confirmText, setConfirmText] = useState('');

  const handleLeave = async () => {
    if (confirmText !== club.name) return;

    setLoading(true);
    try {
      console.log(club);
      await clubsApi.leaveClub(club.membership_id);
      alert(`You have left ${club.name}.`);
      navigate('/clubs/mine');
    } catch (err) {
      alert('Failed to leave club');
      setLoading(false);
    }
  };

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent}>
        <div className={styles.container}>
          <header className={styles.header}>
            <div>
              <h2>Leave Club</h2>
              <p>Permanently end your membership with {club.name}</p>
            </div>
          </header>

          <div className={styles.content}>
            <div className={styles.warningBox}>
              <Icon icon={uiIcons.alertOutline} className={styles.warningIcon} />
              <div className={styles.warningText}>
                <h3>Are you absolutely sure?</h3>
                <p>
                  Leaving the club means you will lose access to the club dashboard, member directory, internal events, and volunteer tasks.
                  Any incomplete tasks assigned to you will be unassigned.
                </p>
                <p>
                  This action <strong>cannot be undone</strong>. If you change your mind later, you will need to apply to join again.
                </p>
              </div>
            </div>

            <div className={styles.confirmSection}>
              <label>
                Please type <strong>{club.name}</strong> to confirm.
              </label>
              <Input
                type="text"
                value={confirmText}
                onChange={e => setConfirmText(e.target.value)}
                placeholder={club.name}
              />

              <Button
                variant="danger"
                onClick={handleLeave}
                disabled={confirmText !== club.name || loading}
                style={{ marginTop: '1rem' }}
              >
                {loading ? 'Leaving...' : 'Yes, I want to leave'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeaveClubView;