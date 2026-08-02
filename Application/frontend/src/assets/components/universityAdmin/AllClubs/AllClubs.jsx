import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { SearchInput } from '../../ui/SearchInput/SearchInput';
import { universityAdminApi } from '@api/universityAdminApis/universityAdmin';
import styles from './AllClubs.module.css';
import { uiIcons, dashboardIcons } from '../../../icons/registry';

export const AllClubs = () => {
  const [clubs, setClubs] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    universityAdminApi.getAllClubs().then((data) => {
      if (isMounted) {
        setClubs(data);
        setLoading(false);
      }
    });
    return () => { isMounted = false; };
  }, []);

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
          <h2 className={styles.title}>All Clubs</h2>
          <p className={styles.subtitle}>Every club registered at your university.</p>
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
        ]}
        data={filtered}
        emptyIcon={dashboardIcons.accountGroupOutline}
        emptyTitle="No clubs found"
        emptyDesc="Clubs registered at your university will appear here."
      />
    </div>
  );
};
