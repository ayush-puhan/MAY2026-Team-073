import React from 'react';
import { ContextPanel, ContextPanelSection, ContextPanelLink } from './ContextPanel';
import { dashboardIcons } from '../../../icons/registry';

export const StudentContextPanel = ({ isVerified }) => {
  return (
    <ContextPanel title="Campus Home">
      {isVerified ? (
        <>
          <ContextPanelSection>
            <ContextPanelLink to="/student-dashboard" exact label="Home" icon={dashboardIcons.dashboard} />
            <ContextPanelLink to="/student-dashboard/recent" label="Recently Visited" icon={dashboardIcons.recent} />
            <ContextPanelLink to="/student-dashboard/upcoming" label="My Upcoming" icon={dashboardIcons.events} />
          </ContextPanelSection>
          <ContextPanelSection title="Quick Links">
            <ContextPanelLink to="/student-dashboard/saved" label="Saved Items" icon={dashboardIcons.bookmarks} />
            <ContextPanelLink to="/student-dashboard/rewards" label="Rewards Hub" icon={dashboardIcons.rewards} />
          </ContextPanelSection>
        </>
      ) : (
        <>
          <ContextPanelSection>
            <ContextPanelLink to="/student-dashboard" exact label="Home" icon={dashboardIcons.dashboard} />
            <ContextPanelLink to="/student-dashboard/events" label="Public Events" icon={dashboardIcons.events} />
          </ContextPanelSection>
          <ContextPanelSection title="Quick Links">
            <ContextPanelLink to="/student-dashboard/helpdesk" label="Helpdesk" icon={dashboardIcons.helpdesk} />
          </ContextPanelSection>
        </>
      )}
    </ContextPanel>
  );
};
