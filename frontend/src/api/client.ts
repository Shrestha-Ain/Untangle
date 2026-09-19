import axios from 'axios'

/**
 * Axios instance pre-configured for the FastAPI backend.
 *
 * baseURL reads from Vite's environment variable system:
 *   • In development: set VITE_API_URL in frontend/.env.local
 *   • In production: set it at build time or deployment config
 *
 * The request interceptor automatically attaches the JWT token
 * stored in localStorage, so every store/component that uses
 * `api.get(...)` is automatically authenticated.
 */
const rawBaseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const apiBaseUrl = rawBaseUrl.endsWith('/api/v1') ? rawBaseUrl : `${rawBaseUrl.replace(/\/+$/, '')}/api/v1`

export const api = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach Clerk session token before every request.
api.interceptors.request.use(async (config) => {
  try {
    const clerk = (window as any).Clerk
    if (clerk?.session) {
      const token = await clerk.session.getToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
  } catch (err) {
    console.warn('[API Interceptor] Could not fetch Clerk token:', err)
  }
  return config
})
