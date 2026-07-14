/**
 * ClubConnect API Client
 * 
 * Central API service using Axios. All feature-specific API files
 * (auth.api.js, clubs.api.js, events.api.js, etc.) import from here.
 * 
 * SWITCHING TO BACKEND:
 * Just change VITE_API_URL in .env from "http://localhost:3000" (json-server)
 * to "http://localhost:5000/api" (Flask backend). Nothing else breaks.
 * 
 * JWT TOKEN STORAGE:
 * - Token is stored in localStorage under key 'token'
 * - User object is stored in localStorage under key 'user'
 * - The request interceptor auto-attaches the token to every outgoing request
 * - The response interceptor auto-clears storage on 401 (expired/invalid token)
 * - When Flask backend is ready, it will return a real JWT on login,
 *   and this interceptor will send it on every subsequent request automatically.
 */

import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// ── Request Interceptor ──
// Automatically attach JWT token from localStorage to every request
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response Interceptor ──
// Handle global errors like 401 Unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      if (error.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        // window.location.href = '/login'; // Enable when needed
      }
      // Extract server error message if available
      const serverMessage =
        error.response.data?.message ||
        error.response.data?.error ||
        error.response.statusText;
      return Promise.reject(new Error(serverMessage));
    } else if (error.request) {
      // Request was made but no response received (server down)
      return Promise.reject(
        new Error('Network error: Unable to reach the server. Is json-server running on port 3000?')
      );
    }
    return Promise.reject(error);
  }
);

/**
 * Generic CRUD operations
 * 
 * Usage in feature APIs:
 *   import { api } from './api';
 *   const users = await api.get('/users');
 *   const newClub = await api.post('/clubs', { name: 'Robotics' });
 *   await api.put('/clubs/1', updatedClub);
 *   await api.patch('/clubs/1', { status: 'inactive' });
 *   await api.del('/clubs/1');
 */
export const api = {
  get: async (endpoint) => {
    const response = await apiClient.get(endpoint);
    return response.data;
  },

  post: async (endpoint, data) => {
    const response = await apiClient.post(endpoint, data);
    return response.data;
  },

  put: async (endpoint, data) => {
    const response = await apiClient.put(endpoint, data);
    return response.data;
  },

  patch: async (endpoint, data) => {
    const response = await apiClient.patch(endpoint, data);
    return response.data;
  },

  del: async (endpoint) => {
    const response = await apiClient.delete(endpoint);
    return response.data;
  },
};

export default api;
