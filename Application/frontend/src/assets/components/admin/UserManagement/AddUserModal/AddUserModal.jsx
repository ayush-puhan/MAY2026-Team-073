import { useState, useEffect } from 'react';
import { adminApi } from '@api/adminApis/admin';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../../icons/registry';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';
import { Button } from '../../../ui/Button/Button';
import { USER_ROLES_OPTIONS } from '../../../../../config/enums';
import modalStyles from './AddUserModal.module.css';

export const AddUserModal = ({ onClose, onAdd }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    role: 'student',
    university_id: ''
  });
  const [successData, setSuccessData] = useState(null);
  const [universities, setUniversities] = useState([]);

  useEffect(() => {
    const fetchUnis = async () => {
      try {
        const unis = await adminApi.getUniversities();
        setUniversities(unis);
      } catch (err) {
        console.error("Failed to fetch universities", err);
      }
    };
    fetchUnis();
  }, []);

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const newUser = await adminApi.createUser(formData);
      setSuccessData(newUser);
      onAdd();
    } catch (err) {
      console.error("Failed to create user", err);
    } finally {
      setLoading(false);
    }
  };

  const modalContent = (
    <AnimatePresence>
      <div className={modalStyles.overlay} onClick={onClose}>
        <motion.div 
          className={modalStyles.modal} 
          onClick={e => e.stopPropagation()}
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.2 }}
        >
          <div className={modalStyles.header}>
            <h3>Add New User</h3>
            <button className={modalStyles.closeBtn} onClick={onClose}>
              <Icon icon={uiIcons.close} width="24" />
            </button>
          </div>

          <div className={modalStyles.body}>
            {successData ? (
              <div className={modalStyles.successState}>
                <div className={modalStyles.successIcon}>
                  <Icon icon={uiIcons.checkCircle} width="48" />
                </div>
                <h4>User Created Successfully!</h4>
                <p>The user has been added to the platform.</p>
                
                <div className={modalStyles.credentialsBox}>
                  <div className={modalStyles.credRow}>
                    <span>Email:</span>
                    <strong>{successData.email}</strong>
                  </div>
                  <div className={modalStyles.credRow}>
                    <span>Generated Password:</span>
                    <strong>{successData._tempPassword}</strong>
                  </div>
                  <p className={modalStyles.credHint}>An email has been sent to the user with these credentials.</p>
                </div>
                
                <Button variant="primary" onClick={onClose}>
                  Done
                </Button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className={modalStyles.form}>
                <div className={modalStyles.field}>
                  <label>Full Name <span className={modalStyles.required}>*</span></label>
                  <input 
                    type="text" 
                    name="full_name" 
                    value={formData.full_name} 
                    onChange={handleChange} 
                    required 
                    placeholder="e.g. Jane Doe"
                  />
                </div>
                
                {formData.role === 'student' && (
                  <div className={modalStyles.field}>
                    <label>Campus Email <span className={modalStyles.required}>*</span></label>
                    <input 
                      type="email" 
                      name="email" 
                      value={formData.email} 
                      onChange={handleChange} 
                      required 
                      placeholder="jane.doe@example.edu"
                    />
                  </div>
                )}

                <div className={modalStyles.field}>
                  <label>Role <span className={modalStyles.required}>*</span></label>
                  <Dropdown 
                    name="role" 
                    value={formData.role} 
                    onChange={handleChange}
                    options={USER_ROLES_OPTIONS}
                  />
                </div>

                <div className={modalStyles.field}>
                  <label>University (Auto-assigned by email if blank)</label>
                  <Dropdown 
                    name="university_id" 
                    value={formData.university_id} 
                    onChange={handleChange}
                    options={[{value: '', label: 'Auto-detect from email'}, ...universities.map(u => ({ value: u.id, label: u.name }))]}
                  />
                </div>

                <div className={modalStyles.infoBox}>
                  <Icon icon={uiIcons.informationOutline} width="20" />
                  <p>A secure password will be automatically generated and emailed to the user.</p>
                </div>

                <div className={modalStyles.footer}>
                  <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
                  <Button type="submit" variant="primary" disabled={loading}>
                    {loading ? 'Creating...' : 'Create User'}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );

  return typeof document !== 'undefined' ? createPortal(modalContent, document.body) : null;
};
