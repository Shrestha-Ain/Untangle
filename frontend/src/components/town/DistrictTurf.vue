<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  points: string
  fill: string
  stroke?: string
  textColor?: string
  label?: string
  centerX?: number
  centerY?: number
}>()

// Generate 3D cliff extrusion points by projecting polygon vertices down by 22px
const cliffPoints = computed(() => {
  if (!props.points) return ''
  const pairs = props.points.trim().split(/\s+/)
  if (pairs.length < 3) return ''

  // Project bottom vertices downward to create the 3D vertical plateau cliff
  const bottomPoints = pairs.map((pair) => {
    const [xStr, yStr] = pair.split(',')
    const x = parseFloat(xStr)
    const y = parseFloat(yStr) + 22
    return `${x},${y}`
  })

  return [...pairs, ...bottomPoints.reverse()].join(' ')
})
</script>

<template>
  <g v-if="points" class="district-turf pointer-events-none select-none">
    <!-- 1. Deep 3D Ground Drop Shadow -->
    <polygon
      :points="points"
      fill="#0F172A"
      opacity="0.12"
      transform="translate(18, 30)"
      filter="url(#softGlow)"
    />

    <!-- 2. 3D Vertical Cliff Skirt / Rock Face (Gives real plateau height) -->
    <polygon
      v-if="cliffPoints"
      :points="cliffPoints"
      fill="#64748B"
      opacity="0.75"
    />
    <polygon
      v-if="cliffPoints"
      :points="cliffPoints"
      fill="url(#cliffGradient)"
      opacity="0.85"
    />

    <!-- 3. Top Elevated Turf Surface Platform -->
    <polygon
      :points="points"
      :fill="fill"
      :stroke="stroke || '#38BDF8'"
      stroke-width="3.5"
      stroke-linejoin="round"
      class="transition-all duration-300"
    />

    <!-- 4. Luminous Neon Perimeter Glow Edge -->
    <polygon
      :points="points"
      fill="none"
      :stroke="stroke || '#06B6D4'"
      stroke-width="1.5"
      stroke-dasharray="8, 6"
      opacity="0.6"
    />

    <!-- 5. Elevated 3D District Holographic Banner in Ground Plane -->
    <g
      v-if="label && centerX !== undefined && centerY !== undefined"
      :transform="`translate(${centerX}, ${centerY})`"
    >
      <!-- Capsule Backdrop Shadow -->
      <rect
        :x="-Math.max(60, label.length * 4.8)"
        y="-13"
        :width="Math.max(120, label.length * 9.6)"
        height="26"
        rx="13"
        fill="#0F172A"
        opacity="0.14"
        transform="translate(0, 4)"
      />
      <!-- Capsule Card -->
      <rect
        :x="-Math.max(60, label.length * 4.8)"
        y="-13"
        :width="Math.max(120, label.length * 9.6)"
        height="26"
        rx="13"
        fill="#FFFFFF"
        :stroke="stroke || '#38BDF8'"
        stroke-width="1.8"
        class="shadow-sm"
      />
      <!-- Glowing dot -->
      <circle
        :cx="-Math.max(60, label.length * 4.8) + 12"
        cy="0"
        r="4"
        :fill="textColor || '#0284C7'"
        class="animate-pulse"
      />
      <!-- District Label -->
      <text
        x="6"
        y="4"
        text-anchor="middle"
        :fill="textColor || '#0284C7'"
        class="text-[11px] font-mono font-black uppercase tracking-wider select-none"
      >
        ✦ {{ label }}
      </text>
    </g>
  </g>
</template>
