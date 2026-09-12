/**
 * axios.js — HOW THIS WORKS:
 * ----------------------------
 * Instead of importing axios directly everywhere, we create ONE custom instance.
 * This instance has the baseURL set, so we write:
 *   API.get('/todos/')  instead of  axios.get('http://localhost:8000/todos/')
 *
 * The KEY feature is the REQUEST INTERCEPTOR:
 * Before EVERY request, it checks localStorage for a JWT token.
 * If found, it automatically adds: "Authorization: Bearer <token>"
 * to the request headers.
 *
 * This way, we NEVER have to manually add the token in every API call!
 */

import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// REQUEST INTERCEPTOR — runs before every HTTP request
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      // Add Authorization header with the JWT token
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;  // Must return config, otherwise request is blocked
  },
  (error) => Promise.reject(error)
);

// RESPONSE INTERCEPTOR — runs after every response
API.interceptors.response.use(
  (response) => response,  // Success: just pass through
  (error) => {
    // If we get 401 (Unauthorized) — token is expired or invalid
    if (error.response?.status === 401) {
      localStorage.removeItem('token');  // Clear invalid token
      window.location.href = '/login';   // Redirect to login
    }
    return Promise.reject(error);
  }
);

export default API;
