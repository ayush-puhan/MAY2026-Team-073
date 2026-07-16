import { useState, useEffect } from 'react';
import { adminApi } from '../../../../api/admin.api';
import { Icon } from '@iconify/react';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { SearchInput } from '../../ui/SearchInput/SearchInput';
import { Button } from '../../ui/Button/Button';
import { uiIcons, adminIcons } from '../../../icons/registry';
import { UniversityModal } from './UniversityModal/UniversityModal';
import styles from './PlatformSettings.module.css';

export const PlatformSettings = () => {
  const [universities, setUniversities] = useState([]);
  const [filteredUnis, setFilteredUnis] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUni, setSelectedUni] = useState(null);

  const fetchUniversities = async () => {
    setLoading(true);
    try {
      // If we don't have getUniversities yet, fallback gracefully
      const data = await (adminApi.getUniversities ? adminApi.getUniversities() : adminApi.getPlatformSettings(1).then(d => [d]));
      setUniversities(Array.isArray(data) ? data : [data]);
    } catch (error) {
      console.error("Failed to load universities", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUniversities();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const lowerSearch = searchTerm.toLowerCase();
      setFilteredUnis(universities.filter(u => 
        u.name?.toLowerCase().includes(lowerSearch) || 
        u.domain?.toLowerCase().includes(lowerSearch)
      ));
    } else {
      setFilteredUnis(universities);
    }
  }, [universities, searchTerm]);

  const handleRowClick = (uni) => {
    setSelectedUni(uni);
    setIsModalOpen(true);
  };

  const handleAddClick = () => {
    setSelectedUni(null);
    setIsModalOpen(true);
  };

  const handleModalSave = () => {
    setIsModalOpen(false);
    fetchUniversities();
  };

  const columns = [
    { header: 'ID', cell: (row) => <span>#{row.id || '—'}</span>, width: '80px' },
    { 
      header: 'University Name', 
      cell: (row) => <strong style={{ color: 'var(--foreground)' }}>{row.name}</strong> 
    },
    { header: 'Domain', accessor: 'domain' },
    { header: 'Status', cell: (row) => <StatusBadge status={row.is_active ? 'Active' : 'Maintenance'} /> },
    { header: 'Added', cell: (row) => row.created_at ? new Date(row.created_at).toLocaleDateString() : '—' },
    { header: '', cell: () => <Icon icon={uiIcons.chevronRight} color="var(--muted-foreground)" width="20" /> }
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleSection}>
          <h2 className={styles.title}>Platform Settings (Universities)</h2>
          <p className={styles.subtitle}>Manage universities onboarded to the platform.</p>
        </div>
      </div>

      <div className={styles.controls}>
        <SearchInput 
          placeholder="Search universities..." 
          onChange={setSearchTerm} 
          style={{ width: '300px' }}
        />
        <Button onClick={handleAddClick} variant="primary">
          <Icon icon="mdi:plus" /> Add University
        </Button>
      </div>

      <div className={styles.content}>
        {loading ? (
          <div className={styles.loading}><Icon icon={uiIcons.loading} className="spin" width="32" /></div>
        ) : (
          <DataTable 
            columns={columns} 
            data={filteredUnis} 
            onRowClick={handleRowClick}
            emptyTitle="No universities found"
            emptyDesc="Try adjusting your search criteria."
          />
        )}
      </div>

      {isModalOpen && (
        <UniversityModal 
          onClose={() => setIsModalOpen(false)}
          onSave={handleModalSave}
          university={selectedUni}
        />
      )}
    </div>
  );
};
