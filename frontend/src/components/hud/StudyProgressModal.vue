<script setup lang="ts">
import { computed } from 'vue'
import { useProgressStore } from '@/stores/progress'
import { useGraphStore } from '@/stores/graph'

const props = defineProps<{
  mode: 'research' | 'study'
}>()

const progressStore = useProgressStore()
const graphStore = useGraphStore()

const percentage = computed(() => progressStore.completionPercentage)
const breakdown = computed(() => progressStore.topicBreakdown)
const completedCount = computed(() => progressStore.completedTopics.length)
const totalCount = computed(() => progressStore.totalTopics)

function handleSelectTopic(topicId: string) {
  graphStore.selectEntity(topicId)
  const idx = graphStore.learningPath.indexOf(topicId)
  if (idx !== -1) {
    graphStore.setPathIndex(idx)
  }
  progressStore.closeProgressModal()
}

function toggleComplete(topicId: string) {
  progressStore.toggleTopicCompletion(topicId)
}

function handleMarkAll() {
  breakdown.value.forEach((t) => {
    progressStore.markTopicCompleted(t.id)
  })
}

function handleReset() {
  if (confirm('Reset your study progress for this document?')) {
    progressStore.resetProgress()
  }
}
</script>

<template>
  <!-- Modal Backdrop -->
  <div
    v-if="progressStore.isProgressModalOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-950/80 backdrop-blur-md animate-in fade-in select-none"
    @click.self="progressStore.closeProgressModal"
  >
    <!-- Modal Card -->
    <div
      class="relative w-full max-w-lg bg-white dark:bg-[#0B1120] rounded-3xl border-2 border-slate-200 dark:border-slate-800 shadow-[0_24px_64px_rgba(15,23,42,0.24)] flex flex-col max-h-[85vh] overflow-hidden text-slate-900 dark:text-white"
    >
      <!-- Header -->
      <div class="px-5 py-4 bg-[#F0F4F8] dark:bg-[#0F172A] border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-blue-600 text-white flex items-center justify-center shadow-md font-black text-lg">
            <span class="material-symbols-outlined text-2xl">analytics</span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="font-extrabold text-sm tracking-tight">
                {{ mode === 'study' ? 'Curriculum Study Progress' : 'Research Paper Mastery Tracker' }}
              </h3>
              <span class="px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-sky-300 border border-blue-200 dark:border-blue-800 text-[10px] font-mono font-bold">
                {{ mode === 'study' ? 'Syllabus' : 'Literature' }}
              </span>
            </div>
            <p class="text-[11px] text-slate-500 dark:text-slate-400">
              Track your reading, concept mastery, and prerequisite milestone completion.
            </p>
          </div>
        </div>

        <button
          @click="progressStore.closeProgressModal"
          class="w-8 h-8 rounded-xl bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-300 flex items-center justify-center transition-colors border border-slate-200 dark:border-slate-700 cursor-pointer"
          title="Close progress tracker"
        >
          <span class="material-symbols-outlined text-lg">close</span>
        </button>
      </div>

      <!-- Main Progress Hero Card -->
      <div class="p-5 border-b border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-900/40">
        <div class="flex items-center justify-between gap-4">
          <div class="space-y-1">
            <span class="text-[11px] font-mono uppercase tracking-wider font-extrabold text-blue-600 dark:text-sky-400">
              Overall Completion
            </span>
            <div class="flex items-baseline gap-2">
              <span class="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">
                {{ percentage }}%
              </span>
              <span class="text-xs font-bold text-slate-500 dark:text-slate-400">
                ({{ completedCount }} of {{ totalCount }} Topics Mastered)
              </span>
            </div>
            <p class="text-[11.5px] text-slate-500 dark:text-slate-400">
              {{ percentage === 100 ? '🎉 Exceptional! Full curriculum mastered!' : percentage >= 50 ? '⚡ Great momentum! Over halfway through the material.' : '📖 In progress. Review topics and test with Quiz Master.' }}
            </p>
          </div>

          <!-- Circular Metric Pill -->
          <div class="relative w-16 h-16 rounded-full border-4 border-slate-200 dark:border-slate-800 flex items-center justify-center shrink-0">
            <div
              class="absolute inset-0 rounded-full border-4 border-blue-600 dark:border-sky-400 transition-all duration-500"
              :style="{ clipPath: `polygon(0 0, 100% 0, 100% ${percentage}%, 0 ${percentage}%)` }"
            ></div>
            <span class="material-symbols-outlined text-2xl text-blue-600 dark:text-sky-400">
              {{ percentage === 100 ? 'verified' : 'school' }}
            </span>
          </div>
        </div>

        <!-- Solid Progress Bar (No Gradients) -->
        <div class="w-full h-2.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden mt-4">
          <div
            class="h-full bg-blue-600 dark:bg-sky-400 rounded-full transition-all duration-500"
            :style="{ width: `${percentage}%` }"
          ></div>
        </div>
      </div>

      <!-- Topic List Header with Bulk Actions -->
      <div class="px-5 py-2.5 bg-white dark:bg-[#0B1120] border-b border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs">
        <span class="font-extrabold text-slate-800 dark:text-slate-200 flex items-center gap-1.5 font-mono">
          <span class="material-symbols-outlined text-sm text-blue-600 dark:text-sky-400">format_list_bulleted</span>
          Topic Breakdown by Percentage
        </span>

        <div class="flex items-center gap-2">
          <button
            @click="handleMarkAll"
            class="text-[10.5px] font-bold text-blue-600 dark:text-sky-400 hover:underline cursor-pointer"
          >
            Mark All Done
          </button>
          <span class="text-slate-300 dark:text-slate-700">•</span>
          <button
            @click="handleReset"
            class="text-[10.5px] font-bold text-rose-500 hover:underline cursor-pointer"
          >
            Reset
          </button>
        </div>
      </div>

      <!-- Topics Scrollable Breakdown List -->
      <div class="flex-1 overflow-y-auto p-4 space-y-2 regulus-scroll select-text">
        <div
          v-for="topic in breakdown"
          :key="topic.id"
          class="p-3 rounded-2xl border transition-all flex items-center justify-between gap-3 group"
          :class="[
            topic.isCompleted
              ? 'bg-emerald-50/60 dark:bg-emerald-950/20 border-emerald-300 dark:border-emerald-800/60'
              : 'bg-white dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 hover:border-blue-400 dark:hover:border-blue-600',
          ]"
        >
          <!-- Left: Checkbox & Name -->
          <div class="flex items-center gap-3 min-w-0">
            <!-- Toggle Checkbox Button -->
            <button
              @click.stop="toggleComplete(topic.id)"
              class="w-6 h-6 rounded-lg flex items-center justify-center transition-all cursor-pointer shrink-0 border"
              :class="[
                topic.isCompleted
                  ? 'bg-emerald-600 border-emerald-600 text-white shadow-xs'
                  : 'bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-transparent hover:border-blue-500',
              ]"
              :title="topic.isCompleted ? 'Mark as Incomplete' : 'Mark as Mastered'"
            >
              <span class="material-symbols-outlined text-sm font-black">check</span>
            </button>

            <!-- Name and Step Number -->
            <div class="min-w-0 cursor-pointer text-left" @click="handleSelectTopic(topic.id)">
              <div class="flex items-center gap-1.5">
                <span class="text-[9.5px] font-mono px-1.5 py-0.2 rounded font-bold"
                  :class="topic.isCompleted ? 'bg-emerald-200 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'"
                >
                  Step {{ topic.stepIndex }}
                </span>
                <span class="text-[9px] font-mono uppercase font-bold text-slate-400">
                  {{ topic.type }}
                </span>
              </div>
              <h4
                class="text-xs font-bold leading-snug truncate group-hover:text-blue-600 dark:group-hover:text-sky-300 mt-0.5"
                :class="topic.isCompleted ? 'text-emerald-900 dark:text-emerald-200 line-through opacity-85' : 'text-slate-900 dark:text-slate-100'"
              >
                {{ topic.name }}
              </h4>
            </div>
          </div>

          <!-- Right: Percentage Weight & Jump Action -->
          <div class="flex items-center gap-2 shrink-0">
            <span class="px-2 py-0.5 rounded-md font-mono text-[10px] font-bold"
              :class="topic.isCompleted ? 'bg-emerald-100 dark:bg-emerald-900/80 text-emerald-800 dark:text-emerald-200' : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'"
            >
              {{ topic.percentageWeight }}%
            </span>

            <button
              @click.stop="handleSelectTopic(topic.id)"
              class="p-1 rounded-lg text-slate-400 hover:text-blue-600 dark:hover:text-sky-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
              title="Focus this topic on the 3D map"
            >
              <span class="material-symbols-outlined text-base">near_me</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-5 py-3 bg-[#F0F4F8] dark:bg-[#0F172A] border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs">
        <span class="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
          Persisted locally • Updates 3D Map & Quiz progress
        </span>

        <button
          @click="progressStore.closeProgressModal"
          class="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs transition-colors cursor-pointer shadow-xs"
        >
          Done
        </button>
      </div>
    </div>
  </div>
</template>
