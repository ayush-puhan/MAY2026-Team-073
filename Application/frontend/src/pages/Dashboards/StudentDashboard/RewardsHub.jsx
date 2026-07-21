import React from 'react';
import { rewardsIcons } from '../../../assets/icons/registry';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ContextLayout } from '../../../assets/components/ui/ContextLayout/ContextLayout';
import { ContextPanel, ContextPanelSection, ContextPanelLink } from '../../../assets/components/ui/ContextLayout/ContextPanel';
import { RewardsEarn } from '../../../assets/components/rewards/RewardsEarn/RewardsEarn';
import { RewardsStore } from '../../../assets/components/rewards/RewardsStore/RewardsStore';
import { RewardsHistory } from '../../../assets/components/rewards/RewardsHistory/RewardsHistory';

export const RewardsHub = () => {
  const location = useLocation();

  return (
    <ContextLayout>
      <ContextPanel title="Rewards Hub">
        <ContextPanelSection>
          <ContextPanelLink 
            to="/student-dashboard/rewards/earn" 
            icon={rewardsIcons.earn} 
            label="Earn Points" 
          />
          <ContextPanelLink 
            to="/student-dashboard/rewards/store" 
            icon={rewardsIcons.store} 
            label="Redeem Rewards" 
          />
          <ContextPanelLink 
            to="/student-dashboard/rewards/history" 
            icon={rewardsIcons.history} 
            label="My History" 
          />
        </ContextPanelSection>
      </ContextPanel>

      <div style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
        <Routes>
          <Route path="earn" element={<RewardsEarn />} />
          <Route path="store" element={<RewardsStore />} />
          <Route path="history" element={<RewardsHistory />} />
          <Route path="*" element={<Navigate to="earn" replace />} />
        </Routes>
      </div>
    </ContextLayout>
  );
};
