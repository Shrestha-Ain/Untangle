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

// Request interceptor — inject Bearer token on every outgoing request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor — redirect to login on 401 (token expired/invalid)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

