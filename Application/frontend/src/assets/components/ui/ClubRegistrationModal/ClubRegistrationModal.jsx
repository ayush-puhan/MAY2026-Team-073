import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Icon } from '@iconify/react';
import { Button } from '../Button/Button';
import { Input } from '../Input/Input';
import { Dropdown } from '../Dropdown/Dropdown';
import { uiIcons, dashboardIcons, authIcons, landingIcons } from '../../../icons/registry';
import { useToast } from '../../../../context/ToastContext';
import { useSession } from '../../../../context/SessionContext';
import styles from './ClubRegistrationModal.module.css';

export const ClubRegistrationModal = ({ isOpen, onClose, club, onJoin }) => {
  const { showError } = useToast();
  const { user } = useSession();

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    roll_number: '',
    motivation: '',
    previous_experience: '',
    skills: '',
    portfolio_url: '',
    weekly_availability: '',
    interests: []
  });
  const [availableInterests, setAvailableInterests] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Auto-fill from user session when modal opens
  useEffect(() => {
    if (isOpen && user) {
      setFormData(prev => ({
        ...prev,
        full_name: user.full_name || prev.full_name,
        email: user.email || prev.email,
        roll_number: user.student_profile?.roll_number || prev.roll_number,
        motivation: '',
        previous_experience: '',
        skills: '',
        portfolio_url: '',
        weekly_availability: '',
        interests: []
      }));
    }
  }, [isOpen, user]);

  useEffect(() => {
    const fetchInterests = async () => {
      try {
        const { api } = await import('../../../../api/api');
        const data = await api.get('/interests');
        setAvailableInterests(data || []);
      } catch (e) {
        console.error('Failed to fetch interests', e);
      }
    };
    if (isOpen) {
      fetchInterests();
    }
  }, [isOpen]);

  if (!isOpen || !club) return null;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
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
    if (isSubmitting) return;
    if (!formData.motivation) {
      showError('Please provide your motivation for joining');
      return;
    }
    setIsSubmitting(true);
    try {
      await onJoin(formData);
    } catch (err) {
      // error handled by parent
    } finally {
      setIsSubmitting(false);
    }
  };

  const modalContent = (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <div className={styles.iconWrapper}>
            <Icon icon={landingIcons.accountGroup} />
          </div>
          <div className={styles.headerText}>
            <h3>Join Club</h3>
            <p>{club.name}</p>
          </div>
          <button className={styles.closeButton} onClick={onClose}>
            <Icon icon={uiIcons.close} />
          </button>
        </div>

        <form className={styles.form} onSubmit={handleSubmit} noValidate>
          {/* Auto-filled applicant info (read-only) */}
          <div className={styles.confirmationMessage} style={{ marginBottom: '1.5rem', background: 'var(--bg-card-hover)', padding: '1rem', borderRadius: '8px' }}>
            <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Applying as <strong>{formData.full_name || 'Student'}</strong> ({formData.email || 'N/A'})
              {formData.roll_number && <> • Roll No: <strong>{formData.roll_number}</strong></>}
            </p>
          </div>
          
          <div className={styles.formGroup}>
            <label>Motivation for joining *</label>
            <textarea
              name="motivation"
              placeholder="Why do you want to join this club?"
              value={formData.motivation}
              onChange={handleChange}
              className={styles.textarea}
              rows={3}
            />
          </div>

          <div className={styles.formGroup}>
            <label>Previous Experience (Optional)</label>
            <textarea
              name="previous_experience"
              placeholder="Any relevant past experience?"
              value={formData.previous_experience}
              onChange={handleChange}
              className={styles.textarea}
              rows={2}
            />
          </div>

          <div className={styles.formGroup}>
            <label>Skills (Optional)</label>
            <Input
              name="skills"
              placeholder="e.g. Design, Coding, Event Management"
              value={formData.skills}
              onChange={handleChange}
            />
          </div>

          <div className={styles.formGroup}>
            <label>Portfolio URL (Optional)</label>
            <Input
              name="portfolio_url"
              placeholder="https://..."
              value={formData.portfolio_url}
              onChange={handleChange}
            />
          </div>

          <div className={styles.formGroup}>
            <label>Weekly Availability (Optional)</label>
            <Dropdown
              name="weekly_availability"
              value={formData.weekly_availability}
              onChange={handleChange}
              options={[
                { value: '', label: 'Select availability...' },
                { value: '1-5 hrs', label: '1-5 hrs' },
                { value: '5-10 hrs', label: '5-10 hrs' },
                { value: '10-15 hrs', label: '10-15 hrs' },
                { value: '15+ hrs', label: '15+ hrs' }
              ]}
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

          <div className={styles.footer}>
            <Button variant="outline" type="button" onClick={onClose} disabled={isSubmitting}>Cancel</Button>
            <Button variant="primary" type="submit" disabled={isSubmitting} isLoading={isSubmitting}>
              <Icon icon={authIcons.check} /> {isSubmitting ? 'Submitting...' : 'Submit Request'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
