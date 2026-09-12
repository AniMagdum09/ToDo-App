/**
 * main.jsx — HOW THIS WORKS:
 * ----------------------------
 * This is the very first JavaScript file that runs.
 * It mounts the entire React app into the HTML DOM.
 *
 * In index.html there is: <div id="root"></div>
 * ReactDOM.createRoot() takes that div and hands control to React.
 * From here, React manages everything inside that div.
 *
 * StrictMode:
 * In development, StrictMode deliberately renders components TWICE
 * to catch side effects and bugs. In production, it renders once normally.
 * This is why you might see useEffect running twice in dev.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
