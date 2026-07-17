import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Icon } from '@iconify/react';
import { useToast } from '../../../../../context/ToastContext';
import { Button } from '../../Button/Button';
import { Dropdown } from '../../Dropdown/Dropdown';
import styles from '../ProfileSettingsModal.module.css';

export const PreferencesTab = ({
  formData,
  setFormData,
  handleChange,
  showInterests,
  masterData,
  isVerified,
  isAdminOrFaculty
}) => {
  const { showError } = useToast();
  const [showInterestSearch, setShowInterestSearch] = useState(false);
  const [selectedInterestId, setSelectedInterestId] = useState('');

  const handleOpenInterestSearch = () => {
    if (formData.interests.length >= 6) {
      showError("Only 6 interests allowed");
      return;
    }
    setShowInterestSearch(true);
  };

  const handleAddInterest = () => {
    if (formData.interests.length >= 6) {
      showError("Only 6 interests allowed");
      return;
    }
    if (!selectedInterestId) return;
    const id = String(selectedInterestId);
    if (!formData.interests.some(fid => String(fid) === id)) {
      setFormData(prev => ({ ...prev, interests: [...prev.interests, id] }));
    }
    setSelectedInterestId('');
    setShowInterestSearch(false);
  };

  const handleRemoveInterest = (id) => {
    const strId = String(id);
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.filter(intId => String(intId) !== strId)
    }));
  };

  return (
    <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className={styles.tabPane}>
      {showInterests ? (
        <div className={styles.interestsSection} style={{ marginTop: 0, marginBottom: '1.5rem' }}>
          <div className={styles.interestsHeader}>
            <label>Interests & Hobbies <span className={styles.required}>*</span></label>
            {!showInterestSearch && (
              <Button 
                variant="outline"
                size="sm"
                className={`${styles.addInterestBtn} ${formData.interests.length >= 6 ? styles.addInterestBtnDisabled : ''}`} 
                onClick={handleOpenInterestSearch}
                icon="mdi:plus"
              >
                Add Interest
              </Button>
            )}
          </div>
          {showInterestSearch && (
            <div className={styles.interestSelectWrapper}>
              <Dropdown 
                name="interest"
                value={selectedInterestId} 
                onChange={e => setSelectedInterestId(e.target.value)}
                placeholder="Select an interest..."
                options={masterData.interests
                  .filter(i => !formData.interests.some(fid => String(fid) === String(i.id)))
                  .map(i => ({ value: i.id, label: i.name }))
                }
              />
              <Button onClick={handleAddInterest}>Add</Button>
              <Button variant="outline" onClick={() => setShowInterestSearch(false)}>Cancel</Button>
            </div>
          )}
          <div className={styles.chipsContainer}>
            {formData.interests.map(id => {
              const interest = masterData.interests.find(i => String(i.id) === String(id));
              return interest ? (
               <div key={id} className={styles.chip}>
                  {interest.name}
                  <button type="button" className={styles.removeChipBtn} onClick={() => handleRemoveInterest(id)}>
                    <Icon icon="mdi:close-circle" />
                  </button>
                </div>
              ) : null;
            })}
          </div>
        </div>
      ) : null}

      <div className={styles.accessibilitySection} style={{ marginTop: showInterests ? '2rem' : '0' }}>
        <div className={styles.interestsHeader}>
          <label>Notification & Preferences</label>
        </div>
        
        <div className={styles.toggleField}>
          <div className={styles.toggleLabel}>
            <Icon icon="mdi:eye-outline" className={styles.toggleIcon} />
            <div>
              <strong>Color Blind Mode</strong>
              <p className={styles.hint}>Enhances contrast and changes colors for better visibility.</p>
            </div>
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
            <div className={styles.switch}>
              <input type="checkbox" name="color_blind_mode" checked={Boolean(formData.color_blind_mode)} onChange={handleChange} />
              <span className={styles.slider}></span>
            </div>
            <span style={{ fontSize: '0.9rem', color: 'var(--foreground)' }}>Enable Color-Blind Support</span>
          </label>
        </div>

        <div className={styles.toggleField} style={{ marginTop: '1.5rem' }}>
          <div className={styles.toggleLabel}>
            <Icon icon="mdi:email-outline" className={styles.toggleIcon} />
            <div>
              <strong>Email Notifications</strong>
              <p className={styles.hint}>Receive important updates and reminders via email.</p>
            </div>
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
            <div className={styles.switch}>
              <input type="checkbox" name="email_notifications" checked={Boolean(formData.email_notifications ?? true)} onChange={handleChange} />
              <span className={styles.slider}></span>
            </div>
            <span style={{ fontSize: '0.9rem', color: 'var(--foreground)' }}>Enable Email Alerts</span>
          </label>
        </div>

        {!isAdminOrFaculty && !isVerified && (
          <div className={styles.toggleField} style={{ marginTop: '1.5rem' }}>
            <div className={styles.toggleLabel}>
              <Icon icon="mdi:incognito" className={styles.toggleIcon} />
              <div>
                <strong>Browse Public Events Only</strong>
                <p className={styles.hint}>Disable campus email verification reminders.</p>
              </div>
            </div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
              <div className={styles.switch}>
                <input type="checkbox" name="browse_public_only" checked={Boolean(formData.browse_public_only)} onChange={handleChange} />
                <span className={styles.slider}></span>
              </div>
              <span style={{ fontSize: '0.9rem', color: 'var(--foreground)' }}>Hide verification reminder</span>
            </label>
          </div>
        )}
      </div>


    </motion.div>
  );
};
