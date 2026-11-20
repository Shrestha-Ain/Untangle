<script setup lang="ts">
import { ref, watch, computed, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useGraphStore } from '@/stores/graph'
import { renderMarkdown } from '@/utils/markdownRenderer'
import { useDraggableResizable } from '@/composables/useDraggableResizable'

const props = defineProps<{
  documentId: string
  mode: 'research' | 'study'
}>()

const chatStore = useChatStore()
const graphStore = useGraphStore()
const queryInput = ref('')
const isExpanded = ref(false)
const scrollContainer = ref<HTMLDivElement | null>(null)
const expandedCitations = ref<Record<string, boolean>>({})

const selectedNode = computed(() => {
  if (!graphStore.selectedEntityId) return null
  return graphStore.nodes.find((n) => n.id === graphStore.selectedEntityId) || null
})

const suggestedQuestions = computed(() => {
  if (selectedNode.value) {
    const name = selectedNode.value.name
    return [
      { text: `Explain ${name} using a simple analogy`, icon: '💡', tag: 'Analogy' },
      { text: `How does ${name} work step-by-step?`, icon: '⚙️', tag: 'Mechanism' },
      { text: `What are the key prerequisites for ${name}?`, icon: '🔗', tag: 'Roadmap' },
      { text: `What are common exam traps for ${name}?`, icon: '⚠️', tag: 'Exam Trap' },
    ]
  }

  if (props.mode === 'study') {
    return [
      { text: 'Explain Process Virtualization and the fork-exec pattern', icon: '⚡', tag: 'Process API' },
      { text: 'What is the difference between a Process and a Thread?', icon: '🧵', tag: 'Concurrency' },
      { text: 'How does Compare-And-Swap build lock-free primitives?', icon: '🔒', tag: 'Locks' },
      { text: 'Why does Amdahl\'s Law limit multicore speedup?', icon: '📐', tag: 'Performance' },
    ]
  }

  return [
    { text: 'How does Scaled Dot-Product Attention compute scores?', icon: '⚡', tag: 'Attention' },
    { text: 'Why is Positional Encoding necessary for Transformers?', icon: '📐', tag: 'Encoding' },
    { text: 'What is the advantage of Multi-Head Attention over single-head?', icon: '🧠', tag: 'MHA' },
    { text: 'How does this architecture compare to BERT and modern LLMs?', icon: '🌐', tag: 'Industry' },
  ]
})

function handleQuickQuestion(qText: string) {
  if (chatStore.isStreaming) return
  isExpanded.value = true
  queryInput.value = qText
  handleSend()
}

function toggleCitation(msgId: string) {
  expandedCitations.value[msgId] = !expandedCitations.value[msgId]
}

function clearTowerFocus() {
  graphStore.selectEntity(null)
  chatStore.setSearchScope('document')
}

async function handleSend() {
  const q = queryInput.value.trim()
  if (!q || chatStore.isStreaming) return
  isExpanded.value = true
  queryInput.value = ''
  await chatStore.sendMessage(q, props.documentId, props.mode)
}

// Draggable & Resizable window setup for expanded AI Chat
const {
  style,
  onDragStart,
  onResizeStart,
  resetPlacement,
  isDragging,
  isCustomPositioned,
} = useDraggableResizable({
  initialWidth: 540,
  initialHeight: 520,
  minWidth: 380,
  maxWidth: 920,
  minHeight: 320,
  maxHeight: 860,
  defaultPlacement: 'bottom-left',
  storageKey: 'regulus_chat',
})

watch(
  () => chatStore.messages.length,
  async () => {
    await nextTick()
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  }
)
</script>

