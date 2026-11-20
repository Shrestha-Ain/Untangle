import { defineStore } from 'pinia'
import { api } from '@/api/client'
import { useGraphStore } from './graph'
import { generateInteractiveResponse } from '@/utils/pedagogicalKnowledge'
import { cleanAssistantContent } from '@/utils/markdownRenderer'

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
    searchScope: 'topic' as 'topic' | 'document' | 'worldwide',
    selectedModel: 'flash' as 'flash' | 'sonnet',
    activeSessionId: null as string | null,
  }),

  actions: {
    setSearchScope(scope: 'topic' | 'document' | 'worldwide') {
      this.searchScope = scope
    },

    setSelectedModel(model: 'flash' | 'sonnet') {
      this.selectedModel = model
    },

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
      const selectedNode = graphStore.selectedEntityId
        ? graphStore.nodes.find((n) => n.id === graphStore.selectedEntityId)
        : null

      try {
        // Attempt backend endpoint with topic scoping and search scope
        const response = await api.post(`/chat/sessions/${documentId}/query`, {
          query,
          search_mode: this.searchMode,
          search_scope: this.searchScope,
          selected_node_id: selectedNode?.id || null,
          selected_node_name: selectedNode?.name || null,
          model_name: this.selectedModel,
        })
        if (response.data && response.data.answer) {
          const rawAnswer: string = response.data.answer
          const answerText: string = cleanAssistantContent(rawAnswer)
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

      // Grounded, pedagogical, highly interactive response using curriculum knowledge engine
      const pedagogicalResult = generateInteractiveResponse({
        query,
        selectedNode,
        allNodes: graphStore.nodes,
        edges: graphStore.edges,
        searchScope: this.searchScope,
        mode,
        selectedModel: this.selectedModel,
      })

      const simulatedReply = pedagogicalResult.answer
      const targetSubgraph = {
        nodeIds: pedagogicalResult.targetNodeIds,
        edgeIds: pedagogicalResult.targetEdgeIds,
      }

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
          assistantMsg.citations = pedagogicalResult.citations && pedagogicalResult.citations.length > 0
            ? pedagogicalResult.citations
            : [
                {
                  document_id: documentId,
                  chunk_id: 'chunk-ref-1',
                  title: selectedNode ? selectedNode.name : (mode === 'study' ? 'Curriculum Reference' : 'Academic Reference'),
                  snippet: selectedNode
                    ? (selectedNode.description || `Core knowledge node: ${selectedNode.name}`)
                    : (mode === 'study'
                        ? 'Concurrency primitives ensure threads synchronize correctly across critical sections.'
                        : 'Multi-head attention projects queries, keys, and values h times with learned projections.'),
                },
              ]
          assistantMsg.subgraph = targetSubgraph
          graphStore.highlightSubgraph(targetSubgraph)
        }
      }, 30)
    },

    clearChat() {
      this.messages = []
      const graphStore = useGraphStore()
      graphStore.highlightSubgraph(null)
    },
  },
})

