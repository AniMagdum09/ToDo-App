/**
 * App.jsx — HOW THIS WORKS:
 * ---------------------------
 * The root component. It:
 * 1. Wraps everything in AuthProvider (makes auth state available app-wide)
 * 2. Sets up React Router with routes
 * 3. Defines ProtectedRoute — guards pages that require login
 *
 * React Router concepts:
 * - <BrowserRouter> → uses browser history API (real URL changes)
 * - <Routes>        → renders the FIRST matching route
 * - <Route>         → maps a URL path to a component
 * - <Navigate>      → programmatic redirect (replaces old <Redirect>)
 *
 * ProtectedRoute pattern:
 * If user has a token → render the page normally.
 * If no token → redirect to /login.
 * This prevents logged-out users from accessing the dashboard.
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import './App.css';

/**
 * ProtectedRoute — wraps pages that require authentication.
 *
 * Usage:
 *   <ProtectedRoute>
 *     <Dashboard />
 *   </ProtectedRoute>
 *
 * If token exists → renders Dashboard.
 * If no token → redirects to /login.
 *
 * Note: This only checks if a token EXISTS in localStorage.
 * The actual token validity is checked on every API call by FastAPI.
 * If token is expired, FastAPI returns 401 → axios interceptor redirects to /login.
 */
function ProtectedRoute({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" replace />;
  // replace=true means the /login replaces current entry in browser history
  // So pressing "back" after being redirected doesn't loop back
}

function App() {
  return (
    <AuthProvider>
      {/* AuthProvider must wrap Router so ProtectedRoute can call useAuth() */}
      <Router>
        <Routes>
          {/* Public routes — accessible without login */}
          <Route path="/login"    element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected route — requires login */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          {/* Default redirect: / → /dashboard (ProtectedRoute handles auth check) */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* Catch-all: any unknown URL → /dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
