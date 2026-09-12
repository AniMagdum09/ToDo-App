import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite config — https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,   // Dev server port (default)
  },
})
