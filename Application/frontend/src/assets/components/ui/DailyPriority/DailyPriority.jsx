import React from 'react';
import styles from './DailyPriority.module.css';

export const DailyPriority = () => {
  const agenda = [
    { id: 1, time: '10:00 AM', title: 'Registration Deadline', type: 'deadline', color: 'var(--orange)' },
    { id: 2, time: '02:00 PM', title: 'Robotics Club Meetup', type: 'meeting', color: 'var(--blue)' },
    { id: 3, time: '05:30 PM', title: 'Musical Night Rehearsal', type: 'event', color: 'var(--purple)' },
  ];

  return (
    <div className={styles.prioritySection}>
      <h3 className={styles.sectionTitle}>Agenda</h3>
      <div className={styles.timeline}>
        {agenda.map((item, index) => (
          <div key={item.id} className={styles.timelineItem}>
            <div className={styles.timeLineCol}>
              <div className={styles.dot} style={{ borderColor: item.color, backgroundColor: item.color }} />
              {index !== agenda.length - 1 && <div className={styles.line} />}
            </div>
            <div className={styles.contentCol}>
              <span className={styles.time}>{item.time}</span>
              <p className={styles.itemTitle}>{item.title}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};


