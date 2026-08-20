import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate, useParams, Outlet } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../api';
import { useSession } from '../../../../context/SessionContext';
import { ClubCard } from '../../ui/ClubCard/ClubCard';
import { ClubInfoModal } from '../../ui/ClubInfoModal/ClubInfoModal';
import { ClubRegistrationModal } from '../../ui/ClubRegistrationModal/ClubRegistrationModal';
import { ProposeClubModal } from '../ui/ProposeClubModal/ProposeClubModal';
import { useToast } from '../../../../context/ToastContext';
import { ContextLayout } from '../../ui/ContextLayout/ContextLayout';
import { ContextPanel, ContextPanelSection, ContextPanelLink } from '../../ui/ContextLayout/ContextPanel';
import { SecondaryHeader } from '../../ui/SecondaryHeader/SecondaryHeader';
import { ClubDashboard } from '../views/ClubDashboard/ClubDashboard';
import { ClubAnnouncementsView } from '../views/ClubAnnouncements/ClubAnnouncementsView';
import { ClubMembersView } from '../views/ClubMembers/ClubMembersView';
import { MembershipRequestsView } from '../views/MembershipRequests/MembershipRequestsView';
import { MyTasksView } from '../views/MyTasks/MyTasksView';
import ClubEventsView from '../views/ClubEvents/ClubEventsView';
import ManageTasksView from '../views/ManageTasks/ManageTasksView';
import CertificatesView from '../views/Certificates/CertificatesView';
import ClubBudgetView from '../views/ClubBudget/ClubBudgetView';
import ClubAnalyticsView from '../views/ClubAnalytics/ClubAnalyticsView';
import CommitteesView from '../views/Committees/CommitteesView';
import CommitteeWorkspaceView from '../views/CommitteeWorkspace/CommitteeWorkspaceView';
import ClubActivityLogView from '../views/ClubActivityLog/ClubActivityLogView';
import ClubSettingsView from '../views/ClubSettings/ClubSettingsView';
import { ClubResourcesView } from '../views/ClubResources/ClubResourcesView';
import ManageRolesView from '../views/ManageRoles/ManageRolesView';
import LeaveClubView from '../views/LeaveClub/LeaveClubView';
import ApplicationStatusView from '../views/ApplicationStatus/ApplicationStatusView';
import WithdrawApplicationView from '../views/WithdrawApplication/WithdrawApplicationView';
import {
  getClubPanelSections,
  getRoleLabel,
  getRoleIcon,
  getRoleColor,
  canPostAnnouncement,
  canManageMembers,
  canManageTasks,
  canViewBudget,
  canViewClubSettings,
  canViewCommittees,
  canAssignRoles,
  canViewAnalytics
} from '../../../../utils/clubPermissions';
import layoutStyles from '../../ui/ContextLayout/ContextLayout.module.css';
import styles from './ClubsHub.module.css';
import { landingIcons, uiIcons, dashboardIcons } from '../../../icons/registry';

const getClubIcon = (category) => {
  const c = category?.toLowerCase() || '';
  if (c.includes('art') || c.includes('culture')) return landingIcons.clubCultural;
  if (c.includes('music')) return landingIcons.clubMusic;
  if (c.includes('code') || c.includes('tech') || c.includes('engineer')) return landingIcons.clubCode;
  if (c.includes('health') || c.includes('well')) return landingIcons.clubMentalHealth;
  if (c.includes('food') || c.includes('culinary')) return landingIcons.clubFood;
  return landingIcons.clubCultural;
};

// -- Header with search + tabs --
const DiscoverHeader = ({ title, subtitle, searchQuery, setSearchQuery, activeTab, onTabChange }) => {
  const tabs = [
    { id: 'all', label: 'All', icon: 'mdi:view-grid-outline' },
    { id: 'engineering', label: 'Engineering', icon: 'mdi:hammer-wrench' },
    { id: 'arts', label: 'Arts & Culture', icon: 'mdi:palette' },
    { id: 'sports', label: 'Sports', icon: 'mdi:basketball' },
    { id: 'wellness', label: 'Wellness', icon: 'mdi:leaf' }
  ];

  return (
    <>
      <SecondaryHeader 
        tabs={tabs} 
        activeTab={activeTab} 
        onTabChange={onTabChange} 
        searchQuery={searchQuery} 
        onSearchChange={setSearchQuery} 
        searchPlaceholder="Search clubs..." 
      />
      <div className={styles.heroBanner}>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
    </>
  );
};

