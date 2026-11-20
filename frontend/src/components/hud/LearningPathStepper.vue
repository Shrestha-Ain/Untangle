<script setup lang="ts">
import { computed, ref, onBeforeUnmount } from 'vue'
import { useGraphStore } from '@/stores/graph'
import { useProgressStore } from '@/stores/progress'
import { useDraggableResizable } from '@/composables/useDraggableResizable'

const graphStore = useGraphStore()
const progressStore = useProgressStore()

const totalSteps = computed(() => graphStore.learningPath.length)
const currentStepNum = computed(() => graphStore.currentPathIndex + 1)
const currentNode = computed(() => graphStore.currentPathNode)
const isCurrentInterchangeable = computed(() => graphStore.currentStepIsInterchangeable)

const prevNode = computed(() => {
  const idx = graphStore.currentPathIndex
  if (idx <= 0) return null
  const id = graphStore.learningPath[idx - 1]
  return graphStore.nodes.find((n) => n.id === id) ?? null
})

const nextNode = computed(() => {
  const idx = graphStore.currentPathIndex
  if (idx >= totalSteps.value - 1) return null
  const id = graphStore.learningPath[idx + 1]
  return graphStore.nodes.find((n) => n.id === id) ?? null
})

const canPrev = computed(() => graphStore.currentPathIndex > 0)
const canNext = computed(() => graphStore.currentPathIndex < totalSteps.value - 1)

// Roadmap Flow drawer toggle
const isRoadmapOpen = ref(false)

// Auto-Tour functionality
const isAutoPlaying = ref(false)
let autoPlayTimer: ReturnType<typeof setInterval> | null = null

function toggleAutoPlay() {
  if (isAutoPlaying.value) {
    stopAutoPlay()
  } else {
    startAutoPlay()
  }
}

function startAutoPlay() {
  isAutoPlaying.value = true
  autoPlayTimer = setInterval(() => {
    if (graphStore.currentPathIndex < totalSteps.value - 1) {
      graphStore.nextPathStep()
    } else {
      graphStore.setPathIndex(0)
    }
  }, 3500)
}

function stopAutoPlay() {
  isAutoPlaying.value = false
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer)
    autoPlayTimer = null
  }
}

function onPrev() {
  stopAutoPlay()
  graphStore.prevPathStep()
}

function onNext() {
  stopAutoPlay()
  graphStore.nextPathStep()
}

function onSliderChange(event: Event) {
  stopAutoPlay()
  const target = event.target as HTMLInputElement
  const newIndex = parseInt(target.value, 10)
  if (!isNaN(newIndex)) {
    graphStore.setPathIndex(newIndex)
  }
}

function onStepClick(index: number) {
  stopAutoPlay()
  graphStore.setPathIndex(index)
}

function getNodeName(id: string): string {
  const node = graphStore.nodes.find((n) => n.id === id)
  return node?.name || id
}

function selectRoadmapStep(index: number) {
  stopAutoPlay()
  graphStore.setPathIndex(index)
  isRoadmapOpen.value = false
}

// Draggable & Resizable window setup
const {
  style,
  onDragStart,
  onResizeStart,
  resetPlacement,
  isDragging,
  isCustomPositioned,
} = useDraggableResizable({
  initialWidth: 640,
  initialHeight: 124,
  minWidth: 420,
  maxWidth: 980,
  minHeight: 100,
  maxHeight: 520,
  defaultPlacement: 'top-center',
  storageKey: 'learning_stepper',
})

onBeforeUnmount(() => {
  stopAutoPlay()
})
</script>

