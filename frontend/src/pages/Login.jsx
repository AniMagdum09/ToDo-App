/**
 * Login.jsx — HOW THIS WORKS:
 * -----------------------------
 * A controlled form with:
 * - Local state for each input field (email, password)
 * - Error state for showing API errors
 * - Loading state for disabling button while request is in-flight
 *
 * On submit:
 * 1. Calls login() from AuthContext → makes POST /auth/login
 * 2. On success → navigate to /dashboard
 * 3. On failure → show the error message from FastAPI
 *
 * Controlled vs Uncontrolled:
 * Controlled = React state controls the input value.
 * onChange updates state → state updates input value.
 * This way React always knows what's in the input.
 */

import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

function Login() {
  // Each input has its own piece of state
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  const { login } = useAuth();
  const navigate  = useNavigate();  // Programmatic navigation (like <Link> but in code)

  const handleSubmit = async (e) => {
    e.preventDefault();  // Prevent browser from reloading the page (default form behavior)

    setError('');       // Clear previous error
    setLoading(true);   // Disable submit button

    try {
      await login(email, password);
      navigate('/dashboard');  // Redirect to dashboard on success
    } catch (err) {
      // FastAPI sends errors in: { detail: "Invalid email or password" }
      setError(err.response?.data?.detail || 'Login failed. Try again.');
    } finally {
      setLoading(false);  // Re-enable button whether success or failure
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <div className="auth-header">
          <span className="auth-icon">📝</span>
          <h2>Welcome back</h2>
          <p>Log in to your Todo account</p>
        </div>

        {/* Show error if login fails */}
        {error && <div className="error-banner">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Logging in...' : 'Log In'}
          </button>
        </form>

        <p className="auth-footer">
          Don't have an account? <Link to="/register">Register here</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
