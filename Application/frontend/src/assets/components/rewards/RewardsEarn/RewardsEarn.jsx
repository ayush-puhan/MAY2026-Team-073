import React, { useEffect, useState } from 'react';
import { useSession } from '../../../../context/SessionContext';
import { rewardsApi } from '../../../../api';
import { TaskCard } from '../TaskCard/TaskCard';
import { Icon } from '@iconify/react';
import { rewardsIcons } from '../../../icons/registry';
import { useToast } from '../../../../context/ToastContext';
import { ViewAllTasksModal } from './ViewAllTasksModal';
import styles from './RewardsEarn.module.css';

export const RewardsEarn = () => {
  const { user } = useSession();
  const [tasks, setTasks] = useState([]);
  const [completions, setCompletions] = useState([]);
  const [streak, setStreak] = useState(1);
  const [points, setPoints] = useState(0);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { showSuccess, showError } = useToast();

  const loadData = async () => {
    try {
      const [allTasks, userCompletions, userPoints] = await Promise.all([
        rewardsApi.getRewardTasks(),
        rewardsApi.getTaskCompletions(user.id),
        rewardsApi.getUserPoints(user.id)
      ]);
      const visibleTasks = allTasks.filter(t => user.is_verified || !t.requires_verified);
      setTasks(visibleTasks);
      setCompletions(userCompletions);
      setPoints(userPoints);

      // Calculate simple mock streak
      const today = new Date().toISOString().split('T')[0];
      const hasToday = userCompletions.some(c => c.completed_at.startsWith(today));
      setStreak(hasToday ? 2 : 1);
    } catch (err) {
      console.error('Failed to load rewards data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user.id]);

  const handleCompleteTask = async (task) => {
    try {
      await rewardsApi.completeTask(user.id, task.id);
      showSuccess(`Task "${task.title}" completed! You earned ${task.points} points.`);
      await loadData();
    } catch (err) {
      console.error('Failed to complete task', err);
      showError('Failed to complete task. Please try again.');
    }
  };

  const isTaskCompleted = (taskId) => {
    return completions.some(c => c.task_id === taskId);
  };

  if (loading) return <div className={styles.loader}><Icon icon="line-md:loading-twotone-loop" /> Loading...</div>;

  const getTier = (pts) => {
    if (pts >= 3000) return { name: 'Platinum', color: '#E5E4E2' };
    if (pts >= 1500) return { name: 'Gold', color: '#FFD700' };
    if (pts >= 500) return { name: 'Silver', color: '#C0C0C0' };
    return { name: 'Bronze', color: '#CD7F32' };
  };

  const tier = getTier(points);

  const renderSection = (title, icon, type) => {
    const sectionTasks = tasks.filter(t => t.type === type && t.is_active);
    if (sectionTasks.length === 0) return null;

    return (
      <div className={styles.taskSection}>
        <h3 className={styles.sectionTitle}>
          <Icon icon={icon} /> {title}
        </h3>
        <div className={styles.taskGrid}>
          {sectionTasks.map(task => (
            <TaskCard 
              key={task.id} 
              task={task} 
              isCompleted={isTaskCompleted(task.id)}
              onComplete={handleCompleteTask} 
            />
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className={styles.container}>
      <div className={styles.headerCard}>
        <div className={styles.profileSection}>
          <div className={styles.avatar}>
            <Icon icon={rewardsIcons.account} />
          </div>
          <div>
            <h2 className={styles.userName}>{user.first_name} {user.last_name}</h2>
            <div className={styles.tierBadge} style={{ color: tier.color, borderColor: tier.color }}>
              <Icon icon={rewardsIcons.shieldStar} /> {tier.name} Member
            </div>
          </div>
        </div>
        
        <div className={styles.pointsDisplay}>
          <div className={styles.pointsLabel}>Available Points</div>
          <div className={styles.pointsValue}>
            <Icon icon={rewardsIcons.starFourPoints} className={styles.pointsIcon} />
            {points.toLocaleString()}
          </div>
        </div>
      </div>

      <div className={styles.progressSection}>
        <h3 className={styles.sectionTitle}><Icon icon={rewardsIcons.trendingUp} /> Your Progress</h3>
        <div className={styles.streakCard}>
          <div className={styles.streakHeader}>
            <div className={styles.streakInfo}>
              <Icon icon={rewardsIcons.fire} className={styles.fireIcon} />
              <div>
                <h4>Daily Streak</h4>
                <p>{streak} Day{streak > 1 ? 's' : ''}</p>
              </div>
            </div>
            <div className={styles.streakBonus}>
              <span>Stamp bonus</span>
              <span className={styles.bonusPoints}>+150 pts</span>
            </div>
          </div>
          <div className={styles.stamps}>
            {[1,2,3,4,5,6,7].map(day => (
              <div key={day} className={`${styles.stamp} ${day <= streak ? styles.stampActive : ''}`}>
                {day === 7 ? <Icon icon={rewardsIcons.gift} /> : <Icon icon={rewardsIcons.star} />}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className={styles.tasksContainer}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.25rem' }}>Tasks</h2>
          <button 
            onClick={() => setIsModalOpen(true)}
            style={{ padding: '0.5rem 1rem', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.9rem', fontWeight: '500' }}
          >
            View All Tasks
          </button>
        </div>
        {renderSection("Daily Tasks", rewardsIcons.calendarToday, "daily")}
        {renderSection("Weekly Challenges", rewardsIcons.calendarWeek, "weekly")}
        {renderSection("Monthly Goals", rewardsIcons.calendarMonth, "monthly")}
        {renderSection("One-Time Achievements", rewardsIcons.trophyAward, "one_time")}
      </div>
      
      <ViewAllTasksModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        tasks={tasks}
        completions={completions}
        onCompleteTask={handleCompleteTask}
      />
    </div>
  );
};
