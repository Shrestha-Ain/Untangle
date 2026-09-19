<script setup lang="ts">
import { computed } from 'vue'
import { useGraphStore } from '@/stores/graph'

const props = defineProps<{
  mode: 'research' | 'study'
}>()

const graphStore = useGraphStore()
const entity = computed(() => graphStore.selectedEntity)

const connectedRoadsCount = computed(() => {
  if (!entity.value) return 0
  return graphStore.edges.filter(
    (e) => e.source_id === entity.value?.id || e.target_id === entity.value?.id
  ).length
})

const cardTheme = computed(() => {
  if (!entity.value) {
    return {
      bg: 'bg-teal-50',
      text: 'text-teal-700',
      border: 'border-teal-200',
      iconBg: 'bg-teal-100',
      iconText: 'text-teal-700',
      icon: 'lightbulb',
    }
  }
  switch (entity.value.type) {
    case 'PERSON':
      return {
        bg: 'bg-purple-50',
        text: 'text-purple-700',
        border: 'border-purple-200',
        iconBg: 'bg-purple-100',
        iconText: 'text-purple-700',
        icon: 'person',
      }
    case 'ORG':
      return {
        bg: 'bg-blue-50',
        text: 'text-blue-700',
        border: 'border-blue-200',
        iconBg: 'bg-blue-100',
        iconText: 'text-blue-700',
        icon: 'corporate_fare',
      }
    case 'LOCATION':
      return {
        bg: 'bg-amber-50',
        text: 'text-amber-800',
        border: 'border-amber-200',
        iconBg: 'bg-amber-100',
        iconText: 'text-amber-800',
        icon: 'dataset',
      }
    case 'CHAPTER':
      return {
        bg: 'bg-emerald-50',
        text: 'text-emerald-800',
        border: 'border-emerald-200',
        iconBg: 'bg-emerald-100',
        iconText: 'text-emerald-800',
        icon: 'menu_book',
      }
    case 'SECTION':
      return {
        bg: 'bg-amber-50',
        text: 'text-amber-800',
        border: 'border-amber-200',
        iconBg: 'bg-amber-100',
        iconText: 'text-amber-800',
        icon: 'segment',
      }
    case 'TOPIC':
    case 'CONCEPT':
    default:
      return {
        bg: 'bg-cyan-50',
        text: 'text-cyan-800',
        border: 'border-cyan-200',
        iconBg: 'bg-cyan-100',
        iconText: 'text-cyan-700',
        icon: 'lightbulb',
      }
  }
})

function closeCard() {
  graphStore.selectEntity(null)
}

function exploreConnections() {
  if (!entity.value) return
  const neighborIds = [entity.value.id]
  const edgeIds: string[] = []

  graphStore.edges.forEach((e) => {
    if (e.source_id === entity.value?.id) {
      neighborIds.push(e.target_id)
      edgeIds.push(e.id)
    } else if (e.target_id === entity.value?.id) {
      neighborIds.push(e.source_id)
      edgeIds.push(e.id)
    }
  })

  graphStore.highlightSubgraph({ nodeIds: neighborIds, edgeIds })
}

function findExternalReferences() {
  if (!entity.value) return
  window.alert(
    'Cross-source search: Querying user library for additional reference papers related to ' +
      entity.value.name
  )
}
</script>

<template>
  <aside
    v-if="entity"
    class="fixed top-20 right-4 w-80 bg-white/95 backdrop-blur-xl rounded-3xl p-5 shadow-[0_12px_40px_rgba(0,0,0,0.12)] border border-white/80 z-30 space-y-4 drawer-scroll animate-in fade-in slide-in-from-right-4 duration-200"
  >
    <!-- Header with Type Icon Avatar & Close Button (page2 style) -->
    <div class="flex items-start justify-between">
      <div class="flex items-center gap-2.5">
        <div
          class="w-10 h-10 rounded-2xl flex items-center justify-center shadow-xs"
          :class="[cardTheme.iconBg, cardTheme.iconText]"
        >
          <span class="material-symbols-outlined text-xl">{{ cardTheme.icon }}</span>
        </div>
        <div>
          <span
            class="font-mono text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border"
            :class="[cardTheme.bg, cardTheme.text, cardTheme.border]"
          >
            {{ entity.type }}
          </span>
          <h2 class="font-bold text-[#1C1B18] text-base leading-tight mt-1 line-clamp-1">
            {{ entity.name }}
          </h2>
        </div>
      </div>
      <button
        @click="closeCard"
        class="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition-colors"
        title="Close details"
      >
        <span class="material-symbols-outlined text-[16px]">close</span>
      </button>
    </div>

    <!-- Quick Stats Grid (Clean academic telemetry) -->
    <div class="grid grid-cols-3 gap-2">
      <div class="bg-slate-50 rounded-2xl p-2.5 text-center border border-slate-100">
        <div class="text-[10px] font-bold text-slate-400 uppercase">Type</div>
        <div class="font-mono font-bold text-[#0D9488] text-xs truncate max-w-[80px] mx-auto mt-0.5">
          {{ entity.type }}
        </div>
      </div>
      <div class="bg-slate-50 rounded-2xl p-2.5 text-center border border-slate-100">
        <div class="text-[10px] font-bold text-slate-400 uppercase">
          {{ mode === 'study' ? 'Depth' : 'Mentions' }}
        </div>
        <div class="font-mono font-bold text-[#7C3AED] text-base">{{ entity.mention_count ?? 1 }}×</div>
      </div>
      <div class="bg-slate-50 rounded-2xl p-2.5 text-center border border-slate-100">
        <div class="text-[10px] font-bold text-slate-400 uppercase">Connections</div>
        <div class="font-mono font-bold text-[#D97706] text-base">{{ connectedRoadsCount }}</div>
      </div>
    </div>

    <!-- Description -->
    <p class="text-xs text-slate-600 leading-relaxed bg-slate-50/80 p-3.5 rounded-2xl border border-slate-100">
      {{ entity.description || 'Core concept extracted during knowledge graph analysis.' }}
    </p>

    <!-- Action Buttons -->
    <div class="space-y-2 pt-1">
      <button
        @click="graphStore.openTopicDossier(entity.id)"
        class="w-full py-2.5 text-xs font-bold text-white bg-[#3D6B5A] hover:bg-[#2C5043] rounded-xl shadow-[0_3px_0_#2C5043] active:translate-y-px transition-all flex items-center justify-center gap-1.5"
      >
        <span class="material-symbols-outlined text-sm">menu_book</span>
        <span>Read Everything on This Topic</span>
      </button>

      <button
        @click="exploreConnections"
        class="w-full py-2 text-xs font-semibold text-[#1C1B18] bg-[#EFEFED] hover:bg-[#E4E3DF] rounded-xl border border-[#D4D3CE] active:translate-y-px transition-all flex items-center justify-center gap-1.5"
      >
        <span class="material-symbols-outlined text-sm text-[#3D6B5A]">hub</span>
        <span>Highlight Connections</span>
      </button>

      <button
        v-if="mode === 'study'"
        @click="findExternalReferences"
        class="w-full py-1.5 text-xs font-medium text-[#8C6A2C] bg-[#F5EFE3] hover:bg-[#EFE8D6] rounded-xl border border-[#DDD0B0] transition-colors flex items-center justify-center gap-1.5"
      >
        <span class="material-symbols-outlined text-sm">link</span>
        <span>Find External References</span>
      </button>
    </div>
  </aside>
</template>
