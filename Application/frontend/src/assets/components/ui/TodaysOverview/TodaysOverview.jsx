import React from 'react';
import { Icon } from '@iconify/react';
import styles from './TodaysOverview.module.css';
import { calendarIcons } from '../../../icons/registry';

export const TodaysOverview = () => {
  const agenda = [
    { id: 1, time: '10:00 AM', title: 'Registration Deadline', desc: 'Hackathon 2024', type: 'deadline', color: 'var(--orange)' },
    { id: 2, time: '02:00 PM', title: 'Robotics Club Meetup', desc: 'Lab 3', type: 'meeting', color: 'var(--blue)' },
    { id: 3, time: '05:30 PM', title: 'Musical Night Rehearsal', desc: 'Auditorium', type: 'event', color: 'var(--purple)' },
  ];

  return (
    <div className={styles.widgetCard}>
      <div className={styles.header}>
        <h3 className={styles.title}>
          <Icon icon={calendarIcons.calendarToday} width="20" />
          Today's Overview
        </h3>
      </div>
      <div className={styles.content}>
        <div className={styles.timeline}>
          {agenda.map((item, index) => (
            <div key={item.id} className={styles.timelineItem}>
              <div className={styles.timeLineCol}>
                <div className={styles.dot} style={{ borderColor: item.color }} />
                {index !== agenda.length - 1 && <div className={styles.line} />}
              </div>
              <div className={styles.contentCol}>
                <span className={styles.time}>{item.time}</span>
                <p className={styles.itemTitle}>{item.title}</p>
                <p className={styles.itemDesc}>{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
