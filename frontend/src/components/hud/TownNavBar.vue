<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGraphStore } from '@/stores/graph'
import ModeBadge from '@/components/shared/ModeBadge.vue'

const props = defineProps<{
  title: string
  mode: 'research' | 'study'
  activeFilter: string
}>()

const emit = defineEmits<{
  (e: 'update:activeFilter', filter: string): void
  (e: 'recenter'): void
  (e: 'zoomIn'): void
  (e: 'zoomOut'): void
}>()

const router = useRouter()
const graphStore = useGraphStore()

const filterOptions = computed(() => {
  if (props.mode === 'study') {
    const chapCount = graphStore.nodes.filter((n) => n.type === 'CHAPTER').length
    const secCount = graphStore.nodes.filter((n) => n.type === 'SECTION').length
    const topCount = graphStore.nodes.filter((n) => n.type === 'TOPIC' || n.type === 'CONCEPT').length
    return [
      { id: 'ALL', label: 'All Elements', icon: 'hub', count: graphStore.nodes.length },
      { id: 'CHAPTER', label: 'Chapters', icon: 'menu_book', count: chapCount },
      { id: 'SECTION', label: 'Sections', icon: 'segment', count: secCount },
      { id: 'TOPIC', label: 'Topics', icon: 'lightbulb', count: topCount },
    ]
  }

  const conceptCount = graphStore.nodes.filter((n) => n.type === 'CONCEPT' || n.type === 'TOPIC').length
  const authorCount = graphStore.nodes.filter((n) => n.type === 'PERSON').length
  const orgCount = graphStore.nodes.filter((n) => n.type === 'ORG').length
  const arenaCount = graphStore.nodes.filter((n) => n.type === 'LOCATION').length

  const list = [
    { id: 'ALL', label: 'All Nodes', icon: 'hub', count: graphStore.nodes.length },
    { id: 'CONCEPT', label: 'Concepts', icon: 'lightbulb', count: conceptCount },
    { id: 'PERSON', label: 'Authors', icon: 'person', count: authorCount },
    { id: 'ORG', label: 'Organizations', icon: 'corporate_fare', count: orgCount },
  ]
  if (arenaCount > 0) {
    list.push({ id: 'LOCATION', label: 'Benchmarks', icon: 'dataset', count: arenaCount })
  }
  return list
})
</script>

<template>
  <header class="absolute top-4 left-4 right-4 z-10 flex items-center justify-between pointer-events-none gap-3">
    <!-- Left: Back Button & Realm Title -->
    <div class="pointer-events-auto flex items-center gap-3 bg-white/95 backdrop-blur-md border border-white/80 px-3.5 py-2 rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.08)]">
      <button
        @click="router.push('/')"
        class="w-8 h-8 rounded-xl flex items-center justify-center text-[#5C5A54] hover:text-[#1C1B18] hover:bg-[#EFEFED] transition-colors"
        title="Back to Dashboard"
      >
        <span class="material-symbols-outlined text-lg">arrow_back</span>
      </button>

      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-[20px] text-teal-700">hub</span>
        <span class="text-xs font-extrabold text-[#1C1B18] max-w-[180px] sm:max-w-xs truncate">
          {{ title }}
        </span>
        <ModeBadge :mode="mode" size="sm" />
      </div>
    </div>

    <!-- Center: Type Filters with Count Badges (page2 style) -->
    <div class="pointer-events-auto hidden md:flex items-center gap-1.5 bg-white/95 backdrop-blur-md border border-white/80 p-1.5 rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.08)]">
      <button
        v-for="opt in filterOptions"
        :key="opt.id"
        @click="emit('update:activeFilter', opt.id)"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all"
        :class="[
          activeFilter === opt.id
            ? 'bg-[#00685F] text-white shadow-xs'
            : 'text-slate-600 hover:bg-slate-100 hover:text-slate-800'
        ]"
      >
        <span class="material-symbols-outlined text-[15px]">{{ opt.icon }}</span>
        <span>{{ opt.label }}</span>
        <span
          class="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold"
          :class="activeFilter === opt.id ? 'bg-white/20 text-white' : 'bg-slate-200/80 text-slate-600'"
        >
          {{ opt.count }}
        </span>
      </button>
    </div>

    <!-- Right: Pan/Zoom Controls & Exam Gist Trigger -->
    <div class="pointer-events-auto flex items-center gap-2">
      <!-- Exam Gist Quick Review Button -->
      <button
        @click="graphStore.openExamGist()"
        class="px-3.5 h-10 rounded-2xl bg-gradient-to-r from-amber-500 to-amber-600 text-white font-bold text-xs shadow-md hover:brightness-105 flex items-center gap-1.5 transition-all active:scale-95"
        title="Open High-Yield Exam Revision Sheet"
      >
        <span class="material-symbols-outlined text-base">bolt</span>
        <span class="hidden sm:inline">Exam Gist</span>
      </button>

      <!-- View Controls -->
      <div class="flex items-center gap-1 bg-white/95 backdrop-blur-md border border-white/80 p-1 rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.08)]">
        <button
          @click="emit('zoomIn')"
          class="w-8 h-8 rounded-xl flex items-center justify-center text-slate-700 hover:bg-slate-100 transition-colors active:scale-95"
          title="Zoom In"
        >
          <span class="material-symbols-outlined text-base">add</span>
        </button>
        <button
          @click="emit('zoomOut')"
          class="w-8 h-8 rounded-xl flex items-center justify-center text-slate-700 hover:bg-slate-100 transition-colors active:scale-95"
          title="Zoom Out"
        >
          <span class="material-symbols-outlined text-base">remove</span>
        </button>
        <button
          @click="emit('recenter')"
          class="w-8 h-8 rounded-xl flex items-center justify-center text-slate-700 hover:bg-slate-100 transition-colors active:scale-95"
          title="Recenter Map"
        >
          <span class="material-symbols-outlined text-base">filter_center_focus</span>
        </button>
      </div>
    </div>
  </header>
</template>
