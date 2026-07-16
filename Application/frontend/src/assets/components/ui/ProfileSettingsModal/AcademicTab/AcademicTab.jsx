import React from 'react';
import { motion } from 'framer-motion';
import { Dropdown } from '../../Dropdown/Dropdown';
import styles from '../ProfileSettingsModal.module.css';

export const AcademicTab = ({
  formData,
  errors,
  handleChange,
  masterData,
  isStudent,
  showDepartment
}) => {
  return (
    <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className={styles.tabPane}>
      {showDepartment && (
        <div className={styles.row}>
          <div className={styles.field}>
            <label>Department <span className={styles.required}>*</span></label>
            <Dropdown 
              name="department_id" 
              value={formData.department_id || ''} 
              onChange={handleChange} 
              placeholder="Select Department"
              options={masterData.departments.map(d => ({ value: d.id, label: d.name }))}
              className={`${errors.department_id ? styles.inputError : ''}`}
            />
          </div>
          {isStudent && (
            <div className={styles.field}>
              <label>Program <span className={styles.required}>*</span></label>
              <Dropdown 
                name="student_profile.program_id" 
                value={formData.student_profile?.program_id || ''} 
                onChange={handleChange} 
                placeholder="Select Program"
                options={masterData.programs
                  .filter(p => !formData.department_id || p.department_id === parseInt(formData.department_id))
                  .map(p => ({ value: p.id, label: p.name }))}
                className={`${errors.program_id ? styles.inputError : ''}`}
              />
            </div>
          )}
        </div>
      )}

      {isStudent && (
        <>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Academic Year <span className={styles.required}>*</span></label>
              <Dropdown 
                name="student_profile.academic_year" 
                value={formData.student_profile?.academic_year || ''} 
                onChange={handleChange} 
                placeholder="Select Year"
                options={[
                  { value: '1', label: '1st Year' },
                  { value: '2', label: '2nd Year' },
                  { value: '3', label: '3rd Year' },
                  { value: '4', label: '4th Year' }
                ]}
                className={`${errors.academic_year ? styles.inputError : ''}`}
              />
            </div>
            <div className={styles.field}>
              <label>Semester <span className={styles.required}>*</span></label>
              <Dropdown 
                name="student_profile.semester" 
                value={formData.student_profile?.semester || ''} 
                onChange={handleChange} 
                placeholder="Select Semester"
                options={[1,2,3,4,5,6,7,8].map(s => ({ value: String(s), label: `${s}th Sem` }))}
                className={`${errors.semester ? styles.inputError : ''}`}
              />
            </div>
          </div>

          <div className={styles.row}>
            <div className={styles.field}>
              <label>Batch <span className={styles.required}>*</span></label>
              <Dropdown 
                name="student_profile.batch" 
                value={formData.student_profile?.batch || ''} 
                onChange={handleChange} 
                placeholder="Select Batch"
                options={[2021,2022,2023,2024,2025,2026,2027,2028].map(y => ({ value: String(y), label: String(y) }))}
                className={`${errors.batch ? styles.inputError : ''}`}
              />
            </div>
            <div className={styles.field}>
              <label>Section</label>
              <Dropdown 
                name="student_profile.section" 
                value={formData.student_profile?.section || ''} 
                onChange={handleChange} 
                placeholder="Select Section"
                options={['A','B','C','D','E','F','G'].map(s => ({ value: s, label: `Section ${s}` }))}
              />
            </div>
          </div>
        </>
      )}
    </motion.div>
  );
};
