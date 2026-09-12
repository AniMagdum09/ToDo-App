/**
 * AuthContext.jsx — HOW THIS WORKS:
 * ------------------------------------
 * Problem: Multiple components need to know "is the user logged in?"
 * Without Context: you'd pass login/logout as props through every component (prop drilling).
 * With Context: ANY component can access auth state by calling useAuth().
 *
 * Think of Context as a GLOBAL STORE for auth state.
 *
 * Flow:
 * 1. AuthProvider wraps the entire app (in App.jsx)
 * 2. It holds token and user state
 * 3. Any child component calls useAuth() to get: { token, login, logout, register }
 *
 * Example usage in any component:
 *   const { login, logout, token } = useAuth();
 */

import { createContext, useContext, useState } from 'react';
import API from '../api/axios';

// Step 1: Create the Context object
// This is like creating the "store" — empty for now
const AuthContext = createContext();


// Step 2: Create the Provider component
// This wraps the app and PROVIDES the auth values to all children
export function AuthProvider({ children }) {
  // Initialize token from localStorage — so login persists on page refresh
  const [token, setToken] = useState(localStorage.getItem('token'));

  const login = async (email, password) => {
    /**
     * Calls POST /auth/login
     * On success: saves token to localStorage AND state
     * Throws error on failure — the calling component handles the error
     */
    const response = await API.post('/auth/login', { email, password });
    const { access_token } = response.data;

    localStorage.setItem('token', access_token);  // Persist across page refreshes
    setToken(access_token);                         // Update React state
    return response.data;
  };

  const register = async (username, email, password) => {
    /**
     * Calls POST /auth/register
     * Returns user data on success
     * Does NOT log in automatically — user must login after register
     */
    const response = await API.post('/auth/register', { username, email, password });
    return response.data;
  };

  const logout = () => {
    /**
     * Clears token from localStorage and React state
     * axios.js interceptor will stop sending Authorization header
     */
    localStorage.removeItem('token');
    setToken(null);
  };

  // Step 3: Provide values to all children
  return (
    <AuthContext.Provider value={{ token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}


// Step 4: Custom hook for easy access
// Instead of: const { login } = useContext(AuthContext)  ← verbose
// We write:   const { login } = useAuth()               ← clean
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside <AuthProvider>');
  }
  return context;
};