<template>
  <div
    v-if="totalSteps > 0"
    :style="style"
    class="pointer-events-auto select-none transition-shadow duration-150"
    :class="[
      isDragging ? 'shadow-2xl opacity-95 scale-[1.01]' : 'shadow-[0_16px_40px_rgba(15,23,42,0.14)]',
    ]"
  >
    <!-- Main Stepper HUD Capsule -->
    <div
      class="bg-white/95 dark:bg-[#0B0F17]/95 backdrop-blur-xl px-4 py-2.5 rounded-3xl border border-white/90 dark:border-slate-800 shadow-sm relative flex flex-col justify-between h-full group transition-colors"
    >
      <!-- 1. Top Drag Grip Bar & Reset Control -->
      <div
        class="flex items-center justify-between pb-1 cursor-move text-slate-400 dark:text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 transition-colors border-b border-slate-100 dark:border-slate-800"
        @mousedown="onDragStart"
        @touchstart="onDragStart"
        title="Drag anywhere to move"
      >
        <div class="flex items-center gap-1.5 relative group/drag">
          <span class="material-symbols-outlined text-[15px] text-[#10B981]">drag_indicator</span>
          <span class="text-[9.5px] font-mono font-black text-slate-500 dark:text-slate-400 uppercase tracking-widest">
            Learning Path Slider
          </span>
          <!-- Dynamic hover popup tag (ONLY pops up on hover) -->
          <span class="absolute left-0 -top-7 pointer-events-none opacity-0 group-hover/drag:opacity-100 transition-opacity px-2 py-0.5 rounded bg-slate-900 text-white text-[9px] font-mono shadow-md whitespace-nowrap z-50">
            ✋ Drag to move slider
          </span>
        </div>

        <div class="flex items-center gap-1.5 no-drag">
          <button
            v-if="isCustomPositioned"
            @click.stop="resetPlacement"
            class="px-1.5 py-0.5 rounded text-[9.5px] font-mono font-bold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 flex items-center gap-0.5 transition-colors"
            title="Snap back to default top-center"
          >
            <span class="material-symbols-outlined text-[13px]">restart_alt</span>
            <span>Reset Pos</span>
          </button>
        </div>
      </div>

      <!-- 2. Controls & Step Info Row -->
      <div class="flex items-center justify-between gap-2 pt-1">
        <!-- Left Navigation Arrow (Previous Step) -->
        <button
          @click="onPrev"
          :disabled="!canPrev"
          class="w-8 h-8 rounded-xl flex items-center justify-center bg-slate-100 text-[#1C1B18] hover:bg-emerald-50 hover:text-emerald-700 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-xs shrink-0"
          :title="prevNode ? `Previous Step: ${prevNode.name}` : 'First step'"
        >
          <span class="material-symbols-outlined text-lg">arrow_back</span>
        </button>

        <!-- Center Step Info: Sequence Step, Topic Name, and Flow Context -->
        <div class="flex-1 text-center min-w-0 px-2">
          <!-- Status Badges -->
          <div class="flex items-center justify-center gap-1.5 flex-wrap">
            <span class="text-[10px] font-mono font-black uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
              Step {{ currentStepNum }} of {{ totalSteps }}
            </span>

            <span
              v-if="isCurrentInterchangeable"
              class="text-[9px] font-mono font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200"
              title="This topic can be studied in flexible order with adjacent topics"
            >
              ⇄ Flexible Order
            </span>
            <span
              v-else
              class="text-[9px] font-mono font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-teal-50 text-teal-700 border border-teal-200"
              title="Prerequisite-ordered step (unidirectional)"
            >
              → Sequential
            </span>

            <span
              v-if="currentNode?.type"
              class="text-[9px] font-mono font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200"
            >
              {{ currentNode.type }}
            </span>

            <!-- Quick Mark Mastered Button for Current Step -->
            <button
              v-if="currentNode"
              @click.stop="progressStore.toggleTopicCompletion(currentNode.id)"
              class="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold flex items-center gap-1 border transition-all cursor-pointer shadow-2xs"
              :class="[
                progressStore.isTopicCompleted(currentNode.id)
                  ? 'bg-emerald-600 border-emerald-600 text-white'
                  : 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300'
              ]"
              :title="progressStore.isTopicCompleted(currentNode.id) ? 'Topic Mastered! Click to unmark' : 'Click to mark as studied'"
            >
              <span class="material-symbols-outlined text-[12px]">
                {{ progressStore.isTopicCompleted(currentNode.id) ? 'check_circle' : 'radio_button_unchecked' }}
              </span>
              <span>{{ progressStore.isTopicCompleted(currentNode.id) ? 'Mastered' : 'Mark Done' }}</span>
            </button>
          </div>

          <!-- Step Name (Bold, Prominent) -->
          <div class="text-xs sm:text-sm font-black text-[#1C1B18] truncate leading-tight mt-0.5" :title="currentNode?.name">
            {{ currentNode?.name ?? 'Select a Concept' }}
          </div>

          <!-- Sequence Context: Which topic precedes, which follows -->
          <div class="flex items-center justify-center gap-2 mt-0.5 text-[10px] font-mono leading-none">
            <span v-if="prevNode" class="text-slate-400 truncate max-w-[130px]" :title="`Builds upon: ${prevNode.name}`">
              ← Pre: {{ prevNode.name }}
            </span>
            <span v-else class="text-slate-400 italic">
              Foundational Start
            </span>

            <span class="text-slate-300">•</span>

            <span v-if="nextNode" class="text-teal-700 font-bold truncate max-w-[140px]" :title="`Leads to: ${nextNode.name}`">
              ↳ Leads to: {{ nextNode.name }} →
            </span>
            <span v-else class="text-emerald-700 font-bold">
              ★ Curriculum Complete
            </span>
          </div>
        </div>

        <!-- Right Navigation Arrow (Next Step) -->
        <button
          @click="onNext"
          :disabled="!canNext"
          class="w-8 h-8 rounded-xl flex items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 hover:bg-emerald-50 dark:hover:bg-slate-700 hover:text-emerald-700 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-xs shrink-0"
          :title="nextNode ? `Next Step: ${nextNode.name}` : 'Final milestone'"
        >
          <span class="material-symbols-outlined text-lg">arrow_forward</span>
        </button>

        <!-- Action Quick-Links: Roadmap Flow, Auto-Tour and Dossier -->
        <div class="flex items-center gap-1 shrink-0 ml-1">
          <!-- Flow Roadmap Toggle -->
          <button
            @click="isRoadmapOpen = !isRoadmapOpen"
            class="flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-[11px] font-bold transition-all shadow-xs active:scale-95 border"
            :class="[
              isRoadmapOpen
                ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 border-slate-200 dark:border-slate-700'
            ]"
            title="View complete sequential topic roadmap"
          >
            <span class="material-symbols-outlined text-sm">alt_route</span>
            <span class="hidden md:inline">Roadmap</span>
          </button>

          <!-- Study Progress Metric Pill Button -->
          <button
            @click="progressStore.openProgressModal"
            class="flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-[11px] font-bold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800 hover:bg-emerald-100 transition-all shadow-xs active:scale-95 cursor-pointer"
            title="View topic completion percentage and breakdown"
          >
            <span class="material-symbols-outlined text-sm">donut_large</span>
            <span>{{ progressStore.completionPercentage }}%</span>
          </button>

          <!-- Auto-Play Tour Toggle -->
          <button
            @click="toggleAutoPlay"
            class="flex items-center gap-1 px-2 py-1.5 rounded-xl text-[11px] font-bold transition-all shadow-xs active:scale-95"
            :class="[
              isAutoPlaying
                ? 'bg-blue-600 text-white ring-2 ring-blue-600/30'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
            ]"
            :title="isAutoPlaying ? 'Pause automatic tour' : 'Start automatic tour through steps'"
          >
            <span class="material-symbols-outlined text-sm">
              {{ isAutoPlaying ? 'pause' : 'play_arrow' }}
            </span>
            <span class="hidden md:inline">{{ isAutoPlaying ? 'Playing' : 'Auto' }}</span>
          </button>

          <!-- Read Dossier Button -->
          <button
            v-if="currentNode"
            @click="graphStore.openTopicDossier(currentNode.id)"
            class="hidden sm:inline-flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-bold text-white bg-blue-600 hover:bg-blue-500 active:scale-95 rounded-xl shadow-xs transition-all"
            title="Read detailed topic dossier"
          >
            <span class="material-symbols-outlined text-sm">menu_book</span>
            <span>Dossier</span>
          </button>
        </div>
      </div>

      <!-- 3. Interactive Step Slider & Timeline Track -->
      <div class="relative w-full mt-2 pt-1 px-1">
        <!-- Background Slider Rail Track with Colored Progress Fill -->
        <div class="relative w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full">
          <div
            class="h-full bg-blue-600 rounded-full transition-all duration-300"
            :style="{ width: `${(graphStore.currentPathIndex / Math.max(totalSteps - 1, 1)) * 100}%` }"
          ></div>
        </div>

        <!-- Interactive Step Milestone Bubbles & Directional Arrows -->
        <div class="relative -mt-3.5 flex items-center justify-between w-full">
          <template v-for="(stepId, idx) in graphStore.learningPath" :key="stepId">
            <!-- Step Node Button -->
            <button
              @click="onStepClick(idx)"
              class="relative z-10 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-mono font-bold transition-all shadow-xs"
              :class="[
                idx === graphStore.currentPathIndex
                  ? 'bg-blue-600 text-white ring-4 ring-blue-500/30 scale-110 shadow-md'
                  : idx < graphStore.currentPathIndex
                    ? 'bg-blue-500 text-white'
                    : 'bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-300 dark:border-slate-700 hover:border-slate-500'
              ]"
              :title="`Step ${idx + 1}: ${getNodeName(stepId)}`"
            >
              <span v-if="idx < graphStore.currentPathIndex" class="material-symbols-outlined text-xs">check</span>
              <span v-else>{{ idx + 1 }}</span>
            </button>

            <!-- Inter-step directional indicator between milestones -->
            <span
              v-if="idx < totalSteps - 1"
              class="flex-1 text-center text-[10px] font-bold select-none pointer-events-none transition-colors px-0.5"
              :class="[
                graphStore.isStepPairInterchangeable(stepId, graphStore.learningPath[idx + 1])
                  ? 'text-amber-500'
                  : idx < graphStore.currentPathIndex
                    ? 'text-blue-500 dark:text-blue-400'
                    : 'text-slate-400'
              ]"
              :title="
                graphStore.isStepPairInterchangeable(stepId, graphStore.learningPath[idx + 1])
                  ? `Steps ${idx + 1} and ${idx + 2} are interchangeable (flexible order)`
                  : `Step ${idx + 1} → Step ${idx + 2} (unidirectional prerequisite)`
              "
            >
              {{ graphStore.isStepPairInterchangeable(stepId, graphStore.learningPath[idx + 1]) ? '⇄' : '→' }}
            </span>
          </template>
        </div>

        <!-- Native Range Input (Transparent Overlay for Smooth Dragging & Scrubbing) -->
        <input
          type="range"
          min="0"
          :max="totalSteps - 1"
          step="1"
          :value="graphStore.currentPathIndex"
          @input="onSliderChange"
          class="absolute inset-0 opacity-0 cursor-pointer w-full h-full z-20"
          title="Slide or drag to navigate through steps"
        />
      </div>

      <!-- 4. Resizing Handles -->
      <!-- Right Edge Resize -->
      <div
        @mousedown.stop="onResizeStart($event, 'e')"
        @touchstart.stop="onResizeStart($event, 'e')"
        class="absolute top-1/2 right-0 w-2.5 h-12 -translate-y-1/2 cursor-e-resize hover:bg-teal-400/40 rounded-l transition-colors"
        title="Drag edge to resize slider width"
      ></div>

      <!-- Left Edge Resize -->
      <div
        @mousedown.stop="onResizeStart($event, 'w')"
        @touchstart.stop="onResizeStart($event, 'w')"
        class="absolute top-1/2 left-0 w-2.5 h-12 -translate-y-1/2 cursor-w-resize hover:bg-teal-400/40 rounded-r transition-colors"
        title="Drag edge to resize slider width"
      ></div>

      <!-- Bottom Edge Resize -->
      <div
        @mousedown.stop="onResizeStart($event, 's')"
        @touchstart.stop="onResizeStart($event, 's')"
        class="absolute bottom-0 left-1/2 -translate-x-1/2 w-20 h-2 cursor-s-resize hover:bg-teal-400/40 rounded-t transition-colors"
        title="Drag to resize slider height"
      ></div>

      <!-- Bottom-Right Corner Resize Grip -->
      <div
        @mousedown.stop="onResizeStart($event, 'se')"
        @touchstart.stop="onResizeStart($event, 'se')"
        class="absolute bottom-1 right-1.5 w-4 h-4 cursor-se-resize flex items-center justify-center text-slate-300 hover:text-teal-600 transition-colors"
        title="Drag corner to resize slider"
      >
        <span class="text-[11px] leading-none select-none">⋱</span>
      </div>
    </div>

    <!-- SEQUENTIAL TOPIC ROADMAP FLOW POPOVER (Shows which topic is after which one) -->
    <div
      v-if="isRoadmapOpen"
      class="mt-2 bg-white/98 backdrop-blur-xl rounded-2xl border border-slate-200/90 shadow-2xl p-4 max-h-[60vh] overflow-y-auto space-y-2 animate-in fade-in slide-in-from-top-2 duration-200"
    >
      <div class="flex items-center justify-between border-b border-slate-100 pb-2">
        <div>
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-teal-600 text-base">route</span>
            <h3 class="text-xs font-black text-[#1C1B18] uppercase tracking-wider font-mono">
              Topic Learning Progression Flow
            </h3>
          </div>
          <p class="text-[11px] text-slate-500 mt-0.5">
            Step-by-step prerequisite order. Topics marked with ⇄ can be studied interchangeably.
          </p>
        </div>

        <button
          @click="isRoadmapOpen = false"
          class="w-6 h-6 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 flex items-center justify-center transition-colors"
        >
          <span class="material-symbols-outlined text-sm">close</span>
        </button>
      </div>

      <!-- Roadmap Flow Chain List -->
      <div class="space-y-1.5 pt-1">
        <template v-for="(stepId, idx) in graphStore.learningPath" :key="stepId">
          <div
            @click="selectRoadmapStep(idx)"
            class="flex items-center justify-between p-2 rounded-xl border cursor-pointer transition-all hover:translate-x-1"
            :class="[
              idx === graphStore.currentPathIndex
                ? 'bg-teal-50 border-teal-300 ring-2 ring-teal-500/20 shadow-xs'
                : idx < graphStore.currentPathIndex
                  ? 'bg-slate-50/80 border-slate-200 text-slate-600'
                  : 'bg-white border-slate-100 hover:border-slate-300'
            ]"
          >
            <div class="flex items-center gap-2.5 min-w-0">
              <!-- Step Number Badge -->
              <div
                class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-mono font-bold flex-shrink-0"
                :class="[
                  idx === graphStore.currentPathIndex
                    ? 'bg-teal-600 text-white shadow-xs'
                    : idx < graphStore.currentPathIndex
                      ? 'bg-emerald-500 text-white'
                      : 'bg-slate-200 text-slate-600'
                ]"
              >
                <span v-if="idx < graphStore.currentPathIndex" class="material-symbols-outlined text-xs">check</span>
                <span v-else>{{ idx + 1 }}</span>
              </div>

              <!-- Topic Name & Preceding / Following Context -->
              <div class="min-w-0">
                <div class="text-xs font-bold text-[#1C1B18] truncate flex items-center gap-1.5">
                  <span>{{ getNodeName(stepId) }}</span>
                  <span
                    v-if="idx === graphStore.currentPathIndex"
                    class="text-[9px] font-mono uppercase bg-teal-600 text-white px-1.5 py-0.2 rounded"
                  >
                    Active
                  </span>
                </div>
                <div class="text-[10px] text-slate-400 font-mono truncate">
                  <span v-if="idx === 0">Starting Foundation</span>
                  <span v-else>Follows: {{ getNodeName(graphStore.learningPath[idx - 1]) }}</span>
                  <span v-if="idx < totalSteps - 1"> · Leads to: {{ getNodeName(graphStore.learningPath[idx + 1]) }}</span>
                </div>
              </div>
            </div>

            <!-- Flow Arrow Icon -->
            <div class="flex items-center gap-1.5 flex-shrink-0 ml-2">
              <span
                v-if="idx < totalSteps - 1 && graphStore.isStepPairInterchangeable(stepId, graphStore.learningPath[idx + 1])"
                class="text-[10px] font-mono text-amber-600 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded font-bold"
                title="Interchangeable with next step"
              >
                ⇄ Flex
              </span>
              <span class="material-symbols-outlined text-slate-300 text-sm">
                chevron_right
              </span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
