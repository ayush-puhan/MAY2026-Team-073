import React, { useState } from 'react';
import { Icon } from '@iconify/react';
import { rewardsIcons } from '../../../icons/registry';
import { ConfirmModal } from '../../ui/ConfirmModal/ConfirmModal';
import { useToast } from '../../../../context/ToastContext';
import styles from './StoreItemCard.module.css';

export const StoreItemCard = ({ item, userPoints, onRedeem }) => {
  const [loading, setLoading] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const { showError } = useToast();
  const canAfford = userPoints >= item.points_cost;

  const handleRedeemClick = () => {
    if (!canAfford) {
      showError(`Insufficient points! You need ${item.points_cost - userPoints} more points to redeem ${item.name}.`);
      return;
    }
    setIsConfirmOpen(true);
  };

  const handleConfirmRedeem = async () => {
    setLoading(true);
    await onRedeem(item);
    setLoading(false);
  };

  return (
    <div className={`${styles.card} ${!canAfford ? styles.cannotAfford : ''}`}>
      <div className={styles.iconArea}>
        <Icon icon={item.icon} className={styles.largeIcon} />
        <div className={styles.categoryBadge}>{item.category}</div>
      </div>
      
      <div className={styles.content}>
        <h4 className={styles.title}>{item.name}</h4>
        <p className={styles.desc}>{item.description}</p>
        
        <div className={styles.footer}>
          <div className={styles.price}>
            <Icon icon={rewardsIcons.starFourPoints} className={styles.pointsIcon} />
            <span className={canAfford ? styles.affordable : styles.tooExpensive}>
              {item.points_cost} pts
            </span>
          </div>
          
          <button 
            className={styles.redeemBtn} 
            onClick={handleRedeemClick}
            disabled={loading || item.stock <= 0}
          >
            {loading ? <Icon icon="line-md:loading-twotone-loop" /> : 
             item.stock <= 0 ? 'Out of Stock' : 'Redeem'}
          </button>
        </div>
      </div>
      
      <ConfirmModal 
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={handleConfirmRedeem}
        title="Confirm Redemption"
        message={`Are you sure you want to redeem ${item.name} for ${item.points_cost} points?`}
        confirmText="Redeem"
        type="primary"
      />
    </div>
  );
};
