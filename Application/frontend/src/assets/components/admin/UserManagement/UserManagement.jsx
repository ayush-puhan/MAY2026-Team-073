import { useState, useEffect } from 'react';
import { adminApi } from '@api/adminApis/admin';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { FilterTabs } from '../../ui/FilterTabs/FilterTabs';
import { SearchInput } from '../../ui/SearchInput/SearchInput';
import { Button } from '../../ui/Button/Button';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';
import { UserDetailModal } from './UserDetailModal/UserDetailModal';
import { AddUserModal } from './AddUserModal/AddUserModal';
import { USER_ROLES_OPTIONS } from '../../../../config/enums';
import styles from './UserManagement.module.css';

export const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [isAddUserOpen, setIsAddUserOpen] = useState(false);

  const tabs = [
    { id: 'all', label: 'All Users' },
    { id: 'active', label: 'Active' },
    { id: 'inactive', label: 'Inactive' }
  ];

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getUsers();
      setUsers(data);
      setFilteredUsers(data);
    } catch (error) {
      console.error("Failed to load users", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    let result = users;
    
    // Filter by Tab
    if (activeTab === 'active') result = result.filter(u => u.is_active);
    if (activeTab === 'inactive') result = result.filter(u => !u.is_active);
    
    // Filter by Search
    if (searchTerm) {
      const lowerSearch = searchTerm.toLowerCase();
      result = result.filter(u => 
        u.full_name?.toLowerCase().includes(lowerSearch) || 
        u.email?.toLowerCase().includes(lowerSearch)
      );
    }

    setFilteredUsers(result);
  }, [users, activeTab, searchTerm]);

  const handleRowClick = async (user) => {
    try {
      const fullUser = await adminApi.getUserById(user.id);
      setSelectedUser(fullUser);
    } catch (error) {
      console.error("Failed to load full user details", error);
    }
  };

  const handleUserUpdate = () => {
    fetchUsers();
    setSelectedUser(null);
  };

  const handleUserAdded = () => {
    fetchUsers();
  };

  const columns = [
    { 
      header: 'Name', 
      cell: (row) => (
        <div className={styles.userCell}>
          <div className={styles.avatar}>
            {row.full_name?.charAt(0).toUpperCase()}
          </div>
          <div>
            <div className={styles.userName}>{row.full_name}</div>
            {row.role === 'student' && <div className={styles.userEmail}>{row.email}</div>}
          </div>
        </div>
      )
    },
    { header: 'Role', cell: (row) => <span className={styles.roleLabel}>{USER_ROLES_OPTIONS.find(r => r.value === row.role)?.label || row.role}</span> },
    { header: 'Status', cell: (row) => <StatusBadge status={row.is_active ? 'Active' : 'Inactive'} /> },
    { header: 'Joined', cell: (row) => new Date(row.created_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' }) },
    { header: '', cell: () => <Icon icon={uiIcons.chevronRight} color="var(--muted-foreground)" width="20" /> }
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleSection}>
          <h2 className={styles.title}>User Management</h2>
          <p className={styles.subtitle}>View and manage platform users, roles, and account statuses.</p>
        </div>
        <Button onClick={() => setIsAddUserOpen(true)} variant="primary">
          <Icon icon={uiIcons.plus} /> Add User
        </Button>
      </div>

      <div className={styles.controls}>
        <FilterTabs 
          tabs={tabs} 
          activeTab={activeTab} 
          onTabChange={setActiveTab} 
        />
        <SearchInput 
          placeholder="Search users..." 
          onChange={setSearchTerm} 
          style={{ width: '300px' }}
        />
      </div>

      {loading ? (
        <div className={styles.loading}><Icon icon={uiIcons.loading} className="spin" width="32" /></div>
      ) : (
        <DataTable 
          columns={columns} 
          data={filteredUsers} 
          onRowClick={handleRowClick}
          emptyTitle="No users found"
          emptyDesc="Try adjusting your search or filters."
        />
      )}

      {selectedUser && (
        <UserDetailModal 
          user={selectedUser} 
          onClose={() => setSelectedUser(null)} 
          onUpdate={handleUserUpdate}
        />
      )}

      {isAddUserOpen && (
        <AddUserModal 
          onClose={() => setIsAddUserOpen(false)}
          onAdd={handleUserAdded}
        />
      )}
    </div>
  );
};
