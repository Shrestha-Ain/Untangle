<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGraphStore } from '@/stores/graph'
import type { DocumentItem } from '@/stores/documents'
import ModeBadge from '@/components/shared/ModeBadge.vue'
import StatCounter from '@/components/shared/StatCounter.vue'

const props = defineProps<{
  doc: DocumentItem
}>()

const emit = defineEmits<{
  (e: 'delete', id: string): void
}>()

const router = useRouter()
const graphStore = useGraphStore()

function openMap() {
  router.push(`/realm/${props.doc.id}`)
}

// Sample top preview tags for lively card presentation
const previewTags = computed(() => {
  if (props.doc.id === 'doc-attention-1706') {
    return ['Attention', 'Vaswani', 'Scaled Dot-Product', 'Ensemble']
  }
  if (props.doc.id === 'doc-ostep-book') {
    return ['Virtualization', 'Concurrency', 'Process API', 'Locks']
  }
  if (props.doc.source_mode === 'study') {
    return ['Chapters', 'Sections', 'Concepts']
  }
  return ['Entities', 'Triples', 'Communities']
})
</script>

<template>
  <div
    class="bg-white dark:bg-[#0F172A] rounded-3xl border-2 border-slate-200 dark:border-slate-800 p-6 shadow-[0_2px_12px_rgba(15,23,42,0.06)] dark:shadow-[0_4px_24px_rgba(0,0,0,0.4)] hover:shadow-[0_8px_30px_rgba(37,99,235,0.12)] dark:hover:shadow-[0_8px_30px_rgba(37,99,235,0.2)] hover:-translate-y-1 hover:border-blue-400 dark:hover:border-blue-600 transition-all duration-200 flex flex-col justify-between group relative overflow-hidden"
  >
    <!-- Soft Decorative Top-Right Corner Glow -->
    <div
      class="absolute -top-16 -right-16 w-32 h-32 rounded-full blur-2xl pointer-events-none transition-opacity duration-300 opacity-40 group-hover:opacity-70"
      :class="doc.source_mode === 'study' ? 'bg-cyan-100 dark:bg-cyan-900/30' : 'bg-blue-100 dark:bg-blue-900/30'"
    ></div>

    <!-- Top Row: Mode Badge + Status / Delete Button -->
    <div class="relative z-10">
      <div class="flex items-center justify-between gap-2 mb-3.5">
        <ModeBadge :mode="doc.source_mode" size="sm" />
        <div class="flex items-center gap-1.5">
          <span
            v-if="doc.status !== 'ready'"
            class="px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider bg-amber-50 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded-md"
          >
            {{ doc.status }}
          </span>
          <button
            @click.stop="emit('delete', doc.id)"
            class="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
            title="Delete map"
          >
            <span class="material-symbols-outlined text-base">delete</span>
          </button>
        </div>
      </div>

      <!-- Title & Author -->
      <h3 class="text-base font-extrabold text-slate-900 dark:text-white line-clamp-2 leading-snug group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
        {{ doc.title }}
      </h3>
      <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-1 font-medium">
        {{ doc.author ?? doc.filename }}
      </p>

      <!-- Stats Grid -->
      <div class="grid grid-cols-3 gap-2 my-4">
        <template v-if="doc.source_mode === 'research'">
          <StatCounter label="Entities" :value="doc.entity_count" />
          <StatCounter label="Roads" :value="doc.relationship_count" />
          <StatCounter label="Districts" :value="doc.community_count" />
        </template>
        <template v-else>
          <StatCounter label="Chapters" :value="doc.chapter_count" />
          <StatCounter label="Sections" :value="doc.section_count" />
          <StatCounter label="Topics" :value="doc.topic_count" />
        </template>
      </div>

      <!-- Interactive Concept Mini-Tag Strip -->
      <div class="flex flex-wrap gap-1 mb-4">
        <span
          v-for="tag in previewTags"
          :key="tag"
          class="px-2 py-0.5 text-[10px] font-mono font-medium rounded-md bg-slate-100 dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700"
        >
          #{{ tag }}
        </span>
      </div>
    </div>

    <!-- Bottom Actions -->
    <div class="relative z-10 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
      <span class="text-[11px] font-mono text-slate-400 dark:text-slate-500">
        {{ new Date(doc.created_at).toLocaleDateString() }}
      </span>

      <div v-if="doc.status === 'ready'" class="flex items-center gap-2">
        <button
          @click.stop="graphStore.openExamGist(doc.id)"
          class="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-semibold text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/60 hover:bg-amber-100 dark:hover:bg-amber-900/60 border border-amber-200 dark:border-amber-800 rounded-xl transition-all active:translate-y-px"
          title="Review High-Yield Exam Gist"
        >
          <span class="material-symbols-outlined text-sm text-amber-500">bolt</span>
          <span>Exam Gist</span>
        </button>

        <button
          @click="openMap"
          class="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 rounded-xl shadow-[0_3px_0_#1D4ED8] active:translate-y-px transition-all"
        >
          <span>Open Map</span>
          <span class="material-symbols-outlined text-xs">arrow_forward</span>
        </button>
      </div>

      <span
        v-else
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-400 bg-slate-100 dark:bg-slate-800 rounded-xl cursor-not-allowed"
      >
        <span class="w-3 h-3 rounded-full border-2 border-slate-400 border-t-transparent animate-spin inline-block"></span>
        Processing
      </span>
    </div>
  </div>
</template>
