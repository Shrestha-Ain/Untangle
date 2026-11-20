import { defineStore } from 'pinia'
import { useGraphStore } from '@/stores/graph'

export interface TopicProgressItem {
  id: string
  name: string
  type: string
  stepIndex: number
  isCompleted: boolean
  percentageWeight: number
}

export const useProgressStore = defineStore('progress', {
  state: () => ({
    // Set of completed topic/node IDs mapped by documentId
    completedByDoc: {} as Record<string, string[]>,
    isProgressModalOpen: false,
  }),

  getters: {
    /**
     * Array of completed topic IDs for the current active document.
     */
    currentDocCompletedIds(): string[] {
      const graphStore = useGraphStore()
      const docId = graphStore.currentDocumentId || 'doc-attention-1706'
      return this.completedByDoc[docId] || []
    },

    /**
     * Total number of topics in the learning path.
     */
    totalTopics(): number {
      const graphStore = useGraphStore()
      return graphStore.learningPath.length || graphStore.nodes.length || 1
    },

    /**
     * Overall percentage of curriculum / paper completed (0 to 100%).
     */
    completionPercentage(): number {
      if (this.totalTopics === 0) return 0
      const completedCount = this.currentDocCompletedIds.length
      const pct = Math.round((completedCount / this.totalTopics) * 100)
      return Math.min(100, Math.max(0, pct))
    },

    /**
     * Detailed topic breakdown list with completion status and relative weight.
     */
    topicBreakdown(): TopicProgressItem[] {
      const graphStore = useGraphStore()
      const completedSet = new Set(this.currentDocCompletedIds)
      const list = graphStore.learningPath.length > 0 ? graphStore.learningPath : graphStore.nodes.map((n) => n.id)
      const total = list.length || 1
      const weightPerTopic = Number((100 / total).toFixed(1))

      return list.map((id, idx) => {
        const node = graphStore.nodes.find((n) => n.id === id)
        return {
          id,
          name: node?.name || id,
          type: node?.type || 'CONCEPT',
          stepIndex: idx + 1,
          isCompleted: completedSet.has(id),
          percentageWeight: weightPerTopic,
        }
      })
    },

    /**
     * List of topics that have been mastered.
     */
    completedTopics(): TopicProgressItem[] {
      return this.topicBreakdown.filter((t) => t.isCompleted)
    },

    /**
     * List of upcoming / remaining topics to study.
     */
    remainingTopics(): TopicProgressItem[] {
      return this.topicBreakdown.filter((t) => !t.isCompleted)
    },

    /**
     * Checks if a specific topic is completed.
     */
    isTopicCompleted: (state) => (topicId: string): boolean => {
      const graphStore = useGraphStore()
      const docId = graphStore.currentDocumentId || 'doc-attention-1706'
      const list = state.completedByDoc[docId] || []
      return list.includes(topicId)
    },
  },

  actions: {
    /**
     * Loads persisted progress from localStorage.
     */
    initProgress() {
      try {
        const raw = localStorage.getItem('untangle_study_progress')
        if (raw) {
          this.completedByDoc = JSON.parse(raw)
        }
      } catch (e) {
        console.warn('Failed to load study progress from localStorage', e)
      }
    },

    /**
     * Persists current state to localStorage.
     */
    saveProgress() {
      try {
        localStorage.setItem('untangle_study_progress', JSON.stringify(this.completedByDoc))
      } catch (e) {
        console.warn('Failed to save study progress to localStorage', e)
      }
    },

    /**
     * Toggles a topic's completion status.
     */
    toggleTopicCompletion(topicId: string, docIdOverride?: string) {
      const graphStore = useGraphStore()
      const docId = docIdOverride || graphStore.currentDocumentId || 'doc-attention-1706'

      if (!this.completedByDoc[docId]) {
        this.completedByDoc[docId] = []
      }

      const list = this.completedByDoc[docId]
      const idx = list.indexOf(topicId)
      if (idx !== -1) {
        list.splice(idx, 1)
      } else {
        list.push(topicId)
      }

      this.saveProgress()
    },

    /**
     * Marks a topic explicitly as completed.
     */
    markTopicCompleted(topicId: string, docIdOverride?: string) {
      const graphStore = useGraphStore()
      const docId = docIdOverride || graphStore.currentDocumentId || 'doc-attention-1706'

      if (!this.completedByDoc[docId]) {
        this.completedByDoc[docId] = []
      }

      const list = this.completedByDoc[docId]
      if (!list.includes(topicId)) {
        list.push(topicId)
        this.saveProgress()
      }
    },

    /**
     * Marks the currently selected path step as completed.
     */
    markCurrentStepCompleted() {
      const graphStore = useGraphStore()
      const currentId = graphStore.currentPathNodeId
      if (currentId) {
        this.markTopicCompleted(currentId)
      }
    },

    /**
     * Clears progress for the current document.
     */
    resetProgress(docIdOverride?: string) {
      const graphStore = useGraphStore()
      const docId = docIdOverride || graphStore.currentDocumentId || 'doc-attention-1706'
      this.completedByDoc[docId] = []
      this.saveProgress()
    },

    openProgressModal() {
      this.isProgressModalOpen = true
    },

    closeProgressModal() {
      this.isProgressModalOpen = false
    },
  },
})
