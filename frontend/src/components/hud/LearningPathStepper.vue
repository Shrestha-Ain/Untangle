<script setup lang="ts">
import { computed, ref, onBeforeUnmount } from 'vue'
import { useGraphStore } from '@/stores/graph'

const graphStore = useGraphStore()

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

onBeforeUnmount(() => {
  stopAutoPlay()
})
</script>

<template>
  <div v-if="totalSteps > 0" class="fixed top-16 sm:top-20 left-1/2 -translate-x-1/2 z-30 pointer-events-auto w-[94vw] max-w-2xl">
    <!-- Main Stepper HUD Capsule -->
    <div
      class="bg-white/95 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-white/80 shadow-[0_12px_36px_rgba(0,0,0,0.12)] transition-all select-none"
    >
      <!-- Top Row: Navigation Arrows, Topic Sequence Info & Controls -->
      <div class="flex items-center justify-between gap-2">
        <!-- Left Navigation Arrow (Previous Step) -->
        <button
          @click="onPrev"
          :disabled="!canPrev"
          class="w-8 h-8 rounded-xl flex items-center justify-center bg-slate-100 text-[#1C1B18] hover:bg-[#E8F0EC] hover:text-[#0D9488] active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
          :title="prevNode ? `Previous Step: ${prevNode.name}` : 'First step'"
        >
          <span class="material-symbols-outlined text-lg">arrow_back</span>
        </button>

        <!-- Center Step Info: Sequence Step, Topic Name, and Flow Context -->
        <div class="flex-1 text-center min-w-0 px-2">
          <!-- Status Badges -->
          <div class="flex items-center justify-center gap-1.5 flex-wrap">
            <span class="text-[10px] font-mono font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#EBF7F2] text-[#0D9488]">
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
              class="text-[9px] font-mono font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200"
              title="Prerequisite-ordered step (unidirectional)"
            >
              → Sequential
            </span>

            <span
              v-if="currentNode?.type"
              class="text-[9px] font-mono font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 border border-slate-200"
            >
              {{ currentNode.type }}
            </span>
          </div>

          <!-- Step Name (Bold, Prominent) -->
          <div class="text-xs sm:text-sm font-extrabold text-[#1C1B18] truncate leading-tight mt-0.5" :title="currentNode?.name">
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
          class="w-8 h-8 rounded-xl flex items-center justify-center bg-slate-100 text-[#1C1B18] hover:bg-[#E8F0EC] hover:text-[#0D9488] active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
          :title="nextNode ? `Next Step: ${nextNode.name}` : 'Final milestone'"
        >
          <span class="material-symbols-outlined text-lg">arrow_forward</span>
        </button>

        <!-- Action Quick-Links: Roadmap Flow, Auto-Tour and Dossier -->
        <div class="flex items-center gap-1 ml-1">
          <!-- Flow Roadmap Toggle -->
          <button
            @click="isRoadmapOpen = !isRoadmapOpen"
            class="flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-[11px] font-bold transition-all shadow-sm active:scale-95 border"
            :class="[
              isRoadmapOpen
                ? 'bg-[#0D9488] text-white border-[#0D9488] shadow-md'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-200'
            ]"
            title="View complete sequential topic roadmap (which topic is after which one)"
          >
            <span class="material-symbols-outlined text-sm">alt_route</span>
            <span class="hidden md:inline">Roadmap</span>
          </button>

          <!-- Auto-Play Tour Toggle -->
          <button
            @click="toggleAutoPlay"
            class="flex items-center gap-1 px-2 py-1.5 rounded-xl text-[11px] font-bold transition-all shadow-sm active:scale-95"
            :class="[
              isAutoPlaying
                ? 'bg-[#0D9488] text-white ring-2 ring-[#0D9488]/30'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
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
            class="hidden sm:inline-flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-bold text-white bg-[#0D9488] hover:bg-[#0B7A6F] active:scale-95 rounded-xl shadow-sm transition-all"
            title="Read detailed topic dossier"
          >
            <span class="material-symbols-outlined text-sm">menu_book</span>
            <span>Dossier</span>
          </button>
        </div>
      </div>

      <!-- Bottom Row: Interactive Step Slider & Timeline Track -->
      <div class="relative w-full mt-2.5 pt-1 px-1">
        <!-- Background Slider Rail Track with Colored Progress Fill -->
        <div class="relative w-full h-1.5 bg-slate-200 rounded-full">
          <div
            class="h-full bg-gradient-to-r from-[#06B6D4] via-[#10B981] to-[#0D9488] rounded-full transition-all duration-300"
            :style="{ width: `${(graphStore.currentPathIndex / Math.max(totalSteps - 1, 1)) * 100}%` }"
          ></div>
        </div>

        <!-- Interactive Step Milestone Bubbles & Directional Arrows -->
        <div class="relative -mt-3.5 flex items-center justify-between w-full">
          <template v-for="(stepId, idx) in graphStore.learningPath" :key="stepId">
            <!-- Step Node Button -->
            <button
              @click="onStepClick(idx)"
              class="relative z-10 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-mono font-bold transition-all shadow-sm"
              :class="[
                idx === graphStore.currentPathIndex
                  ? 'bg-[#0D9488] text-white ring-4 ring-[#0D9488]/30 scale-110 shadow-md'
                  : idx < graphStore.currentPathIndex
                    ? 'bg-[#10B981] text-white'
                    : 'bg-white text-slate-500 border border-slate-300 hover:border-slate-500'
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
                    ? 'text-emerald-500'
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
    </div>

    <!-- SEQUENTIAL TOPIC ROADMAP FLOW POPOVER (Shows which topic is after which one) -->
    <div
      v-if="isRoadmapOpen"
      class="mt-2 bg-white/98 backdrop-blur-xl rounded-2xl border border-slate-200/90 shadow-2xl p-4 max-h-[60vh] overflow-y-auto space-y-2 animate-in fade-in slide-in-from-top-2 duration-200"
    >
      <div class="flex items-center justify-between border-b border-slate-100 pb-2">
        <div>
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-[#0D9488] text-base">route</span>
            <h3 class="text-xs font-bold text-[#1C1B18] uppercase tracking-wider font-mono">
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
                    ? 'bg-[#0D9488] text-white shadow-xs'
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
                    class="text-[9px] font-mono uppercase bg-[#0D9488] text-white px-1.5 py-0.2 rounded"
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
