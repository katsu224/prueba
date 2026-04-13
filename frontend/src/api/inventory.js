/**
 * api/inventory.js
 * Servicios HTTP para productos, categorías, movimientos y kardex.
 * 
 * Cada función encapsula una llamada al backend FastAPI
 * y retorna directamente los datos de la respuesta.
 */
import client from './client';

/* ========== CATEGORÍAS ========== */
export const categoriesApi = {
  getAll: async () => {
    const { data } = await client.get('/categories/');
    return data;
  },
  getById: async (id) => {
    const { data } = await client.get(`/categories/${id}`);
    return data;
  },
  create: async (categoryData) => {
    const { data } = await client.post('/categories/', categoryData);
    return data;
  },
  update: async (id, categoryData) => {
    const { data } = await client.put(`/categories/${id}`, categoryData);
    return data;
  },
  delete: async (id) => {
    await client.delete(`/categories/${id}`);
  },
};

/* ========== PRODUCTOS ========== */
export const productsApi = {
  getAll: async (params = {}) => {
    const { data } = await client.get('/products/', { params });
    return data;
  },
  getById: async (id) => {
    const { data } = await client.get(`/products/${id}`);
    return data;
  },
  create: async (productData) => {
    const { data } = await client.post('/products/', productData);
    return data;
  },
  update: async (id, productData) => {
    const { data } = await client.put(`/products/${id}`, productData);
    return data;
  },
  deactivate: async (id) => {
    const { data } = await client.delete(`/products/${id}`);
    return data;
  },
};

/* ========== MOVIMIENTOS ========== */
export const movementsApi = {
  getAll: async (params = {}) => {
    const { data } = await client.get('/movements/', { params });
    return data;
  },
  getTypes: async () => {
    const { data } = await client.get('/movements/types');
    return data;
  },
  create: async (movementData) => {
    const { data } = await client.post('/movements/', movementData);
    return data;
  },
};

/* ========== KARDEX ========== */
export const kardexApi = {
  getKardex: async (productId, params = {}) => {
    const { data } = await client.get(`/kardex/${productId}`, { params });
    return data;
  },
  getProductStock: async (productId) => {
    const { data } = await client.get(`/kardex/stock/${productId}`);
    return data;
  },
  getAllStock: async () => {
    const { data } = await client.get('/kardex/dashboard/stock');
    return data;
  },
  getLowStock: async () => {
    const { data } = await client.get('/kardex/dashboard/low-stock');
    return data;
  },
};
