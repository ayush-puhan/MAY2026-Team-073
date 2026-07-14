import React from 'react';
import { motion } from 'framer-motion';
import { Icon } from '@iconify/react';
import styles from '../ProfileSettingsModal.module.css';

export const PreferencesTab = ({
  formData,
  handleChange,
  showInterests,
  showInterestSearch,
  handleOpenInterestSearch,
  selectedInterestId,
  setSelectedInterestId,
  masterData,
  handleAddInterest,
  setShowInterestSearch,
  handleRemoveInterest
}) => {
  return (
    <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className={styles.tabPane}>
      {showInterests ? (
        <div className={styles.interestsSection} style={{ marginTop: 0, marginBottom: '1.5rem' }}>
          <div className={styles.interestsHeader}>
            <label>Interests & Hobbies <span className={styles.required}>*</span></label>
            {!showInterestSearch && (
              <button 
                type="button" 
                className={`${styles.addInterestBtn} ${formData.interests.length >= 6 ? styles.addInterestBtnDisabled : ''}`} 
                onClick={handleOpenInterestSearch}
              >
                <Icon icon="mdi:plus" /> Add Interest
              </button>
            )}
          </div>
          {showInterestSearch && (
            <div className={styles.interestSelectWrapper}>
              <select value={selectedInterestId} onChange={e => setSelectedInterestId(e.target.value)} className={`${styles.input} ${styles.interestSelect}`}>
                <option value="">Select an interest...</option>
                {masterData.interests
                  .filter(i => !formData.interests.some(fid => String(fid) === String(i.id)))
                  .map(i => <option key={i.id} value={i.id}>{i.name}</option>)
                }
              </select>
              <button type="button" className={styles.addBtn} onClick={handleAddInterest}>Add</button>
              <button type="button" className={styles.removeBtn} onClick={() => setShowInterestSearch(false)}>Cancel</button>
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
          <label>Accessibility Options</label>
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
      </div>
    </motion.div>
  );
};
