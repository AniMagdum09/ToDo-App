/**
 * TodoItem.jsx — HOW THIS WORKS:
 * --------------------------------
 * Displays a single todo.
 * Receives the todo data and callback functions from Dashboard (parent).
 *
 * Props:
 * - todo       → the todo object { id, title, description, completed, created_at }
 * - onToggle   → function(id, completed) — called when checkbox clicked
 * - onDelete   → function(id) — called when delete button clicked
 *
 * This component is STATELESS — it doesn't manage any state itself.
 * All actions are passed up to Dashboard via callbacks.
 * Dashboard handles the API calls and updates the todos list.
 *
 * This makes TodoItem highly reusable and easy to test.
 */

function TodoItem({ todo, onToggle, onDelete }) {
  const formattedDate = new Date(todo.created_at).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });

  return (
    <div className={`todo-item ${todo.completed ? 'todo-completed' : ''}`}>
      {/* Left side: checkbox + content */}
      <div className="todo-left">
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={() => onToggle(todo.id, todo.completed)}
          className="todo-checkbox"
          title={todo.completed ? 'Mark incomplete' : 'Mark complete'}
        />
        <div className="todo-content">
          <h3 className="todo-title">{todo.title}</h3>
          {todo.description && (
            <p className="todo-description">{todo.description}</p>
          )}
          <span className="todo-date">{formattedDate}</span>
        </div>
      </div>

      {/* Right side: delete button */}
      <button
        className="btn-delete"
        onClick={() => onDelete(todo.id)}
        title="Delete todo"
      >
        🗑️
      </button>
    </div>
  );
}

export default TodoItem;
