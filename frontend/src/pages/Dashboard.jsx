/**
 * Dashboard.jsx — HOW THIS WORKS:
 * ---------------------------------
 * This is the "container" component — it manages all the state and API calls.
 * Child components (TodoForm, TodoItem) just receive data and callbacks.
 *
 * State managed here:
 * - todos     → array of all todo objects from API
 * - loading   → show spinner while fetching
 * - filter    → 'all' | 'active' | 'completed' (for tabs)
 *
 * Key React concept — Optimistic UI:
 * Instead of waiting for the API to respond to show changes,
 * we update the UI immediately and sync with the backend.
 * This makes the app feel instant.
 *
 * useEffect:
 * Runs after the component mounts (renders for the first time).
 * We fetch todos here — once, when the page loads.
 * The empty [] dependency array means "run once on mount".
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import API from '../api/axios';
import TodoForm from '../components/TodoForm';
import TodoItem from '../components/TodoItem';

function Dashboard() {
  const [todos, setTodos]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter]   = useState('all'); // 'all' | 'active' | 'completed'
  const [error, setError]     = useState('');

  const { logout, token } = useAuth();
  const navigate          = useNavigate();

  // ── FETCH ALL TODOS ON PAGE LOAD ──────────────────────────────────
  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchTodos();
  }, []); // [] = run once after first render

  const fetchTodos = async () => {
    try {
      setLoading(true);
      const response = await API.get('/todos/');
      // API.get auto-attaches JWT token (from axios interceptor)
      // FastAPI returns only THIS user's todos
      setTodos(response.data);
    } catch (err) {
      setError('Failed to load todos. Please refresh.');
    } finally {
      setLoading(false);
    }
  };

  // ── ADD TODO ───────────────────────────────────────────────────────
  const addTodo = async (title, description) => {
    try {
      const response = await API.post('/todos/', { title, description });
      // Add new todo to the BEGINNING of the list (newest first)
      setTodos(prev => [response.data, ...prev]);
    } catch (err) {
      setError('Failed to add todo. Try again.');
    }
  };

  // ── TOGGLE COMPLETED ───────────────────────────────────────────────
  const toggleTodo = async (id, currentCompleted) => {
    try {
      // OPTIMISTIC UPDATE: change UI immediately before API responds
      setTodos(prev =>
        prev.map(t => t.id === id ? { ...t, completed: !currentCompleted } : t)
      );
      // Then sync with backend
      await API.put(`/todos/${id}`, { completed: !currentCompleted });
    } catch (err) {
      // If API fails, revert the optimistic update
      setTodos(prev =>
        prev.map(t => t.id === id ? { ...t, completed: currentCompleted } : t)
      );
      setError('Failed to update todo.');
    }
  };

  // ── DELETE TODO ────────────────────────────────────────────────────
  const deleteTodo = async (id) => {
    try {
      // Optimistic: remove from UI first
      setTodos(prev => prev.filter(t => t.id !== id));
      await API.delete(`/todos/${id}`);
    } catch (err) {
      // If delete fails, re-fetch to get correct state
      fetchTodos();
      setError('Failed to delete todo.');
    }
  };

  // ── HANDLE LOGOUT ──────────────────────────────────────────────────
  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // ── FILTER TODOS ───────────────────────────────────────────────────
  const filteredTodos = todos.filter(t => {
    if (filter === 'active')    return !t.completed;
    if (filter === 'completed') return t.completed;
    return true; // 'all'
  });

  // ── STATS ──────────────────────────────────────────────────────────
  const totalCount     = todos.length;
  const completedCount = todos.filter(t => t.completed).length;
  const activeCount    = totalCount - completedCount;

  // ── RENDER ─────────────────────────────────────────────────────────
  return (
    <div className="dashboard">

      {/* NAVBAR */}
      <nav className="navbar">
        <div className="navbar-brand">📝 TodoApp</div>
        <button className="btn-logout" onClick={handleLogout}>
          Logout
        </button>
      </nav>

      <div className="dashboard-content">

        {/* STATS BAR */}
        <div className="stats-bar">
          <div className="stat">
            <span className="stat-number">{totalCount}</span>
            <span className="stat-label">Total</span>
          </div>
          <div className="stat">
            <span className="stat-number">{activeCount}</span>
            <span className="stat-label">Pending</span>
          </div>
          <div className="stat">
            <span className="stat-number">{completedCount}</span>
            <span className="stat-label">Done</span>
          </div>
        </div>

        {/* ADD TODO FORM */}
        <TodoForm onAdd={addTodo} />

        {/* ERROR MESSAGE */}
        {error && (
          <div className="error-banner" onClick={() => setError('')}>
            {error} (click to dismiss)
          </div>
        )}

        {/* FILTER TABS */}
        <div className="filter-tabs">
          {['all', 'active', 'completed'].map(tab => (
            <button
              key={tab}
              className={`tab-btn ${filter === tab ? 'tab-active' : ''}`}
              onClick={() => setFilter(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
              {tab === 'active'    && activeCount    > 0 && <span className="tab-badge">{activeCount}</span>}
              {tab === 'completed' && completedCount > 0 && <span className="tab-badge done">{completedCount}</span>}
            </button>
          ))}
        </div>

        {/* TODO LIST */}
        {loading ? (
          <div className="loading">Loading your todos...</div>
        ) : filteredTodos.length === 0 ? (
          <div className="empty-state">
            {filter === 'all'
              ? "No todos yet! Add one above 👆"
              : filter === 'active'
              ? "No pending todos. Great job! 🎉"
              : "No completed todos yet. Get going! 💪"}
          </div>
        ) : (
          <div className="todo-list">
            {filteredTodos.map(todo => (
              <TodoItem
                key={todo.id}
                todo={todo}
                onToggle={toggleTodo}
                onDelete={deleteTodo}
              />
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

export default Dashboard;
