<script setup lang="ts">
import { computed, ref, onBeforeUnmount } from 'vue'
import { useGraphStore } from '@/stores/graph'

const graphStore = useGraphStore()

const totalSteps = computed(() => graphStore.learningPath.length)
const currentStepNum = computed(() => graphStore.currentPathIndex + 1)
const currentNode = computed(() => graphStore.currentPathNode)

const canPrev = computed(() => graphStore.currentPathIndex > 0)
const canNext = computed(() => graphStore.currentPathIndex < totalSteps.value - 1)

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
      // Loop back to first step
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

onBeforeUnmount(() => {
  stopAutoPlay()
})
</script>

<template>
  <div
    v-if="totalSteps > 0"
    class="absolute top-16 sm:top-20 left-1/2 -translate-x-1/2 z-30 pointer-events-auto w-[94vw] max-w-xl bg-white/95 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-white/80 shadow-[0_12px_36px_rgba(0,0,0,0.12)] transition-all select-none"
  >
    <!-- Top Row: Left Arrow, Step Number & Step Name, Right Arrow, Auto-Play & Dossier -->
    <div class="flex items-center justify-between gap-2">
      <!-- Left Navigation Arrow (Auto-navigates to Previous Step) -->
      <button
        @click="onPrev"
        :disabled="!canPrev"
        class="w-8 h-8 rounded-xl flex items-center justify-center bg-slate-100 text-[#1C1B18] hover:bg-[#E8F0EC] hover:text-[#0D9488] active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        title="Previous Step"
      >
        <span class="material-symbols-outlined text-lg">arrow_back</span>
      </button>

      <!-- Center Step Info: Step Number & Current Topic Name -->
      <div class="flex-1 text-center min-w-0 px-2">
        <div class="flex items-center justify-center gap-1.5 flex-wrap">
          <span class="text-[10px] font-mono font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#EBF7F2] text-[#0D9488]">
            Step {{ currentStepNum }} of {{ totalSteps }}
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
      </div>

      <!-- Right Navigation Arrow (Auto-navigates to Next Step) -->
      <button
        @click="onNext"
        :disabled="!canNext"
        class="w-8 h-8 rounded-xl flex items-center justify-center bg-slate-100 text-[#1C1B18] hover:bg-[#E8F0EC] hover:text-[#0D9488] active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        title="Next Step"
      >
        <span class="material-symbols-outlined text-lg">arrow_forward</span>
      </button>

      <!-- Action Quick-Links: Auto-Tour and Dossier -->
      <div class="flex items-center gap-1.5 ml-1">
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

      <!-- Interactive Step Milestone Bubbles -->
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
</template>
