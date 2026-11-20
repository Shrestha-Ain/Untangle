import { defineStore } from 'pinia'
import { useGraphStore } from './graph'

const STORAGE_KEY = 'untangle_user_notes_v1'

export interface DocumentNotesState {
  docNotes: string
  topicNotes: Record<string, string>
  lastUpdated: string
}

export const useNotesStore = defineStore('notes', {
  state: () => ({
    isOpen: false,
    activeTab: 'topic' as 'topic' | 'document',
    notesByDoc: {} as Record<string, DocumentNotesState>,
  }),

  actions: {
    initNotes() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY)
        if (raw) {
          this.notesByDoc = JSON.parse(raw)
        }
      } catch (err) {
        console.warn('Could not read notes from localStorage:', err)
      }
    },

    saveToStorage() {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.notesByDoc))
      } catch (err) {
        console.warn('Could not persist notes to localStorage:', err)
      }
    },

    ensureDocState(docId: string): DocumentNotesState {
      if (!this.notesByDoc[docId]) {
        this.notesByDoc[docId] = {
          docNotes: '',
          topicNotes: {},
          lastUpdated: new Date().toISOString(),
        }
      }
      return this.notesByDoc[docId]
    },

    openNotes(tab: 'topic' | 'document' = 'topic') {
      this.initNotes()
      this.activeTab = tab
      this.isOpen = true
    },

    closeNotes() {
      this.isOpen = false
    },

    getTopicNote(docId: string, nodeId: string): string {
      this.initNotes()
      const state = this.notesByDoc[docId]
      return state?.topicNotes[nodeId] || ''
    },

    setTopicNote(docId: string, nodeId: string, content: string) {
      const state = this.ensureDocState(docId)
      state.topicNotes[nodeId] = content
      state.lastUpdated = new Date().toISOString()
      this.saveToStorage()
    },

    getDocNote(docId: string): string {
      this.initNotes()
      const state = this.notesByDoc[docId]
      return state?.docNotes || ''
    },

    setDocNote(docId: string, content: string) {
      const state = this.ensureDocState(docId)
      state.docNotes = content
      state.lastUpdated = new Date().toISOString()
      this.saveToStorage()
    },

    exportNotesAsMarkdown(docId: string, docTitle?: string) {
      const graphStore = useGraphStore()
      const state = this.ensureDocState(docId)
      const title = docTitle || graphStore.currentDocumentTitle || 'Document'

      let md = `# Study Notes: ${title}\n`
      md += `*Exported from Untangle Knowledge Platform on ${new Date().toLocaleDateString()}*\n\n`

      md += `## 📚 Overall Document Notes\n`
      md += `${state.docNotes || '*(No overall notes recorded)*'}\n\n`
      md += `---\n\n`

      md += `## 📌 Topic-Specific Notes\n\n`
      const topicEntries = Object.entries(state.topicNotes)
      if (topicEntries.length === 0) {
        md += `*(No topic notes recorded)*\n`
      } else {
        for (const [nodeId, noteText] of topicEntries) {
          const node = graphStore.nodes.find((n) => n.id === nodeId)
          const nodeName = node?.name || nodeId
          md += `### ${nodeName} (${node?.type || 'Topic'})\n`
          md += `${noteText}\n\n`
        }
      }

      // Trigger browser file download
      const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `untangle_notes_${docId.slice(0, 8)}.md`
      a.click()
      URL.revokeObjectURL(url)
    },
  },
})
