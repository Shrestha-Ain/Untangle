import { defineStore } from 'pinia'
import { api } from '@/api/client'
import { useGraphStore } from './graph'

export interface CitationItem {
  document_id: string
  chunk_id: string
  title?: string
  snippet?: string
}

export interface SourceSuggestion {
  id: string
  title: string
  relevance: number
  reason: string
  source_type: 'paper' | 'book'
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: CitationItem[]
  subgraph?: { nodeIds: string[]; edgeIds: string[] }
  suggestedSources?: SourceSuggestion[]
  timestamp: string
  isStreaming?: boolean
}

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [] as ChatMessage[],
    isStreaming: false,
    searchMode: 'local' as 'local' | 'global',
    activeSessionId: null as string | null,
  }),

  actions: {
    async sendMessage(query: string, documentId: string, mode: 'research' | 'study' = 'research') {
      const userMsg: ChatMessage = {
        id: 'msg-' + Date.now(),
        role: 'user',
        content: query,
        timestamp: new Date().toISOString(),
      }
      this.messages.push(userMsg)

      const assistantMsgId = 'asst-' + (Date.now() + 1)
      const assistantMsg: ChatMessage = {
        id: assistantMsgId,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        isStreaming: true,
      }
      this.messages.push(assistantMsg)
      this.isStreaming = true

      const graphStore = useGraphStore()

      try {
        // Attempt backend streaming / endpoint
        const response = await api.post(`/chat/sessions/${documentId}/query`, {
          query,
          search_mode: this.searchMode,
        })
        if (response.data) {
          assistantMsg.content = response.data.answer
          assistantMsg.citations = response.data.citations
          assistantMsg.subgraph = response.data.subgraph
          assistantMsg.suggestedSources = response.data.suggested_sources
          assistantMsg.isStreaming = false
          this.isStreaming = false
          if (assistantMsg.subgraph) {
            graphStore.highlightSubgraph(assistantMsg.subgraph)
          }
          return
        }
      } catch (err) {
        console.warn('Backend chat offline, simulating Regulus response:', err)
      }

      // Simulated streaming reply from Regulus
      let simulatedReply = ''
      let targetSubgraph = { nodeIds: [] as string[], edgeIds: [] as string[] }
      let suggestedSources: SourceSuggestion[] = []

      if (mode === 'study') {
        simulatedReply =
          'In Operating Systems, concurrency primitives like mutexes and locks are designed to guarantee mutual exclusion when accessing shared memory regions. Under the hood, modern kernels rely on atomic hardware instructions such as Compare-And-Swap (CAS).\n\nIf multiple threads contend for the lock, parallel speedup becomes bounded by the sequential fraction of execution.'
        targetSubgraph = {
          nodeIds: ['chap-2', 'sec-2-1', 'top-2-1-1', 'top-ext-paper'],
          edgeIds: ['e-5', 'e-6', 'e-7'],
        }
        suggestedSources = [
          {
            id: 'doc-amdahl-1967',
            title: 'Validity of the Single Processor Approach to Achieving Large Scale Computing Capabilities (Amdahl, 1967)',
            relevance: 94,
            reason: 'Formal mathematical proof for parallel speedup bounds referenced in this section.',
            source_type: 'paper',
          },
        ]
      } else {
        simulatedReply =
          'The Multi-Head Attention module allows the model to jointly attend to information from different representation subspaces at different positions. Instead of performing a single attention function, Queries, Keys, and Values are projected h times with parameter matrices into Scaled Dot-Product attention heads.\n\nAshish Vaswani and the Google Brain team established that this enables direct modeling of dependencies regardless of sequential distance.'
        targetSubgraph = {
          nodeIds: ['n-attn', 'n-sdpa', 'n-vaswani', 'n-brain'],
          edgeIds: ['e-1', 'e-2', 'e-3'],
        }
      }

      // Stream words
      const words = simulatedReply.split(' ')
      let i = 0
      const timer = setInterval(() => {
        if (i < words.length) {
          assistantMsg.content += (i === 0 ? '' : ' ') + words[i]
          i++
        } else {
          clearInterval(timer)
          assistantMsg.isStreaming = false
          this.isStreaming = false
          assistantMsg.citations = [
            {
              document_id: documentId,
              chunk_id: 'chunk-42',
              title: mode === 'study' ? 'OSTEP §28.4' : 'Attention Is All You Need §3.2.2',
              snippet:
                mode === 'study'
                  ? 'A lock is just a variable... its state indicates whether any thread holds the lock.'
                  : 'Multi-head attention allows the model to jointly attend to information...',
            },
          ]
          assistantMsg.subgraph = targetSubgraph
          assistantMsg.suggestedSources = suggestedSources
          graphStore.highlightSubgraph(targetSubgraph)
        }
      }, 45)
    },

    clearChat() {
      this.messages = []
      const graphStore = useGraphStore()
      graphStore.highlightSubgraph(null)
    },
  },
})

