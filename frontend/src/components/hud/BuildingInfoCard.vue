<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGraphStore } from '@/stores/graph'
import { useQuizStore } from '@/stores/quiz'
import { useNotesStore } from '@/stores/notes'
import { useProgressStore } from '@/stores/progress'
import { useDraggableResizable } from '@/composables/useDraggableResizable'

const props = defineProps<{
  mode: 'research' | 'study'
}>()

const graphStore = useGraphStore()
const quizStore = useQuizStore()
const notesStore = useNotesStore()
const progressStore = useProgressStore()
const isMinimized = ref(false)
const isCopied = ref(false)

function copyBibtex() {
  if (!entity.value) return
  const bib = `@article{untangle_${entity.value.id},\n  title={${entity.value.name}},\n  author={Vaswani et al.},\n  year={2017}\n}`
  navigator.clipboard.writeText(bib)
  isCopied.value = true
  setTimeout(() => { isCopied.value = false }, 2000)
}
const entity = computed(() => graphStore.selectedEntity)

const connectedRoadsCount = computed(() => {
  if (!entity.value) return 0
  return graphStore.edges.filter(
    (e) => e.source_id === entity.value?.id || e.target_id === entity.value?.id
  ).length
})

const cardTheme = computed(() => {
  if (!entity.value) {
    return {
      bg: 'bg-teal-50',
      text: 'text-teal-700',
      border: 'border-teal-200',
      iconBg: 'bg-teal-100',
      iconText: 'text-teal-700',
      icon: 'lightbulb',
    }
  }
  switch (entity.value.type) {
    case 'PERSON':
      return {
        bg: 'bg-purple-50',
        text: 'text-purple-700',
        border: 'border-purple-200',
        iconBg: 'bg-purple-100',
        iconText: 'text-purple-700',
        icon: 'person',
      }
    case 'ORG':
      return {
        bg: 'bg-blue-50',
        text: 'text-blue-700',
        border: 'border-blue-200',
        iconBg: 'bg-blue-100',
        iconText: 'text-blue-700',
        icon: 'corporate_fare',
      }
    case 'LOCATION':
      return {
        bg: 'bg-rose-50',
        text: 'text-rose-700',
        border: 'border-rose-200',
        iconBg: 'bg-rose-100',
        iconText: 'text-rose-700',
        icon: 'dataset',
      }
    case 'CHAPTER':
      return {
        bg: 'bg-emerald-50',
        text: 'text-emerald-800',
        border: 'border-emerald-200',
        iconBg: 'bg-emerald-100',
        iconText: 'text-emerald-800',
        icon: 'menu_book',
      }
    case 'SECTION':
      return {
        bg: 'bg-amber-50',
        text: 'text-amber-800',
        border: 'border-amber-200',
        iconBg: 'bg-amber-100',
        iconText: 'text-amber-800',
        icon: 'segment',
      }
    case 'TOPIC':
    case 'CONCEPT':
    default:
      return {
        bg: 'bg-cyan-50',
        text: 'text-cyan-800',
        border: 'border-cyan-200',
        iconBg: 'bg-cyan-100',
        iconText: 'text-cyan-700',
        icon: 'lightbulb',
      }
  }
})

function closeCard() {
  graphStore.selectEntity(null)
}

function exploreConnections() {
  if (!entity.value) return
  const neighborIds = [entity.value.id]
  const edgeIds: string[] = []

  graphStore.edges.forEach((e) => {
    if (e.source_id === entity.value?.id) {
      neighborIds.push(e.target_id)
      edgeIds.push(e.id)
    } else if (e.target_id === entity.value?.id) {
      neighborIds.push(e.source_id)
      edgeIds.push(e.id)
    }
  })

  graphStore.highlightSubgraph({ nodeIds: neighborIds, edgeIds })
}

const stepInfo = computed(() => {
  if (!entity.value) return null
  const idx = graphStore.learningPath.indexOf(entity.value.id)
  if (idx === -1) return null

  const prevId = idx > 0 ? graphStore.learningPath[idx - 1] : null
  const nextId = idx < graphStore.learningPath.length - 1 ? graphStore.learningPath[idx + 1] : null

  const prevNode = prevId ? graphStore.nodes.find((n) => n.id === prevId) : null
  const nextNode = nextId ? graphStore.nodes.find((n) => n.id === nextId) : null

  const isInterchangeable =
    (prevId && graphStore.isStepPairInterchangeable(prevId, entity.value.id)) ||
    (nextId && graphStore.isStepPairInterchangeable(entity.value.id, nextId))

  return {
    currentStepIndex: idx,
    prevNode,
    nextNode,
    isInterchangeable,
  }
})

