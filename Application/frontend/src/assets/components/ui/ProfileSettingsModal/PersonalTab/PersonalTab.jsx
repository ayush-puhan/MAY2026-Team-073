import React from 'react';
import { motion } from 'framer-motion';
import { Icon } from '@iconify/react';
import { useToast } from '../../../../../context/ToastContext';
import { Button } from '../../Button/Button';
import { Dropdown } from '../../Dropdown/Dropdown';
import { Input } from '../../Input/Input';
import styles from '../ProfileSettingsModal.module.css';

export const PersonalTab = ({ 
  formData, 
  errors, 
  handleChange, 
  setFormData, 
  user
}) => {
  const { showError } = useToast();

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      showError("Image size must be under 2MB");
      return;
    }
    const reader = new FileReader();
    reader.onloadend = () => {
      setFormData((prev) => ({ ...prev, profile_photo_url: reader.result }));
    };
    reader.readAsDataURL(file);
  };

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
            <Button variant="outline" type="button" className={styles.removeBtn} onClick={() => setFormData(prev => ({ ...prev, profile_photo_url: '' }))}>Remove</Button>
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
          <Input 
            name="full_name" 
            value={formData.full_name || ''} 
            onChange={handleChange} 
            error={errors.full_name} 
          />
        </div>
        <div className={styles.field}>
          <label>Phone Number <span className={styles.required}>*</span></label>
          <Input 
            type="tel" 
            name="phone" 
            value={formData.phone || ''} 
            onChange={handleChange} 
            placeholder="+91 98765 43210" 
            error={errors.phone} 
          />
        </div>
      </div>

      <div className={styles.row}>
        <div className={styles.field}>
          <label>Gender</label>
          <Dropdown 
            name="gender" 
            value={formData.gender || ''} 
            onChange={handleChange} 
            placeholder="Select Gender"
            options={[
              { value: 'male', label: 'Male' },
              { value: 'female', label: 'Female' },
              { value: 'other', label: 'Other' },
              { value: 'prefer_not_to_say', label: 'Prefer not to say' }
            ]}
          />
        </div>
        <div className={styles.field}>
          <label>Date of Birth</label>
          <Input 
            type="date" 
            name="dob" 
            value={formData.dob || ''} 
            onChange={handleChange} 
            error={errors.dob} 
          />
        </div>
      </div>
    </motion.div>
  );
};
