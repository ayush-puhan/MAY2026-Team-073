import React, { useState, useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import styles from "./ResetPasswordForm.module.css";
import { authApi } from "@api/authApis/auth";
import { validatePassword, getStrengthLabel } from "../../../../api/validation";
import { useToast } from "../../../../context/ToastContext";
import { Icon } from "@iconify/react";
import { motion } from "framer-motion";
import clsx from "clsx";
import { uiIcons } from "../../../icons/registry";

export const ResetPasswordForm = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [formData, setFormData] = useState({
    password: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();

  const pwResult = useMemo(
    () => validatePassword(formData.password),
    [formData.password],
  );

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    if (errors[name]) setErrors({ ...errors, [name]: null });
  };

  const validate = () => {
    const e = {};
    if (!pwResult.isValid) e.password = pwResult.errors[0];
    if (formData.password !== formData.confirmPassword)
      e.confirmPassword = "Passwords do not match";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleReset = async (e) => {
    e.preventDefault();
    if (!token) {
      showError("Invalid or missing reset token.");
      return;
    }
    if (!validate()) return;

    setIsLoading(true);
    try {
      await authApi.resetPassword(token, formData.password);
      showSuccess("Password reset successfully! Please log in.");
      navigate("/login");
    } catch (err) {
      showError(err.message || "Failed to reset password.");
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) {
    return (
      <div className={styles.container}>
        <h1 className={styles.heading}>Invalid Reset Link</h1>
        <p className={styles.subtitle}>
          The reset link is missing or malformed. Please request a new one.
        </p>
        <button
          onClick={() => navigate("/forgot-password")}
          className={styles.submitBtn}
        >
          Request New Link
        </button>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>Create new password</h1>
      <p className={styles.subtitle}>
        Your new password must be different from previous used passwords.
      </p>

      <form onSubmit={handleReset} className={styles.form} noValidate>
        <div className={styles.fieldGroup}>
          <div className={styles.passwordWrapper}>
            <input
              name="password"
              type={showPassword ? "text" : "password"}
              placeholder="New password *"
              className={clsx(
                styles.input,
                errors.password && styles.inputError,
              )}
              value={formData.password}
              onChange={handleChange}
            />
            <button
              type="button"
              className={styles.eyeBtn}
              onClick={() => setShowPassword(!showPassword)}
            >
              <Icon
                icon={showPassword ? "mdi:eye-off-outline" : "mdi:eye-outline"}
              />
            </button>
          </div>
          {formData.password && (
            <>
              <div className={styles.strengthMeter}>
                {[1, 2, 3, 4].map((level) => (
                  <div
                    key={level}
                    className={clsx(
                      styles.bar,
                      pwResult.strength >= level &&
                        styles[`str${pwResult.strength}`],
                    )}
                  />
                ))}
              </div>
              <span className={styles.strengthLabel}>
                Strength · {getStrengthLabel(pwResult.strength)}
              </span>
            </>
          )}
          {errors.password && (
            <span className={styles.errorText}>{errors.password}</span>
          )}
        </div>

        <div className={styles.fieldGroup}>
          <div className={styles.passwordWrapper}>
            <input
              name="confirmPassword"
              type={showConfirmPassword ? "text" : "password"}
              placeholder="Confirm password *"
              className={clsx(
                styles.input,
                errors.confirmPassword && styles.inputError,
              )}
              value={formData.confirmPassword}
              onChange={handleChange}
            />
            <button
              type="button"
              className={styles.eyeBtn}
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              <Icon
                icon={
                  showConfirmPassword
                    ? "mdi:eye-off-outline"
                    : "mdi:eye-outline"
                }
              />
            </button>
          </div>
          {errors.confirmPassword && (
            <span className={styles.errorText}>{errors.confirmPassword}</span>
          )}
        </div>

        <motion.button
          type="submit"
          className={styles.submitBtn}
          disabled={isLoading}
          whileTap={{ scale: 0.98 }}
        >
          {isLoading ? (
            <Icon icon={uiIcons.loading} className={styles.spinner} />
          ) : (
            <Icon icon={uiIcons.check} />
          )}
          {isLoading ? "Resetting..." : "Reset Password"}
        </motion.button>
      </form>
    </div>
  );
};
