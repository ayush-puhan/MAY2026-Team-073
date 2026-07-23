import React, { useState, useEffect } from 'react';
import { useOutletContext, Navigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/mockbackendApis/clubsApis/clubs';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import styles from './ClubSettingsView.module.css';
import { Input } from '../../../ui/Input/Input';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import { Button } from '../../../ui/Button/Button';
import { canViewClubSettings } from '../../../../../utils/clubPermissions';
import { useToast } from '../../../../../context/ToastContext';

const ClubSettingsView = () => {
  const { club, currentUserId, userRole } = useOutletContext();
  const { addToast } = useToast();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: '',
    banner_url: '',
    logo_url: ''
  });
  const [loading, setLoading] = useState(false);

  if (!canViewClubSettings(userRole) && userRole !== 'system_admin') {
    return <Navigate to={`/clubs/${club?.id || ''}`} replace />;
  }

  useEffect(() => {
    if (club) {
      setFormData({
        name: club.name || '',
        description: club.description || '',
        status: club.status || 'active',
        banner_url: club.banner_url || '',
        logo_url: club.logo_url || ''
      });
    }
  }, [club]);

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await clubsApi.updateClubSettings(club.id, formData, currentUserId);
      addToast({ title: 'Success', message: 'Settings updated successfully!', type: 'success' });
      setTimeout(() => window.dispatchEvent(new Event('refreshClubs')), 500);
    } catch (err) {
      addToast({ title: 'Error', message: 'Failed to update settings', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent}>
        <div className={styles.container}>
          <header className={styles.header}>
            <div>
              <h2>Club Settings</h2>
              <p>Update {club.name}'s profile and configuration</p>
            </div>
          </header>

          <form className={styles.settingsForm} onSubmit={handleSubmit}>
            <div className={styles.formSection}>
              <h3>General Information</h3>
              <div className={styles.formGroup}>
                <Input 
                  label="Club Name"
                  name="name" 
                  value={formData.name} 
                  onChange={handleChange} 
                  required 
                />
              </div>
              
              <div className={styles.formGroup} style={{gridColumn: '1 / -1'}}>
                <Input 
                  label="Description"
                  as="textarea"
                  name="description" 
                  value={formData.description} 
                  onChange={handleChange} 
                  rows={5} 
                  required 
                />
              </div>
            </div>

            <div className={styles.formSection}>
              <h3>Media & Branding</h3>
              {formData.banner_url && (
                <div className={styles.bannerPreview} style={{ backgroundImage: `url(${formData.banner_url})` }}></div>
              )}
              <div className={styles.formGrid}>
                <div className={styles.formGroup}>
                  <Input 
                    label="Banner Image URL"
                    name="banner_url"
                    type="url"
                    value={formData.banner_url}
                    onChange={handleChange}
                    placeholder="https://example.com/banner.jpg"
                  />
                </div>
                <div className={styles.formGroup}>
                  <Input 
                    label="Logo URL"
                    name="logo_url"
                    type="url"
                    value={formData.logo_url}
                    onChange={handleChange}
                    placeholder="https://example.com/logo.png"
                  />
                </div>
              </div>
            </div>

            <div className={styles.formSection}>
              <h3>Status</h3>
              <div className={styles.formGroup}>
                <Dropdown 
                  label="Club Status"
                  name="status"
                  value={formData.status}
                  onChange={(val) => setFormData(prev => ({...prev, status: val}))}
                  options={[
                    { value: 'active', label: 'Active' },
                    { value: 'inactive', label: 'Inactive' },
                    { value: 'archived', label: 'Archived' }
                  ]}
                />
                <p className={styles.helpText}>Inactive clubs won't appear in discovery but retain data.</p>
              </div>
            </div>

            <div className={styles.formActions}>
              <Button type="submit" variant="primary" disabled={loading}>
                {loading ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ClubSettingsView;