<template>
  <!-- 1. Collapsed Floating Dock Capsule (Does NOT hide the map!) -->
  <div
    v-if="!isExpanded"
    @click="isExpanded = true"
    class="fixed bottom-4 left-4 z-20 flex items-center gap-3 px-4 py-2.5 bg-white/95 backdrop-blur-xl rounded-2xl border border-slate-200 shadow-[0_8px_32px_rgba(15,23,42,0.12)] hover:border-teal-500 hover:shadow-[0_12px_36px_rgba(13,148,136,0.24)] cursor-pointer select-none transition-all duration-200 group active:scale-[0.98]"
  >
    <div class="w-8 h-8 rounded-xl bg-[#10B981] text-white font-black text-sm flex items-center justify-center shadow-xs group-hover:scale-105 transition-transform">
      R
    </div>
    <div class="flex flex-col text-left">
      <div class="flex items-center gap-1.5">
        <span class="text-xs font-black text-[#1C1B18]">Regulus AI Guide</span>
        <span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold">
          {{ mode === 'study' ? 'Curriculum' : 'Copilot' }}
        </span>
      </div>
      <span class="text-[10px] text-slate-500 font-medium truncate max-w-[210px]">
        {{ selectedNode ? `Ask about ${selectedNode.name}` : 'Click to ask questions or view topics' }}
      </span>
    </div>
    <div class="ml-1 px-2.5 py-1 rounded-xl bg-emerald-50 text-emerald-700 text-[11px] font-bold flex items-center gap-1 border border-emerald-200 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
      <span>💬 Chat</span>
      <span class="material-symbols-outlined text-sm">expand_less</span>
    </div>
  </div>

  <!-- 2. Expanded Movable & Resizable Interactive Chat Window -->
  <div
    v-else
    :style="style"
    class="bg-white/95 dark:bg-[#0F172A]/95 backdrop-blur-2xl rounded-3xl border border-slate-200 dark:border-slate-800 shadow-[0_20px_50px_rgba(15,23,42,0.18)] flex flex-col overflow-hidden animate-in fade-in select-none relative transition-colors"
    :class="[
      isDragging ? 'shadow-2xl scale-[1.01]' : '',
    ]"
  >
    <!-- Top Header Bar (Acts as Drag Grip) -->
    <div
      class="px-4 py-3 bg-[#F0F4F8] dark:bg-[#111C35] border-b border-slate-200 dark:border-slate-800 flex items-center justify-between cursor-move select-none relative group/chatdrag"
      @mousedown="onDragStart"
      @touchstart="onDragStart"
      title="Drag to move chat window"
    >
      <!-- Dynamic hover popup tag (ONLY pops up on hover) -->
      <span class="absolute -top-7 left-3 pointer-events-none opacity-0 group-hover/chatdrag:opacity-100 transition-opacity px-2 py-0.5 rounded bg-slate-900 text-white text-[9px] font-mono shadow-md whitespace-nowrap z-50">
        ✋ Drag to move chat
      </span>

      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-xl bg-blue-600 text-white font-black text-sm flex items-center justify-center shadow-xs">
          R
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-black text-slate-900 dark:text-white">Regulus AI Guide</span>
            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 font-bold">
              {{ mode === 'study' ? 'Curriculum Engine' : 'Research Copilot' }}
            </span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-1.5 no-drag">
        <!-- Reset position button -->
        <button
          v-if="isCustomPositioned"
          @click.stop="resetPlacement"
          class="px-1.5 py-0.5 rounded text-[9.5px] font-mono font-bold bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 flex items-center gap-0.5 transition-colors border border-slate-200 dark:border-slate-700"
          title="Snap back to default dock placement"
        >
          <span class="material-symbols-outlined text-[13px]">restart_alt</span>
          <span>Reset</span>
        </button>

        <button
          @click.stop="chatStore.clearChat"
          class="text-[10px] font-medium text-slate-400 hover:text-slate-800 dark:hover:text-white px-2 py-1 rounded-lg hover:bg-white dark:hover:bg-slate-800 transition-colors"
          title="Clear Conversation"
        >
          Clear
        </button>

        <!-- Minimize button to reveal entire map -->
        <button
          @click.stop="isExpanded = false"
          class="px-2 py-1 rounded-lg bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold flex items-center gap-1 transition-colors border border-slate-200 dark:border-slate-700"
          title="Minimize chat to view complete map"
        >
          <span class="material-symbols-outlined text-sm">unfold_less</span>
          <span class="text-[10px]">Minimize</span>
        </button>
      </div>
    </div>

    <!-- Messages Container -->
    <div
      ref="scrollContainer"
      class="flex-1 p-4 overflow-y-auto space-y-4 regulus-scroll text-xs no-drag select-text"
    >
      <!-- Welcome Message & Suggested Questions if empty -->
      <div
        v-if="chatStore.messages.length === 0"
        class="py-3 space-y-3.5 text-center"
      >
        <div class="space-y-1 text-slate-400">
          <span class="material-symbols-outlined text-3xl text-blue-600 dark:text-blue-400">psychology</span>
          <p class="text-xs font-black text-slate-900 dark:text-white">
            {{ selectedNode ? `Focused on: ${selectedNode.name}` : `Regulus AI for this ${mode === 'study' ? 'Textbook' : 'Research Paper'}` }}
          </p>
          <p class="text-[11px] max-w-sm mx-auto text-slate-500 dark:text-slate-400">
            {{ selectedNode ? `Ask anything about ${selectedNode.name}, or click a recommended prompt below:` : 'Select any tower on the map to focus, or choose a prompt below:' }}
          </p>
        </div>

        <!-- Suggested Questions Grid (Interactive Clickable Cards) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left pt-1">
          <button
            v-for="(sq, idx) in suggestedQuestions"
            :key="idx"
            @click="handleQuickQuestion(sq.text)"
            :disabled="chatStore.isStreaming"
            class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/90 hover:border-blue-500 dark:hover:border-blue-500 hover:bg-blue-50/50 dark:hover:bg-slate-800 active:scale-[0.98] transition-all flex items-start gap-2 group shadow-2xs"
          >
            <span class="text-base shrink-0 mt-0.5">{{ sq.icon }}</span>
            <div class="min-w-0">
              <span class="text-[9px] font-mono font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider block">
                {{ sq.tag }}
              </span>
              <p class="text-[11px] text-slate-800 dark:text-slate-200 font-semibold leading-tight group-hover:text-blue-600 dark:group-hover:text-blue-300">
                {{ sq.text }}
              </p>
            </div>
          </button>
        </div>
      </div>

      <!-- Message History -->
      <div
        v-for="msg in chatStore.messages"
        :key="msg.id"
        class="space-y-2"
      >
        <!-- User bubble -->
        <div
          v-if="msg.role === 'user'"
          class="ml-auto max-w-[85%] bg-blue-600 text-white p-3 rounded-2xl rounded-tr-xs font-medium leading-relaxed text-xs shadow-xs"
        >
          {{ msg.content }}
        </div>

        <!-- Assistant bubble with Rich Markdown Parser -->
        <div
          v-else
          class="mr-auto max-w-[95%] bg-white dark:bg-[#0F172A] p-3.5 rounded-2xl rounded-tl-xs border border-slate-200 dark:border-slate-800 shadow-xs space-y-2 text-slate-900 dark:text-slate-100"
        >
          <!-- Structured Markdown Output -->
          <div
            class="leading-relaxed regulus-markdown-content"
            v-html="renderMarkdown(msg.content)"
          ></div>

          <!-- Streaming cursor -->
          <span
            v-if="msg.isStreaming"
            class="inline-block w-2 h-3.5 bg-blue-500 animate-pulse ml-0.5 rounded-xs"
          ></span>

          <!-- Citations / Clues Accordion -->
          <div
            v-if="msg.citations && msg.citations.length > 0"
            class="pt-2 border-t border-slate-100 dark:border-slate-800"
          >
            <button
              @click="toggleCitation(msg.id)"
              class="flex items-center gap-1.5 text-[11px] font-mono font-bold text-teal-700 dark:text-teal-400 hover:underline"
            >
              <span class="material-symbols-outlined text-xs">find_in_page</span>
              <span>Grounded Citations ({{ msg.citations.length }})</span>
              <span class="material-symbols-outlined text-xs">
                {{ expandedCitations[msg.id] ? 'expand_less' : 'expand_more' }}
              </span>
            </button>

            <div
              v-show="expandedCitations[msg.id]"
              class="mt-2 space-y-1.5 p-2.5 bg-slate-50 dark:bg-slate-800/80 rounded-lg border border-slate-200 dark:border-slate-700"
            >
              <div
                v-for="c in msg.citations"
                :key="c.chunk_id"
                class="space-y-0.5"
              >
                <div class="font-mono text-[10px] text-slate-500 dark:text-slate-400 font-bold">
                  {{ c.title ?? c.chunk_id }}
                </div>
                <p class="font-mono text-[10.5px] text-slate-600 dark:text-slate-300 italic bg-white dark:bg-slate-900 p-1.5 rounded border border-slate-200 dark:border-slate-700">
                  "{{ c.snippet }}"
                </p>
              </div>
            </div>
          </div>

          <!-- Suggested External Sources -->
          <div
            v-if="msg.suggestedSources && msg.suggestedSources.length > 0"
            class="mt-2 p-2.5 rounded-xl bg-amber-50/80 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 space-y-1.5"
          >
            <div class="flex items-center gap-1 text-[11px] font-bold text-amber-800 dark:text-amber-300">
              <span class="material-symbols-outlined text-sm">link</span>
              <span>Suggested External Context</span>
            </div>
            <div
              v-for="s in msg.suggestedSources"
              :key="s.id"
              class="space-y-1"
            >
              <p class="text-[11px] text-slate-900 dark:text-slate-100 font-bold">{{ s.title }}</p>
              <p class="text-[10px] text-slate-600 dark:text-slate-400">{{ s.reason }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Tower Focus Bar (if a node is selected) -->
    <div
      v-if="selectedNode"
      class="px-3.5 py-1.5 bg-blue-50/90 dark:bg-blue-950/60 border-t border-blue-200 dark:border-blue-800/80 flex items-center justify-between text-[11px] no-drag"
    >
      <div class="flex items-center gap-1.5 text-blue-900 dark:text-blue-200 font-medium truncate">
        <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
        <span>Local Focus:</span>
        <strong class="text-slate-900 dark:text-white truncate">{{ selectedNode.name }}</strong>
        <span class="text-[10px] px-1 rounded bg-blue-200 dark:bg-blue-800 text-blue-800 dark:text-blue-200 font-mono uppercase font-bold">
          {{ selectedNode.type }}
        </span>
      </div>
      <button
        @click="clearTowerFocus"
        class="text-[10px] text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white underline ml-2 shrink-0 font-bold"
        title="Unfocus tower and ask about whole document"
      >
        ✕ Clear Focus
      </button>
    </div>

    <!-- Scope & Model Control Bar -->
    <div
      class="px-3 py-2 bg-[#F0F4F8] dark:bg-[#111C35] border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-1 text-[10.5px] select-none no-drag"
    >
      <!-- Scope Selector Pills -->
      <div class="flex items-center gap-1 bg-slate-200/80 dark:bg-slate-800 p-0.5 rounded-xl border border-slate-300 dark:border-slate-700">
        <button
          @click="chatStore.setSearchScope('topic')"
          :class="[
            'px-2 py-0.5 rounded-lg font-medium transition-all flex items-center gap-1',
            chatStore.searchScope === 'topic'
              ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs font-bold'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
          ]"
          title="Focus specifically on the selected tower and its local context"
        >
          <span>🎯</span>
          <span>Topic Focus</span>
        </button>

        <button
          @click="chatStore.setSearchScope('document')"
          :class="[
            'px-2 py-0.5 rounded-lg font-medium transition-all flex items-center gap-1',
            chatStore.searchScope === 'document'
              ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs font-bold'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
          ]"
          title="Search across the entire document graph and verbatim text"
        >
          <span>📄</span>
          <span>Document RAG</span>
        </button>

        <button
          @click="chatStore.setSearchScope('worldwide')"
          :class="[
            'px-2 py-0.5 rounded-lg font-medium transition-all flex items-center gap-1',
            chatStore.searchScope === 'worldwide'
              ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs font-bold'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
          ]"
          title="Search worldwide scientific, engineering, and web knowledge"
        >
          <span>🌐</span>
          <span>Worldwide</span>
        </button>
      </div>

      <!-- Model Switcher Selector -->
      <div class="flex items-center gap-1 bg-slate-200/80 dark:bg-slate-800 p-0.5 rounded-xl border border-slate-300 dark:border-slate-700">
        <button
          @click="chatStore.setSelectedModel('flash')"
          :class="[
            'px-2 py-0.5 rounded-lg font-medium transition-all flex items-center gap-0.5',
            chatStore.selectedModel === 'flash'
              ? 'bg-blue-600 text-white shadow-xs font-bold'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
          ]"
          title="Fast low-latency inference"
        >
          <span>⚡</span>
          <span>Flash</span>
        </button>

        <button
          @click="chatStore.setSelectedModel('sonnet')"
          :class="[
            'px-2 py-0.5 rounded-lg font-medium transition-all flex items-center gap-0.5',
            chatStore.selectedModel === 'sonnet'
              ? 'bg-slate-900 dark:bg-slate-700 text-white shadow-xs font-bold'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white',
          ]"
          title="Deep reasoning & rigorous analysis"
        >
          <span>🧠</span>
          <span>Sonnet</span>
        </button>
      </div>
    </div>

    <!-- Quick Suggestion Chips Ribbon -->
    <div
      class="px-3 py-1.5 bg-[#F0F4F8]/80 dark:bg-[#111C35]/80 border-t border-slate-200 dark:border-slate-800 flex items-center gap-1.5 overflow-x-auto no-scrollbar text-[11px] no-drag"
    >
      <span class="text-[10px] font-mono text-slate-400 shrink-0 font-bold">Suggested:</span>
      <button
        v-for="(sq, idx) in suggestedQuestions"
        :key="idx"
        @click="handleQuickQuestion(sq.text)"
        :disabled="chatStore.isStreaming"
        class="shrink-0 px-2.5 py-1 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-slate-700 active:scale-95 transition-all flex items-center gap-1 shadow-2xs font-medium"
      >
        <span>{{ sq.icon }}</span>
        <span>{{ sq.tag }}</span>
      </button>
    </div>

    <!-- Input Bar -->
    <div
      class="p-3 bg-[#F0F4F8] dark:bg-[#111C35] border-t border-slate-200 dark:border-slate-800 flex items-center gap-2 no-drag"
    >
      <input
        v-model="queryInput"
        type="text"
        :placeholder="
          chatStore.searchScope === 'topic' && selectedNode
            ? `Ask about ${selectedNode.name}...`
            : chatStore.searchScope === 'worldwide'
            ? 'Search worldwide engineering knowledge...'
            : `Ask Regulus about this ${mode === 'study' ? 'textbook' : 'paper'}...`
        "
        class="flex-1 px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-inner"
        :disabled="chatStore.isStreaming"
        @keydown.enter="handleSend"
      />
      <button
        @click="handleSend"
        :disabled="chatStore.isStreaming || !queryInput.trim()"
        class="px-4 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl shadow-sm active:translate-y-px transition-all shrink-0"
      >
        Ask
      </button>
    </div>

    <!-- Resizing Handles -->
    <!-- Top Edge Resize -->
    <div
      @mousedown.stop="onResizeStart($event, 'n')"
      @touchstart.stop="onResizeStart($event, 'n')"
      class="absolute top-0 left-12 right-12 h-2 cursor-n-resize hover:bg-teal-400/30 transition-colors"
      title="Drag to resize height"
    ></div>

    <!-- Right Edge Resize -->
    <div
      @mousedown.stop="onResizeStart($event, 'e')"
      @touchstart.stop="onResizeStart($event, 'e')"
      class="absolute top-12 bottom-12 right-0 w-2.5 cursor-e-resize hover:bg-teal-400/30 transition-colors"
      title="Drag to resize width"
    ></div>

    <!-- Top-Right Corner Resize Grip -->
    <div
      @mousedown.stop="onResizeStart($event, 'ne')"
      @touchstart.stop="onResizeStart($event, 'ne')"
      class="absolute top-1.5 right-1.5 w-4 h-4 cursor-ne-resize flex items-center justify-center text-slate-300 hover:text-teal-600 transition-colors"
      title="Drag corner to resize"
    >
      <span class="text-[11px] leading-none select-none">⋰</span>
    </div>

    <!-- Bottom-Right Corner Resize Grip -->
    <div
      @mousedown.stop="onResizeStart($event, 'se')"
      @touchstart.stop="onResizeStart($event, 'se')"
      class="absolute bottom-1.5 right-1.5 w-4 h-4 cursor-se-resize flex items-center justify-center text-slate-300 hover:text-teal-600 transition-colors"
      title="Drag corner to resize"
    >
      <span class="text-[11px] leading-none select-none">⋱</span>
    </div>
  </div>
</template>

<style scoped>
.regulus-scroll::-webkit-scrollbar {
  width: 5px;
}
.regulus-scroll::-webkit-scrollbar-thumb {
  background: #CBD5E1;
  border-radius: 4px;
}
.regulus-scroll::-webkit-scrollbar-thumb:hover {
  background: #94A3B8;
}
</style>
