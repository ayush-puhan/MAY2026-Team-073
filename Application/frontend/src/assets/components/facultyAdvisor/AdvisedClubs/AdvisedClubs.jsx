import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { DataTable, RowChevron } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { SearchInput } from '../../ui/SearchInput/SearchInput';
import { facultyAdvisorApi } from '@api/facultyAdvisorApis/facultyAdvisor';
import { useSession } from '../../../../context/SessionContext';
import { ClubDetailModal } from './ClubDetailModal/ClubDetailModal';
import styles from './AdvisedClubs.module.css';
import { uiIcons, dashboardIcons } from '../../../icons/registry';

export const AdvisedClubs = () => {
  const { user } = useSession();
  const [clubs, setClubs] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedClubId, setSelectedClubId] = useState(null);

  useEffect(() => {
    let isMounted = true;
    facultyAdvisorApi.getAdvisedClubs(user.id).then((data) => {
      if (isMounted) {
        setClubs(data);
        setLoading(false);
      }
    });
    return () => { isMounted = false; };
  }, [user.id]);

  useEffect(() => {
    setFiltered(
      clubs.filter((c) => c.name.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }, [clubs, searchTerm]);

  if (loading) {
    return (
      <div className={styles.loading}>
        <Icon icon={uiIcons.loading} className="animate-spin" width="32" />
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Advised Clubs</h2>
          <p className={styles.subtitle}>Clubs you supervise as faculty advisor.</p>
        </div>
      </div>

      <div className={styles.controls}>
        <SearchInput placeholder="Search clubs..." onChange={setSearchTerm} />
      </div>

      <DataTable
        columns={[
          { header: 'Name', accessor: 'name' },
          { header: 'Category', accessor: 'category' },
          { header: 'Members', accessor: 'member_count_cache' },
          { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
          { header: '', cell: () => <RowChevron /> },
        ]}
        data={filtered}
        onRowClick={(row) => setSelectedClubId(row.id)}
        emptyIcon={dashboardIcons.accountGroupOutline}
        emptyTitle="No advised clubs"
        emptyDesc="Clubs assigned to you as faculty advisor will appear here."
      />

      {selectedClubId && (
        <ClubDetailModal clubId={selectedClubId} onClose={() => setSelectedClubId(null)} />
      )}
    </div>
  );
};
