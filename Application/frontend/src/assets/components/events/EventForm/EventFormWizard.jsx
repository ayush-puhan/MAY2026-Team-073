import React, { useState } from 'react';
import { Icon } from '@iconify/react';
import { Button } from '../../ui/Button/Button';
import { Input } from '../../ui/Input/Input';
import { EventSessionManager } from '../EventSessionManager/EventSessionManager';
import styles from './EventFormWizard.module.css';

const STEPS = [
  { id: 'basic', label: 'Basic Info', icon: 'mdi:information-outline' },
  { id: 'timing', label: 'Date & Time', icon: 'mdi:clock-outline' },
  { id: 'settings', label: 'Settings & Sessions', icon: 'mdi:cog-outline' }
];

const EventFormWizard = ({ initialData, onSubmit, onCancel, isEditing }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    title: initialData?.title || '',
    description: initialData?.description || '',
    venue: initialData?.venue || '',
    sponsors: initialData?.sponsors || '',
    banner: initialData?.banner || '',
    start_at: initialData?.start_at || '',
    end_at: initialData?.end_at || '',
    registration_deadline: initialData?.registration_deadline || '',
    requires_external_participants: initialData?.requires_external_participants || false,
    is_public: initialData?.is_public || false
  });
  
  // Note: For simplicity in the wizard, we handle sessions in step 3
  const [sessions, setSessions] = useState(initialData?.sessions || []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) setCurrentStep(c => c + 1);
  };

  const handlePrev = () => {
    if (currentStep > 0) setCurrentStep(c => c - 1);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData, sessions);
  };

  const isStepValid = () => {
    if (currentStep === 0) return formData.title.trim() !== '';
    if (currentStep === 1) return formData.start_at !== '' && formData.end_at !== '';
    return true;
  };

  return (
    <div className={styles.wizardOverlay} onClick={onCancel}>
      <div className={styles.wizardContent} onClick={e => e.stopPropagation()}>
        <div className={styles.wizardHeader}>
          <h3>{isEditing ? 'Edit Event' : 'Schedule New Event'}</h3>
          <button className={styles.closeBtn} onClick={onCancel}><Icon icon="mdi:close" /></button>
        </div>

        <div className={styles.stepper}>
          {STEPS.map((step, index) => (
            <div key={step.id} className={`${styles.stepIndicator} ${currentStep === index ? styles.active : ''} ${currentStep > index ? styles.completed : ''}`}>
              <div className={styles.stepIcon}>
                <Icon icon={currentStep > index ? 'mdi:check' : step.icon} />
              </div>
              <span>{step.label}</span>
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit} className={styles.formBody}>
          {currentStep === 0 && (
            <div className={styles.stepContent}>
              <Input
                label="Event Title *"
                name="title"
                placeholder="e.g., Annual Tech Meetup"
                value={formData.title}
                onChange={handleInputChange}
                required
              />
              <Input
                label="Venue (Optional)"
                name="venue"
                placeholder="e.g., Main Auditorium"
                value={formData.venue}
                onChange={handleInputChange}
              />
              <div className={styles.inputGroup}>
                <label className={styles.label}>Description</label>
                <textarea
                  className={styles.textarea}
                  name="description"
                  placeholder="Detailed description of the event..."
                  rows="4"
                  value={formData.description}
                  onChange={handleInputChange}
                />
              </div>
            </div>
          )}

          {currentStep === 1 && (
            <div className={styles.stepContent}>
              <div className={styles.grid2}>
                <Input
                  label="Start Time *"
                  type="datetime-local"
                  name="start_at"
                  value={formData.start_at}
                  onChange={handleInputChange}
                  required
                />
                <Input
                  label="End Time *"
                  type="datetime-local"
                  name="end_at"
                  value={formData.end_at}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <Input
                label="Registration Deadline (Optional)"
                type="datetime-local"
                name="registration_deadline"
                value={formData.registration_deadline}
                onChange={handleInputChange}
              />
            </div>
          )}

          {currentStep === 2 && (
            <div className={styles.stepContent}>
              <Input
                label="Sponsors (Optional, comma separated)"
                name="sponsors"
                placeholder="e.g. Google, GitHub"
                value={formData.sponsors}
                onChange={handleInputChange}
              />
              <Input
                label="Banner URL (Optional)"
                name="banner"
                placeholder="https://example.com/banner.png"
                value={formData.banner}
                onChange={handleInputChange}
              />
              
              <div className={styles.checkboxGroup}>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    name="requires_external_participants"
                    checked={formData.requires_external_participants}
                    onChange={handleInputChange}
                  />
                  <span>Public Event (Requires External Participants)</span>
                </label>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    name="is_public"
                    checked={formData.is_public}
                    onChange={handleInputChange}
                  />
                  <span>Open Club Event (Open to any University Student)</span>
                </label>
              </div>

              {!isEditing && (
                <div className={styles.sessionManagerWrapper}>
                  <h4>Initial Sessions</h4>
                  <p className={styles.helpText}>You can add more sessions later in the Manage Event view.</p>
                  <EventSessionManager sessions={sessions} setSessions={setSessions} />
                </div>
              )}
            </div>
          )}

          <div className={styles.wizardFooter}>
            {currentStep > 0 ? (
              <Button variant="outline" type="button" onClick={handlePrev}>Back</Button>
            ) : (
              <Button variant="outline" type="button" onClick={onCancel}>Cancel</Button>
            )}
            
            {currentStep < STEPS.length - 1 ? (
              <Button type="button" onClick={(e) => { e.preventDefault(); handleNext(); }} disabled={!isStepValid()}>Next</Button>
            ) : (
              <Button type="submit" disabled={!isStepValid()}>
                {isEditing ? 'Save Changes' : 'Submit Event'}
              </Button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default EventFormWizard;
