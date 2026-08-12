import React from 'react';
import { motion } from 'framer-motion';
import { SearchInput } from '../../../../ui/SearchInput/SearchInput';
import { DataTable } from '../../../../ui/DataTable/DataTable';
import styles from '../ClubDetailModal.module.css';

export const CommitteesStep = ({ club, filteredCommittees, onSearch }) => {
  return (
    <motion.div
      key="committees"
      initial={{ opacity: 0, x: 8 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -8 }}
      transition={{ duration: 0.15 }}
      className={styles.section}
    >
      <h4 className={styles.sectionTitle}>Committees ({club.committees?.length || 0})</h4>
      <SearchInput placeholder="Search committees..." onChange={onSearch} />
      <DataTable
        columns={[
          { header: 'Name', accessor: 'name' },
          { header: 'Description', accessor: 'description' },
        ]}
        data={filteredCommittees}
        emptyTitle="No committees found"
        emptyDesc="No committees set up yet."
      />
    </motion.div>
  );
};