const filterClubsByTab = (clubs, tab) => {
  if (tab === 'all') return clubs;
  return clubs.filter(c => c.category?.toLowerCase().includes(tab.toLowerCase()));
};

// -- All Clubs View (Discover) --
const AllClubsView = ({ clubs, onJoinClick, searchQuery, setSearchQuery }) => {
  const [activeTab, setActiveTab] = useState('all');
  
  const searchFiltered = clubs.filter(c => {
    const q = searchQuery.toLowerCase();
    return (
      c.name?.toLowerCase().includes(q) || 
      c.description?.toLowerCase().includes(q) ||
      c.category?.toLowerCase().includes(q) ||
      c.banner?.toLowerCase().includes(q)
    );
  });

  const tabFiltered = filterClubsByTab(searchFiltered, activeTab);

  const getBadge = (club) => {
    if (club.membership_status === 'approved') return '✓ Joined';
    if (club.membership_status === 'pending') return '⏳ Pending';
    return null;
  };

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent} style={{ paddingTop: '0' }}>
        <DiscoverHeader 
          title="DISCOVER CAMPUS CLUBS" 
          subtitle="Find your community. From robotics to music, explore clubs across the university." 
          searchQuery={searchQuery} 
          setSearchQuery={setSearchQuery} 
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
        
        <div className={styles.splitLayout}>
          <div className={styles.categorySection}>
            <div className={styles.grid}>
              {tabFiltered.length > 0 ? (
                tabFiltered.map(c => (
                  <ClubCard 
                    key={c.id}
                    icon={getClubIcon(c.category)}
                    title={c.name}
                    subtitle={`${c.members || 0} members • ${c.awards || 0} awards`}
                    university={c.university?.name || "IIT Delhi"}
                    rightElement={getBadge(c)}
                    bannerKeyword={c.banner || c.category?.toLowerCase()}
                    bannerUrl={c.banner_url}
                    onClick={() => onJoinClick(c)}
                    interests={c.interests}
                  />
                ))
              ) : (
                <div className={styles.emptyState}>
                  <Icon icon={uiIcons.accountSearch} />
                  <p>No clubs found in this category.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// -- My Clubs Grid View --
const MyClubsView = ({ myClubs, onClubSelect }) => (
  <div className={layoutStyles.workspaceArea}>
    <div className={layoutStyles.workspaceContent}>
      <h2 className={styles.sectionTitle} style={{ marginBottom: '1.5rem' }}>My Clubs</h2>
      <div className={styles.grid}>
        {myClubs.length > 0 ? (
          myClubs.map(c => (
            <ClubCard 
              key={c.id}
              icon={getClubIcon(c.category)}
              title={c.name}
              subtitle={`${c.members || 0} members • ${getRoleLabel(c.role_in_club)}`}
              university={c.university?.name || "IIT Delhi"}
              bannerKeyword={c.banner || c.category?.toLowerCase()}
              bannerUrl={c.banner_url}
              onClick={() => onClubSelect(c)}
              interests={c.interests}
            />
          ))
        ) : (
          <div className={styles.emptyState}>
            <Icon icon={landingIcons.accountGroup} />
            <p>You haven't joined any clubs yet.</p>
          </div>
        )}
      </div>
    </div>
  </div>
);

// -- Club Workspace (routes for sub-views inside a selected club) --
const ClubWorkspace = ({ club, userRole, user, onBack, basePath }) => {
  const { addToast } = useToast();
  const navigate = useNavigate();
  const [members, setMembers] = useState([]);
  const [requests, setRequests] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loadingMembers, setLoadingMembers] = useState(true);
  const [loadingRequests, setLoadingRequests] = useState(true);
  const [loadingTasks, setLoadingTasks] = useState(true);

  const clubBasePath = `${basePath}/mine/${club.id}`;

  // Fetch members
  useEffect(() => {
    setLoadingMembers(true);
    clubsApi.getClubMembers(club.id)
      .then(setMembers)
      .catch(err => console.error('Failed to fetch members:', err))
      .finally(() => setLoadingMembers(false));
  }, [club.id]);

  // Fetch pending requests (only for leaders)
  useEffect(() => {
    if (canManageMembers(userRole)) {
      setLoadingRequests(true);
      clubsApi.getClubApplications(club.id)
        .then(reqs => setRequests((reqs || []).filter(r => r.status === 'pending')))
        .catch(err => console.error('Failed to fetch requests:', err))
        .finally(() => setLoadingRequests(false));
    } else {
      setLoadingRequests(false);
    }
  }, [club.id, userRole]);

  // Fetch my tasks
  useEffect(() => {
    if (user?.id) {
      setLoadingTasks(true);
      clubsApi.getMyTasks(club.id, user.id)
        .then(setTasks)
        .catch(err => console.error('Failed to fetch tasks:', err))
        .finally(() => setLoadingTasks(false));
    }
  }, [club.id, user?.id]);

  // Handlers
  const handleApprove = async (applicationId) => {
    try {
      await clubsApi.reviewApplication(applicationId, 'approved', user.id);
      setRequests(prev => prev.filter(r => String(r.id) !== String(applicationId)));
      addToast({ title: 'Approved', message: 'Application approved successfully!', type: 'success' });
      // Refresh members
      const updated = await clubsApi.getClubMembers(club.id);
      setMembers(updated);
    } catch (err) {
      addToast({ title: 'Error', message: err.message || 'Failed to approve.', type: 'error' });
      throw err;
    }
  };

  const handleReject = async (applicationId, reason) => {
    try {
      await clubsApi.reviewApplication(applicationId, 'rejected', user.id, reason);
      setRequests(prev => prev.filter(r => String(r.id) !== String(applicationId)));
      addToast({ title: 'Rejected', message: 'Application rejected.', type: 'info' });
    } catch (err) {
      addToast({ title: 'Error', message: err.message || 'Failed to reject.', type: 'error' });
      throw err;
    }
  };

  const handleRoleChange = async (membershipId, newRole) => {
    try {
      await clubsApi.updateMemberRole(club.id, membershipId, newRole, user.id);
      setMembers(prev => prev.map(m => String(m.id) === String(membershipId) ? { ...m, role_in_club: newRole } : m));
      addToast({ title: 'Updated', message: 'Member role updated.', type: 'success' });
    } catch (err) {
      addToast({ title: 'Error', message: err.message || 'Failed to update role.', type: 'error' });
    }
  };

  const handleRemoveMember = async (membershipId) => {
    try {
      await clubsApi.removeMember(club.id, membershipId, user.id);
      setMembers(prev => prev.filter(m => String(m.id) !== String(membershipId)));
      addToast({ title: 'Removed', message: 'Member removed from club.', type: 'info' });
    } catch (err) {
      addToast({ title: 'Error', message: err.message || 'Failed to remove member.', type: 'error' });
    }
  };

  const handleTaskUpdate = async (taskId, newStatus) => {
    try {
      await clubsApi.updateTaskStatus(taskId, newStatus, user.id);
      setTasks(prev => prev.map(t => String(t.id) === String(taskId) ? { ...t, status: newStatus } : t));
      addToast({ title: 'Updated', message: `Task marked as ${newStatus.toLowerCase()}.`, type: 'success' });
    } catch (err) {
      addToast({ title: 'Error', message: err.message || 'Failed to update task.', type: 'error' });
    }
  };

  const handlePostAnnouncement = () => {
    const announcementsPath = basePath.includes('/student-dashboard') ? '/student-dashboard/announcements' : '/announcements';
    navigate(`${announcementsPath}?club_id=${club.id}&club_name=${encodeURIComponent(club.name)}`);
  };

  const ProtectedClubRoute = ({ children, checkPermission, userRole, redirectPath = "dashboard" }) => {
    if (checkPermission && !checkPermission(userRole)) {
      return <Navigate to={`../${redirectPath}`} replace />;
    }
    return children;
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative' }}>
      <Routes>
        <Route element={<Outlet context={{ club, userRole, currentUserId: user?.id }} />}>
          <Route 
            path="dashboard" 
          element={
            <ClubDashboard 
              club={club} 
              userRole={userRole}
              membersCount={members.length}
              pendingCount={requests.length}
              tasksCount={tasks.filter(t => t.status === 'ASSIGNED' || t.status === 'IN_PROGRESS').length}
            />
          } 
        />
        <Route path="announcements" element={<ClubAnnouncementsView />} />
        <Route 
          path="members" 
          element={
            <ClubMembersView 
              club={club} 
              userRole={userRole}
              members={members}
              onRoleChange={handleRoleChange}
              onRemoveMember={handleRemoveMember}
            />
          } 
        />
        <Route 
          path="requests" 
          element={
            <ProtectedClubRoute checkPermission={canManageMembers} userRole={userRole}>
              <MembershipRequestsView 
                club={club} 
                userRole={userRole}
                requests={requests}
                onApprove={handleApprove}
                onReject={handleReject}
                loading={loadingRequests}
              />
            </ProtectedClubRoute>
          } 
        />
        <Route 
          path="tasks" 
          element={
            <MyTasksView 
              club={club} 
              userRole={userRole}
              tasks={tasks}
              onUpdateStatus={handleTaskUpdate}
              loading={loadingTasks}
            />
          } 
        />
        {/* Phase 2 routes */}
        <Route path="events" element={<ClubEventsView />} />
        <Route 
          path="manage-tasks" 
          element={
            <ProtectedClubRoute checkPermission={canManageTasks} userRole={userRole}>
              <ManageTasksView />
            </ProtectedClubRoute>
          } 
        />
        <Route 
          path="committees" 
          element={
            <ProtectedClubRoute checkPermission={canViewCommittees} userRole={userRole}>
              <CommitteesView />
            </ProtectedClubRoute>
          } 
        />
        <Route 
          path="committees/:committeeId/*"
          element={<CommitteeWorkspaceView />}
        />
        <Route 
          path="activity-log" 
          element={
            <ProtectedClubRoute checkPermission={(role) => ['president', 'vice_president'].includes(role)} userRole={userRole}>
              <ClubActivityLogView />
            </ProtectedClubRoute>
          } 
        />
        <Route path="resources" element={<ClubResourcesView club={club} userRole={userRole} />} />
        <Route 
          path="budget" 
          element={
            <ProtectedClubRoute checkPermission={canViewBudget} userRole={userRole}>
              <ClubBudgetView />
            </ProtectedClubRoute>
          } 
        />
        <Route 
          path="settings" 
          element={
            <ProtectedClubRoute checkPermission={canViewClubSettings} userRole={userRole}>
              <ClubSettingsView />
            </ProtectedClubRoute>
          } 
        />
        <Route 
          path="roles" 
          element={
            <ProtectedClubRoute checkPermission={canAssignRoles} userRole={userRole}>
              <ManageRolesView />
            </ProtectedClubRoute>
          } 
        />
        <Route 
          path="analytics" 
          element={
            <ProtectedClubRoute checkPermission={canViewAnalytics} userRole={userRole}>
              <ClubAnalyticsView />
            </ProtectedClubRoute>
          } 
        />
        <Route path="certificates" element={<CertificatesView />} />
        <Route path="leave" element={<LeaveClubView />} />
        <Route path="status" element={<ApplicationStatusView />} />
          <Route path="withdraw" element={<WithdrawApplicationView />} />
          <Route path="*" element={<Navigate to={`${clubBasePath}/dashboard`} replace />} />
        </Route>
      </Routes>

      {/* Floating Announcement Button */}
      {canPostAnnouncement(userRole) && (
        <button className={styles.floatingBtn} onClick={handlePostAnnouncement} title="Post Announcement">
          <Icon icon={dashboardIcons.bullhornOutline} />
        </button>
      )}
    </div>
  );
};

// -- Main Hub --
export const ClubsHub = () => {
  const { user } = useSession();
  const { addToast } = useToast();
  const location = useLocation();
  const navigate = useNavigate();
  const [clubs, setClubs] = useState([]);
  const [myClubs, setMyClubs] = useState([]);
  const [selectedClub, setSelectedClub] = useState(null);
  const [userRoleInClub, setUserRoleInClub] = useState(null);
  const [infoClub, setInfoClub] = useState(null);
  const [joinClub, setJoinClub] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [pendingRequestsCount, setPendingRequestsCount] = useState(0);
  const [showProposeModal, setShowProposeModal] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  const isVerified = user?.student_profile?.is_verified === 1 || user?.student_profile?.is_verified === true;
  const basePath = location.pathname.includes('/student-dashboard') ? '/student-dashboard/clubs' : '/clubs';

  // Auto-close modals on any navigation
  useEffect(() => {
    setInfoClub(null);
    setJoinClub(null);
  }, [location.key]);

  // Detect club selection from URL
  useEffect(() => {
    const match = location.pathname.match(/\/clubs\/mine\/(\d+)/);
    if (match) {
      const clubId = match[1];
      const club = myClubs.find(c => String(c.id) === clubId);
      if (club && (!selectedClub || String(selectedClub.id) !== clubId)) {
        setSelectedClub(club);
        setUserRoleInClub(club.role_in_club);
      }
    } else if (selectedClub) {
      // If there's no match (e.g. at /clubs, /clubs/mine, etc), clear selected club
      setSelectedClub(null);
      setUserRoleInClub(null);
    }
  }, [location.pathname, myClubs]);

  // Fetch clubs data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [allData, myData] = await Promise.all([
          clubsApi.getAllClubs({ status: 'ACTIVE' }),
          user?.id ? clubsApi.getUserClubs(user.id) : Promise.resolve([])
        ]);
        // Build a map of club_id -> { membership_status, role_in_club }
        const myClubMap = new Map();
        myData.forEach(c => myClubMap.set(c.id, { 
          membership_status: 'approved', 
          role_in_club: c.role_in_club 
        }));

        // Also check for pending memberships (user applied but not yet approved)
        if (user?.id) {
          try {
            const userApplications = await clubsApi.getUserApplications(user.id);
            if (userApplications?.length) {
              userApplications.forEach(app => {
                if (app.status === 'pending') {
                  const cid = Number(app.club_id);
                  if (!myClubMap.has(cid)) {
                    myClubMap.set(cid, { 
                      membership_status: 'pending', 
                      role_in_club: null 
                    });
                  }
                }
              });
            }
          } catch (e) { /* ignore - pending check is optional */ }
        }
        
        setClubs(allData.map(c => ({
          ...c,
          membership_status: myClubMap.get(c.id)?.membership_status || null,
          role_in_club: myClubMap.get(c.id)?.role_in_club || null
        })));
        setMyClubs(myData);
      } catch (err) {
        console.error("Failed to load clubs", err);
      } finally {
        setIsInitialLoad(false);
      }
    };
    fetchData();
    window.addEventListener('refreshClubs', fetchData);
    return () => window.removeEventListener('refreshClubs', fetchData);
  }, [user]);
  // Poll for requests count to show badge
  useEffect(() => {
    if (selectedClub && canManageMembers(userRoleInClub)) {
      clubsApi.getClubApplications(selectedClub.id)
        .then(reqs => setPendingRequestsCount((reqs || []).filter(r => r.status === 'pending').length))
        .catch(() => setPendingRequestsCount(0));
    } else {
      setPendingRequestsCount(0);
    }
  }, [selectedClub, userRoleInClub]);

  const handleJoinSubmit = async (formData) => {
    try {
      await clubsApi.submitJoinApplication(joinClub.id, user.id, formData);
      addToast({ title: 'Success', message: `Application to join ${joinClub.name} submitted!`, type: 'success' });
      setJoinClub(null);
      setClubs(clubs.map(c => c.id === joinClub.id ? { ...c, membership_status: 'pending' } : c));
      window.dispatchEvent(new Event('refreshNotifications'));
      
      // Update the currently viewed club so the modal updates in real-time
      if (infoClub && infoClub.id === joinClub.id) {
        setInfoClub(prev => ({ ...prev, membership_status: 'pending' }));
      }
    } catch (error) {
      addToast({ title: 'Error', message: error.message || 'Failed to submit application.', type: 'error' });
    }
  };

  const handleInfoOpen = (club) => {
    // Enrich with membership info if the club is in myClubs
    const myClubEntry = myClubs.find(c => c.id === club.id);
    if (myClubEntry) {
      setInfoClub({ 
        ...club, 
        ...myClubEntry, 
        membership_status: 'approved',
        role_in_club: myClubEntry.role_in_club 
      });
    } else {
      // Check if it's in the enriched clubs list (might have pending status)
      const enrichedClub = clubs.find(c => c.id === club.id);
      setInfoClub(enrichedClub || club);
    }
  };

  const handleClubSelect = (club) => {
    // If coming from discover view, find the myClubs entry for full data
    const myClubEntry = myClubs.find(c => c.id === club.id);
    const clubData = myClubEntry || club;
    const role = clubData.role_in_club || club.role_in_club;
    
    setSelectedClub(clubData);
    setUserRoleInClub(role);
    navigate(`${basePath}/mine/${club.id}/dashboard`);
  };

  const handleBackToMyClubs = () => {
    // Only navigate. The useEffect will handle clearing selectedClub 
    // when the URL changes, preventing a race condition with the Catch-All route.
    navigate(`${basePath}/mine`);
  };

  // Build context panel sections based on state
  const panelSections = useMemo(() => {
    if (selectedClub && userRoleInClub) {
      return getClubPanelSections(userRoleInClub, `${basePath}/mine/${selectedClub.id}`, pendingRequestsCount);
    }
    return null;
  }, [selectedClub, userRoleInClub, basePath, pendingRequestsCount]);

  if (isInitialLoad) {
    return (
      <ContextLayout>
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
          Loading your clubs...
        </div>
      </ContextLayout>
    );
  }

  return (
    <ContextLayout>
      <ContextPanel title={selectedClub ? null : "Clubs Hub"}>
        {selectedClub && userRoleInClub ? (
          <>
            {/* Back button */}
            <button className={layoutStyles.panelBackBtn} onClick={handleBackToMyClubs}>
              <Icon icon={uiIcons.arrowLeft} /> Back to My Clubs
            </button>

            {/* Club header without role badge to reduce clutter */}
            <div className={layoutStyles.clubHeader}>
              <div className={layoutStyles.clubHeaderName}>{selectedClub.name}</div>
            </div>

            {/* Role-based navigation sections */}
            {panelSections && panelSections.map(section => (
              <ContextPanelSection key={section.title} title={section.title}>
                {section.items.map(item => (
                  <ContextPanelLink 
                    key={item.to}
                    to={item.to}
                    icon={item.icon}
                    label={item.label}
                    badge={item.badge}
                  />
                ))}
              </ContextPanelSection>
            ))}
          </>
        ) : (
          <>
            <ContextPanelSection title="Discover">
              <ContextPanelLink 
                to={basePath}
                exact={true}
                icon={landingIcons.compassOutline} 
                label="All Clubs" 
              />
            </ContextPanelSection>

            {isVerified && (
              <ContextPanelSection title="My Clubs">
                <ContextPanelLink 
                  to={`${basePath}/mine`}
                  icon={dashboardIcons.accountGroupOutline} 
                  label="Joined Clubs" 
                  badge={myClubs.length > 0 ? myClubs.length : null}
                />
              </ContextPanelSection>
            )}

            {isVerified && (
              <ContextPanelSection title="Start a Club">
                <button 
                  className={layoutStyles.panelBackBtn} 
                  style={{ width: '100%', marginTop: '0.5rem', color: 'var(--primary)', borderColor: 'var(--primary)' }}
                  onClick={() => setShowProposeModal(true)}
                >
                  <Icon icon={uiIcons.plusCircleOutline} /> Propose New Club
                </button>
              </ContextPanelSection>
            )}
          </>
        )}
      </ContextPanel>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Routes>
          <Route 
            index 
            element={
              <AllClubsView 
                clubs={clubs} 
                onJoinClick={handleInfoOpen}
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
              />
            } 
          />
          <Route 
            path="mine" 
            element={
              <MyClubsView 
                myClubs={myClubs}
                onClubSelect={handleInfoOpen}
              />
            } 
          />
          {selectedClub && userRoleInClub && (
            <Route 
              path={`mine/${selectedClub.id}/*`}
              element={
                <ClubWorkspace
                  club={selectedClub}
                  userRole={userRoleInClub}
                  user={user}
                  onBack={handleBackToMyClubs}
                  basePath={basePath}
                />
              }
            />
          )}
          <Route path="*" element={<Navigate to={basePath} replace />} />
        </Routes>
      </div>

      <ClubInfoModal 
        club={infoClub} 
        onClose={() => setInfoClub(null)} 
        onJoinClick={(c) => {
          if (!isVerified) {
            addToast({ title: 'Verification Required', message: 'You must be a verified student to join clubs.', type: 'warning' });
            return;
          }
          setJoinClub(c);
        }} 
        onOpenWorkspace={(c) => {
          setInfoClub(null);
          handleClubSelect(c);
        }}
      />

      <ClubRegistrationModal 
        isOpen={!!joinClub}
        onClose={() => setJoinClub(null)}
        club={joinClub}
        onJoin={handleJoinSubmit}
      />

      <ProposeClubModal 
        isOpen={showProposeModal}
        onClose={() => setShowProposeModal(false)}
      />
    </ContextLayout>
  );
};



