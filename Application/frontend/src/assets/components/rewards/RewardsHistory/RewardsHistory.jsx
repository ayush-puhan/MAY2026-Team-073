import React, { useEffect, useState } from 'react';
import { useSession } from '../../../../context/SessionContext';
import { rewardsApi } from '../../../../api';
import { Icon } from '@iconify/react';
import { rewardsIcons } from '../../../icons/registry';
import styles from './RewardsHistory.module.css';

export const RewardsHistory = () => {
  const { user } = useSession();
  const [pointsHistory, setPointsHistory] = useState([]);
  const [redemptions, setRedemptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('earned');

  useEffect(() => {
    const loadData = async () => {
      try {
        const [ph, r] = await Promise.all([
          rewardsApi.getPointsHistory(user.id),
          rewardsApi.getRedemptionHistory(user.id)
        ]);
        setPointsHistory(ph.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
        setRedemptions(r.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
      } catch (err) {
        console.error('Failed to load history', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [user.id]);

  if (loading) return <div className={styles.loader}><Icon icon="line-md:loading-twotone-loop" /> Loading...</div>;

  const totalEarned = pointsHistory.reduce((sum, item) => sum + item.points, 0);
  const totalSpent = redemptions.reduce((sum, item) => sum + item.points_spent, 0);

  const renderEarned = () => (
    <div className={styles.list}>
      {pointsHistory.map(item => (
        <div key={item.id} className={styles.listItem}>
          <div className={styles.itemIconWrapper}>
            <Icon icon={rewardsIcons.starPlus} className={styles.earnedIcon} />
          </div>
          <div className={styles.itemInfo}>
            <h4>{item.reason}</h4>
            <span>{new Date(item.created_at).toLocaleString()}</span>
          </div>
          <div className={styles.itemPointsEarned}>
            +{item.points} pts
          </div>
        </div>
      ))}
      {pointsHistory.length === 0 && (
        <div className={styles.emptyState}>No points earned yet. Start completing tasks!</div>
      )}
    </div>
  );

  const renderSpent = () => (
    <div className={styles.list}>
      {redemptions.map(item => (
        <div key={item.id} className={styles.listItem}>
          <div className={styles.itemIconWrapper}>
            <Icon icon={rewardsIcons.giftOpen} className={styles.spentIcon} />
          </div>
          <div className={styles.itemInfo}>
            <h4>{item.reward_description}</h4>
            <span>{new Date(item.created_at).toLocaleString()} &middot; Status: {item.status}</span>
          </div>
          <div className={styles.itemPointsSpent}>
            -{item.points_spent} pts
          </div>
        </div>
      ))}
      {redemptions.length === 0 && (
        <div className={styles.emptyState}>No items redeemed yet. Visit the store!</div>
      )}
    </div>
  );

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Rewards History</h2>
      
      <div className={styles.statsContainer}>
        <div className={styles.statCard}>
          <Icon icon={rewardsIcons.starCircle} className={styles.statIcon} style={{color: 'var(--success)'}} />
          <div className={styles.statContent}>
            <span>Total Earned</span>
            <h3>{totalEarned.toLocaleString()} pts</h3>
          </div>
        </div>
        <div className={styles.statCard}>
          <Icon icon={rewardsIcons.cartArrowUp} className={styles.statIcon} style={{color: '#ff6b6b'}} />
          <div className={styles.statContent}>
            <span>Total Spent</span>
            <h3>{totalSpent.toLocaleString()} pts</h3>
          </div>
        </div>
      </div>

      <div className={styles.tabsContainer}>
        <button 
          className={`${styles.tabBtn} ${activeTab === 'earned' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('earned')}
        >
          Points Earned
        </button>
        <button 
          className={`${styles.tabBtn} ${activeTab === 'spent' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('spent')}
        >
          Redemptions
        </button>
      </div>

      <div className={styles.contentArea}>
        {activeTab === 'earned' ? renderEarned() : renderSpent()}
      </div>
    </div>
  );
};
