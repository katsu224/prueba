/**
 * api/client.js
 * Cliente HTTP centralizado con Axios.
 * 
 * Configura la base URL y el interceptor que agrega
 * automáticamente el token JWT a todas las peticiones.
 * También maneja errores de autenticación (401).
 */
import axios from 'axios';

// Base URL del backend FastAPI
const API_BASE = '/api/v1';

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

// Interceptor de response: maneja errores globales
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido, redirigir a login
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default client;
