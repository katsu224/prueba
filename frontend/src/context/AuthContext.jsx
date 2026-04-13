/**
 * context/AuthContext.jsx
 * Contexto de autenticación global.
 * 
 * Maneja el estado de autenticación (token, usuario) y provee
 * funciones de login, register y logout a toda la app.
 * El token se persiste en localStorage para mantener la sesión.
 */
import { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Al montar, verificar si hay un token y cargar el usuario
  useEffect(() => {
    if (token) {
      authApi.getMe(token)
        .then(userData => {
          setUser(userData);
        })
        .catch((err) => {
          // Evitar cerrar sesión si es un error de red o de Vercel (404/403)
          if (err.response && err.response.status === 401) {
            // Token inválido o expirado, limpiar sesión
            localStorage.removeItem('token');
            setToken(null);
            setUser(null);
          } else {
            console.error("Error al obtener usuario:", err);
            // Podrías decidir no borrar la sesión en caso de error de red
            // Sin embargo, sin usuario la UI puede fallar. Dejamos el token intacto.
          }
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  /** Inicia sesión y guarda el token */
  const login = async (username, password) => {
    const data = await authApi.login(username, password);
    localStorage.setItem('token', data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  /** Registra un nuevo usuario */
  const register = async (userData) => {
    return await authApi.register(userData);
  };

  /** Cierra la sesión */
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/** Hook para acceder al contexto de autenticación */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return context;
}
