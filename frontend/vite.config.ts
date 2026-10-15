import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // En dev, le front appelle /api/... et Vite relaie vers FastAPI : même origine,
    // donc pas de CORS, et ça marche aussi depuis un téléphone (npm run dev -- --host).
    proxy: {
      '/api': { target: 'http://localhost:8000', rewrite: (path) => path.replace(/^\/api/, '') },
    },
  },
})
