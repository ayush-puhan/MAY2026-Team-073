import React from 'react';
import { motion } from 'framer-motion';
import { Icon } from '@iconify/react';
import styles from '../ProfileSettingsModal.module.css';

export const PersonalTab = ({ 
  formData, 
  errors, 
  handleChange, 
  handleImageUpload, 
  setFormData, 
  user
}) => {
  return (
    <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className={styles.tabPane}>
      <div className={styles.avatarSection}>
        <div className={styles.avatarPreview}>
          {formData.profile_photo_url ? (
            <img src={formData.profile_photo_url} alt="Avatar Preview" className={styles.avatarImg} />
          ) : (
            <Icon icon="mdi:account" className={styles.avatarIcon} />
          )}
        </div>
        <div className={styles.avatarInfo}>
          <label>Profile Photo</label>
          <div className={styles.uploadWrapper}>
            <input type="file" accept="image/png, image/jpeg" onChange={handleImageUpload} className={styles.fileInput} id="avatar-upload" />
            <label htmlFor="avatar-upload" className={styles.uploadBtn}>
              <Icon icon="mdi:cloud-upload" /> Upload Image
            </label>
            <button type="button" className={styles.removeBtn} onClick={() => setFormData(prev => ({ ...prev, profile_photo_url: '' }))}>Remove</button>
          </div>
          <p className={styles.hint}>JPG or PNG. Max size 2MB.</p>
        </div>
      </div>

      <div className={styles.row}>
        <div className={styles.field}>
          <label>
            Full Name <span className={styles.required}>*</span>
            {user?.role && <span className={styles.roleBadge}>{user.role.replace(/_/g, ' ').toUpperCase()}</span>}
          </label>
          <input type="text" name="full_name" value={formData.full_name} onChange={handleChange} className={`${styles.input} ${errors.full_name ? styles.inputError : ''}`} />
          {errors.full_name && <span className={styles.errorText}>{errors.full_name}</span>}
        </div>
        <div className={styles.field}>
          <label>Phone Number <span className={styles.required}>*</span></label>
          <input type="tel" name="phone" value={formData.phone || ''} onChange={handleChange} placeholder="+91 98765 43210" className={`${styles.input} ${errors.phone ? styles.inputError : ''}`} />
          {errors.phone && <span className={styles.errorText}>{errors.phone}</span>}
        </div>
      </div>

      <div className={styles.row}>
        <div className={styles.field}>
          <label>Gender</label>
          <select name="gender" value={formData.gender || ''} onChange={handleChange} className={styles.input}>
            <option value="">Select Gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
            <option value="prefer_not_to_say">Prefer not to say</option>
          </select>
        </div>
        <div className={styles.field}>
          <label>Date of Birth</label>
          <input type="date" name="dob" value={formData.dob || ''} onChange={handleChange} className={`${styles.input} ${errors.dob ? styles.inputError : ''}`} />
          {errors.dob && <span className={styles.errorText}>{errors.dob}</span>}
        </div>
      </div>
    </motion.div>
  );
};
