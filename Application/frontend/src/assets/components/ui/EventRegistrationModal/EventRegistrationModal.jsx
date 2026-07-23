import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { Icon } from '@iconify/react';
import { Button } from '../Button/Button';
import { Input } from '../Input/Input';
import { Dropdown } from '../Dropdown/Dropdown';
import { uiIcons, dashboardIcons, authIcons } from '../../../icons/registry';
import { useToast } from '../../../../context/ToastContext';
import { useSession } from '../../../../context/SessionContext';
import styles from './EventRegistrationModal.module.css';

export const EventRegistrationModal = ({ isOpen, onClose, event, onRegister, isExternal = false }) => {
  if (!isOpen || !event) return null;

  const { showError } = useToast();
  const { user } = useSession();

  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    affiliation: user?.university?.name || '',
    participant_type: 'other_university_student'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;

    if (!formData.full_name || !formData.email) {
      showError('Please fill in required fields');
      return;
    }
    
    if (isExternal && !formData.participant_type) {
      showError('Please select a participant type');
      return;
    }

    setIsSubmitting(true);
    try {
      await onRegister(formData);
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
            <Icon icon={dashboardIcons.calendar} />
          </div>
          <div className={styles.headerText}>
            <h3>Register for Event</h3>
            <p>{event.title}</p>
          </div>
          <button className={styles.closeButton} onClick={onClose}>
            <Icon icon={uiIcons.close} />
          </button>
        </div>

        <form className={styles.form} onSubmit={handleSubmit} noValidate>
          {!isExternal && (
            <div className={styles.confirmationMessage}>
              <p>
                You are registering as a verified university student. We've pre-filled your details, but you may update them for this specific registration if needed.
              </p>
            </div>
          )}
          <div className={styles.formGroup}>
              <label>Full Name *</label>
              <Input 
                name="full_name"
                placeholder="e.g. John Doe"
                value={formData.full_name}
                onChange={handleChange}
                required
              />
            </div>
          
          <div className={styles.formGroup}>
            <label>Email Address *</label>
            <Input 
              name="email"
              type="email"
              placeholder="e.g. john@example.com"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          {isExternal && (
            <>
              <div className={styles.formGroup}>
                <label>Affiliation (Optional)</label>
                <input
                  type="text"
                  name="affiliation"
                  value={formData.affiliation}
                  onChange={handleChange}
                  placeholder="e.g. Computer Science Dept, Google Inc."
                  disabled={isSubmitting}
                />
              </div>

              <div className={styles.formGroup}>
                <label>Participant Type *</label>
                <Dropdown
                  name="participant_type"
                  value={formData.participant_type}
                  onChange={handleChange}
                  disabled={isSubmitting}
                  options={[
                    { value: 'other_university_student', label: 'Other University Student' },
                    { value: 'guest_speaker', label: 'Guest Speaker' },
                    { value: 'competition_participant', label: 'Competition Participant' }
                  ]}
                />
              </div>
            </>
          )}

          <div className={styles.footer}>
            <Button variant="outline" type="button" onClick={onClose} disabled={isSubmitting}>Cancel</Button>
            <Button variant="primary" type="submit" disabled={isSubmitting} isLoading={isSubmitting}>
              <Icon icon={authIcons.check} /> {isSubmitting ? 'Registering...' : 'Confirm Registration'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
