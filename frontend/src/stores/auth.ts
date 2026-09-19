import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'

export interface BackendUser {
  id: string
  clerk_id: string
  email: string | null
  first_name: string | null
  last_name: string | null
  image_url: string | null
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export const useAuthStore = defineStore('auth', () => {
  const backendUser = ref<BackendUser | null>(null)
  const isSyncing = ref(false)
  const isBackendConnected = ref(false)
  const syncError = ref<string | null>(null)

  /**
   * Syncs the authenticated Clerk session with the FastAPI backend.
   * Calls GET /api/v1/auth/me with Bearer token, which triggers JIT
   * provisioning in the local database and returns the synced User record.
   */
  async function syncWithBackend(): Promise<BackendUser | null> {
    isSyncing.value = true
    syncError.value = null
    try {
      const response = await api.get<BackendUser>('/auth/me')
      backendUser.value = response.data
      isBackendConnected.value = true
      return response.data
    } catch (err: any) {
      console.warn('[AuthStore] Backend sync failed:', err?.response?.data || err?.message)
      syncError.value = err?.response?.data?.detail || err?.message || 'Sync failed'
      isBackendConnected.value = false
      return null
    } finally {
      isSyncing.value = false
    }
  }

  function clearAuth() {
    backendUser.value = null
    isBackendConnected.value = false
    syncError.value = null
  }

  return {
    backendUser,
    isSyncing,
    isBackendConnected,
    syncError,
    syncWithBackend,
    clearAuth,
  }
})

