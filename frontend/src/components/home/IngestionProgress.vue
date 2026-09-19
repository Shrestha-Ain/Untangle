<script setup lang="ts">
import { computed } from 'vue'
import { useDocumentsStore } from '@/stores/documents'

const documentsStore = useDocumentsStore()
const ingestion = computed(() => documentsStore.ingestionState)

const activeDoc = computed(() => {
  if (!ingestion.value?.documentId) return null
  return documentsStore.documents.find((d) => d.id === ingestion.value?.documentId)
})

const mode = computed(() => activeDoc.value?.source_mode ?? 'research')

const steps = computed(() => {
  if (mode.value === 'study') {
    return [
      { id: 'parse', label: '1. Parse Book' },
      { id: 'extract', label: '2. Hierarchy Deconstruction' },
      { id: 'link', label: '3. Conceptual Links' },
    ]
  }
  return [
    { id: 'parse', label: '1. Parse Chunks' },
    { id: 'extract', label: '2. Entity Extraction' },
    { id: 'cluster', label: '3. Leiden Clustering' },
  ]
})

function isStepDone(stepId: string) {
  const current = ingestion.value?.step
  if (!current) return false
  if (current === 'ready') return true
  if (stepId === 'parse') return current !== 'parse'
  if (stepId === 'extract') return (current as string) === 'cluster' || (current as string) === 'link'
  return false
}

function isStepActive(stepId: string) {
  return ingestion.value?.step === stepId
}
</script>

<template>
  <div
    v-if="ingestion"
    class="w-full bg-white rounded-2xl border border-[#E4E3DF] p-6 shadow-[0_1px_3px_rgba(28,27,24,0.08)] space-y-4 transition-all"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <span class="w-2.5 h-2.5 rounded-full bg-[#3D6B5A] animate-pulse"></span>
        <div>
          <h3 class="text-sm font-bold text-[#1C1B18]">
            Constructing Knowledge Map: {{ activeDoc?.title ?? 'Active Document' }}
          </h3>
          <p class="text-xs text-[#5C5A54] mt-0.5">{{ ingestion.detail }}</p>
        </div>
      </div>
      <span class="text-xs font-mono font-bold text-[#3D6B5A] bg-[#E8F0EC] px-2 py-0.5 rounded border border-[#C4D8CC]">
        {{ ingestion.progress }}%
      </span>
    </div>

    <!-- Progress Bar -->
    <div class="w-full bg-[#EFEFED] rounded-full h-2 overflow-hidden">
      <div
        class="h-full transition-all duration-300 rounded-full"
        :class="mode === 'study' ? 'bg-[#C49A3C]' : 'bg-[#3D6B5A]'"
        :style="{ width: `${ingestion.progress}%` }"
      ></div>
    </div>

    <!-- Stepper Indicator -->
    <div class="grid grid-cols-3 gap-2 pt-1">
      <div
        v-for="step in steps"
        :key="step.id"
        class="flex items-center gap-2 p-2 rounded-lg border text-xs font-medium"
        :class="[
          isStepDone(step.id)
            ? 'bg-[#E8F0EC]/60 border-[#C4D8CC] text-[#3D6B5A]'
            : isStepActive(step.id)
            ? 'bg-white border-[#3D6B5A] text-[#1C1B18] shadow-sm font-bold'
            : 'bg-[#F7F6F3] border-[#E4E3DF] text-[#8A877F]'
        ]"
      >
        <span
          v-if="isStepDone(step.id)"
          class="material-symbols-outlined text-sm text-[#4E9A7D]"
        >
          check_circle
        </span>
        <span
          v-else-if="isStepActive(step.id)"
          class="w-3.5 h-3.5 rounded-full border-2 border-[#3D6B5A] border-t-transparent animate-spin inline-block flex-shrink-0"
        ></span>
        <span
          v-else
          class="w-3.5 h-3.5 rounded-full bg-[#D4D3CE] inline-block flex-shrink-0"
        ></span>
        <span class="truncate">{{ step.label }}</span>
      </div>
    </div>
  </div>
</template>
