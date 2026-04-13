/**
 * api/auth.js
 * Servicios de autenticación (login, register, getMe).
 * 
 * El login usa form-data (OAuth2PasswordRequestForm) porque
 * FastAPI lo requiere en el endpoint de login con OAuth2.
 */
import client from './client';

export const authApi = {
  /** Registra un nuevo usuario */
  register: async (userData) => {
    const { data } = await client.post('/auth/register', userData);
    return data;
  },

  /** Inicia sesión. Envía como form-data (requerido por OAuth2) */
  login: async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const { data } = await client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return data;
  },

  /** Obtiene los datos del usuario autenticado */
  getMe: async (token) => {
    const { data } = await client.get('/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return data;
  },
};
