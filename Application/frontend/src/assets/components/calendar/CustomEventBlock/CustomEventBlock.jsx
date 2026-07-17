import React from 'react';
import { format } from 'date-fns';
import { Icon } from '@iconify/react';
import { calendarIcons } from '../../../icons/registry';
import styles from './CustomEventBlock.module.css';

const CustomEventBlock = ({ event }) => {
  const timeString = `${format(new Date(event.start), 'h:mm a')}`;
  
  return (
    <div className={styles.eventContent} title={`${timeString} - ${event.sessionTitle}`}>
      {event.hasConflict && (
        <div className={styles.conflictBadge} title="Conflict with another registered event">
          <Icon icon={calendarIcons.conflict} width="12" />
        </div>
      )}
      <span className={styles.eventTime}>{timeString}</span>
      <span className={styles.eventTitle}>{event.sessionTitle}</span>
    </div>
  );
};

export default CustomEventBlock;

