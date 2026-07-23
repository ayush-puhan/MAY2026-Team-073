import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import styles from './ProposeClubModal.module.css';
import { clubsApi, authApi } from '../../../../../api';
import { useSession } from '../../../../../context/SessionContext';
import { useToast } from '../../../../../context/ToastContext';
import { uiIcons } from '../../../../icons/registry';

export const ProposeClubModal = ({ isOpen, onClose }) => {
  const { user } = useSession();
  const { addToast } = useToast();
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    faculty_advisor_id: '',
    interests: []
  });
  const [loading, setLoading] = useState(false);
  const [faculties, setFaculties] = useState([]);
  const [availableInterests, setAvailableInterests] = useState([]);

  useEffect(() => {
    if (isOpen) {
      authApi.getFacultyAdvisors()
        .then(data => setFaculties(data || []))
        .catch(err => console.error("Failed to fetch faculties", err));
      
      const fetchInterests = async () => {
        try {
          const { api } = await import('../../../../../api/api');
          const data = await api.get('/interests');
          setAvailableInterests(data || []);
        } catch (e) {
          console.error('Failed to fetch interests', e);
        }
      };
      fetchInterests();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleInterestToggle = (id) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(id) 
        ? prev.interests.filter(i => i !== id)
        : [...prev.interests, id]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await clubsApi.requestClubCreation(user?.id, {
        ...formData
      });
      addToast({ title: 'Proposal Submitted', message: 'Your club proposal has been sent for faculty review.', type: 'success' });
      onClose();
    } catch (err) {
      addToast({ title: 'Request Failed', message: err.message || 'Failed to submit proposal.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.header}>
          <h2>Propose a New Club</h2>
          <button className={styles.closeBtn} onClick={onClose}>
            <Icon icon={uiIcons.close} />
          </button>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label>Club Name</label>
            <input 
              type="text" 
              name="name" 
              value={formData.name} 
              onChange={handleChange} 
              placeholder="e.g. AI & Robotics Society"
              required 
            />
          </div>

          <div className={styles.formGroup}>
            <label>Category</label>
            <select name="category" value={formData.category} onChange={handleChange} required>
              <option value="">Select a category</option>
              <option value="Engineering">Engineering</option>
              <option value="Arts & Culture">Arts & Culture</option>
              <option value="Sports">Sports</option>
              <option value="Wellness">Wellness</option>
              <option value="Business">Business</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label>Mission / Description</label>
            <textarea 
              name="description" 
              value={formData.description} 
              onChange={handleChange} 
              placeholder="Describe the purpose and goals of the club..."
              rows={4}
              required 
            />
          </div>

          <div className={styles.formGroup}>
            <label>Areas of Interest</label>
            <div className={styles.checkboxGroup}>
              {availableInterests.map(interest => (
                <label key={interest.id} className={styles.checkboxItem}>
                  <input
                    type="checkbox"
                    checked={formData.interests.includes(interest.id)}
                    onChange={() => handleInterestToggle(interest.id)}
                  />
                  {interest.name}
                </label>
              ))}
            </div>
          </div>

          <div className={styles.facultySection}>
            <h4>Faculty Advisor Details</h4>
            <p className={styles.helpText}>A faculty member is required to sponsor your new club.</p>
            
            <div className={styles.formGroup}>
              <label>Select Faculty Advisor</label>
              <select 
                name="faculty_advisor_id" 
                value={formData.faculty_advisor_id} 
                onChange={handleChange} 
                required
              >
                <option value="">-- Choose a Faculty Advisor --</option>
                {faculties.map(f => (
                  <option key={f.id} value={f.id}>{f.full_name} ({f.email})</option>
                ))}
              </select>
            </div>
          </div>

          <div className={styles.actions}>
            <button type="button" className={styles.cancelBtn} onClick={onClose}>Cancel</button>
            <button type="submit" className={styles.submitBtn} disabled={loading}>
              {loading ? 'Submitting...' : 'Submit Proposal'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
