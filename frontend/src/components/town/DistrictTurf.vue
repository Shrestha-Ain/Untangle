<script setup lang="ts">
defineProps<{
  points: string
  fill: string
  stroke?: string
  textColor?: string
  label?: string
  centerX?: number
  centerY?: number
}>()
</script>

<template>
  <g v-if="points" class="district-turf pointer-events-none select-none">
    <!-- Base Turf Polygon (Soft Island Platform) -->
    <polygon
      :points="points"
      :fill="fill"
      :stroke="stroke || '#CCD8F4'"
      stroke-width="3"
      stroke-linejoin="round"
      class="transition-all duration-300"
    />

    <!-- Embedded District Banner in Ground Plane -->
    <g v-if="label && centerX !== undefined && centerY !== undefined" :transform="`translate(${centerX}, ${centerY})`" opacity="0.8">
      <text
        x="0"
        y="0"
        text-anchor="middle"
        :fill="textColor || '#3B82F6'"
        class="text-[11.5px] font-mono font-extrabold uppercase tracking-widest drop-shadow-xs select-none"
      >
        ✦ {{ label }}
      </text>
    </g>
  </g>
</template>
