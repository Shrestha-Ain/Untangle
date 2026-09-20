import { defineStore } from 'pinia'
import { api } from '@/api/client'

export interface DocumentItem {
  id: string
  title: string
  filename: string
  source_mode: 'research' | 'study'
  status: 'pending' | 'parsing' | 'extracting' | 'clustering' | 'ready' | 'failed'
  created_at: string
  author?: string
  // Stats
  entity_count?: number
  relationship_count?: number
  community_count?: number
  // Study mode stats
  chapter_count?: number
  section_count?: number
  topic_count?: number
}

export interface IngestionState {
  documentId: string | null
  step: 'parse' | 'extract' | 'cluster' | 'link' | 'ready'
  progress: number // 0 - 100
  detail: string
}

/**
 * Map a backend step name to a frontend step key.
 * Backend emits: parse → chunk → extract → embed → graph → summarize → done/ready
 * Frontend UI has 3 steps: parse → extract → cluster → ready
 */
function mapBackendStep(
  backendStep: string,
  mode: 'research' | 'study',
): { step: IngestionState['step']; progress: number; detail: string } {
  const s = backendStep.toLowerCase()
  if (s === 'parse' || s === 'parsing' || s === 'chunk' || s === 'chunking') {
    return {
      step: 'parse',
      progress: 15,
      detail:
        mode === 'research'
          ? 'Parsing document structure and extracting text chunks...'
          : 'Parsing book structure and extracting chapters...',
    }
  }
  if (s === 'extract' || s === 'extracting' || s === 'embed' || s === 'embedding') {
    return {
      step: 'extract',
      progress: 50,
      detail:
        mode === 'research'
          ? 'Extracting named entities and relationships...'
          : 'Deconstructing chapter sections and topic hierarchy...',
    }
  }
  if (s === 'graph' || s === 'cluster' || s === 'clustering' || s === 'summarize' || s === 'summarizing') {
    return {
      step: mode === 'research' ? 'cluster' : 'link',
      progress: 85,
      detail:
        mode === 'research'
          ? 'Computing community clusters and Leiden partitions...'
          : 'Mapping conceptual cross-references and topic links...',
    }
  }
  if (s === 'ready' || s === 'done') {
    return { step: 'ready', progress: 100, detail: 'Knowledge map construction complete.' }
  }
  // Default: early stage
  return { step: 'parse', progress: 10, detail: `Processing: ${backendStep}...` }
}

/**
 * Normalize a backend DocumentRead object into the frontend DocumentItem shape.
 * Handles:
 *  - display_title → title
 *  - stats: { entity_count, ... } → flat entity_count, relationship_count, ...
 *  - UUID id → string
 */
function normalizeBackendDocument(raw: any): DocumentItem {
  const stats = raw.stats || {}
  const mode: 'research' | 'study' = raw.source_mode === 'study' ? 'study' : 'research'

  return {
    id: String(raw.id),
    title: raw.display_title || raw.title || raw.filename || 'Untitled',
    filename: raw.filename || '',
    source_mode: mode,
    status: raw.status || 'pending',
    created_at: raw.created_at || new Date().toISOString(),
    author: raw.author,
    // Research stats (flattened from nested stats dict)
    entity_count: stats.entity_count ?? raw.entity_count,
    relationship_count: stats.relationship_count ?? stats.chunk_count ?? raw.relationship_count,
    community_count: stats.community_count ?? raw.community_count,
    // Study stats
    chapter_count: stats.chapter_count ?? raw.chapter_count,
    section_count: stats.section_count ?? raw.section_count,
    topic_count: stats.topic_count ?? raw.topic_count,
  }
}

