<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useNotesStore } from '@/stores/notes'
import { useGraphStore } from '@/stores/graph'

const props = defineProps<{
  documentId: string
}>()

const notesStore = useNotesStore()
const graphStore = useGraphStore()

const textareaRef = ref<HTMLTextAreaElement | null>(null)

const activeNode = computed(() => {
  if (!graphStore.selectedEntityId) {
    return graphStore.nodes[0] || null
  }
  return graphStore.nodes.find((n) => n.id === graphStore.selectedEntityId) || null
})

const topicContent = ref('')
const docContent = ref('')

// Load note content whenever drawer opens or active topic changes
function syncNotes() {
  if (props.documentId) {
    if (activeNode.value) {
      topicContent.value = notesStore.getTopicNote(props.documentId, activeNode.value.id)
    }
    docContent.value = notesStore.getDocNote(props.documentId)
  }
}

watch(
  () => [notesStore.isOpen, activeNode.value?.id],
  () => {
    if (notesStore.isOpen) {
      syncNotes()
    }
  },
  { immediate: true }
)

function onTopicInput() {
  if (activeNode.value && props.documentId) {
    notesStore.setTopicNote(props.documentId, activeNode.value.id, topicContent.value)
  }
}

function onDocInput() {
  if (props.documentId) {
    notesStore.setDocNote(props.documentId, docContent.value)
  }
}

function insertMarkdown(prefix: string, suffix: string = '') {
  const el = textareaRef.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const currentVal = notesStore.activeTab === 'topic' ? topicContent.value : docContent.value
  const selectedText = currentVal.substring(start, end)
  const replacement = `${prefix}${selectedText || 'text'}${suffix}`

  const updated = currentVal.substring(0, start) + replacement + currentVal.substring(end)
  if (notesStore.activeTab === 'topic') {
    topicContent.value = updated
    onTopicInput()
  } else {
    docContent.value = updated
    onDocInput()
  }

  setTimeout(() => {
    el.focus()
    el.setSelectionRange(start + prefix.length, start + replacement.length - suffix.length)
  }, 50)
}

function handleExport() {
  notesStore.exportNotesAsMarkdown(props.documentId, graphStore.currentDocumentTitle || undefined)
}
</script>

