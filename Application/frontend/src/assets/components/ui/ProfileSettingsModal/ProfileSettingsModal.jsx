import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import { authApi } from '../../../../api/auth.api';
import { validateDOB } from '../../../../api/validation';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { useNavigate } from 'react-router-dom';
import { ConfirmModal } from '../ConfirmModal/ConfirmModal';
import styles from './ProfileSettingsModal.module.css';

export const ProfileSettingsModal = ({ isOpen, onClose, user }) => {
  const { updateUser, logout } = useSession();
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();
  
  const [formData, setFormData] = useState({
    full_name: user?.full_name || user?.name || '',
    phone: user?.phone || '',
    dob: user?.dob || '',
    profile_photo_url: user?.profile_photo_url || user?.avatar || '',
    accessibility_prefs: user?.accessibility_prefs || '',
    roll_number: user?.roll_number || '',
    gender: user?.gender || '',
    department_id: user?.department_id ? String(user.department_id) : '',
    student_profile: {
      program_id: user?.student_profile?.program_id ? String(user.student_profile.program_id) : '',
      academic_year: user?.student_profile?.academic_year ? String(user.student_profile.academic_year) : '',
      semester: user?.student_profile?.semester ? String(user.student_profile.semester) : '',
      batch: user?.student_profile?.batch || '',
      section: user?.student_profile?.section || ''
    },
    interests: user?.interests || [],
    color_blind_mode: user?.color_blind_mode || false
  });
  
  const [masterData, setMasterData] = useState({
    departments: [],
    programs: [],
    interests: []
  });
  
  const [errors, setErrors] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');
  
  const [showInterestSearch, setShowInterestSearch] = useState(false);
  const [selectedInterestId, setSelectedInterestId] = useState('');
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const [fullUser, setFullUser] = useState(user);

  const handleDeleteAccount = async () => {
    try {
      await authApi.deleteAccount(user.id);
      showSuccess('Account deleted successfully');
      logout();
      navigate('/');
    } catch (err) {
      showError('Failed to delete account');
      console.error(err);
    } finally {
      setIsDeleteModalOpen(false);
    }
  };

  useEffect(() => {
    const fetchMasterData = async () => {
      try {
        const [dept, prog, int] = await Promise.all([
          authApi.getDepartments().catch(err => { console.error("Dept error", err); return []; }),
          authApi.getPrograms().catch(err => { console.error("Prog error", err); return []; }),
          authApi.getInterests().catch(err => { console.error("Int error", err); return []; })
        ]);
        setMasterData({ departments: dept || [], programs: prog || [], interests: int || [] });
      } catch (err) {
        console.error("Failed to load master data", err);
      }
    };
    fetchMasterData();
  }, []);

  useEffect(() => {
    if (user?.id && isOpen) {
      const loadProfile = async () => {
        try {
          const loadedUser = await authApi.getFullProfile(user.id);
          setFullUser(loadedUser);
          setFormData({
            full_name: loadedUser?.full_name || user?.full_name || user?.name || '',
            phone: loadedUser?.phone || user?.phone || '',
            dob: loadedUser?.dob || '',
            profile_photo_url: loadedUser?.profile_photo_url || loadedUser?.avatar || user?.profile_photo_url || user?.avatar || '',
            accessibility_prefs: loadedUser?.accessibility_prefs || '',
            roll_number: loadedUser?.roll_number || user?.roll_number || '',
            gender: loadedUser?.gender || user?.gender || '',
            department_id: loadedUser?.department_id ? String(loadedUser.department_id) : (user?.department_id ? String(user.department_id) : ''),
            student_profile: {
              program_id: loadedUser?.student_profile?.program_id ? String(loadedUser.student_profile.program_id) : '',
              academic_year: loadedUser?.student_profile?.academic_year ? String(loadedUser.student_profile.academic_year) : '',
              semester: loadedUser?.student_profile?.semester ? String(loadedUser.student_profile.semester) : '',
              batch: loadedUser?.student_profile?.batch || '',
              section: loadedUser?.student_profile?.section || ''
            },
            interests: loadedUser?.interests || [],
            color_blind_mode: loadedUser?.color_blind_mode || user?.color_blind_mode || false
          });
          setErrors({});
          setActiveTab('profile');
        } catch(err) {
          showError("Failed to load full profile");
          // Fallback to basic user data if full profile fails to load
          setFormData(prev => ({
            ...prev,
            full_name: user?.full_name || user?.name || '',
            phone: user?.phone || '',
            roll_number: user?.roll_number || '',
            profile_photo_url: user?.profile_photo_url || user?.avatar || ''
          }));
        }
      };
      loadProfile();
    }
  }, [user?.id, isOpen]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (type === 'checkbox') {
      setFormData(prev => ({ ...prev, [name]: checked }));
      return;
    }
    if (['program_id', 'academic_year', 'semester', 'batch', 'section'].includes(name)) {
      setFormData(prev => ({
        ...prev,
        student_profile: { ...prev.student_profile, [name]: value }
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: null }));
  };

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

  const handleOpenInterestSearch = () => {
    if (formData.interests.length >= 6) {
      showError("Only 6 interests allowed");
      return;
    }
    setShowInterestSearch(true);
  };

  const handleRemoveInterest = (id) => {
    const strId = String(id);
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.filter(intId => String(intId) !== strId)
    }));
  };

  const validate = () => {
    const newErrors = {};
    let missingRequired = [];

    if (!formData.full_name?.trim()) {
      newErrors.full_name = "Full name is required";
      missingRequired.push("Full Name");
    }

    if (!formData.phone?.trim()) {
      newErrors.phone = "Phone number is required";
      missingRequired.push("Phone Number");
    } else if (!/^\+?\d{10,15}$/.test(formData.phone.replace(/[\s-]/g, ''))) {
      newErrors.phone = "Invalid phone format";
    }
    
    if (showDepartment && !formData.department_id) {
      newErrors.department_id = "Department is required";
      missingRequired.push("Department");
    }

    if (isStudent) {
      if (!formData.student_profile.program_id) {
        newErrors.program_id = "Program is required";
        missingRequired.push("Program");
      }
      if (!formData.student_profile.academic_year) {
        newErrors.academic_year = "Academic Year is required";
        missingRequired.push("Academic Year");
      }
      if (!formData.student_profile.semester) {
        newErrors.semester = "Semester is required";
        missingRequired.push("Semester");
      }
    }
    
    let hasInterestError = false;
    if (showInterests && formData.interests.length < 2) {
      newErrors.interests = "Please add at least 2 interests";
      hasInterestError = true;
    }

    if (formData.dob) {
      const dobError = validateDOB(formData.dob);
      if (dobError) newErrors.dob = dobError;
    }
    setErrors(newErrors);
    
    return {
      isValid: Object.keys(newErrors).length === 0,
      missingRequired,
      hasInterestError,
      errors: newErrors
    };
  };

  const handleSave = async () => {
    const validation = validate();
    if (!validation.isValid) {
      const { errors } = validation;
      if (errors.full_name || errors.phone || errors.dob) {
        setActiveTab('profile');
      } else if (errors.department_id || errors.program_id || errors.academic_year || errors.semester) {
        setActiveTab('academic');
      } else if (errors.interests) {
        setActiveTab('preferences');
      }

      if (validation.missingRequired.length > 1) {
        showError("Please fill all required fields");
      } else if (validation.missingRequired.length === 1) {
        showError(`${validation.missingRequired[0]} is required`);
      } else if (validation.hasInterestError) {
        showError("Please add at least 2 interests for personal recommendations.");
      } else {
        showError("Please fix the errors in the form before saving.");
      }
      return;
    }
    if (user && user.id) {
      setIsSaving(true);
      try {
        const payload = { ...formData };
        
        // Remove irrelevant fields based on role
        if (!showDepartment) {
          delete payload.department_id;
        } else if (payload.department_id) {
          payload.department_id = parseInt(payload.department_id, 10);
        }
        
        if (!isStudent) {
          delete payload.student_profile;
        } else if (payload.student_profile?.program_id) {
          payload.student_profile.program_id = parseInt(payload.student_profile.program_id, 10);
        }
        
        if (!showInterests) {
          delete payload.interests;
        } else if (payload.interests) {
          payload.interests = payload.interests.map(id => parseInt(id, 10));
        }

        const updated = await authApi.updateProfile(user.id, payload);
        const updatedUser = { ...user, ...updated };
        updatedUser.name = updatedUser.full_name;
        updatedUser.avatar = updatedUser.profile_photo_url;
        localStorage.setItem('user', JSON.stringify(updatedUser));
        updateUser(updatedUser);
        showSuccess("Profile updated successfully!");
        onClose();
      } catch (err) {
        showError("Failed to update profile");
      } finally {
        setIsSaving(false);
      }
    }
  };

  const handleResetPassword = async () => {
    if (!user?.email) return;
    setIsResetting(true);
    try {
      const res = await authApi.forgotPassword(user.email);
      showSuccess(res.message || 'Password reset link sent to your email!');
    } catch (err) {
      showError('Failed to send reset link.');
    } finally {
      setIsResetting(false);
    }
  };

  const getRoleConfig = (role) => {
    switch (role) {
      case 'student':
      case 'applicant':
      case 'member':
        return { isStudent: true, showDepartment: true, showPreferences: true, showInterests: true };
      case 'faculty_advisor':
      case 'faculty':
        return { isStudent: false, showDepartment: true, showPreferences: true, showInterests: false };
      case 'system_admin':
      case 'student_affairs_office':
      case 'dean_student_welfare':
        return { isStudent: false, showDepartment: false, showPreferences: true, showInterests: false };
      default:
        return { isStudent: false, showDepartment: false, showPreferences: true, showInterests: false };
    }
  };

  const { isStudent, showDepartment, showPreferences, showInterests } = getRoleConfig(user?.role);

  const modalContent = (
    <div data-colorblind={user?.color_blind_mode ? "true" : undefined}>
      <AnimatePresence>
        {isOpen && (
          <div className={styles.overlay}>
            <motion.div
              className={styles.backdrop}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onClose}
            />
            <motion.div
              className={styles.modal}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <div className={styles.header}>
                <h3>Profile Settings</h3>
                <button className={styles.closeBtn} onClick={onClose}>
                  <Icon icon="mdi:close" />
                </button>
              </div>

            <div className={styles.tabs}>
              <button className={`${styles.tabBtn} ${activeTab === 'profile' ? styles.activeTab : ''}`} onClick={() => setActiveTab('profile')}>Profile</button>
              {showDepartment && (
                <button className={`${styles.tabBtn} ${activeTab === 'academic' ? styles.activeTab : ''}`} onClick={() => setActiveTab('academic')}>Academic</button>
              )}
              <button className={`${styles.tabBtn} ${activeTab === 'security' ? styles.activeTab : ''}`} onClick={() => setActiveTab('security')}>Security</button>
              {showPreferences && (
                <button className={`${styles.tabBtn} ${activeTab === 'preferences' ? styles.activeTab : ''}`} onClick={() => setActiveTab('preferences')}>Preferences</button>
              )}
            </div>
            
            <div className={styles.content}>
              {activeTab === 'profile' && (
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
                        <option value="MALE">Male</option>
                        <option value="FEMALE">Female</option>
                        <option value="OTHER">Other</option>
                        <option value="PREFER_NOT_TO_SAY">Prefer not to say</option>
                      </select>
                    </div>
                    <div className={styles.field}>
                      <label>Date of Birth</label>
                      <input type="date" name="dob" value={formData.dob || ''} onChange={handleChange} className={`${styles.input} ${errors.dob ? styles.inputError : ''}`} />
                      {errors.dob && <span className={styles.errorText}>{errors.dob}</span>}
                    </div>
                  </div>

                </motion.div>
              )}

              {showDepartment && activeTab === 'academic' && (
                <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className={styles.tabPane}>
                  <div className={styles.row}>
                    <div className={styles.field}>
                      <label>Department <span className={styles.required}>*</span></label>
                      <select name="department_id" value={formData.department_id || ''} onChange={handleChange} className={`${styles.input} ${errors.department_id ? styles.inputError : ''}`}>
                        <option value="">Select Department</option>
                        {masterData.departments.map(d => (
                          <option key={d.id} value={d.id}>{d.name}</option>
                        ))}
                      </select>
                    </div>
                    {isStudent && (
                      <div className={styles.field}>
                        <label>Program <span className={styles.required}>*</span></label>
                        <select name="program_id" value={formData.student_profile.program_id || ''} onChange={handleChange} className={`${styles.input} ${errors.program_id ? styles.inputError : ''}`}>
                          <option value="">Select Program</option>
                          {masterData.programs
                            .filter(p => !formData.department_id || p.department_id === parseInt(formData.department_id))
                            .map(p => (
                            <option key={p.id} value={p.id}>{p.name}</option>
                          ))}
                        </select>
                      </div>
                    )}
                  </div>

                  {isStudent && (
                    <div className={styles.row}>
                      <div className={styles.field}>
                        <label>Academic Year <span className={styles.required}>*</span></label>
                        <select name="academic_year" value={formData.student_profile.academic_year || ''} onChange={handleChange} className={`${styles.input} ${errors.academic_year ? styles.inputError : ''}`}>
                          <option value="">Select Year</option>
                          <option value="1">1st Year</option>
                          <option value="2">2nd Year</option>
                          <option value="3">3rd Year</option>
                          <option value="4">4th Year</option>
                        </select>
                      </div>
                      <div className={styles.field}>
                        <label>Semester <span className={styles.required}>*</span></label>
                        <select name="semester" value={formData.student_profile.semester || ''} onChange={handleChange} className={`${styles.input} ${errors.semester ? styles.inputError : ''}`}>
                          <option value="">Select Semester</option>
                          {[1,2,3,4,5,6,7,8].map(s => <option key={s} value={String(s)}>{s}th Sem</option>)}
                        </select>
                      </div>
                    </div>
                  )}

                  {isStudent && (
                    <div className={styles.row}>
                      <div className={styles.field}>
                        <label>Batch</label>
                        <input type="text" name="batch" value={formData.student_profile.batch || ''} onChange={handleChange} className={styles.input} placeholder="e.g. 2024" />
                      </div>
                      <div className={styles.field}>
                        <label>Section</label>
                        <input type="text" name="section" value={formData.student_profile.section || ''} onChange={handleChange} className={styles.input} placeholder="e.g. A" />
                      </div>
                    </div>
                  )}
                </motion.div>
              )}

              {activeTab === 'security' && (
                <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className={styles.tabPane}>
                  <div className={styles.row}>
                    <div className={styles.field}>
                      <label>Email Address <span className={styles.required}>*</span>
                        {fullUser?.email_verified ? (
                          <span className={styles.verifiedBadge}><Icon icon="mdi:check-decagram" /> Verified</span>
                        ) : (
                          fullUser?.auth_provider === 'LOCAL' && (
                            <button type="button" className={styles.verifyEmailBtn} onClick={() => showSuccess("Verification link sent!")}>Verify Email</button>
                          )
                        )}
                      </label>
                      <input type="email" value={fullUser?.email || ''} disabled className={`${styles.input} ${styles.disabled}`} title="Contact admin to change email" />
                    </div>
                    <div className={styles.field}>
                      <label>University ID</label>
                      <input type="text" name="roll_number" value={formData.roll_number} onChange={handleChange} className={styles.input} placeholder="e.g. UID12345" />
                    </div>
                  </div>

                  <div className={`${styles.row} ${styles.passwordRow}`}>
                    <div className={styles.field}>
                      <label>Password <span className={styles.required}>*</span></label>
                      <input type="password" value="********" disabled className={`${styles.input} ${styles.disabled}`} />
                    </div>
                    <div className={styles.field}>
                      <label>&nbsp;</label>
                      <div className={styles.resetWrapper}>
                        <button type="button" className={styles.resetPwBtn} onClick={handleResetPassword} disabled={isResetting}>
                          {isResetting ? 'Sending link...' : 'Reset Password'}
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className={styles.dangerZone}>
                    <div className={styles.dangerInfo}>
                      <h4>Delete Account</h4>
                      <p>Permanently remove your account and all associated data. This action cannot be undone.</p>
                    </div>
                    <button type="button" className={styles.deleteBtn} onClick={() => setIsDeleteModalOpen(true)}>
                      Delete Account
                    </button>
                  </div>
                </motion.div>
              )}

              {showPreferences && activeTab === 'preferences' && (
                <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className={styles.tabPane}>
                  
                  {showInterests && (
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
                  )}

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
                      <label className={styles.switch}>
                        <input type="checkbox" name="color_blind_mode" checked={formData.color_blind_mode} onChange={handleChange} />
                        <span className={styles.slider}></span>
                      </label>
                    </div>
                  </div>

                </motion.div>
              )}
            </div>

            <div className={styles.footer}>
              <button className={styles.cancelBtn} onClick={onClose} disabled={isSaving}>Cancel</button>
              <button className={styles.saveBtn} onClick={handleSave} disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
    
    <ConfirmModal 
      isOpen={isDeleteModalOpen}
      title="Delete Account"
      message="Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently removed."
      confirmText="Delete"
      cancelText="Cancel"
      type="danger"
      onConfirm={handleDeleteAccount}
      onCancel={() => setIsDeleteModalOpen(false)}
    />
    </div>
  );

  return createPortal(modalContent, document.body);
};