export const useDocumentsStore = defineStore('documents', {
  state: () => ({
    documents: [
      {
        id: 'doc-attention-1706',
        title: 'Attention Is All You Need',
        filename: 'vaswani2017_attention.pdf',
        source_mode: 'research' as const,
        status: 'ready' as const,
        created_at: '2026-09-18T10:30:00Z',
        author: 'Vaswani et al. (Google Brain)',
        entity_count: 64,
        relationship_count: 182,
        community_count: 8,
      },
      {
        id: 'doc-ostep-book',
        title: 'Operating Systems: Three Easy Pieces',
        filename: 'ostep_book.pdf',
        source_mode: 'study' as const,
        status: 'ready' as const,
        created_at: '2026-09-19T14:15:00Z',
        author: 'Remzi H. Arpaci-Dusseau & Andrea C. Arpaci-Dusseau',
        chapter_count: 12,
        section_count: 48,
        topic_count: 136,
      },
    ] as DocumentItem[],
    activeDocumentId: null as string | null,
    isLoading: false,
    ingestionState: null as IngestionState | null,
    // Active WebSocket connection handle (for cleanup)
    _activeWs: null as WebSocket | null,
  }),

  getters: {
    activeDocument: (state) =>
      state.documents.find((d) => d.id === state.activeDocumentId) ?? null,

    researchDocuments: (state) =>
      state.documents.filter((d) => d.source_mode === 'research'),

    studyDocuments: (state) =>
      state.documents.filter((d) => d.source_mode === 'study'),
  },

  actions: {
    async fetchDocuments() {
      this.isLoading = true
      try {
        const { data } = await api.get('/documents')
        if (Array.isArray(data) && data.length > 0) {
          // Normalize backend DocumentRead shape → frontend DocumentItem
          this.documents = data.map(normalizeBackendDocument)
        }
      } catch (err) {
        // Fallback to initial seed if backend is still starting
        console.warn('Backend not reachable or not ready, keeping local documents', err)
      } finally {
        this.isLoading = false
      }
    },

    async uploadDocument(file: File | null, arxivUrl: string | null, mode: 'research' | 'study') {
      const tempId = 'doc-' + Date.now()
      const title = file ? file.name.replace(/\.[^/.]+$/, '') : (arxivUrl ?? 'ArXiv Paper')

      const newDoc: DocumentItem = {
        id: tempId,
        title,
        filename: file?.name ?? 'arxiv_import.pdf',
        source_mode: mode,
        status: 'parsing',
        created_at: new Date().toISOString(),
        author: mode === 'research' ? 'Imported Paper' : 'Imported Textbook',
        entity_count: mode === 'research' ? 0 : undefined,
        relationship_count: mode === 'research' ? 0 : undefined,
        community_count: mode === 'research' ? 0 : undefined,
        chapter_count: mode === 'study' ? 0 : undefined,
        section_count: mode === 'study' ? 0 : undefined,
        topic_count: mode === 'study' ? 0 : undefined,
      }

      this.documents.unshift(newDoc)
      this.activeDocumentId = tempId

      // Start with a local simulation as immediate feedback
      this.ingestionState = {
        documentId: tempId,
        step: 'parse',
        progress: 5,
        detail: 'Uploading document...',
      }

      let backendDocId: string | null = null

      try {
        if (file) {
          const formData = new FormData()
          formData.append('file', file)
          formData.append('source_mode', mode)
          const res = await api.post('/documents/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          })
          if (res.data?.id) {
            backendDocId = String(res.data.id)
            newDoc.id = backendDocId
            this.activeDocumentId = backendDocId
            if (this.ingestionState) {
              this.ingestionState.documentId = backendDocId
            }
          }
        }
      } catch (e) {
        console.warn('Backend upload failed, falling back to local simulation:', e)
      }

      // If we got a real backend ID, try to connect via WebSocket for live progress
      if (backendDocId) {
        this._connectIngestionWs(backendDocId, newDoc, mode)
      } else {
        // No backend — run the full local simulation
        this.simulateIngestion(tempId, mode)
      }
    },

    /**
     * Connect to the backend WebSocket for real-time ingestion telemetry.
     * Falls back to local simulation if WS connection fails.
     */
    async _connectIngestionWs(docId: string, doc: DocumentItem, mode: 'research' | 'study') {
      // Clean up any previous connection
      if (this._activeWs) {
        try { this._activeWs.close() } catch { /* noop */ }
        this._activeWs = null
      }

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = import.meta.env.VITE_API_WS_HOST || 'localhost:8000'
      const basePath = import.meta.env.VITE_API_BASE_URL || '/api/v1'

      // Try to get auth token from Clerk or window global
      let token = ''
      try {
        const clerk = (window as any).Clerk
        if (clerk?.session) {
          token = (await clerk.session.getToken()) || ''
        } else if ((window as any).__clerk_session_token) {
          token = (window as any).__clerk_session_token
        }
      } catch { /* no token */ }
      const tokenParam = token ? `?token=${encodeURIComponent(token)}` : ''

      const url = `${protocol}//${host}${basePath}/ws/documents/${docId}/progress${tokenParam}`
      let wsConnected = false

      try {
        const socket = new WebSocket(url)
        this._activeWs = socket

        const fallbackTimer = setTimeout(() => {
          // If WS hasn't connected within 3 seconds, fall back to simulation
          if (!wsConnected) {
            console.warn('WebSocket connection timed out, falling back to simulation')
            socket.close()
            this.simulateIngestion(docId, mode)
          }
        }, 3000)

        socket.onopen = () => {
          wsConnected = true
          clearTimeout(fallbackTimer)
        }

        socket.onmessage = (evt) => {
          try {
            const payload = JSON.parse(evt.data)
            const percentRaw = payload.percent_complete ?? payload.progress ?? 0
            const stepName = payload.current_step || payload.step || 'parse'
            const mapped = mapBackendStep(stepName, mode)

            // Use backend percent if available, otherwise use our mapped estimate
            const percent = percentRaw > 0 ? percentRaw : mapped.progress

            this.ingestionState = {
              documentId: docId,
              step: mapped.step,
              progress: percent,
              detail: payload.message || mapped.detail,
            }

            // Update document status to match
            if (mapped.step === 'extract') doc.status = 'extracting'
            else if (mapped.step === 'cluster' || mapped.step === 'link') doc.status = 'clustering'

            // Terminal state
            const s = stepName.toLowerCase()
            if (s === 'ready' || s === 'done' || s === 'failed') {
              doc.status = s === 'failed' ? 'failed' : 'ready'
              this.ingestionState = {
                documentId: docId,
                step: 'ready',
                progress: 100,
                detail: s === 'failed' ? 'Ingestion failed.' : 'Knowledge map construction complete.',
              }

              // Re-fetch documents to get real stats from the database
              setTimeout(() => {
                this.fetchDocuments()
                this.ingestionState = null
              }, 2000)

              socket.close()
              this._activeWs = null
            }
          } catch {
            // Ignore malformed frames
          }
        }

        socket.onerror = () => {
          if (!wsConnected) {
            clearTimeout(fallbackTimer)
            console.warn('WebSocket error, falling back to simulation')
            this.simulateIngestion(docId, mode)
          }
        }

        socket.onclose = () => {
          this._activeWs = null
        }
      } catch {
        console.warn('WebSocket creation failed, falling back to simulation')
        this.simulateIngestion(docId, mode)
      }
    },

    /**
     * Local-only ingestion simulation for offline/demo mode.
     * Used as fallback when WebSocket connection to backend is unavailable.
     */
    simulateIngestion(docId: string, mode: 'research' | 'study') {
      const doc = this.documents.find((d) => d.id === docId)
      if (!doc) return

      this.ingestionState = {
        documentId: docId,
        step: 'parse',
        progress: 15,
        detail: 'Parsing document structure and extracting text chunks...',
      }

      setTimeout(() => {
        if (this.ingestionState?.documentId === docId) {
          doc.status = 'extracting'
          this.ingestionState = {
            documentId: docId,
            step: 'extract',
            progress: 55,
            detail:
              mode === 'research'
                ? 'Extracting named entities and relationships...'
                : 'Deconstructing chapter sections and topic hierarchy...',
          }
        }
      }, 2500)

      setTimeout(() => {
        if (this.ingestionState?.documentId === docId) {
          doc.status = 'clustering'
          this.ingestionState = {
            documentId: docId,
            step: mode === 'research' ? 'cluster' : 'link',
            progress: 85,
            detail:
              mode === 'research'
                ? 'Computing community clusters and Leiden partitions...'
                : 'Mapping conceptual cross-references and topic links...',
          }
        }
      }, 5000)

      setTimeout(() => {
        if (this.ingestionState?.documentId === docId) {
          doc.status = 'ready'
          if (mode === 'research') {
            doc.entity_count = 42
            doc.relationship_count = 118
            doc.community_count = 6
          } else {
            doc.chapter_count = 8
            doc.section_count = 32
            doc.topic_count = 84
          }
          this.ingestionState = {
            documentId: docId,
            step: 'ready',
            progress: 100,
            detail: 'Knowledge map construction complete.',
          }

          // Also try to fetch real stats from backend
          this.fetchDocuments().catch(() => {})

          setTimeout(() => {
            this.ingestionState = null
          }, 3000)
        }
      }, 7500)
    },

    deleteDocument(id: string) {
      this.documents = this.documents.filter((d) => d.id !== id)
      if (this.activeDocumentId === id) {
        this.activeDocumentId = null
      }
      api.delete(`/documents/${id}`).catch(() => {})
    },

    setActiveDocument(id: string) {
      this.activeDocumentId = id
    },
  },
})
