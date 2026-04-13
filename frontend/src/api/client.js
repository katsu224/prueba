/**
 * api/client.js
 * Cliente HTTP centralizado con Axios.
 * 
 * Configura la base URL y el interceptor que agrega
 * automáticamente el token JWT a todas las peticiones.
 * También maneja errores de autenticación (401).
 */
import axios from 'axios';

// Base URL del backend FastAPI.
// Usa la variable de entorno si existe (para producción en Vercel),
// de lo contrario usa el proxy local de Vite o path relativo.
const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de request: agrega el token JWT
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

import { authApi } from './auth';

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Interceptor de response: maneja errores globales y token refresh
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si recibimos 401 y no es ya un intento de refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Ignorar rutas de auth o login explícito
      if (originalRequest.url.includes('/auth/login') || originalRequest.url.includes('/auth/refresh')) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Poner en cola mientras otro request hace el refresh
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = 'Bearer ' + token;
            return client(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const data = await authApi.refreshToken(refreshToken);
        
        // Guardar nuevos tokens
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        
        // Procesar cola
        processQueue(null, data.access_token);
        
        // Ejecutar request original
        originalRequest.headers.Authorization = 'Bearer ' + data.access_token;
        return client(originalRequest);
        
      } catch (refreshError) {
        processQueue(refreshError, null);
        
        // Solo redirigir si el refresh token falla (401 explícito o no existe)
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    
    return Promise.reject(error);
  }
);

export default client;
