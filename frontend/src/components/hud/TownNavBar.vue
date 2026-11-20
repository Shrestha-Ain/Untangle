<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGraphStore } from '@/stores/graph'
import { useQuizStore } from '@/stores/quiz'
import { useNotesStore } from '@/stores/notes'
import { useThemeStore } from '@/stores/theme'
import { useProgressStore } from '@/stores/progress'
import ModeBadge from '@/components/shared/ModeBadge.vue'

const props = withDefaults(
  defineProps<{
    title: string
    mode: 'research' | 'study'
    activeFilter: string
    is3DActive?: boolean
  }>(),
  {
    is3DActive: true,
  }
)

const emit = defineEmits<{
  (e: 'update:activeFilter', filter: string): void
  (e: 'recenter'): void
  (e: 'zoomIn'): void
  (e: 'zoomOut'): void
  (e: 'toggle3D'): void
  (e: 'setCameraIsometric'): void
  (e: 'setCameraTopDown'): void
}>()

const router = useRouter()
const graphStore = useGraphStore()
const quizStore = useQuizStore()
const notesStore = useNotesStore()
const themeStore = useThemeStore()
const progressStore = useProgressStore()

const filterOptions = computed(() => {
  if (props.mode === 'study') {
    const chapCount = graphStore.nodes.filter((n) => n.type === 'CHAPTER').length
    const secCount = graphStore.nodes.filter((n) => n.type === 'SECTION').length
    const topCount = graphStore.nodes.filter((n) => n.type === 'TOPIC' || n.type === 'CONCEPT').length
    return [
      { id: 'ALL', label: 'All Elements', icon: 'hub', count: graphStore.nodes.length, activeBg: 'bg-[#0F172A]' },
      { id: 'CHAPTER', label: 'Chapters', icon: 'menu_book', count: chapCount, activeBg: 'bg-[#10B981]' },
      { id: 'SECTION', label: 'Sections', icon: 'segment', count: secCount, activeBg: 'bg-[#F59E0B]' },
      { id: 'TOPIC', label: 'Topics', icon: 'lightbulb', count: topCount, activeBg: 'bg-[#06B6D4]' },
    ]
  }

  const conceptCount = graphStore.nodes.filter((n) => n.type === 'CONCEPT' || n.type === 'TOPIC').length
  const authorCount = graphStore.nodes.filter((n) => n.type === 'PERSON').length
  const orgCount = graphStore.nodes.filter((n) => n.type === 'ORG').length
  const arenaCount = graphStore.nodes.filter((n) => n.type === 'LOCATION').length

  const list = [
    { id: 'ALL', label: 'All Nodes', icon: 'hub', count: graphStore.nodes.length, activeBg: 'bg-[#0F172A]' },
    { id: 'CONCEPT', label: 'Concepts', icon: 'lightbulb', count: conceptCount, activeBg: 'bg-[#06B6D4]' },
    { id: 'PERSON', label: 'Authors', icon: 'person', count: authorCount, activeBg: 'bg-[#8B5CF6]' },
    { id: 'ORG', label: 'Organizations', icon: 'corporate_fare', count: orgCount, activeBg: 'bg-[#2563EB]' },
  ]
  if (arenaCount > 0) {
    list.push({ id: 'LOCATION', label: 'Benchmarks', icon: 'dataset', count: arenaCount, activeBg: 'bg-[#EF4444]' })
  }
  return list
})
</script>

