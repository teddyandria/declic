import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    // PWA installable : manifeste + service worker qui met en cache l'appli (pas les données).
    VitePWA({
      registerType: 'autoUpdate', // nouvelle version prise au prochain lancement, sans bouton à cliquer
      includeAssets: ['favicon.svg', 'apple-touch-icon-180x180.png'],
      manifest: {
        name: 'Déclic',
        short_name: 'Déclic',
        description: 'Ta leçon en 5 minutes. Pas plus.',
        lang: 'fr',
        start_url: '/',
        display: 'standalone',
        orientation: 'portrait',
        theme_color: '#3156F5',
        background_color: '#F5F6FB',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: 'maskable-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        navigateFallback: '/index.html',
        // Les appels API ne passent jamais par le cache : pas de mode hors ligne (hors périmètre du MVP).
        navigateFallbackDenylist: [/^\/api\//],
      },
    }),
  ],
  server: {
    // En dev, le front appelle /api/... et Vite relaie vers FastAPI : même origine,
    // donc pas de CORS, et ça marche aussi depuis un téléphone (npm run dev -- --host).
    proxy: {
      '/api': { target: 'http://localhost:8000', rewrite: (path) => path.replace(/^\/api/, '') },
    },
  },
})
