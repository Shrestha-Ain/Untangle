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
          this.documents = data
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

      // Simulate ingestion progression if offline, or trigger backend API
      this.simulateIngestion(tempId, mode)

      try {
        if (file) {
          const formData = new FormData()
          formData.append('file', file)
          formData.append('source_mode', mode)
          const res = await api.post('/documents/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          })
          if (res.data?.id) {
            newDoc.id = res.data.id
            this.activeDocumentId = res.data.id
            if (this.ingestionState) {
              this.ingestionState.documentId = res.data.id
            }
          }
        }
      } catch (e) {
        console.warn('Backend upload skipped (mock mode active):', e)
      }
    },

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

