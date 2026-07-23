import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import { authApi } from '@api/authApis/auth';
import { notificationApi } from '../../../../api';
import { validateDOB } from '../../../../api/validation';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { uiIcons } from '../../../icons/registry';
import { Button } from '../Button/Button';
import { PersonalTab } from './PersonalTab/PersonalTab';
import { AcademicTab } from './AcademicTab/AcademicTab';
import { PreferencesTab } from './PreferencesTab/PreferencesTab';
import { SecurityTab } from './SecurityTab/SecurityTab';
import { checkIsVerified } from '../../../../utils/verification';
import { ErrorBoundary } from '../ErrorBoundary/ErrorBoundary';
import styles from './ProfileSettingsModal.module.css';

export const ProfileSettingsModal = ({ isOpen, onClose, user }) => {
  const { updateUser } = useSession();
  const { showSuccess, showError } = useToast();
  
  const [formData, setFormData] = useState({
    full_name: user?.full_name || user?.name || '',
    phone: user?.phone || '',
    dob: user?.dob || '',
    gender: user?.gender || '',
    roll_number: user?.roll_number || '',
    profile_photo_url: user?.profile_photo_url || user?.avatar || '',
    color_blind_mode: Boolean(user?.color_blind_mode),
    browse_public_only: Boolean(user?.browse_public_only),
    department_id: user?.department_id || '',
    interests: user?.interests || [],
    student_profile: {
      program_id: user?.student_profile?.program_id || '',
      academic_year: user?.student_profile?.academic_year || '',
      semester: user?.student_profile?.semester || '',
      batch: user?.student_profile?.batch || '',
      section: user?.student_profile?.section || '',
      institutional_email: user?.student_profile?.institutional_email || '',
      is_verified: user?.student_profile?.is_verified || false
    }
  });

  const [activeTab, setActiveTab] = useState('profile');
  const [isSaving, setIsSaving] = useState(false);
  const [errors, setErrors] = useState({});
  const [fullUser, setFullUser] = useState(null);
  
  const [masterData, setMasterData] = useState({
    departments: [], programs: [], interests: []
  });

  useEffect(() => {
    if (isOpen && user?.id) {
      Promise.all([
        authApi.getDepartments(),
        authApi.getPrograms(),
        authApi.getInterests(),
        authApi.getFullProfile(user.id)
      ]).then(([deps, progs, ints, latestUser]) => {
        setMasterData({
          departments: deps || [],
          programs: progs || [],
          interests: ints || []
        });
        
        setFullUser(latestUser);
        
        let accPrefs = {};
        try {
          if (latestUser.accessibility_prefs) {
            accPrefs = typeof latestUser.accessibility_prefs === 'string' 
              ? JSON.parse(latestUser.accessibility_prefs) 
              : latestUser.accessibility_prefs;
          }
        } catch(e) { console.error('Failed to parse accessibility_prefs', e); }

        setFormData(prev => ({
          ...prev,
          full_name: latestUser.full_name || latestUser.name || '',
          phone: latestUser.phone || '',
          dob: latestUser.dob || '',
          gender: latestUser.gender || '',
          roll_number: latestUser.roll_number || '',
          profile_photo_url: latestUser.profile_photo_url || latestUser.avatar || '',
          color_blind_mode: Boolean(latestUser.color_blind_mode),
          browse_public_only: Boolean(accPrefs.browse_public_only),
          email_notifications: accPrefs.email_notifications ?? true,
          department_id: latestUser.department_id || '',
          interests: latestUser.interests || [],
          student_profile: {
            program_id: latestUser.student_profile?.program_id || '',
            academic_year: latestUser.student_profile?.academic_year || '',
            semester: latestUser.student_profile?.semester || '',
            batch: latestUser.student_profile?.batch || '',
            section: latestUser.student_profile?.section || '',
            institutional_email: latestUser.student_profile?.institutional_email || '',
            is_verified: latestUser.student_profile?.is_verified || false
          }
        }));
      }).catch(err => {
        showError("Failed to load some profile data");
      });
    }
  }, [isOpen, user?.id]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => { document.body.style.overflow = 'unset'; };
  }, [isOpen]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name.startsWith('student_profile.')) {
      const field = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        student_profile: {
          ...prev.student_profile,
          [field]: value
        }
      }));
      if (errors[field]) setErrors(prev => ({ ...prev, [field]: null }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      }));
      if (errors[name]) setErrors(prev => ({ ...prev, [name]: null }));
    }
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
        
        let oldAccPrefs = {};
        try {
          if (user.accessibility_prefs) {
            oldAccPrefs = typeof user.accessibility_prefs === 'string'
              ? JSON.parse(user.accessibility_prefs)
              : user.accessibility_prefs;
          }
        } catch(e) {}
        const oldEmailNotifications = oldAccPrefs.email_notifications ?? true;
        const newEmailNotifications = payload.email_notifications;

        // Pack UI preferences into accessibility_prefs to align with auth.py schema
        payload.accessibility_prefs = JSON.stringify({
          browse_public_only: payload.browse_public_only,
          email_notifications: newEmailNotifications
        });
        delete payload.browse_public_only;
        delete payload.email_notifications;

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
        
        // Ensure frontend state has browse_public_only flatly available for other UI components if needed
        let accPrefs = {};
        try {
          if (updatedUser.accessibility_prefs) {
            accPrefs = typeof updatedUser.accessibility_prefs === 'string'
              ? JSON.parse(updatedUser.accessibility_prefs)
              : updatedUser.accessibility_prefs;
          }
        } catch(e) {}
        updatedUser.browse_public_only = Boolean(accPrefs.browse_public_only);
        updatedUser.email_notifications = accPrefs.email_notifications ?? true;

        localStorage.setItem('user', JSON.stringify(updatedUser));
        updateUser(updatedUser);
        
        if (oldEmailNotifications !== newEmailNotifications) {
          // Fire the backend email API to inform the user of the preference change
          try {
            if (newEmailNotifications) {
              await notificationApi.sendEmail(user.id, 'MEMBERSHIP_UPDATE', {
                subject: 'Email Notifications Activated',
                body: 'You have enabled email notifications on ClubConnect. You will now receive email alerts for event registrations, club updates, and more.',
                email: updatedUser.email
              });
            } else {
              await notificationApi.sendEmail(user.id, 'MEMBERSHIP_UPDATE', {
                subject: 'Email Notifications Deactivated',
                body: 'You have disabled email notifications on ClubConnect. You will no longer receive email alerts.',
                email: updatedUser.email
              });
            }
          } catch (emailErr) {
            console.error('Failed to send email preference notification', emailErr);
          }

          if (newEmailNotifications) {
            showSuccess("Profile updated! You will now receive email alerts.");
          } else {
            showSuccess("Profile updated! You won't receive email alerts anymore.");
          }
        } else {
          showSuccess("Profile updated successfully!");
        }
        
        onClose();
      } catch (err) {
        showError("Failed to update profile");
      } finally {
        setIsSaving(false);
      }
    }
  };

  const getRoleConfig = (role) => {
    const isStudentRole = role?.toLowerCase() === 'student';
    return { 
      isStudent: isStudentRole, 
      showDepartment: isStudentRole, 
      showPreferences: true, 
      showInterests: isStudentRole, 
      isAdminOrFaculty: !isStudentRole 
    };
  };

  const { isStudent, showDepartment, showPreferences, showInterests, isAdminOrFaculty } = getRoleConfig(user?.role);
  const resolvedUser = fullUser || user;
  const isVerified = checkIsVerified(resolvedUser);

  const modalContent = (
    <ErrorBoundary onClose={onClose}>
      <div>
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
                    <Icon icon={uiIcons.close} />
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
                  <AnimatePresence mode="wait">
                    {activeTab === 'profile' && (
                      <PersonalTab
                        formData={formData}
                        handleChange={handleChange}
                        setFormData={setFormData}
                        user={resolvedUser}
                        errors={errors}
                        key="profile"
                        isStudent={isStudent}
                        isAdminOrFaculty={isAdminOrFaculty}
                      />
                    )}
                    {showDepartment && activeTab === 'academic' && (
                      <AcademicTab
                        formData={formData}
                        handleChange={handleChange}
                        masterData={masterData}
                        isStudent={isStudent}
                        showDepartment={showDepartment}
                        errors={errors}
                        key="academic"
                      />
                    )}
                    {showPreferences && activeTab === 'preferences' && (
                      <PreferencesTab
                        formData={formData}
                        handleChange={handleChange}
                        setFormData={setFormData}
                        showInterests={showInterests}
                        masterData={masterData}
                        isVerified={isVerified}
                        key="preferences"
                        isAdminOrFaculty={isAdminOrFaculty}
                      />
                    )}
                    {activeTab === 'security' && (
                      <SecurityTab
                        fullUser={resolvedUser}
                        formData={formData}
                        handleChange={handleChange}
                        key="security"
                        isAdminOrFaculty={isAdminOrFaculty}
                      />
                    )}
                  </AnimatePresence>
                </div>
              
                <div className={styles.footer}>
                  <Button variant="outline" className={styles.cancelBtn} onClick={onClose} disabled={isSaving}>Cancel</Button>
                  <Button className={styles.saveBtn} onClick={handleSave} disabled={isSaving} isLoading={isSaving}>
                    Save Changes
                  </Button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </ErrorBoundary>
  );

  return typeof document !== 'undefined' ? createPortal(modalContent, document.body) : null;
};
