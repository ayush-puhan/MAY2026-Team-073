import React from 'react';
import { Icon } from '@iconify/react';
import styles from './DataTable.module.css';
import { EmptyState } from '../EmptyState/EmptyState';

// columns: [{ header, accessor?, cell? }]
export const DataTable = ({ columns = [], data = [], onRowClick, emptyIcon, emptyTitle = 'No records found', emptyDesc }) => {
  if (!data.length) {
    return <EmptyState icon={emptyIcon} title={emptyTitle} description={emptyDesc} />;
  }

  return (
    <div className={styles.tableWrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            {columns.map((col, idx) => (
              <th key={idx}>{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr
              key={row.id ?? rowIdx}
              className={onRowClick ? styles.clickableRow : undefined}
              onClick={() => onRowClick?.(row)}
            >
              {columns.map((col, colIdx) => (
                <td key={colIdx}>
                  {col.cell ? col.cell(row) : row[col.accessor]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export const RowChevron = () => <Icon icon="mdi:chevron-right" className={styles.rowChevron} />;
