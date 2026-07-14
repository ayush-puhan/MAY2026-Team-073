import React from 'react';
import { motion } from 'framer-motion';
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
      )}

      {isStudent && (
        <>
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

          <div className={styles.row}>
            <div className={styles.field}>
              <label>Batch <span className={styles.required}>*</span></label>
              <input type="text" name="batch" value={formData.student_profile.batch || ''} onChange={handleChange} className={`${styles.input} ${errors.batch ? styles.inputError : ''}`} placeholder="e.g. 2024" />
            </div>
            <div className={styles.field}>
              <label>Section</label>
              <input type="text" name="section" value={formData.student_profile.section || ''} onChange={handleChange} className={styles.input} placeholder="e.g. A" />
            </div>
          </div>
        </>
      )}
    </motion.div>
  );
};
