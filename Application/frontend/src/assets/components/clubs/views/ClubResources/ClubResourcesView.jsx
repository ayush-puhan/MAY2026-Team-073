import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import styles from './ClubResourcesView.module.css';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import { clubsApi } from '../../../../../api/backendApis/clubsApis/clubs';
import { canManageResources } from '../../../../../utils/clubPermissions';
import { useToast } from '../../../../../context/ToastContext';
import { useSession } from '../../../../../context/SessionContext';
import { EmptyState } from '../../../ui/EmptyState/EmptyState';
import { Input } from '../../../ui/Input/Input';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import { Button } from '../../../ui/Button/Button';
import { ConfirmModal } from '../../../ui/ConfirmModal/ConfirmModal';

export const ClubResourcesView = ({ club, userRole }) => {
  const { user } = useSession();
  const { addToast } = useToast();
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [resourceToDelete, setResourceToDelete] = useState(null);
  
  const [formData, setFormData] = useState({
    title: '',
    doc_type: 'general',
    file_url: ''
  });

  const canManage = canManageResources(userRole);

  useEffect(() => {
    fetchResources();
  }, [club.id]);

  const fetchResources = async () => {
    try {
      setLoading(true);
      const res = await clubsApi.getClubResources(club.id);
      setResources(res);
    } catch (err) {
      addToast('Failed to load resources', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (resourceId) => {
    setResourceToDelete(resourceId);
  };

  const confirmDelete = async () => {
    if (!resourceToDelete) return;
    try {
      await clubsApi.deleteClubResource(club.id, resourceToDelete, user.id);
      addToast('Resource deleted successfully', 'success');
      setResources(resources.filter(r => r.id !== resourceToDelete));
    } catch (err) {
      addToast(err.message || 'Failed to delete resource', 'error');
    } finally {
      setResourceToDelete(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title || !formData.file_url) {
      addToast('Please fill out all fields', 'warning');
      return;
    }
    try {
      const newDoc = await clubsApi.addClubResource(club.id, formData, user.id);
      addToast('Resource added successfully', 'success');
      setResources([...resources, newDoc]);
      setIsModalOpen(false);
      setFormData({ title: '', doc_type: 'general', file_url: '' });
    } catch (err) {
      addToast(err.message || 'Failed to add resource', 'error');
    }
  };

  const getDocIcon = (type) => {
    switch (type) {
      case 'meeting_minutes': return 'mdi:file-document-outline';
      case 'presentation': return 'mdi:presentation-play';
      case 'rulebook': return 'mdi:book-open-variant';
      case 'drive_link': return 'mdi:google-drive';
      default: return 'mdi:file-outline';
    }
  };

  const getDocLabel = (type) => {
    switch (type) {
      case 'meeting_minutes': return 'Meeting Minutes';
      case 'presentation': return 'Presentation';
      case 'rulebook': return 'Rulebook';
      case 'drive_link': return 'Drive Link';
      case 'file': return 'File';
      default: return 'Document';
    }
  };

  return (
    <>
      <div className={layoutStyles.workspaceArea}>
        <div className={layoutStyles.workspaceHeader} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 className={styles.headerTitle} style={{ fontSize: '1.5rem', fontWeight: 700, margin: '0 0 0.5rem 0' }}>Club Resources</h1>
            <p className={styles.headerSubtitle} style={{ color: 'var(--muted-foreground)', margin: 0 }}>Important documents, links, and meeting minutes for {club.name}.</p>
          </div>
          {canManage && (
            <Button onClick={() => setIsModalOpen(true)} icon="mdi:plus">
              Add Resource
            </Button>
          )}
        </div>

        <div className={layoutStyles.workspaceContent}>
          {loading ? (
            <div className={styles.loading}>Loading resources...</div>
          ) : resources.length === 0 ? (
            <EmptyState
              icon="mdi:folder-open-outline"
              title="No Resources Found"
              description="There are currently no documents or links shared in this club."
              action={canManage ? { label: 'Add Resource', onClick: () => setIsModalOpen(true) } : null}
            />
          ) : (
            <div className={styles.resourceGrid}>
              {resources.map(resource => (
                <div key={resource.id} className={styles.resourceCard}>
                  <div className={styles.resourceIconWrapper}>
                    <Icon icon={getDocIcon(resource.doc_type)} className={styles.resourceIcon} />
                  </div>
                  <div className={styles.resourceInfo}>
                    <h3 className={styles.resourceTitle}>{resource.title}</h3>
                    <p className={styles.resourceMeta}>
                      <span className={styles.badge}>{getDocLabel(resource.doc_type)}</span>
                      <span className={styles.date}>
                        {new Date(resource.created_at).toLocaleDateString()}
                      </span>
                    </p>
                  </div>
                  <div className={styles.resourceActions}>
                    <a href={resource.file_url} target="_blank" rel="noreferrer" className={styles.actionBtn} title="View Resource">
                      <Icon icon="mdi:open-in-new" />
                    </a>
                    {canManage && (
                      <button type="button" onClick={() => handleDeleteClick(resource.id)} className={`${styles.actionBtn} ${styles.deleteBtn}`} title="Delete Resource">
                        <Icon icon="mdi:trash-can-outline" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {isModalOpen && (
        <div className={styles.modalOverlay} onClick={() => setIsModalOpen(false)}>
          <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>Add New Resource</h2>
              <button className={styles.closeBtn} onClick={() => setIsModalOpen(false)}>
                <Icon icon="mdi:close" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className={styles.form}>
              <div className={styles.formGroup}>
                <Input 
                  label="Title"
                  value={formData.title} 
                  onChange={e => setFormData({...formData, title: e.target.value})} 
                  placeholder="e.g. Fall 2026 Kickoff Slides"
                  required
                />
              </div>
              <div className={styles.formGroup}>
                <Dropdown
                  label="Resource Type"
                  value={formData.doc_type} 
                  onChange={val => setFormData({...formData, doc_type: val})}
                  options={[
                    { value: "general", label: "Document" },
                    { value: "meeting_minutes", label: "Meeting Minutes" },
                    { value: "presentation", label: "Presentation" },
                    { value: "rulebook", label: "Rulebook" },
                    { value: "file", label: "File" },
                    { value: "drive_link", label: "Drive Link" }
                  ]}
                />
              </div>
              <div className={styles.formGroup}>
                <Input 
                  label="URL or Drive Link"
                  type="url" 
                  value={formData.file_url} 
                  onChange={e => setFormData({...formData, file_url: e.target.value})} 
                  placeholder="https://..."
                  required
                />
              </div>
              <div className={styles.formActions}>
                <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                <Button type="submit" variant="primary">Add Resource</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      <ConfirmModal
        isOpen={!!resourceToDelete}
        onClose={() => setResourceToDelete(null)}
        onConfirm={confirmDelete}
        title="Delete Resource"
        message="Are you sure you want to delete this resource? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
      />
    </>
  );
};