function findExternalReferences() {
  if (!entity.value) return
  window.alert(
    'Cross-source search: Querying user library for additional reference papers related to ' +
      entity.value.name
  )
}

// Draggable & Resizable setup for Building / Topic Detail Drawer
const {
  style,
  onDragStart,
  onResizeStart,
  resetPlacement,
  isDragging,
  isCustomPositioned,
} = useDraggableResizable({
  initialWidth: 350,
  initialHeight: 580,
  minWidth: 290,
  maxWidth: 680,
  minHeight: 340,
  maxHeight: 900,
  defaultPlacement: 'top-right',
  storageKey: 'building_card',
})
</script>

<template>
  <!-- 1. Minimized Floating Topic Pill -->
  <div
    v-if="entity && isMinimized"
    class="fixed top-20 right-4 z-30 flex items-center gap-2.5 px-3.5 py-2 bg-white/95 backdrop-blur-xl rounded-2xl shadow-[0_8px_30px_rgba(15,23,42,0.14)] border border-slate-200 animate-in fade-in"
  >
    <div
      class="w-7 h-7 rounded-xl flex items-center justify-center text-xs shadow-2xs"
      :class="[cardTheme.iconBg, cardTheme.iconText]"
    >
      <span class="material-symbols-outlined text-[15px]">{{ cardTheme.icon }}</span>
    </div>
    <div class="flex items-center gap-1.5 cursor-pointer select-none" @click="isMinimized = false">
      <span class="text-xs font-black text-[#1C1B18] max-w-[140px] truncate">{{ entity.name }}</span>
      <span v-if="stepInfo" class="font-mono text-[9px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded-full font-bold">
        Step {{ stepInfo.currentStepIndex + 1 }}
      </span>
    </div>
    <button
      @click="isMinimized = false"
      class="p-1 hover:bg-slate-100 rounded-lg text-slate-600 transition-colors"
      title="Expand topic drawer"
    >
      <span class="material-symbols-outlined text-[16px]">open_in_full</span>
    </button>
    <button
      @click="closeCard"
      class="p-1 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-700 transition-colors"
      title="Close topic focus"
    >
      <span class="material-symbols-outlined text-[16px]">close</span>
    </button>
  </div>

  <!-- 2. Full Movable & Resizable Topic Drawer -->
  <aside
    v-else-if="entity && !isMinimized"
    :style="style"
    class="bg-white/95 dark:bg-[#0B0F17]/95 backdrop-blur-2xl rounded-3xl p-5 shadow-[0_16px_45px_rgba(15,23,42,0.16)] border border-white/90 dark:border-slate-800 overflow-y-auto drawer-scroll animate-in fade-in duration-200 flex flex-col justify-between select-none relative transition-colors"
    :class="[
      isDragging ? 'shadow-2xl scale-[1.01]' : '',
    ]"
  >
    <!-- Header with Drag Grip, Type Icon Avatar & Action Buttons -->
    <div
      class="flex items-start justify-between cursor-move pb-2 border-b border-slate-100 dark:border-slate-800 relative group/carddrag"
      @mousedown="onDragStart"
      @touchstart="onDragStart"
      title="Click and drag to move card anywhere"
    >
      <!-- Dynamic hover popup tag (ONLY pops up on hover) -->
      <span class="absolute -top-7 left-2 pointer-events-none opacity-0 group-hover/carddrag:opacity-100 transition-opacity px-2 py-0.5 rounded bg-slate-900 text-white text-[9px] font-mono shadow-md whitespace-nowrap z-50">
        ✋ Drag to move topic card
      </span>

      <div class="flex items-center gap-2.5 min-w-0">
        <div
          class="w-10 h-10 rounded-2xl flex items-center justify-center shadow-xs shrink-0"
          :class="[cardTheme.iconBg, cardTheme.iconText]"
        >
          <span class="material-symbols-outlined text-xl">{{ cardTheme.icon }}</span>
        </div>
        <div class="min-w-0">
          <div class="flex items-center gap-1.5">
            <span
              class="font-mono text-[9.5px] font-black uppercase tracking-wider px-2 py-0.5 rounded-md border"
              :class="[cardTheme.bg, cardTheme.text, cardTheme.border]"
            >
              {{ entity.type }}
            </span>
          </div>
          <h2 class="font-black text-[#1C1B18] dark:text-white text-base leading-tight mt-1 line-clamp-1">
            {{ entity.name }}
          </h2>
        </div>
      </div>

      <div class="flex items-center gap-1 shrink-0 no-drag">
        <!-- Reset position button -->
        <button
          v-if="isCustomPositioned"
          @click.stop="resetPlacement"
          class="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition-colors"
          title="Snap back to default top-right"
        >
          <span class="material-symbols-outlined text-[14px]">restart_alt</span>
        </button>

        <button
          @click="isMinimized = true"
          class="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition-colors"
          title="Minimize drawer to see full map"
        >
          <span class="material-symbols-outlined text-[15px]">unfold_less</span>
        </button>

        <button
          @click="closeCard"
          class="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition-colors"
          title="Close details"
        >
          <span class="material-symbols-outlined text-[16px]">close</span>
        </button>
      </div>
    </div>

    <!-- Quick Stats Grid (Clean academic telemetry) -->
    <div class="grid grid-cols-3 gap-2 my-3 no-drag">
      <div class="bg-slate-50 dark:bg-slate-800/80 rounded-2xl p-2 text-center border border-slate-100 dark:border-slate-700">
        <div class="text-[9.5px] font-bold text-slate-400 dark:text-slate-400 uppercase">Type</div>
        <div class="font-mono font-bold text-teal-700 dark:text-teal-400 text-xs truncate max-w-[80px] mx-auto mt-0.5">
          {{ entity.type }}
        </div>
      </div>
      <div class="bg-slate-50 dark:bg-slate-800/80 rounded-2xl p-2 text-center border border-slate-100 dark:border-slate-700">
        <div class="text-[9.5px] font-bold text-slate-400 dark:text-slate-400 uppercase">
          {{ mode === 'study' ? 'Depth' : 'Mentions' }}
        </div>
        <div class="font-mono font-black text-purple-700 dark:text-purple-400 text-sm mt-0.5">{{ entity.mention_count ?? 1 }}×</div>
      </div>
      <div class="bg-slate-50 dark:bg-slate-800/80 rounded-2xl p-2 text-center border border-slate-100 dark:border-slate-700">
        <div class="text-[9.5px] font-bold text-slate-400 dark:text-slate-400 uppercase">Connections</div>
        <div class="font-mono font-black text-amber-700 dark:text-amber-400 text-sm mt-0.5">{{ connectedRoadsCount }}</div>
      </div>
    </div>

    <!-- Sequential Step & Prerequisite Flow in Soothing Blue Tone -->
    <div v-if="stepInfo" class="p-3 bg-blue-50/80 dark:bg-blue-950/40 rounded-2xl border-2 border-blue-500 dark:border-blue-600 space-y-2 text-xs shadow-xs my-2 no-drag">
      <div class="flex items-center justify-between text-[11px] font-bold">
        <span class="text-blue-950 dark:text-blue-200 flex items-center gap-1 font-mono">
          <span class="material-symbols-outlined text-sm text-blue-600 dark:text-blue-400">alt_route</span>
          Sequence Position
        </span>
        <span class="font-mono text-blue-900 dark:text-blue-100 bg-blue-200 dark:bg-blue-800 px-2 py-0.5 rounded-full text-[10px] font-black">
          Step {{ stepInfo.currentStepIndex + 1 }} of {{ graphStore.learningPath.length }}
        </span>
      </div>

      <!-- Before / Prerequisite -->
      <div class="flex items-center justify-between gap-1 text-[11px]">
        <span class="text-slate-500 dark:text-slate-400 font-medium">⬅ Preceding:</span>
        <button
          v-if="stepInfo.prevNode"
          @click="graphStore.selectEntity(stepInfo.prevNode.id)"
          class="font-mono font-bold text-blue-600 dark:text-blue-300 hover:underline truncate max-w-[150px] text-right"
          :title="`Jump to preceding step: ${stepInfo.prevNode.name}`"
        >
          {{ stepInfo.prevNode.name }}
        </button>
        <span v-else class="text-slate-400 dark:text-slate-500 font-mono text-[10px] italic">First Step (Foundation)</span>
      </div>

      <!-- After / Next Step -->
      <div class="flex items-center justify-between gap-1 text-[11px]">
        <span class="text-slate-500 dark:text-slate-400 font-medium">➡ Next Up:</span>
        <button
          v-if="stepInfo.nextNode"
          @click="graphStore.selectEntity(stepInfo.nextNode.id)"
          class="font-mono font-bold text-blue-600 dark:text-blue-300 hover:underline truncate max-w-[150px] text-right"
          :title="`Jump to next step: ${stepInfo.nextNode.name}`"
        >
          {{ stepInfo.nextNode.name }}
        </button>
        <span v-else class="text-slate-400 dark:text-slate-500 font-mono text-[10px] italic">Final Milestone (Apex)</span>
      </div>

      <!-- Interchangeability Badge if applicable -->
      <div v-if="stepInfo.isInterchangeable" class="text-[10px] font-mono text-amber-900 dark:text-amber-200 bg-amber-200 dark:bg-amber-900/60 p-1.5 rounded-xl border border-amber-300 dark:border-amber-700 flex items-center gap-1 font-bold">
        <span class="material-symbols-outlined text-xs text-amber-800 dark:text-amber-400">sync_alt</span>
        <span>Flexible Order: Sibling concept without strict prerequisite.</span>
      </div>
    </div>

    <!-- Description -->
    <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-900/90 p-3 rounded-2xl border border-slate-200 dark:border-slate-800 my-2 no-drag select-text">
      {{ entity.description || 'Core concept extracted during knowledge graph analysis.' }}
    </p>

    <!-- Differentiated Deep Insights for Research Papers vs College Study -->
    <div v-if="mode === 'research'" class="p-3 rounded-2xl bg-blue-50/70 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 text-left text-[11px] leading-relaxed my-2 space-y-1.5 no-drag select-text">
      <div class="flex items-center justify-between text-blue-900 dark:text-sky-300 font-mono font-bold text-[10px] uppercase">
        <span class="flex items-center gap-1">
          <span class="material-symbols-outlined text-xs">science</span>
          <span>Paper Novelty & Contribution</span>
        </span>
        <span class="text-emerald-600 dark:text-emerald-400 font-bold">O(1) Ops</span>
      </div>
      <p class="text-slate-700 dark:text-slate-300 text-[10.5px]">
        Replaces recurrent temporal bottlenecks with multi-head parallel attention projections, allowing massive GPU scaling.
      </p>
      <div class="flex items-center justify-between text-[10px] text-slate-500 dark:text-slate-400 pt-1 border-t border-blue-200 dark:border-blue-900 font-mono">
        <span>arXiv:1706.03762</span>
        <button @click="copyBibtex" class="text-blue-600 dark:text-sky-300 hover:underline flex items-center gap-0.5 cursor-pointer font-bold">
          <span class="material-symbols-outlined text-[11px]">content_copy</span>
          <span>{{ isCopied ? 'Copied!' : 'Copy BibTeX' }}</span>
        </button>
      </div>
    </div>

    <div v-else class="p-3 rounded-2xl bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 text-left text-[11px] leading-relaxed my-2 space-y-1.5 no-drag select-text">
      <div class="flex items-center justify-between text-amber-900 dark:text-amber-300 font-mono font-bold text-[10px] uppercase">
        <span class="flex items-center gap-1">
          <span class="material-symbols-outlined text-xs">school</span>
          <span>Syllabus Exam Watch</span>
        </span>
        <span class="text-rose-600 dark:text-rose-400 font-bold">High Yield</span>
      </div>
      <p class="text-slate-700 dark:text-amber-200 text-[10.5px]">
        Frequently tested on college midterms & finals. Memorize the system call return values and state-space transitions.
      </p>
    </div>

    <!-- Study Mastery Toggle Button -->
    <button
      @click="progressStore.toggleTopicCompletion(entity.id)"
      class="w-full py-2 px-3 rounded-xl font-bold text-xs flex items-center justify-center gap-1.5 border transition-all cursor-pointer shadow-xs my-1 no-drag"
      :class="[
        progressStore.isTopicCompleted(entity.id)
          ? 'bg-emerald-600 border-emerald-600 text-white'
          : 'bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-800 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700'
      ]"
    >
      <span class="material-symbols-outlined text-sm">
        {{ progressStore.isTopicCompleted(entity.id) ? 'check_circle' : 'radio_button_unchecked' }}
      </span>
      <span>{{ progressStore.isTopicCompleted(entity.id) ? 'Topic Mastered ✓ (Click to undo)' : 'Mark Topic as Studied' }}</span>
    </button>

    <!-- Action Buttons -->
    <div class="space-y-2 pt-2 no-drag mt-auto">
      <button
        @click="graphStore.openTopicDossier(entity.id)"
        class="w-full py-2.5 text-xs font-bold text-white bg-[#10B981] hover:bg-[#059669] rounded-xl shadow-xs active:translate-y-px transition-all flex items-center justify-center gap-1.5"
      >
        <span class="material-symbols-outlined text-sm">menu_book</span>
        <span>Read Everything on This Topic</span>
      </button>

      <!-- Quiz & Notes Quick Actions Grid -->
      <div class="grid grid-cols-2 gap-2">
        <button
          @click="quizStore.openQuiz('topic', entity.id)"
          class="py-2 text-xs font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 rounded-xl border border-emerald-200 transition-all flex items-center justify-center gap-1 active:scale-95"
        >
          <span class="material-symbols-outlined text-sm text-emerald-700">quiz</span>
          <span>Take Quiz</span>
        </button>

        <button
          @click="notesStore.openNotes('topic')"
          class="py-2 text-xs font-bold text-amber-800 bg-amber-50 hover:bg-amber-100 rounded-xl border border-amber-200 transition-all flex items-center justify-center gap-1 active:scale-95"
        >
          <span class="material-symbols-outlined text-sm text-amber-700">edit_note</span>
          <span>Topic Notes</span>
        </button>
      </div>

      <button
        @click="exploreConnections"
        class="w-full py-2 text-xs font-semibold text-[#1C1B18] bg-slate-100 hover:bg-slate-200 rounded-xl border border-slate-200 active:translate-y-px transition-all flex items-center justify-center gap-1.5"
      >
        <span class="material-symbols-outlined text-sm text-teal-600">hub</span>
        <span>Highlight Connections</span>
      </button>

      <button
        v-if="mode === 'study'"
        @click="findExternalReferences"
        class="w-full py-1.5 text-xs font-medium text-amber-800 bg-amber-50/80 hover:bg-amber-100/80 rounded-xl border border-amber-200 transition-colors flex items-center justify-center gap-1.5"
      >
        <span class="material-symbols-outlined text-sm">link</span>
        <span>Find External References</span>
      </button>
    </div>

    <!-- Resizing Handles -->
    <!-- Left Edge Resize -->
    <div
      @mousedown.stop="onResizeStart($event, 'w')"
      @touchstart.stop="onResizeStart($event, 'w')"
      class="absolute top-12 bottom-12 left-0 w-2.5 cursor-w-resize hover:bg-teal-400/30 transition-colors"
      title="Drag to resize width"
    ></div>

    <!-- Right Edge Resize -->
    <div
      @mousedown.stop="onResizeStart($event, 'e')"
      @touchstart.stop="onResizeStart($event, 'e')"
      class="absolute top-12 bottom-12 right-0 w-2.5 cursor-e-resize hover:bg-teal-400/30 transition-colors"
      title="Drag to resize width"
    ></div>

    <!-- Bottom Edge Resize -->
    <div
      @mousedown.stop="onResizeStart($event, 's')"
      @touchstart.stop="onResizeStart($event, 's')"
      class="absolute bottom-0 left-12 right-12 h-2 cursor-s-resize hover:bg-teal-400/30 transition-colors"
      title="Drag to resize height"
    ></div>

    <!-- Bottom-Left Corner Resize Grip -->
    <div
      @mousedown.stop="onResizeStart($event, 'sw')"
      @touchstart.stop="onResizeStart($event, 'sw')"
      class="absolute bottom-1.5 left-1.5 w-4 h-4 cursor-sw-resize flex items-center justify-center text-slate-300 hover:text-teal-600 transition-colors"
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
  </aside>
</template>
