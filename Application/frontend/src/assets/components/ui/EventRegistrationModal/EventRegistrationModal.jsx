import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { Icon } from '@iconify/react';
import { Button } from '../Button/Button';
import { Input } from '../Input/Input';
import { Dropdown } from '../Dropdown/Dropdown';
import { uiIcons, dashboardIcons, authIcons } from '../../../icons/registry';
import styles from './EventRegistrationModal.module.css';

export const EventRegistrationModal = ({ isOpen, onClose, event, onRegister, isExternal = false }) => {
  if (!isOpen || !event) return null;

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    affiliation: '',
    participant_type: 'OTHER_UNIVERSITY_STUDENT'
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onRegister(formData);
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

        <form className={styles.form} onSubmit={handleSubmit}>
          {isExternal ? (
            <>
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

          <div className={styles.formGroup}>
            <label>Affiliation (Optional)</label>
            <Input 
              name="affiliation"
              placeholder="e.g. Computer Science Dept, Google Inc."
              value={formData.affiliation}
              onChange={handleChange}
            />
          </div>

          <div className={styles.formGroup}>
            <label>Participant Type *</label>
            <Dropdown
              name="participant_type"
              value={formData.participant_type}
              onChange={handleChange}
              options={[
                { value: 'OTHER_UNIVERSITY_STUDENT', label: 'Other University Student' },
                { value: 'GUEST_SPEAKER', label: 'Guest Speaker' },
                { value: 'ALUMNI', label: 'Alumni' },
                { value: 'INDUSTRY_PROFESSIONAL', label: 'Industry Professional' },
                { value: 'COMPETITION_PARTICIPANT', label: 'Competition Participant' },
                { value: 'GENERAL_PUBLIC', label: 'General Public' }
              ]}
            />
          </div>
            </>
          ) : (
            <div className={styles.confirmationMessage}>
              <p>You are about to register for <strong>{event.title}</strong> as a verified university student.</p>
              <p>Your institutional details will be automatically attached to your registration.</p>
            </div>
          )}

          <div className={styles.footer}>
            <Button variant="outline" type="button" onClick={onClose}>Cancel</Button>
            <Button variant="primary" type="submit">
              <Icon icon={authIcons.check} /> Confirm Registration
            </Button>
          </div>
        </form>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