<template>
  <header class="absolute top-4 left-4 right-4 z-40 flex items-center justify-between pointer-events-none gap-3 select-none">
    <!-- Left: Back Button & Realm Title (Solid crisp card) -->
    <div class="pointer-events-auto flex items-center gap-3 bg-white dark:bg-[#0F172A] border-2 border-slate-300 dark:border-slate-800 px-3.5 py-2 rounded-2xl shadow-[0_4px_0_#94A3B8] dark:shadow-[0_4px_0_#020617] transition-colors">
      <button
        @click="router.push('/')"
        class="w-8 h-8 rounded-xl flex items-center justify-center text-slate-700 dark:text-slate-300 hover:text-white hover:bg-blue-600 dark:hover:bg-blue-600 transition-colors"
        title="Back to Dashboard"
      >
        <span class="material-symbols-outlined text-lg">arrow_back</span>
      </button>

      <div class="flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block animate-pulse"></span>
        <span class="text-xs font-black text-slate-900 dark:text-white max-w-[180px] sm:max-w-xs truncate">
          {{ title }}
        </span>
        <ModeBadge :mode="mode" size="sm" />
      </div>
    </div>

    <!-- Center: Type Filters with Solid Color Pills -->
    <div class="pointer-events-auto hidden md:flex items-center gap-1.5 bg-white dark:bg-[#0F172A] border-2 border-slate-300 dark:border-slate-800 p-1.5 rounded-2xl shadow-[0_4px_0_#94A3B8] dark:shadow-[0_4px_0_#020617] transition-colors">
      <button
        v-for="opt in filterOptions"
        :key="opt.id"
        @click="emit('update:activeFilter', opt.id)"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-black transition-all active:scale-95"
        :class="[
          activeFilter === opt.id
            ? `${opt.activeBg} text-white shadow-xs`
            : 'text-slate-700 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-slate-800'
        ]"
      >
        <span class="material-symbols-outlined text-[15px]">{{ opt.icon }}</span>
        <span>{{ opt.label }}</span>
        <span
          class="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-black"
          :class="activeFilter === opt.id ? 'bg-white text-slate-900' : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300'"
        >
          {{ opt.count }}
        </span>
      </button>
    </div>

    <!-- Right: 3D Camera Controls, Quiz, Notes & Exam Gist (Solid Vibrant Colors) -->
    <div class="pointer-events-auto flex items-center gap-2">
      <!-- Theme Switcher (Dark / Light Mode) -->
      <button
        @click="themeStore.toggleTheme"
        class="w-10 h-10 rounded-2xl bg-white dark:bg-[#0F172A] border-2 border-slate-300 dark:border-slate-800 shadow-[0_4px_0_#94A3B8] dark:shadow-[0_4px_0_#020617] flex items-center justify-center text-slate-800 dark:text-amber-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all active:translate-y-0.5 active:shadow-xs"
        :title="themeStore.currentTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
      >
        <span class="material-symbols-outlined text-lg">
          {{ themeStore.currentTheme === 'dark' ? 'light_mode' : 'dark_mode' }}
        </span>
      </button>

      <!-- Study Progress / Mastery Indicator (Shows % and opens breakdown) -->
      <button
        @click="progressStore.openProgressModal"
        class="px-3.5 h-10 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-black text-xs border-2 border-slate-300 dark:border-slate-800 shadow-[0_4px_0_#059669] dark:shadow-[0_4px_0_#020617] flex items-center gap-1.5 transition-all active:translate-y-0.5 active:shadow-xs cursor-pointer"
        :title="`${progressStore.completionPercentage}% of topics studied. Click to view breakdown.`"
      >
        <span class="material-symbols-outlined text-base">donut_large</span>
        <span>{{ progressStore.completionPercentage }}% Mastered</span>
      </button>

      <!-- Quiz Master Trigger (Solid Blue-Teal) -->
      <button
        @click="quizStore.openQuiz('topic')"
        class="px-3.5 h-10 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-black text-xs border-2 border-slate-300 dark:border-slate-800 shadow-[0_4px_0_#1D4ED8] dark:shadow-[0_4px_0_#020617] flex items-center gap-1.5 transition-all active:translate-y-0.5 active:shadow-xs"
        title="Take an Interactive Quiz on Topic or Entire PDF"
      >
        <span class="material-symbols-outlined text-base">quiz</span>
        <span class="hidden sm:inline">Quiz</span>
      </button>

      <!-- Personal Notes Trigger (Solid Amber) -->
      <button
        @click="notesStore.openNotes('topic')"
        class="px-3.5 h-10 rounded-2xl bg-[#F59E0B] hover:bg-[#D97706] text-slate-900 font-black text-xs border-2 border-slate-300 dark:border-slate-800 shadow-[0_4px_0_#B45309] dark:shadow-[0_4px_0_#020617] flex items-center gap-1.5 transition-all active:translate-y-0.5 active:shadow-xs"
        title="Open Personal Topic & Document Notes"
      >
        <span class="material-symbols-outlined text-base">edit_note</span>
        <span class="hidden sm:inline">Notes</span>
      </button>

      <!-- Exam Gist Quick Review Trigger (Solid Crimson Red) -->
      <button
        @click="graphStore.openExamGist()"
        class="px-3.5 h-10 rounded-2xl bg-[#EF4444] hover:bg-[#DC2626] text-white font-black text-xs border-2 border-slate-300 dark:border-slate-800 shadow-[0_4px_0_#B91C1C] dark:shadow-[0_4px_0_#020617] flex items-center gap-1.5 transition-all active:translate-y-0.5 active:shadow-xs"
        title="Open High-Yield Exam Revision Sheet"
      >
        <span class="material-symbols-outlined text-base">bolt</span>
        <span class="hidden sm:inline">Exam Gist</span>
      </button>

      <!-- 3D Camera Controls Box (Solid Card in Soothing Theme) -->
      <div class="flex items-center gap-1 bg-white dark:bg-[#0F172A] border-2 border-slate-300 dark:border-slate-800 p-1 rounded-2xl shadow-[0_4px_0_#94A3B8] dark:shadow-[0_4px_0_#020617]">
        <!-- Isometric Preset -->
        <button
          @click="emit('setCameraIsometric')"
          class="px-2.5 h-8 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-blue-600 hover:text-white text-slate-800 dark:text-slate-200 text-[11px] font-black font-mono flex items-center gap-1 transition-colors active:scale-95"
          title="Snap camera to 3D Isometric View"
        >
          <span>3D Iso</span>
        </button>

        <!-- Top-Down Preset -->
        <button
          @click="emit('setCameraTopDown')"
          class="px-2.5 h-8 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-cyan-600 hover:text-white text-slate-800 dark:text-slate-200 text-[11px] font-black font-mono flex items-center gap-1 transition-colors active:scale-95"
          title="Snap camera to Top-Down 3D View"
        >
          <span>Top</span>
        </button>

        <div class="w-px h-5 bg-slate-200 dark:bg-slate-700 mx-0.5"></div>

        <!-- Zoom In -->
        <button
          @click="emit('zoomIn')"
          class="w-8 h-8 rounded-xl flex items-center justify-center text-slate-800 dark:text-slate-200 hover:bg-blue-50 dark:hover:bg-slate-800 transition-colors active:scale-95"
          title="Zoom In"
        >
          <span class="material-symbols-outlined text-base font-bold">add</span>
        </button>

        <!-- Zoom Out -->
        <button
          @click="emit('zoomOut')"
          class="w-8 h-8 rounded-xl flex items-center justify-center text-slate-800 dark:text-slate-200 hover:bg-blue-50 dark:hover:bg-slate-800 transition-colors active:scale-95"
          title="Zoom Out"
        >
          <span class="material-symbols-outlined text-base font-bold">remove</span>
        </button>

        <!-- Reset / Center All -->
        <button
          @click="emit('recenter')"
          class="w-8 h-8 rounded-xl flex items-center justify-center text-white bg-blue-600 hover:bg-blue-500 transition-colors active:scale-95"
          title="Frame All Buildings (Reset 3D Camera)"
        >
          <span class="material-symbols-outlined text-base">crop_free</span>
        </button>
      </div>
    </div>
  </header>
</template>