<template>
  <div
    v-if="notesStore.isOpen"
    class="fixed inset-y-0 right-0 z-40 w-full sm:w-[460px] bg-white shadow-2xl border-l border-slate-200 flex flex-col transition-all duration-300 select-none pointer-events-auto"
  >
    <!-- Drawer Header -->
    <div class="px-5 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-xl bg-amber-600 text-white flex items-center justify-center font-bold text-base shadow-sm">
          <span class="material-symbols-outlined text-lg">edit_note</span>
        </div>
        <div>
          <h3 class="text-xs font-extrabold text-slate-800">
            Personal Study Notes
          </h3>
          <p class="text-[10.5px] text-slate-500">
            Auto-saved locally for this document
          </p>
        </div>
      </div>

      <div class="flex items-center gap-1.5">
        <button
          @click="handleExport"
          class="px-2.5 py-1 rounded-lg bg-slate-200/80 hover:bg-slate-300 text-slate-700 font-mono text-[11px] font-bold transition-all flex items-center gap-1"
          title="Export notes as Markdown (.md)"
        >
          <span class="material-symbols-outlined text-xs">download</span>
          <span>Export .md</span>
        </button>

        <button
          @click="notesStore.closeNotes"
          class="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-colors"
        >
          <span class="material-symbols-outlined text-base">close</span>
        </button>
      </div>
    </div>

    <!-- Tab Switcher (Topic Note vs Document Note) -->
    <div class="px-5 py-2.5 bg-slate-100/60 border-b border-slate-200 flex items-center gap-2 text-xs">
      <button
        @click="notesStore.activeTab = 'topic'"
        class="flex-1 py-1.5 px-3 rounded-xl font-bold transition-all flex items-center justify-center gap-1.5 truncate"
        :class="[
          notesStore.activeTab === 'topic'
            ? 'bg-white text-slate-800 shadow-xs border border-slate-200/80'
            : 'text-slate-500 hover:text-slate-800',
        ]"
      >
        <span>📌</span>
        <span class="truncate">
          {{ activeNode ? activeNode.name : 'Topic Note' }}
        </span>
      </button>

      <button
        @click="notesStore.activeTab = 'document'"
        class="flex-1 py-1.5 px-3 rounded-xl font-bold transition-all flex items-center justify-center gap-1.5"
        :class="[
          notesStore.activeTab === 'document'
            ? 'bg-white text-slate-800 shadow-xs border border-slate-200/80'
            : 'text-slate-500 hover:text-slate-800',
        ]"
      >
        <span>📚</span>
        <span>General PDF Notes</span>
      </button>
    </div>

    <!-- Active Topic Info Bar (when on Topic Tab) -->
    <div
      v-if="notesStore.activeTab === 'topic' && activeNode"
      class="px-5 py-2 bg-amber-50/70 border-b border-amber-200/60 flex items-center justify-between text-[11px]"
    >
      <div class="flex items-center gap-1.5 text-amber-900 font-medium truncate">
        <span class="text-xs">🎯</span>
        <span>Linked to Tower:</span>
        <strong class="truncate">{{ activeNode.name }}</strong>
        <span class="text-[9.5px] px-1 rounded bg-amber-200/80 text-amber-900 font-mono uppercase">
          {{ activeNode.type }}
        </span>
      </div>
    </div>

    <!-- Markdown Helper Formatting Toolbar -->
    <div class="px-4 py-2 bg-slate-50 border-b border-slate-200 flex items-center gap-1 text-slate-600 text-xs">
      <button
        @click="insertMarkdown('**', '**')"
        class="w-7 h-7 rounded hover:bg-slate-200 font-bold flex items-center justify-center transition-colors"
        title="Bold (**text**)"
      >
        B
      </button>
      <button
        @click="insertMarkdown('*', '*')"
        class="w-7 h-7 rounded hover:bg-slate-200 italic font-serif flex items-center justify-center transition-colors"
        title="Italic (*text*)"
      >
        I
      </button>
      <button
        @click="insertMarkdown('• ')"
        class="w-7 h-7 rounded hover:bg-slate-200 flex items-center justify-center transition-colors"
        title="Bullet Point (• )"
      >
        •
      </button>
      <button
        @click="insertMarkdown('`', '`')"
        class="w-7 h-7 rounded hover:bg-slate-200 font-mono text-[11px] flex items-center justify-center transition-colors"
        title="Inline Code (`code`)"
      >
        &lt;&gt;
      </button>
      <button
        @click="insertMarkdown('⚠️ **Exam Note:** ')"
        class="w-7 h-7 rounded hover:bg-slate-200 text-amber-600 flex items-center justify-center transition-colors"
        title="Insert Exam Note Warning"
      >
        ⚠️
      </button>

      <span class="ml-auto text-[10px] text-slate-400 font-mono flex items-center gap-1">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        <span>Auto-saving</span>
      </span>
    </div>

    <!-- Note Textarea -->
    <div class="flex-1 p-5 flex flex-col">
      <textarea
        v-if="notesStore.activeTab === 'topic'"
        ref="textareaRef"
        v-model="topicContent"
        @input="onTopicInput"
        :placeholder="`Write your personal notes for ${activeNode ? activeNode.name : 'this topic'}...\n\n• Key formulas or invariants\n• Intuitive analogies\n• Exam pitfalls to remember`"
        class="w-full flex-1 p-3.5 rounded-2xl border border-slate-200 bg-white text-xs text-slate-800 placeholder-slate-400 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 font-mono leading-relaxed resize-none shadow-2xs"
      ></textarea>

      <textarea
        v-else
        ref="textareaRef"
        v-model="docContent"
        @input="onDocInput"
        placeholder="Write high-level document notes, comprehensive formulas, and cheat-sheet summaries for the entire paper or textbook..."
        class="w-full flex-1 p-3.5 rounded-2xl border border-slate-200 bg-white text-xs text-slate-800 placeholder-slate-400 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 font-mono leading-relaxed resize-none shadow-2xs"
      ></textarea>
    </div>

    <!-- Drawer Footer -->
    <div class="px-5 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-[11px] text-slate-500">
      <span class="font-mono">
        {{ (notesStore.activeTab === 'topic' ? topicContent : docContent).length }} characters
      </span>
      <span class="text-[10.5px] text-slate-400">
        Markdown supported
      </span>
    </div>
  </div>
</template>
