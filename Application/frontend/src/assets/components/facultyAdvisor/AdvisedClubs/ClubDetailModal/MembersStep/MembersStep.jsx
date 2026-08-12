import React from 'react';
import { motion } from 'framer-motion';
import { SearchInput } from '../../../../ui/SearchInput/SearchInput';
import { DataTable } from '../../../../ui/DataTable/DataTable';
import styles from '../ClubDetailModal.module.css';

export const MembersStep = ({ club, filteredMembers, onSearch }) => {
  return (
    <motion.div
      key="members"
      initial={{ opacity: 0, x: 8 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -8 }}
      transition={{ duration: 0.15 }}
      className={styles.section}
    >
      <h4 className={styles.sectionTitle}>Members ({club.members?.length || 0})</h4>
      <SearchInput placeholder="Search users..." onChange={onSearch} />
      <DataTable
        columns={[
          { header: 'Name', accessor: 'user_name' },
          { header: 'Role', cell: (row) => <span className={styles.memberRole}>{row.role_in_club}</span> },
        ]}
        data={filteredMembers}
        emptyTitle="No members found"
        emptyDesc="No approved members yet."
      />
    </motion.div>
  );
};
