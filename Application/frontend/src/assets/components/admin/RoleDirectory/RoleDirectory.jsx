import { useState, useEffect } from 'react';
import { adminApi } from '../../../../api/admin.api';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { SearchInput } from '../../ui/SearchInput/SearchInput';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';
import { USER_ROLES_OPTIONS } from '../../../../config/enums';
import styles from './RoleDirectory.module.css';

export const RoleDirectory = () => {
  const [allUsers, setAllUsers] = useState([]);
  const [selectedRole, setSelectedRole] = useState(USER_ROLES_OPTIONS[0]?.value);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await adminApi.getUsers();
        setAllUsers(data);
      } catch (error) {
        console.error("Failed to load users", error);
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  const filteredUsers = allUsers.filter(u => {
    const matchesRole = u.role === selectedRole;
    const matchesSearch = u.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          u.email?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesRole && matchesSearch;
  });

  const getUserCountForRole = (roleValue) => allUsers.filter(u => u.role === roleValue).length;

  const columns = [
    { header: 'Name', cell: (row) => <span style={{ fontWeight: 500 }}>{row.full_name}</span> },
    { header: 'Status', cell: (row) => <StatusBadge status={row.is_active ? 'Active' : 'Inactive'} /> },
    { header: 'Joined', cell: (row) => new Date(row.created_at).toLocaleDateString() }
  ];

  if (loading) {
    return <div className={styles.loading}><Icon icon={uiIcons.loading} className="spin" width="32" /></div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Role Directory</h2>
        <p className={styles.subtitle}>View users grouped by their platform roles.</p>
      </div>

      <div className={styles.layout}>
        <div className={styles.rolesSidebar}>
          {USER_ROLES_OPTIONS.map(role => (
            <button
              key={role.value}
              className={`${styles.roleBtn} ${selectedRole === role.value ? styles.active : ''}`}
              onClick={() => setSelectedRole(role.value)}
            >
              <div className={styles.roleName}>{role.label}</div>
              <span className={styles.roleCount}>{getUserCountForRole(role.value)}</span>
            </button>
          ))}
        </div>

        <div className={styles.roleContent}>
          <div className={styles.contentHeader}>
            <div className={styles.contentHeaderLeft}>
              <h3>{USER_ROLES_OPTIONS.find(r => r.value === selectedRole)?.label}</h3>
              <span className={styles.userCount}>{filteredUsers.length} Users</span>
            </div>
            <SearchInput 
              placeholder="Search user..." 
              onChange={setSearchTerm}
              style={{ width: '250px' }}
            />
          </div>
          <div className={styles.tableWrapper}>
            <DataTable 
              columns={columns} 
              data={filteredUsers} 
              emptyTitle="No users found"
              emptyDesc={`There are no users with the ${USER_ROLES_OPTIONS.find(r => r.value === selectedRole)?.label} role.`}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
