/**
 * context/ToastContext.jsx
 * Sistema de notificaciones toast global.
 * 
 * Provee funciones showSuccess() y showError() que muestran
 * notificaciones temporales en la esquina superior derecha.
 * Las notificaciones se auto-ocultan después de 3 segundos.
 */
import { createContext, useContext, useState, useCallback } from 'react';
import { HiCheckCircle, HiXCircle } from 'react-icons/hi2';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toast, setToast] = useState(null);

  /** Muestra un toast de éxito */
  const showSuccess = useCallback((message) => {
    setToast({ type: 'success', message });
    setTimeout(() => setToast(null), 3000);
  }, []);

  /** Muestra un toast de error */
  const showError = useCallback((message) => {
    setToast({ type: 'error', message });
    setTimeout(() => setToast(null), 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ showSuccess, showError }}>
      {children}
      {toast && (
        <div className={`toast toast-${toast.type}`} id="toast-notification">
          {toast.type === 'success' ? <HiCheckCircle size={20} /> : <HiXCircle size={20} />}
          {toast.message}
        </div>
      )}
    </ToastContext.Provider>
  );
}

/** Hook para acceder al sistema de toasts */
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast debe usarse dentro de un ToastProvider');
  }
  return context;
}
