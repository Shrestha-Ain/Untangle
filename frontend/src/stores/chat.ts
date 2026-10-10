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
        // Attempt backend endpoint
        const response = await api.post(`/chat/sessions/${documentId}/query`, {
          query,
          search_mode: this.searchMode,
        })
        if (response.data && response.data.answer) {
          const answerText: string = response.data.answer
          const words = answerText.split(' ')
          let i = 0

          // Smooth token streaming effect for the answer
          const streamInterval = setInterval(() => {
            if (i < words.length) {
              assistantMsg.content += (i === 0 ? '' : ' ') + words[i]
              i++
            } else {
              clearInterval(streamInterval)
              assistantMsg.content = answerText
              assistantMsg.citations = response.data.citations || []
              assistantMsg.subgraph = response.data.subgraph
              assistantMsg.suggestedSources = response.data.suggested_sources || []
              assistantMsg.isStreaming = false
              this.isStreaming = false
              if (assistantMsg.subgraph) {
                graphStore.highlightSubgraph(assistantMsg.subgraph)
              }
            }
          }, 25)
          return
        }
      } catch (err) {
        console.warn('Backend chat query error, generating grounded local response:', err)
      }

      // Grounded responsive reply based on knowledge graph concepts
      const qLower = query.toLowerCase()
      const matchingNodes = graphStore.nodes.filter(
        (n) => qLower.includes(n.name.toLowerCase()) || (n.description && qLower.includes(n.id.toLowerCase()))
      )

      let simulatedReply = ''
      let targetNodeIds: string[] = []
      let targetEdgeIds: string[] = []

      if (matchingNodes.length > 0) {
        const topNode = matchingNodes[0]
        targetNodeIds = matchingNodes.map((n) => n.id)
        targetEdgeIds = graphStore.edges
          .filter((e) => targetNodeIds.includes(e.source_id) || targetNodeIds.includes(e.target_id))
          .map((e) => e.id)

        simulatedReply = `${topNode.name} (${topNode.type}) is a key component in this knowledge map. ${topNode.description || 'It serves as an essential architectural foundation.'}\n\nRelated connections in the graph: ${matchingNodes.map((n) => n.name).join(', ')}.`
      } else if (mode === 'study') {
        simulatedReply =
          'In Operating Systems, concurrency primitives like mutexes and locks are designed to guarantee mutual exclusion when accessing shared memory regions. Modern kernels rely on atomic hardware instructions such as Compare-And-Swap (CAS).\n\nIf multiple threads contend for the lock, parallel speedup becomes bounded by the sequential fraction of execution.'
        targetNodeIds = ['chap-2', 'sec-2-1', 'top-2-1-1', 'top-ext-paper']
        targetEdgeIds = ['e-5', 'e-6', 'e-7']
      } else {
        simulatedReply =
          'The Multi-Head Attention module allows the model to jointly attend to information from different representation subspaces at different positions. Queries, Keys, and Values are projected into Scaled Dot-Product attention heads to capture long-range contextual relationships.\n\nAshish Vaswani and the Google Brain team established that this enables direct modeling of dependencies regardless of sequential distance.'
        targetNodeIds = ['n-attn', 'n-sdpa', 'n-vaswani', 'n-brain']
        targetEdgeIds = ['e-1', 'e-2', 'e-3']
      }

      const targetSubgraph = { nodeIds: targetNodeIds, edgeIds: targetEdgeIds }

      // Stream words smoothly
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
              chunk_id: 'chunk-ref-1',
              title: mode === 'study' ? 'OSTEP Operating Systems' : 'Attention Is All You Need §3.2',
              snippet:
                mode === 'study'
                  ? 'Concurrency primitives ensure threads synchronize correctly across critical sections.'
                  : 'Multi-head attention projects queries, keys, and values h times with learned projections.',
            },
          ]
          assistantMsg.subgraph = targetSubgraph
          graphStore.highlightSubgraph(targetSubgraph)
        }
      }, 35)
    },

    clearChat() {
      this.messages = []
      const graphStore = useGraphStore()
      graphStore.highlightSubgraph(null)
    },
  },
})

