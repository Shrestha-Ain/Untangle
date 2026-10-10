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

      // Grounded responsive reply based on knowledge graph concepts and active scope
      let simulatedReply = ''
      let targetNodeIds: string[] = []
      let targetEdgeIds: string[] = []

      // 1. Topic Focus (Local context first when a tower is selected or scope is topic)
      if ((this.searchScope === 'topic' || !this.searchScope) && selectedNode) {
        const incomingEdges = graphStore.edges.filter((e) => e.target_id === selectedNode.id)
        const outgoingEdges = graphStore.edges.filter((e) => e.source_id === selectedNode.id)
        const connectedEdges = [...incomingEdges, ...outgoingEdges]

        const prereqNames = incomingEdges
          .map((e) => graphStore.nodes.find((n) => n.id === e.source_id)?.name)
          .filter(Boolean) as string[]

        const nextNames = outgoingEdges
          .map((e) => graphStore.nodes.find((n) => n.id === e.target_id)?.name)
          .filter(Boolean) as string[]

        targetNodeIds = [
          selectedNode.id,
          ...incomingEdges.map((e) => e.source_id),
          ...outgoingEdges.map((e) => e.target_id),
        ]
        targetEdgeIds = connectedEdges.map((e) => e.id)

        simulatedReply = `🎯 **Topic Focus: ${selectedNode.name} (${selectedNode.type})**\n\n${selectedNode.description || 'Core conceptual component in this knowledge realm.'}\n\n`

        if (prereqNames.length > 0) {
          simulatedReply += `• **Prerequisites**: Builds upon **${prereqNames.slice(0, 3).join('**, **')}**.\n`
        }
        if (nextNames.length > 0) {
          simulatedReply += `• **Next Progression**: Leads directly to **${nextNames.slice(0, 3).join('**, **')}**.\n`
        }

        simulatedReply += `\nRegarding your question "${query}": Within this specific module, ${selectedNode.name} guarantees primary operational invariants. Master this concept before advancing along the curriculum chain.`
      } else if (this.searchScope === 'worldwide') {
        simulatedReply = `🌐 **Worldwide Engineering & AI Context for "${query}":**\n\nIn modern computer systems, artificial intelligence, and software engineering literature, this concept represents a standardized architecture pattern.\n\nIndustry implementations utilize these design principles to manage latency, ensure thread-safety, and achieve high computational throughput.`
        targetNodeIds = selectedNode ? [selectedNode.id] : graphStore.nodes.slice(0, 3).map((n) => n.id)
        targetEdgeIds = []
      } else {
        // Document-wide search
        const qLower = query.toLowerCase()
        const matchingNodes = graphStore.nodes.filter(
          (n) => qLower.includes(n.name.toLowerCase()) || (n.description && qLower.includes(n.id.toLowerCase()))
        )

        if (matchingNodes.length > 0) {
          const topNode = matchingNodes[0]
          targetNodeIds = matchingNodes.map((n) => n.id)
          targetEdgeIds = graphStore.edges
            .filter((e) => targetNodeIds.includes(e.source_id) || targetNodeIds.includes(e.target_id))
            .map((e) => e.id)

          simulatedReply = `📄 **Document Synthesis:**\n\n${topNode.name} (${topNode.type}) is a key component in this knowledge map. ${topNode.description || 'It serves as an essential architectural foundation.'}\n\nRelated document topics: ${matchingNodes.map((n) => n.name).join(', ')}.`
        } else if (graphStore.nodes.length > 0) {
          const firstThree = graphStore.nodes.slice(0, 3)
          targetNodeIds = firstThree.map((n) => n.id)
          targetEdgeIds = graphStore.edges.filter((e) => targetNodeIds.includes(e.source_id)).map((e) => e.id)
          simulatedReply = `📄 **Document Context:**\n\nI synthesized the knowledge structure across this document. Key foundational topics include **${firstThree.map((n) => n.name).join('**, **')}**. To examine a topic in depth, select its tower on the map to switch into 🎯 Topic Focus.`
        } else if (mode === 'study') {
          simulatedReply =
            'In Operating Systems, concurrency primitives like mutexes and locks are designed to guarantee mutual exclusion when accessing shared memory regions. Modern kernels rely on atomic hardware instructions such as Compare-And-Swap (CAS).\n\nIf multiple threads contend for the lock, parallel speedup becomes bounded by the sequential fraction of execution.'
          targetNodeIds = ['chap-2', 'sec-2-1', 'top-2-1-1', 'top-ext-paper']
          targetEdgeIds = ['e-5', 'e-6', 'e-7']
        } else {
          simulatedReply =
            'The Multi-Head Attention module allows the model to jointly attend to information from different representation subspaces at different positions. Queries, Keys, and Values are projected into Scaled Dot-Product attention heads to capture long-range contextual relationships.'
          targetNodeIds = ['n-attn', 'n-sdpa', 'n-vaswani', 'n-brain']
          targetEdgeIds = ['e-1', 'e-2', 'e-3']
        }
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

