/**
 * TodoForm.jsx — HOW THIS WORKS:
 * --------------------------------
 * A simple form component that:
 * - Has its own local state (title, description)
 * - Calls onAdd() (passed from Dashboard) when submitted
 * - Resets itself after submission
 *
 * Props pattern:
 * TodoForm does NOT make API calls directly.
 * Instead, it calls onAdd(title, description) — the parent (Dashboard)
 * handles the API call. This makes TodoForm "dumb" / reusable.
 * This is called the "lift state up" or "container/presentational" pattern.
 */

import { useState } from 'react';

function TodoForm({ onAdd }) {
  const [title, setTitle]             = useState('');
  const [description, setDescription] = useState('');
  const [isExpanded, setIsExpanded]   = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;  // Don't submit empty todos

    onAdd(title.trim(), description.trim());

    // Reset form after submission
    setTitle('');
    setDescription('');
    setIsExpanded(false);
  };

  return (
    <div className="todo-form-card">
      <form onSubmit={handleSubmit}>
        <div className="todo-form-main">
          <input
            type="text"
            placeholder="What needs to be done?"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onFocus={() => setIsExpanded(true)}  // Expand on focus to show description field
            className="todo-title-input"
            required
          />
          <button type="submit" className="btn-add">
            + Add
          </button>
        </div>

        {/* Description field only shows when input is focused */}
        {isExpanded && (
          <div className="todo-form-extra">
            <input
              type="text"
              placeholder="Add a description (optional)..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="todo-desc-input"
            />
          </div>
        )}
      </form>
    </div>
  );
}

export default TodoForm;
