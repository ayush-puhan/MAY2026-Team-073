import React from 'react';
import { Icon } from '@iconify/react';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';
import { TaskCard } from '../TaskCard/TaskCard';
import { rewardsIcons } from '../../../icons/registry';
import styles from './ViewAllTasksModal.module.css';

export const ViewAllTasksModal = ({ isOpen, onClose, tasks, completions, onCompleteTask }) => {
  if (!isOpen) return null;

  const isTaskCompleted = (taskId) => {
    return completions.some(c => c.task_id === taskId);
  };

  const renderSection = (title, icon, type) => {
    const sectionTasks = tasks.filter(t => t.type === type && t.is_active);
    if (sectionTasks.length === 0) return null;

    return (
      <div key={type} className={styles.taskSection}>
        <h3 className={styles.sectionTitle}>
          <Icon icon={icon} /> {title}
        </h3>
        <div className={styles.taskGrid}>
          {sectionTasks.map(task => (
            <TaskCard 
              key={task.id} 
              task={task} 
              isCompleted={isTaskCompleted(task.id)}
              onComplete={onCompleteTask} 
            />
          ))}
        </div>
      </div>
    );
  };

  const modalContent = (
    <AnimatePresence>
      <div className={styles.overlay} onClick={onClose}>
        <motion.div 
          className={styles.modal} 
          onClick={e => e.stopPropagation()}
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.2 }}
        >
          <div className={styles.header}>
            <h2>All Available Tasks</h2>
            <button className={styles.closeBtn} onClick={onClose}>
              <Icon icon="mdi:close" width="24" height="24" />
            </button>
          </div>
          
          <div className={styles.body}>
            {renderSection("Daily Tasks", rewardsIcons.calendarToday, "daily")}
            {renderSection("Weekly Challenges", rewardsIcons.calendarWeek, "weekly")}
            {renderSection("Monthly Goals", rewardsIcons.calendarMonth, "monthly")}
            {renderSection("One-Time Achievements", rewardsIcons.trophyAward, "one_time")}
            {renderSection("Secret Missions", "mdi:incognito", "secret")}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );

  return typeof document !== 'undefined' ? createPortal(modalContent, document.body) : null;
};
