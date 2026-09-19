<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  id: string
  path: string
  relationType: string
  isCrossSource?: boolean
  sourcePos?: { x: number; y: number }
  targetPos?: { x: number; y: number }
}>()

const strokeColor = computed(() => {
  if (props.isCrossSource) return '#F59E0B' // bright amber for cross-source
  const rel = props.relationType.toUpperCase()
  if (rel.includes('FOUNDATION') || rel.includes('TOPIC')) return '#38BDF8' // bright cyan
  if (rel.includes('WORKS') || rel.includes('AUTHOR') || rel.includes('PROPOSED')) return '#A855F7' // purple
  if (rel.includes('COMBINED') || rel.includes('LEADS')) return '#06B6D4' // deep cyan
  if (rel.includes('INFLUENCE') || rel.includes('CONTAINS')) return '#10B981' // emerald
  return '#38BDF8'
})

const midX = computed(() => {
  if (!props.sourcePos || !props.targetPos) return 0
  return (props.sourcePos.x + props.targetPos.x) / 2
})

const midY = computed(() => {
  if (!props.sourcePos || !props.targetPos) return 0
  return (props.sourcePos.y + props.targetPos.y) / 2 - 10
})
</script>

<template>
  <g :id="id" class="energy-road group cursor-pointer select-none">
    <!-- Underlay cobblestone track lane -->
    <path
      :d="path"
      fill="none"
      stroke="#CBD5E1"
      stroke-width="24"
      stroke-linecap="round"
      stroke-linejoin="round"
      opacity="0.85"
    />

    <!-- Clean white surface line -->
    <path
      :d="path"
      fill="none"
      stroke="#FFFFFF"
      stroke-width="14"
      stroke-linecap="round"
      stroke-linejoin="round"
    />

    <!-- Flowing luminous neon particle stream -->
    <path
      :d="path"
      fill="none"
      :stroke="strokeColor"
      stroke-width="4.5"
      stroke-linecap="round"
      stroke-linejoin="round"
      :class="isCrossSource ? 'source-link-stream' : 'energy-stream'"
    />

    <!-- Midpoint relation badge -->
    <g
      v-if="sourcePos && targetPos"
      :transform="`translate(${midX}, ${midY})`"
      class="opacity-80 group-hover:opacity-100 transition-opacity"
    >
      <rect
        x="-42"
        y="-9"
        width="84"
        height="18"
        rx="9"
        fill="#0F172A"
        class="shadow-sm"
      />
      <circle cx="-32" cy="0" r="3" :fill="strokeColor" />
      <text
        x="2"
        y="3.5"
        text-anchor="middle"
        class="text-[9px] font-mono font-bold fill-white tracking-wider uppercase select-none pointer-events-none"
      >
        {{ relationType.replace(/_/g, ' ') }}
      </text>
    </g>
  </g>
</template>
