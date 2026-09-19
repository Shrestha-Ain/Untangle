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
    class="bg-white rounded-3xl border-2 border-[#E4E3DF] p-6 shadow-[0_2px_12px_rgba(28,27,24,0.06)] hover:shadow-[0_8px_30px_rgba(28,27,24,0.12)] hover:-translate-y-1 hover:border-[#D4D3CE] transition-all duration-200 flex flex-col justify-between group relative overflow-hidden"
  >
    <!-- Soft Decorative Top-Right Corner Glow -->
    <div
      class="absolute -top-16 -right-16 w-32 h-32 rounded-full blur-2xl pointer-events-none transition-opacity duration-300 opacity-40 group-hover:opacity-70"
      :class="doc.source_mode === 'study' ? 'bg-amber-100' : 'bg-emerald-100'"
    ></div>

    <!-- Top Row: Mode Badge + Status / Delete Button -->
    <div class="relative z-10">
      <div class="flex items-center justify-between gap-2 mb-3.5">
        <ModeBadge :mode="doc.source_mode" size="sm" />
        <div class="flex items-center gap-1.5">
          <span
            v-if="doc.status !== 'ready'"
            class="px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider bg-amber-50 text-amber-800 border border-amber-200 rounded-md"
          >
            {{ doc.status }}
          </span>
          <button
            @click.stop="emit('delete', doc.id)"
            class="opacity-0 group-hover:opacity-100 text-[#8A877F] hover:text-[#A85A5A] p-1 rounded-lg hover:bg-[#EFEFED] transition-all"
            title="Delete map"
          >
            <span class="material-symbols-outlined text-base">delete</span>
          </button>
        </div>
      </div>

      <!-- Title & Author -->
      <h3 class="text-base font-extrabold text-[#1C1B18] line-clamp-2 leading-snug group-hover:text-[#3D6B5A] transition-colors">
        {{ doc.title }}
      </h3>
      <p class="text-xs text-[#5C5A54] mt-1 line-clamp-1 font-medium">
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

      <!-- Interactive Concept Mini-Tag Strip (Lively touch) -->
      <div class="flex flex-wrap gap-1 mb-4">
        <span
          v-for="tag in previewTags"
          :key="tag"
          class="px-2 py-0.5 text-[10px] font-mono font-medium rounded-md bg-[#F7F6F3] text-[#5C5A54] border border-[#E4E3DF]"
        >
          #{{ tag }}
        </span>
      </div>
    </div>

    <!-- Bottom Actions -->
    <div class="relative z-10 pt-3 border-t border-[#EFEFED] flex items-center justify-between">
      <span class="text-[11px] font-mono text-[#8A877F]">
        {{ new Date(doc.created_at).toLocaleDateString() }}
      </span>

      <div v-if="doc.status === 'ready'" class="flex items-center gap-2">
        <button
          @click.stop="graphStore.openExamGist(doc.id)"
          class="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-semibold text-[#8C6A2C] bg-[#F5EFE3] hover:bg-[#EBDDBF] border border-[#DDD0B0] rounded-xl transition-all active:translate-y-px"
          title="Review High-Yield Exam Gist"
        >
          <span class="material-symbols-outlined text-sm text-[#C49A3C]">bolt</span>
          <span>Exam Gist</span>
        </button>

        <button
          @click="openMap"
          class="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold text-white bg-[#3D6B5A] hover:bg-[#2C5043] rounded-xl shadow-[0_3px_0_#2C5043] active:translate-y-px transition-all"
        >
          <span>Open Map</span>
          <span class="material-symbols-outlined text-xs">arrow_forward</span>
        </button>
      </div>

      <span
        v-else
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[#8A877F] bg-[#EFEFED] rounded-xl cursor-not-allowed"
      >
        <span class="w-3 h-3 rounded-full border-2 border-[#8A877F] border-t-transparent animate-spin inline-block"></span>
        Processing
      </span>
    </div>
  </div>
</template>
