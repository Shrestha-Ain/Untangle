<script setup lang="ts">
import { computed } from 'vue'
import { useGraphStore } from '@/stores/graph'

const graphStore = useGraphStore()

const totalSteps = computed(() => graphStore.learningPath.length)
const currentStepNum = computed(() => graphStore.currentPathIndex + 1)
const currentNode = computed(() => graphStore.currentPathNode)

const canPrev = computed(() => graphStore.currentPathIndex > 0)
const canNext = computed(() => graphStore.currentPathIndex < totalSteps.value - 1)

const isCurrentInterchangeable = computed(() => graphStore.currentStepIsInterchangeable)

function getNodeName(id: string): string {
  const node = graphStore.nodes.find((n) => n.id === id)
  return node?.name || id
}

function isPairInterchangeable(idA: string, idB: string): boolean {
  return graphStore.isStepPairInterchangeable(idA, idB)
}

function onSliderChange(event: Event) {
  const target = event.target as HTMLInputElement
  const newIndex = parseInt(target.value, 10)
  if (!isNaN(newIndex)) {
    graphStore.setPathIndex(newIndex)
  }
}
</script>

<template>
  <div
    v-if="totalSteps > 0"
    class="absolute top-16 sm:top-20 left-1/2 -translate-x-1/2 z-30 pointer-events-auto w-[94vw] max-w-xl bg-white/95 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-white/80 shadow-[0_12px_36px_rgba(0,0,0,0.12)] transition-all select-none"
  >
    <!-- Top Row: Left Arrow, Step Title & Status, Right Arrow, Actions -->
    <div class="flex items-center justify-between gap-2">
      <!-- Left Navigation Arrow (Auto-navigates to Previous Step) -->
      <button
        @click="graphStore.prevPathStep"
        :disabled="!canPrev"
        class="w-8 h-8 rounded-xl flex items-center justify-center bg-slate-100 text-[#1C1B18] hover:bg-[#E8F0EC] hover:text-[#0D9488] active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        title="Previous Step"
      >
        <span class="material-symbols-outlined text-lg">arrow_back</span>
      </button>

      <!-- Center Info: Step Number & Topic Name -->
      <div class="flex-1 text-center min-w-0 px-2">
        <div class="flex items-center justify-center gap-1.5 flex-wrap">
          <span class="text-[10px] font-mono font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#EBF7F2] text-[#0D9488]">
            Step {{ currentStepNum }} of {{ totalSteps }}
          </span>

          <!-- Unidirectional vs Interchangeable Indicator Badge -->
          <span
            v-if="isCurrentInterchangeable"
            class="inline-flex items-center gap-0.5 text-[9px] font-mono font-bold text-amber-700 bg-amber-50 border border-amber-300 rounded px-1.5 py-0.5"
            title="This topic can be studied interchangeably with adjacent topics"
          >
            <span class="material-symbols-outlined text-[11px]">swap_horiz</span>
            <span>Interchangeable</span>
          </span>
          <span
            v-else
            class="inline-flex items-center gap-0.5 text-[9px] font-mono font-bold text-slate-600 bg-slate-100 border border-slate-200 rounded px-1.5 py-0.5"
            title="Prerequisite topic - sequential order recommended"
          >
            <span class="material-symbols-outlined text-[11px]">trending_flat</span>
            <span>Sequential</span>
          </span>
        </div>

        <div class="text-xs sm:text-sm font-extrabold text-[#1C1B18] truncate leading-tight mt-0.5" :title="currentNode?.name">
          {{ currentNode?.name ?? 'Select a Concept' }}
        </div>
      </div>

      <!-- Right Navigation Arrow (Auto-navigates to Next Step) -->
      <button
        @click="graphStore.nextPathStep"
        :disabled="!canNext"
        class="w-8 h-8 rounded-xl flex items-center justify-center bg-slate-100 text-[#1C1B18] hover:bg-[#E8F0EC] hover:text-[#0D9488] active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        title="Next Step"
      >
        <span class="material-symbols-outlined text-lg">arrow_forward</span>
      </button>

      <!-- Read Dossier Quick Trigger -->
      <button
        v-if="currentNode"
        @click="graphStore.openTopicDossier(currentNode.id)"
        class="hidden sm:inline-flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-bold text-white bg-[#0D9488] hover:bg-[#0B7A6F] active:scale-95 rounded-xl shadow-sm transition-all ml-1"
        title="Read detailed topic dossier"
      >
        <span class="material-symbols-outlined text-sm">menu_book</span>
        <span>Dossier</span>
      </button>
    </div>

    <!-- Bottom Row: Interactive Step Slider & Timeline Track with Directional Arrows -->
    <div class="relative w-full mt-2 pt-1 px-1">
      <!-- Background Track with Fill -->
      <div class="relative w-full h-1.5 bg-slate-200 rounded-full">
        <div
          class="h-full bg-gradient-to-r from-[#06B6D4] via-[#10B981] to-[#0D9488] rounded-full transition-all duration-300"
          :style="{ width: `${(graphStore.currentPathIndex / Math.max(totalSteps - 1, 1)) * 100}%` }"
        ></div>
      </div>

      <!-- Step Nodes & Inter-step Directional Arrows -->
      <div class="relative -mt-3.5 flex items-center justify-between w-full">
        <template v-for="(stepId, idx) in graphStore.learningPath" :key="stepId">
          <!-- Step Node Bubble Button -->
          <button
            @click="graphStore.setPathIndex(idx)"
            class="relative z-10 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-mono font-bold transition-all shadow-sm"
            :class="[
              idx === graphStore.currentPathIndex
                ? 'bg-[#0D9488] text-white ring-4 ring-[#0D9488]/30 scale-110'
                : idx < graphStore.currentPathIndex
                  ? 'bg-[#10B981] text-white'
                  : 'bg-white text-slate-500 border border-slate-300 hover:border-slate-500'
            ]"
            :title="`Step ${idx + 1}: ${getNodeName(stepId)}`"
          >
            <span v-if="idx < graphStore.currentPathIndex" class="material-symbols-outlined text-xs">check</span>
            <span v-else>{{ idx + 1 }}</span>
          </button>

          <!-- Inter-step Directional Arrow (Unidirectional vs Interchangeable) -->
          <div
            v-if="idx < totalSteps - 1"
            class="flex-1 flex items-center justify-center text-[11px] select-none leading-none z-10"
            :title="isPairInterchangeable(stepId, graphStore.learningPath[idx + 1])
              ? `Step ${idx + 1} & ${idx + 2} are interchangeable (flexible order)`
              : `Step ${idx + 1} → Step ${idx + 2} (unidirectional requirement)`"
          >
            <span
              class="font-mono font-black transition-colors"
              :class="isPairInterchangeable(stepId, graphStore.learningPath[idx + 1])
                ? 'text-amber-500 font-extrabold text-[12px]'
                : idx < graphStore.currentPathIndex
                  ? 'text-[#10B981]'
                  : 'text-slate-400'"
            >
              {{ isPairInterchangeable(stepId, graphStore.learningPath[idx + 1]) ? '⇄' : '→' }}
            </span>
          </div>
        </template>
      </div>

      <!-- Native Range Input (Transparent Overlay for Smooth Drag Scrubbing) -->
      <input
        type="range"
        min="0"
        :max="totalSteps - 1"
        step="1"
        :value="graphStore.currentPathIndex"
        @input="onSliderChange"
        class="absolute inset-0 opacity-0 cursor-pointer w-full h-full z-20"
        title="Drag or slide to navigate steps"
      />
    </div>
  </div>
</template>
