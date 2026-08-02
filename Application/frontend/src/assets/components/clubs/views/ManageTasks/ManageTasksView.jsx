import React, { useState, useEffect } from 'react';
import { useOutletContext, Navigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/backendApis/clubsApis/clubs';
import { canAssignTaskTo, getRoleLabel, canManageTasks } from '../../../../../utils/clubPermissions';
import styles from './ManageTasksView.module.css';
import { Button } from '../../../ui/Button/Button';
import { EmptyState } from '../../../ui/EmptyState/EmptyState';
import { Input } from '../../../ui/Input/Input';
import { StatusBadge } from '../../../ui/StatusBadge/StatusBadge';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import { DataTable } from '../../../ui/DataTable/DataTable';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import { uiIcons } from '../../../../icons/registry';

const ManageTasksView = () => {
  const { club, userRole, currentUserId } = useOutletContext();
  const [tasks, setTasks] = useState([]);
  const [events, setEvents] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  if (!canManageTasks(userRole) && userRole !== 'system_admin') {
    return <Navigate to={`/clubs/${club?.id || ''}`} replace />;
  }

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [editingTaskId, setEditingTaskId] = useState(null);
  const [newEventId, setNewEventId] = useState('');
  const [newAssigneeId, setNewAssigneeId] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newDueAt, setNewDueAt] = useState('');

  const openForm = (task = null) => {
    if (task) {
      setEditingTaskId(task.id);
      setNewEventId(task.event_id || '');
      setNewAssigneeId(task.assignee_membership_id || '');
      setNewDescription(task.task_description || '');
      // Format to YYYY-MM-DD
      const dateStr = task.due_at ? new Date(task.due_at).toISOString().split('T')[0] : '';
      setNewDueAt(dateStr);
    } else {
      setEditingTaskId(null);
      setNewEventId('');
      setNewAssigneeId('');
      setNewDescription('');
      setNewDueAt('');
    }
    setShowForm(true);
  };

  useEffect(() => {
    fetchData();
  }, [club.id]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [fetchedTasks, fetchedEvents, fetchedMembers] = await Promise.all([
        clubsApi.getClubTasks(club.id),
        clubsApi.getClubEvents(club.id),
        clubsApi.getClubMembers(club.id)
      ]);
      setTasks(fetchedTasks);
      setEvents(fetchedEvents.filter(e => e.status === 'scheduled' || e.status === 'ongoing'));
      setMembers(fetchedMembers);
    } catch (err) {
      console.error(err);
      setError('Failed to load tasks data.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!newEventId || !newAssigneeId || !newDescription || !newDueAt) {
      alert("Please fill all fields");
      return;
    }
    
    try {
      if (editingTaskId) {
        await clubsApi.updateTask(editingTaskId, {
          event_id: newEventId,
          assignee_membership_id: newAssigneeId,
          task_description: newDescription,
          due_at: newDueAt
        }, currentUserId);
      } else {
        await clubsApi.createTask(newEventId, newAssigneeId, currentUserId, newDescription, newDueAt);
      }
      setShowForm(false);
      setEditingTaskId(null);
      setNewEventId('');
      setNewAssigneeId('');
      setNewDescription('');
      setNewDueAt('');
      fetchData();
    } catch (err) {
      alert('Failed to save task');
    }
  };

  const handleUpdateTaskStatus = async (taskId, newStatus) => {
    try {
      await clubsApi.updateTaskStatus(taskId, newStatus, currentUserId);
      fetchData();
    } catch (err) {
      alert('Failed to update task status');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;
    try {
      await clubsApi.deleteTask(taskId);
      fetchData();
    } catch (err) {
      alert('Failed to delete task');
    }
  };

  // Filter members that the current user is allowed to assign tasks to
  const assignableMembers = members.filter(m => canAssignTaskTo(userRole, m.role_in_club));

  if (loading) return <div className={styles.loading}>Loading tasks...</div>;
  if (error) return <div className={styles.error}>{error}</div>;

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent}>
        <div className={styles.container}>
          <header className={styles.header}>
        <div>
          <h2>Manage Tasks</h2>
          <p>Delegate responsibilities and track progress</p>
        </div>
        <Button icon={showForm ? "mdi:close" : "mdi:plus"} onClick={() => showForm ? setShowForm(false) : openForm()}>
          {showForm ? 'Cancel' : 'Assign Task'}
        </Button>
      </header>

      {showForm && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <form className={styles.createForm} onSubmit={handleCreateTask}>
              <h3>{editingTaskId ? 'Edit Task' : 'Assign New Task'}</h3>
              <div className={styles.formGrid}>
                <div className={styles.formGroup}>
                  <Dropdown
                    label="Event"
                    value={newEventId} 
                    onChange={val => setNewEventId(val)}
                    options={[
                      { value: "", label: "Select Event..." },
                      ...events.map(e => ({ value: e.id, label: e.title }))
                    ]}
                  />
                </div>
                <div className={styles.formGroup}>
                  <Dropdown
                    label="Assignee"
                    value={newAssigneeId} 
                    onChange={val => setNewAssigneeId(val)}
                    options={[
                      { value: "", label: "Select Member..." },
                      ...assignableMembers.filter(m => m.id != null).map(m => ({
                        value: m.id,
                        label: `${m.user.full_name} (${getRoleLabel(m.role_in_club)})`
                      }))
                    ]}
                  />
                  {assignableMembers.length === 0 && (
                    <small className={styles.helpText}>No members available to assign tasks to (you can only assign to lower roles).</small>
                  )}
                </div>
                <Input
                  label="Due Date"
                  type="date" 
                  value={newDueAt} 
                  onChange={e => setNewDueAt(e.target.value)} 
                  required 
                />
                <div className={styles.formGroup} style={{ gridColumn: '1 / -1' }}>
                  <Input
                    label="Task Description"
                    as="textarea"
                    value={newDescription} 
                    onChange={e => setNewDescription(e.target.value)} 
                    rows="3" 
                    required
                    placeholder="Describe the responsibilities clearly..."
                  />
                </div>
              </div>
              <div className={styles.formActions}>
                <Button variant="outline" onClick={() => setShowForm(false)} type="button">
                  Cancel
                </Button>
                <Button type="submit" variant="primary" disabled={assignableMembers.length === 0 || !newEventId || !newAssigneeId || !newDescription || !newDueAt}>
                  {editingTaskId ? 'Save Changes' : 'Create & Assign'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {tasks.length === 0 ? (
        <EmptyState 
          icon={uiIcons.clipboardTextOutline} 
          title="No tasks assigned" 
          description="No tasks have been assigned yet." 
        />
      ) : (
        <div className={styles.tableContainer}>
          <DataTable
            columns={[
              {
                header: 'Description',
                cell: (row) => <div className={styles.descCol}>{row.task_description}</div>
              },
              {
                header: 'Event',
                cell: (row) => row.event?.title
              },
              {
                header: 'Assignee',
                cell: (row) => (
                  <div className={styles.assigneeInfo}>
                    <span className={styles.assigneeName}>{row.assignee?.full_name}</span>
                  </div>
                )
              },
              {
                header: 'Status',
                cell: (row) => <StatusBadge status={row.status.replace('_', ' ')} />
              },
              {
                header: 'Due Date',
                cell: (row) => new Date(row.due_at).toLocaleDateString()
              },
              {
                header: 'Actions',
                cell: (row) => {
                  const isAssigner = String(row.assigned_by) === String(currentUserId);
                  if (row.status === 'pending_review' && isAssigner) {
                    return (
                      <div className={styles.actionButtons}>
                        <button 
                          className={`${styles.iconBtn} ${styles.successBtn}`}
                          title="Approve"
                          onClick={() => handleUpdateTaskStatus(row.id, 'completed')}
                        >
                          <Icon icon={uiIcons.checkCircle} />
                        </button>
                        <button 
                          className={`${styles.iconBtn} ${styles.dangerBtn}`}
                          title="Reject"
                          onClick={() => handleUpdateTaskStatus(row.id, 'in_progress')}
                        >
                          <Icon icon={uiIcons.closeCircle} />
                        </button>
                      </div>
                    );
                  } else if (isAssigner && row.status !== 'completed' && row.status !== 'missed') {
                    return (
                      <div className={styles.actionButtons}>
                        <button 
                          className={`${styles.iconBtn}`}
                          title="Edit Task"
                          onClick={() => openForm(row)}
                        >
                          <Icon icon="mdi:pencil" />
                        </button>
                        <button 
                          className={`${styles.iconBtn} ${styles.dangerBtn}`}
                          title="Delete Task"
                          onClick={() => handleDeleteTask(row.id)}
                        >
                          <Icon icon={uiIcons.deleteOutline} />
                        </button>
                      </div>
                    );
                  }
                  return null;
                }
              }
            ]}
            data={tasks}
          />
        </div>
      )}
        </div>
      </div>
    </div>
  );
};

export default ManageTasksView;
