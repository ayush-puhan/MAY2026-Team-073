import React, { useEffect, useState } from 'react';
import { useSession } from '../../../../context/SessionContext';
import { rewardsApi } from '../../../../api';
import { StoreItemCard } from '../StoreItemCard/StoreItemCard';
import { Icon } from '@iconify/react';
import { rewardsIcons } from '../../../icons/registry';
import { useToast } from '../../../../context/ToastContext';
import styles from './RewardsStore.module.css';

export const RewardsStore = () => {
  const { user } = useSession();
  const { showSuccess, showError } = useToast();
  const [items, setItems] = useState([]);
  const [points, setPoints] = useState(0);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  const loadData = async () => {
    try {
      const [storeItems, userPoints] = await Promise.all([
        rewardsApi.getStoreItems(),
        rewardsApi.getUserPoints(user.id)
      ]);
      const visibleItems = storeItems.filter(i => user.is_verified || !i.requires_verified);
      setItems(visibleItems);
      setPoints(userPoints);
    } catch (err) {
      console.error('Failed to load store data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user.id]);

  const handleRedeem = async (item) => {
    try {
      await rewardsApi.redeemItem(user.id, item.id);
      showSuccess(`Successfully requested redemption for: ${item.name}! Check your history for status.`);
      await loadData();
    } catch (err) {
      showError(`Redemption failed: ${err.message}`);
    }
  };

  if (loading) return <div className={styles.loader}><Icon icon="line-md:loading-twotone-loop" /> Loading...</div>;

  const categories = ['all', 'food', 'experience', 'digital', 'merch'];
  const filteredItems = activeTab === 'all' 
    ? items 
    : items.filter(item => item.category === activeTab);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Redeem Rewards</h2>
          <p className={styles.subtitle}>Spend your earned points on exclusive campus perks and merchandise.</p>
        </div>
        
        <div className={styles.pointsDisplay}>
          <div className={styles.pointsLabel}>Available Balance</div>
          <div className={styles.pointsValue}>
            <Icon icon={rewardsIcons.starFourPoints} className={styles.pointsIcon} />
            {points.toLocaleString()} pts
          </div>
        </div>
      </div>

      <div className={styles.tabsContainer}>
        {categories.map(cat => (
          <button 
            key={cat}
            className={`${styles.tabBtn} ${activeTab === cat ? styles.activeTab : ''}`}
            onClick={() => setActiveTab(cat)}
          >
            {cat === 'all' ? 'All Rewards' : cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      <div className={styles.storeGrid}>
        {filteredItems.map(item => (
          <StoreItemCard 
            key={item.id} 
            item={item} 
            userPoints={points} 
            onRedeem={handleRedeem} 
          />
        ))}
        {filteredItems.length === 0 && (
          <div className={styles.emptyState}>
            <Icon icon={rewardsIcons.packageVariant} />
            <p>No items found in this category.</p>
          </div>
        )}
      </div>
    </div>
  );
};
