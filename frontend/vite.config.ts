import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

/**
 * Vite configuration
 *
 * Key choices:
 * • resolve.alias '@' → src/
 *   Lets every file use `import X from '@/components/...'`
 *   instead of fragile relative paths like '../../../'.
 *
 * • server.proxy '/api'
 *   In development, requests to /api/* are proxied to the FastAPI
 *   backend on port 8000. This avoids CORS issues during dev
 *   since the browser sees everything as coming from localhost:5173.
 *   In production, you'd configure Nginx/Vercel to do this proxy instead.
 */
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Proxy /api/* → FastAPI backend during development
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // Proxy WebSocket connections for /ws/*
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
