import React, { useState, useEffect, useMemo } from 'react';
import { Icon } from '@iconify/react';
import { Button } from '../../ui/Button/Button';
import { DataTable } from '../../ui/DataTable/DataTable';
import { EmptyState } from '../../ui/EmptyState/EmptyState';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { AnnouncementComposerModal } from '../Composer/AnnouncementComposerModal';
import { AnnouncementDetailModal } from './AnnouncementDetailModal/AnnouncementDetailModal';
import { announcementsApi } from '@api/announcementsApis/announcements';
import styles from './AnnouncementCenter.module.css';

export const AnnouncementCenter = () => {
  const { user } = useSession();
  const { showSuccess, showError } = useToast();
  const [announcements, setAnnouncements] = useState([]);
  const [clubs, setClubs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isComposerOpen, setIsComposerOpen] = useState(false);
  const [selectedAnnouncement, setSelectedAnnouncement] = useState(null);

  // Role Checks
  const role = user?.role?.toLowerCase() || '';
  const isSysAdmin = role === 'system_admin';
  const isUniAdmin = role === 'dean_student_welfare' || role === 'student_affairs_office';
  const isFaculty = role === 'faculty_advisor';
  
  // Determine if the user can post to ANY club/university
  const hasManagementRoles = user?.club_memberships?.some(m => 
    ['president', 'vice_president', 'secretary', 'treasurer', 'event_coordinator', 'volunteer_coordinator', 'committee_member']
    .includes(m.role.toLowerCase())
  );
  
  const canPost = isSysAdmin || isUniAdmin || isFaculty || hasManagementRoles;

  // Determine allowed post targets (Clubs or University-Wide)
  const allowedPostTargets = [];
  if (isSysAdmin || isUniAdmin) {
    allowedPostTargets.push({ id: 'university', name: 'University-Wide' });
  }
  
  if (isFaculty) {
    const advisedClubs = clubs.filter(c => String(c.faculty_advisor_id) === String(user.id));
    advisedClubs.forEach(c => allowedPostTargets.push({ id: c.id, name: c.name }));
  } else if (hasManagementRoles) {
    user.club_memberships.forEach(m => {
      if (['president', 'vice_president', 'secretary', 'treasurer', 'event_coordinator', 'volunteer_coordinator', 'committee_member'].includes(m.role.toLowerCase())) {
        const club = clubs.find(c => String(c.id) === String(m.club_id));
        if (club) allowedPostTargets.push({ id: club.id, name: club.name });
      }
    });
  }

  const load = async () => {
    setLoading(true);
    try {
      // Only fetch clubs relevant to the user, not all clubs
      let relevantClubs = [];
      if (isSysAdmin) {
        // System admin doesn't need clubs for announcements
        relevantClubs = [];
      } else if (isUniAdmin) {
        // Uni admins see their university's clubs
        const allClubs = await announcementsApi.getClubs();
        relevantClubs = allClubs.filter(c => String(c.university_id) === String(user.university_id));
      } else if (isFaculty) {
        const allClubs = await announcementsApi.getClubs();
        relevantClubs = allClubs.filter(c => String(c.faculty_advisor_id) === String(user.id));
      } else {
        // Students: derive clubs from memberships
        const memberships = user?.club_memberships || [];
        const memberClubIds = memberships.map(m => m.club_id);
        if (memberClubIds.length > 0) {
          const allClubs = await announcementsApi.getClubs();
          relevantClubs = allClubs.filter(c => memberClubIds.includes(c.id));
        }
      }
      setClubs(relevantClubs);

      // Fetch announcements — backend now handles privacy filtering
      let data = [];
      if (isSysAdmin) {
        const allAnnouncements = await announcementsApi.getAnnouncements();
        data = allAnnouncements;
      } else if (isUniAdmin) {
        // Backend now filters to only return user-relevant announcements
        const uniData = await announcementsApi.getAnnouncements('university');
        const perClubData = await Promise.all(relevantClubs.map(c => announcementsApi.getAnnouncements(c.id)));
        data = [...uniData, ...perClubData.flat()];
      } else if (isFaculty) {
        const uniData = await announcementsApi.getAnnouncements('university');
        const perClubData = await Promise.all(relevantClubs.map(c => announcementsApi.getAnnouncements(c.id)));
        data = [...uniData, ...perClubData.flat()];
      } else {
        const uniData = await announcementsApi.getAnnouncements('university');
        const myClubs = user?.club_memberships?.map(m => m.club_id) || [];
        const perClubData = await Promise.all(myClubs.map(id => announcementsApi.getAnnouncements(id)));
        data = [...uniData, ...perClubData.flat()];
      }
      
      data = data.map(a => ({
        ...a,
        club_name: a.club_id ? relevantClubs.find(c => String(c.id) === String(a.club_id))?.name || 'Club' : (a.target_audience === 'system_wide' ? 'System-Wide' : 'University-Wide')
      }));

      const uniqueData = Array.from(new Map(data.map(item => [item.id, item])).values());
      uniqueData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

      setAnnouncements(uniqueData);
    } catch (e) {
      console.error(e);
      showError("Failed to load announcements");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handlePublish = async ({ title, body, club_id }) => {
    try {
      let audience = 'all_members';
      if (isSysAdmin) {
        audience = 'system_wide';
      } else if (!club_id || club_id === 'university') {
        audience = 'university_wide';
      }

      const payload = {
        posted_by: user.id,
        posted_by_role: user.role.toLowerCase(),
        title,
        body,
        target_audience: audience
      };
      
      if (club_id && club_id !== 'university') {
        payload.club_id = club_id;
      }

      await announcementsApi.postAnnouncement(payload);
      showSuccess('Announcement published.');
      setIsComposerOpen(false);
      load();
    } catch (err) {
      showError(err.message || 'Failed to publish announcement.');
    }
  };

  const columns = [
    { 
      header: 'Source', 
      cell: (row) => (
        <span className={styles.cardClubTag}>
          {(row.club_name === 'University-Wide' || row.club_name === 'System-Wide') ? (
            <Icon icon="mdi:bank" className={styles.tagIcon} />
          ) : (
            <Icon icon="mdi:account-group" className={styles.tagIcon} />
          )}
          {row.club_name}
        </span>
      ) 
    },
    { 
      header: 'Title', 
      cell: (row) => <span className={styles.cardTitle}>{row.title}</span>
    },
    { 
      header: 'Date', 
      cell: (row) => <span className={styles.cardDate}>{new Date(row.created_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' })}</span>
    }
  ];

  if (loading) {
    return (
      <div className={styles.loading}>
        <Icon icon="mdi:loading" className="animate-spin" width="32" />
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Announcement Center</h2>
          <p className={styles.subtitle}>Stay updated with the latest news and announcements.</p>
        </div>
        {canPost && (
          <Button variant="primary" icon="mdi:plus" onClick={() => setIsComposerOpen(true)}>
            New Announcement
          </Button>
        )}
      </div>

      <div className={styles.tableWrapper}>
        <DataTable 
          data={announcements}
          columns={columns}
          onRowClick={(row) => setSelectedAnnouncement(row)}
          emptyMessage="No announcements yet. Check back later for updates."
        />
      </div>

      {isComposerOpen && (
        <AnnouncementComposerModal
          onClose={() => setIsComposerOpen(false)}
          onSubmit={handlePublish}
          clubOptions={allowedPostTargets.map(t => ({ value: t.id, label: t.name }))}
          user={user}
        />
      )}

      {selectedAnnouncement && (
        <AnnouncementDetailModal 
          announcement={selectedAnnouncement}
          onClose={() => setSelectedAnnouncement(null)}
        />
      )}
    </div>
  );
};
