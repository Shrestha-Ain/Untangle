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
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// // Request interceptor — inject Bearer token on every outgoing request
// api.interceptors.request.use((config) => {
//   const token = localStorage.getItem('access_token')
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`
//   }
//   return config
// })

// Attach Clerk session token before every request.
// We import lazily inside the interceptor to avoid circular init issues.
api.interceptors.request.use(async (config) => {
  // // @clerk/vue exposes getToken() on the window via the loaded plugin
  // const { getToken } = (window as any).__clerk_frontend_api__ ?? {}
  // Preferred approach: call Clerk's JS SDK directly
  const token = await (window as any).Clerk?.session?.getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
