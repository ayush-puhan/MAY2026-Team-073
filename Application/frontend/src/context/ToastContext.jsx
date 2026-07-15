import { createContext, useContext, useState, useCallback } from 'react';
import { ToastContainer } from '../assets/components/ui/Toast/ToastContainer';

const ToastContext = createContext(null);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const addToast = useCallback((message, type = 'info', duration = 3000) => {
    const id = Date.now().toString() + Math.random().toString(36).substring(2, 9);
    const validDuration = typeof duration === 'number' && !isNaN(duration) ? duration : 3000;
    
    setToasts((prev) => [...prev, { id, message, type }]);

    if (validDuration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, validDuration);
    }
    return id;
  }, []);


  const showSuccess = useCallback((msg, duration) => addToast(msg, 'success', duration), [addToast]);
  const showError = useCallback((msg, duration) => addToast(msg, 'error', duration), [addToast]);
  const showInfo = useCallback((msg, duration) => addToast(msg, 'info', duration), [addToast]);
  const showLoading = useCallback((msg, duration = 0) => addToast(msg, 'loading', duration), [addToast]);

  return (
    <ToastContext.Provider value={{ showSuccess, showError, showInfo, showLoading, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

