<script setup lang="ts">
import { computed } from 'vue'
import { useGraphStore } from '@/stores/graph'

const graphStore = useGraphStore()

const totalSteps = computed(() => graphStore.learningPath.length)
const currentStepNum = computed(() => graphStore.currentPathIndex + 1)
const currentNode = computed(() => graphStore.currentPathNode)

const canPrev = computed(() => graphStore.currentPathIndex > 0)
const canNext = computed(() => graphStore.currentPathIndex < totalSteps.value - 1)
</script>

<template>
  <div
    v-if="totalSteps > 0"
    class="absolute top-20 left-1/2 -translate-x-1/2 z-20 pointer-events-auto flex items-center gap-2 bg-white/95 backdrop-blur-md p-1.5 px-3.5 rounded-2xl border border-white/80 shadow-[0_8px_30px_rgba(0,0,0,0.10)] transition-all select-none"
  >
    <!-- Path Mode Toggle -->
    <button
      @click="graphStore.togglePathMode"
      class="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-xl transition-all"
      :class="[
        graphStore.isPathModeActive
          ? 'bg-[#E8F0EC] text-[#3D6B5A] border border-[#C4D8CC]'
          : 'text-[#8A877F] hover:bg-[#EFEFED] border border-transparent'
      ]"
      title="Toggle guided curriculum path"
    >
      <span
        class="w-2 h-2 rounded-full inline-block"
        :class="graphStore.isPathModeActive ? 'bg-[#4E9A7D] animate-ping' : 'bg-[#8A877F]'"
      ></span>
      <span class="font-mono text-[11px] uppercase tracking-wider">Guided Path</span>
    </button>

    <div class="h-4 w-px bg-[#E4E3DF]"></div>

    <!-- Stepper Controls (visible when path mode is active) -->
    <div class="flex items-center gap-2">
      <!-- Prev Button -->
      <button
        @click="graphStore.prevPathStep"
        :disabled="!canPrev"
        class="w-7 h-7 rounded-lg flex items-center justify-center text-[#5C5A54] hover:text-[#1C1B18] hover:bg-[#EFEFED] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        title="Previous concept in curriculum"
      >
        <span class="material-symbols-outlined text-base">chevron_left</span>
      </button>

      <!-- Active Concept Info -->
      <div class="text-center px-1">
        <div class="text-[10px] font-mono font-bold uppercase tracking-wider text-[#8A877F]">
          Step {{ currentStepNum }} of {{ totalSteps }}
        </div>
        <div class="text-xs font-bold text-[#1C1B18] max-w-[160px] sm:max-w-[220px] truncate leading-tight">
          {{ currentNode?.name ?? 'Select a Concept' }}
        </div>
      </div>

      <!-- Next Button -->
      <button
        @click="graphStore.nextPathStep"
        :disabled="!canNext"
        class="w-7 h-7 rounded-lg flex items-center justify-center text-[#5C5A54] hover:text-[#1C1B18] hover:bg-[#EFEFED] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        title="Next concept in curriculum"
      >
        <span class="material-symbols-outlined text-base">chevron_right</span>
      </button>
    </div>

    <!-- Read Dossier Quick Trigger -->
    <button
      v-if="currentNode"
      @click="graphStore.openTopicDossier(currentNode.id)"
      class="hidden sm:flex items-center gap-1 px-2 py-1 text-[11px] font-bold text-white bg-[#3D6B5A] hover:bg-[#2C5043] rounded-lg shadow-sm transition-colors ml-1"
      title="Read everything related to this concept"
    >
      <span class="material-symbols-outlined text-xs">menu_book</span>
      <span>Read Dossier</span>
    </button>
  </div>
</template>

