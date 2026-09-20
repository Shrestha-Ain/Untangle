import { ref, onUnmounted } from 'vue'

export interface IngestionEvent {
  current_step: string
  percent_complete: number
  message: string
  towers_built?: number
  roads_laid?: number
}

/**
 * Composable to connect to the backend's WebSocket ingestion telemetry.
 * Listens on /ws/documents/{documentId}/progress for real-time step updates
 * published by the Celery worker via Redis pub/sub.
 */
export function useIngestionWebSocket() {
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const lastEvent = ref<IngestionEvent | null>(null)
  const error = ref<string | null>(null)

  function connect(
    documentId: string,
    callbacks: {
      onStep?: (event: IngestionEvent) => void
      onDone?: (event: IngestionEvent) => void
      onError?: (msg: string) => void
    } = {},
  ) {
    disconnect()

    // Build WebSocket URL from current location
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_API_WS_HOST || window.location.host
    const basePath = import.meta.env.VITE_API_BASE_URL || '/api/v1'

    // Try to get Clerk session token for auth
    let tokenParam = ''
    try {
      const clerk = (window as any).Clerk
      if (clerk?.session) {
        const token = clerk.session.getToken()
        if (token && typeof token === 'string') {
          tokenParam = `?token=${encodeURIComponent(token)}`
        }
      } else if ((window as any).__clerk_session_token) {
        tokenParam = `?token=${encodeURIComponent((window as any).__clerk_session_token)}`
      }
    } catch {
      // No auth token available — proceed without (backend may allow in dev)
    }

    const url = `${protocol}//${host}${basePath}/ws/documents/${documentId}/progress${tokenParam}`

    try {
      const socket = new WebSocket(url)
      ws.value = socket

      socket.onopen = () => {
        isConnected.value = true
        error.value = null
      }

      socket.onmessage = (evt) => {
        try {
          const payload: IngestionEvent = JSON.parse(evt.data)
          lastEvent.value = payload

          // Check for terminal state
          const step = payload.current_step?.toLowerCase()
          if (step === 'ready' || step === 'done' || step === 'failed') {
            callbacks.onDone?.(payload)
            if (step === 'failed') {
              callbacks.onError?.(payload.message || 'Ingestion failed')
            }
            // Server will close the connection, but clean up our side too
            disconnect()
          } else {
            callbacks.onStep?.(payload)
          }
        } catch {
          // Ignore unparseable frames
        }
      }

      socket.onerror = () => {
        error.value = 'WebSocket connection error'
        callbacks.onError?.('WebSocket connection error')
      }

      socket.onclose = () => {
        isConnected.value = false
        ws.value = null
      }
    } catch (e) {
      error.value = 'Failed to create WebSocket connection'
      callbacks.onError?.('Failed to create WebSocket connection')
    }
  }

  function disconnect() {
    if (ws.value) {
      try {
        ws.value.close()
      } catch {
        // Already closed
      }
      ws.value = null
      isConnected.value = false
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    lastEvent,
    error,
    connect,
    disconnect,
  }
}

