import { useState, useEffect } from 'react';
import { adminApi } from '../../../../../api/admin.api';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../../icons/registry';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';
import modalStyles from './UniversityModal.module.css';
import { Input } from '../../../ui/Input/Input';
import { Button } from '../../../ui/Button/Button';

export const UniversityModal = ({ onClose, onSave, university = null }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    allowed_domains: '',
    is_active: true
  });

  useEffect(() => {
    if (university) {
      setFormData({
        name: university.name || '',
        domain: university.domain || '',
        allowed_domains: Array.isArray(university.allowed_domains) 
          ? university.allowed_domains.map(d => d.domain).join(', ') 
          : '',
        is_active: university.is_active ?? true
      });
    }
  }, [university]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Parse allowed_domains into array of objects matching DB structure
      const payload = { ...formData };
      payload.allowed_domains = payload.allowed_domains
        .split(',')
        .map(d => d.trim())
        .filter(d => d.length > 0)
        .map(domain => ({ domain }));

      if (university) {
        await adminApi.updatePlatformSettings(university.id, payload);
      } else {
        await adminApi.createUniversity(payload);
      }
      onSave();
    } catch (err) {
      console.error("Failed to save university", err);
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
            <h3>{university ? 'Edit University' : 'Add New University'}</h3>
            <button className={modalStyles.closeBtn} onClick={onClose}>
              <Icon icon={uiIcons.close} width="24" />
            </button>
          </div>

          <div className={modalStyles.body}>
            <form onSubmit={handleSubmit} className={modalStyles.form}>
              <div className={modalStyles.field}>
                <label>University Name <span className={modalStyles.required}>*</span></label>
                <Input 
                  type="text" 
                  name="name" 
                  value={formData.name} 
                  onChange={handleChange} 
                  required 
                  placeholder="e.g. State University"
                />
              </div>
              
              <div className={modalStyles.field}>
                <label>Primary Domain <span className={modalStyles.required}>*</span></label>
                <Input 
                  type="text" 
                  name="domain" 
                  value={formData.domain} 
                  onChange={handleChange} 
                  required 
                  placeholder="e.g. state.edu"
                />
              </div>

              <div className={modalStyles.field}>
                <label>Allowed Email Domains (Comma separated)</label>
                <Input 
                  type="text" 
                  name="allowed_domains" 
                  value={formData.allowed_domains} 
                  onChange={handleChange} 
                  placeholder="e.g. student.state.edu, faculty.state.edu"
                />
              </div>

              <div className={modalStyles.footer}>
                <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" disabled={loading}>
                  {loading ? <Icon icon={uiIcons.loading} className="spin" /> : (university ? 'Save Changes' : 'Add University')}
                </Button>
              </div>
            </form>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );

  return typeof document !== 'undefined' ? createPortal(modalContent, document.body) : null;
};
