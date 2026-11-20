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
  if (rel.includes('FOUNDATION') || rel.includes('TOPIC')) return '#06B6D4' // bright vibrant cyan
  if (rel.includes('WORKS') || rel.includes('AUTHOR') || rel.includes('PROPOSED')) return '#8B5CF6' // luminous purple
  if (rel.includes('COMBINED') || rel.includes('LEADS')) return '#3B82F6' // electric blue
  if (rel.includes('INFLUENCE') || rel.includes('CONTAINS')) return '#10B981' // emerald
  return '#06B6D4'
})

const badgeTextColor = computed(() => {
  if (props.isCrossSource) return '#92400E'
  const rel = props.relationType.toUpperCase()
  if (rel.includes('WORKS') || rel.includes('AUTHOR')) return '#5B21B6'
  if (rel.includes('INFLUENCE') || rel.includes('CONTAINS')) return '#065F46'
  return '#0E7490'
})

const midX = computed(() => {
  if (!props.sourcePos || !props.targetPos) return 0
  return (props.sourcePos.x + props.targetPos.x) / 2
})

const midY = computed(() => {
  if (!props.sourcePos || !props.targetPos) return 0
  return (props.sourcePos.y + props.targetPos.y) / 2 - 12
})
</script>

<template>
  <g :id="id" class="energy-road group cursor-pointer select-none">
    <!-- 1. Road Cast Shadow in 3D ground plane -->
    <path
      :d="path"
      fill="none"
      stroke="#0F172A"
      stroke-width="26"
      stroke-linecap="round"
      stroke-linejoin="round"
      opacity="0.08"
      transform="translate(4, 12)"
    />

    <!-- 2. Lower Stone Bed Viaduct Foundation -->
    <path
      :d="path"
      fill="none"
      stroke="#94A3B8"
      stroke-width="26"
      stroke-linecap="round"
      stroke-linejoin="round"
      opacity="0.9"
    />

    <!-- 3. Upper Smooth Pavement / Concrete Highway -->
    <path
      :d="path"
      fill="none"
      stroke="#F8FAFC"
      stroke-width="18"
      stroke-linecap="round"
      stroke-linejoin="round"
    />

    <!-- 4. Luminous Glowing Energy Conduit Channel -->
    <path
      :d="path"
      fill="none"
      :stroke="strokeColor"
      stroke-width="7"
      stroke-linecap="round"
      stroke-linejoin="round"
      opacity="0.45"
      class="group-hover:opacity-85 transition-opacity duration-200"
    />

    <!-- 5. Pulsing High-Energy Light Pulse Stream (Moving Photons) -->
    <path
      :d="path"
      fill="none"
      :stroke="strokeColor"
      stroke-width="3.5"
      stroke-dasharray="14, 28"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="animated-road-stream"
    />

    <!-- 6. Center Laser Core Line -->
    <path
      :d="path"
      fill="none"
      stroke="#FFFFFF"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
      opacity="0.8"
    />

    <!-- 7. Floating 3D Relationship Tag Pill -->
    <g
      v-if="sourcePos && targetPos"
      :transform="`translate(${midX}, ${midY})`"
      class="transition-transform duration-200 group-hover:scale-110 pointer-events-none"
    >
      <!-- Shadow -->
      <rect
        :x="-Math.max(40, relationType.length * 3.8)"
        y="-10"
        :width="Math.max(80, relationType.length * 7.6)"
        height="22"
        rx="11"
        fill="#0F172A"
        opacity="0.12"
        transform="translate(0, 3)"
      />
      <!-- Badge Body -->
      <rect
        :x="-Math.max(40, relationType.length * 3.8)"
        y="-10"
        :width="Math.max(80, relationType.length * 7.6)"
        height="22"
        rx="11"
        fill="#FFFFFF"
        :stroke="strokeColor"
        stroke-width="1.5"
        class="shadow-xs"
      />
      <!-- Text -->
      <text
        x="0"
        y="4.5"
        text-anchor="middle"
        :fill="badgeTextColor"
        class="text-[9.5px] font-mono font-black uppercase tracking-wider select-none"
      >
        {{ relationType.replace(/_/g, ' ') }}
      </text>
    </g>
  </g>
</template>

<style scoped>
@keyframes roadEnergyFlow {
  from {
    stroke-dashoffset: 84;
  }
  to {
    stroke-dashoffset: 0;
  }
}

.animated-road-stream {
  animation: roadEnergyFlow 1.8s linear infinite;
}
</style>
