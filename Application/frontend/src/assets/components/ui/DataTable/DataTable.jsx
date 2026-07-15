import { useState } from 'react';
import styles from './DataTable.module.css';
import { Icon } from '@iconify/react';
import { EmptyState } from '../EmptyState/EmptyState';
import { Button } from '../Button/Button';

export const DataTable = ({ 
  columns, 
  data, 
  onRowClick,
  emptyTitle = "No data found",
  emptyDesc = "There are no records to display."
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 5;

  if (!data || data.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDesc} />;
  }

  const totalPages = Math.ceil(data.length / rowsPerPage);
  const currentData = data.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage);

  return (
    <div className={styles.tableContainer}>
      <table className={styles.table}>
        <thead>
          <tr>
            {columns.map((col, idx) => (
              <th key={idx} style={{ width: col.width || 'auto' }}>{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {currentData.map((row, rIdx) => (
            <tr 
              key={row.id || rIdx} 
              onClick={() => onRowClick && onRowClick(row)}
              className={onRowClick ? styles.clickableRow : ''}
            >
              {columns.map((col, cIdx) => (
                <td key={cIdx}>
                  {col.cell ? col.cell(row) : row[col.accessor]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      
      {totalPages > 1 && (
        <div className={styles.pagination}>
          <Button 
            variant="outline"
            size="sm"
            disabled={currentPage === 1} 
            onClick={() => setCurrentPage(prev => prev - 1)}
            className={styles.pageBtn}
          >
            <Icon icon="mdi:chevron-left" /> Previous
          </Button>
          <span className={styles.pageInfo}>Page {currentPage} of {totalPages}</span>
          <Button 
            variant="outline"
            size="sm"
            disabled={currentPage === totalPages} 
            onClick={() => setCurrentPage(prev => prev + 1)}
            className={styles.pageBtn}
          >
            Next <Icon icon="mdi:chevron-right" />
          </Button>
        </div>
      )}
    </div>
  );
};
