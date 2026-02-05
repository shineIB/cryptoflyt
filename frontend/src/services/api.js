/**
 * API service for communicating with the backend.
 */
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  updateMe: (data) => api.patch('/auth/me', data),
};

// Prices API
export const pricesAPI = {
  getCurrent: () => api.get('/prices/current'),
  getPrice: (symbol) => api.get(`/prices/current/${symbol}`),
  getHistory: (symbol, period = '24h') => api.get(`/prices/history/${symbol}?period=${period}`),
  getSymbols: () => api.get('/prices/symbols'),
  analyze: (symbols) => api.post('/prices/analyze', { symbols, include_news: true }),
};

// Alerts API
export const alertsAPI = {
  getAll: (activeOnly = false) => api.get(`/alerts?active_only=${activeOnly}`),
  create: (data) => api.post('/alerts', data),
  update: (id, data) => api.patch(`/alerts/${id}`, data),
  delete: (id) => api.delete(`/alerts/${id}`),
  getHistory: (limit = 50) => api.get(`/alerts/history/all?limit=${limit}`),
};

// Portfolio API
export const portfolioAPI = {
  get: () => api.get('/portfolio'),
  addHolding: (data) => api.post('/portfolio/holdings', data),
  updateHolding: (id, data) => api.patch(`/portfolio/holdings/${id}`, data),
  deleteHolding: (id) => api.delete(`/portfolio/holdings/${id}`),
};

export default api;
