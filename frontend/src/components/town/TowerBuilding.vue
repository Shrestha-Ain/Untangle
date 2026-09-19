<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  id: string
  x: number
  y: number
  label: string
  type: string
  level?: number
  mentionCount?: number
  pathOrder?: number
  isSelected?: boolean
  isPathActive?: boolean
}>()

const emit = defineEmits<{
  (e: 'click'): void
}>()

const typeConfig = computed(() => {
  switch (props.type) {
    case 'PERSON':
      return {
        fill: '#7C3AED',
        stroke: '#8B5CF6',
        text: '#3B0764',
        tagDot: '#8B5CF6',
        badge: 'Author',
        tagY: -170,
        beaconY: -202,
      }
    case 'ORG':
      return {
        fill: '#3B82F6',
        stroke: '#3B82F6',
        text: '#1E3A8A',
        tagDot: '#3B82F6',
        badge: 'Org',
        tagY: -146,
        beaconY: -178,
      }
    case 'LOCATION':
      return {
        fill: '#F59E0B',
        stroke: '#F59E0B',
        text: '#78350F',
        tagDot: '#F59E0B',
        badge: 'Benchmark',
        tagY: -130,
        beaconY: -162,
      }
    case 'CHAPTER':
      return {
        fill: '#10B981',
        stroke: '#10B981',
        text: '#064E3B',
        tagDot: '#10B981',
        badge: 'Chapter',
        tagY: -160,
        beaconY: -192,
      }
    case 'SECTION':
      return {
        fill: '#F59E0B',
        stroke: '#D97706',
        text: '#78350F',
        tagDot: '#F59E0B',
        badge: 'Section',
        tagY: -146,
        beaconY: -178,
      }
    case 'TOPIC':
    case 'CONCEPT':
    default:
      return {
        fill: '#06B6D4',
        stroke: '#06B6D4',
        text: '#0E7490',
        tagDot: '#06B6D4',
        badge: 'Concept',
        tagY: -188,
        beaconY: -220,
      }
  }
})
</script>

<template>
  <g
    :id="id"
    :transform="`translate(${x}, ${y})`"
    class="town-building cursor-pointer group select-none"
    :class="{ selected: isSelected }"
    @click.stop="emit('click')"
  >
    <!-- Ground Shadow Ellipse (Realistic page2 depth) -->
    <ellipse
      cx="0"
      cy="6"
      rx="58"
      ry="26"
      fill="#0F172A"
      opacity="0.14"
      class="group-hover:opacity-25 transition-all duration-200"
    />

    <!-- Selection Pulse Ring (Glows when active or current path step) -->
    <ellipse
      v-if="isSelected || isPathActive"
      cx="0"
      cy="6"
      rx="72"
      ry="34"
      fill="none"
      :stroke="typeConfig.stroke"
      stroke-width="3"
      stroke-dasharray="8, 6"
      class="animate-pulse-ring"
    />

    <!-- 2.5D ARCHITECTURAL SPRITES (VIBRANT & RICH COLORS, STRICTLY NO FLAGS) -->
    <g class="transition-transform duration-200 group-hover:-translate-y-2">
      <!-- Archetype 1: Concept / Spire (e.g. Multi-Head Attention) -->
      <g v-if="type === 'CONCEPT' || type === 'TOPIC'">
        <!-- Stepped Base Tier -->
        <polygon fill="#E0F2FE" stroke="#BAE6FD" stroke-width="1.5" points="0,6 48,-18 0,-42 -48,-18" />
        <!-- Stepped Body Walls (Cyan Gradient Facets) -->
        <polygon fill="#0891B2" points="-38,-14 0,4 0,-70 -38,-88" />
        <polygon fill="#06B6D4" points="0,4 38,-14 38,-88 0,-70" />
        <polygon fill="#67E8F9" stroke="#FFFFFF" stroke-width="1.2" points="0,-70 38,-88 0,-106 -38,-88" />

        <!-- Floating Faceted Crystal Gem -->
        <g class="animate-float">
          <polygon
            points="0,-112 28,-138 0,-178 -28,-138"
            fill="url(#cyanCrystalGrad)"
            filter="url(#softGlow)"
          />
          <polygon points="0,-112 28,-138 0,-126" fill="#A5F3FC" opacity="0.9" />
          <circle cx="0" cy="-145" r="5" fill="#FFFFFF" opacity="0.9" />

          <!-- Sky Light Beam -->
          <line
            x1="0"
            y1="-178"
            x2="0"
            y2="-230"
            stroke="#38BDF8"
            stroke-width="3.5"
            stroke-linecap="round"
            class="animate-pulse"
          />
        </g>
      </g>

      <!-- Archetype 2: Person / Research Lodge (Cozy Purple Victorian Academy, NO FLAGS) -->
      <g v-else-if="type === 'PERSON'">
        <!-- Lodge Walls -->
        <polygon fill="#7C3AED" points="-42,-14 0,6 0,-66 -42,-86" />
        <polygon fill="#9333EA" points="0,6 42,-14 42,-86 0,-66" />
        <!-- Steeple Cozy Roof -->
        <polygon fill="url(#purpleRoofGrad)" stroke="#FFFFFF" stroke-width="1.2" points="0,-66 42,-86 0,-146 -42,-86" />
        <!-- Warm Arch Doorway -->
        <polygon fill="#FDE047" points="-12,-1 5,7 5,-22 -12,-29" />
        <!-- Architectural Finial Needle at Apex (strictly NO flags) -->
        <line x1="0" y1="-146" x2="0" y2="-164" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" />
        <circle cx="0" cy="-166" r="3.5" fill="#F59E0B" />
      </g>

      <!-- Archetype 3: Location / Training Arena (Golden Dome Structure) -->
      <g v-else-if="type === 'LOCATION'">
        <!-- Multi-tiered Plinth Base -->
        <polygon fill="#F59E0B" points="-46,-14 0,8 46,-14 0,-36" />
        <polygon fill="#D97706" points="-46,-14 0,8 0,-24 -46,-46" />
        <polygon fill="#B45309" points="0,8 46,-14 46,-46 0,-24" />
        <!-- Golden Training Dome -->
        <path
          d="M -34,-26 Q 0,-102 34,-26 Z"
          fill="url(#amberDomeGrad)"
          filter="url(#softGlow)"
          stroke="#FFFFFF"
          stroke-width="1.2"
        />
        <circle cx="0" cy="-64" r="5.5" fill="#FFFBEB" />
        <!-- Top Plinth Cap -->
        <circle cx="0" cy="-102" r="4.5" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.5" />
      </g>

      <!-- Archetype 4: Chapter / Citadel (Emerald Fortress) -->
      <g v-else-if="type === 'CHAPTER'">
        <!-- Broad Fortress Base -->
        <polygon fill="#047857" points="-52,-18 0,8 0,-52 -52,-76" />
        <polygon fill="#059669" points="0,8 52,-18 52,-76 0,-52" />
        <polygon fill="#34D399" stroke="#FFFFFF" stroke-width="1.2" points="0,-52 52,-76 0,-100 -52,-76" />
        <!-- Central Academic Citadel Spire -->
        <polygon fill="#047857" points="-24,-72 0,-60 0,-122 -24,-134" />
        <polygon fill="#059669" points="0,-60 24,-72 24,-134 0,-122" />
        <polygon fill="#A7F3D0" stroke="#FFFFFF" stroke-width="1" points="0,-122 24,-134 0,-146 -24,-134" />
        <circle cx="0" cy="-147" r="3.5" fill="#F59E0B" />
      </g>

      <!-- Archetype 5: Section & Org / Modern Tech Block -->
      <g v-else>
        <!-- Modern Tiered Cobalt Block -->
        <polygon fill="#2563EB" points="-42,-14 0,6 0,-66 -42,-86" />
        <polygon fill="#3B82F6" points="0,6 42,-14 42,-86 0,-66" />
        <polygon fill="#93C5FD" stroke="#FFFFFF" stroke-width="1.2" points="0,-66 42,-86 0,-106 -42,-86" />
        <!-- Upper Module Tier -->
        <polygon fill="#2563EB" points="-22,-80 0,-70 0,-112 -22,-122" />
        <polygon fill="#60A5FA" points="0,-70 22,-80 22,-122 0,-112" />
        <polygon fill="#FFFFFF" points="0,-112 22,-122 0,-132 -22,-122" />
        <circle cx="0" cy="-125" r="4" fill="#F59E0B" />
      </g>
    </g>

    <!-- FLOATING LEARNING PATH STEP BEACON (Positioned above the building with generous clearance) -->
    <g
      v-if="pathOrder !== undefined"
      :transform="`translate(0, ${typeConfig.beaconY})`"
      class="transition-transform duration-200 pointer-events-none"
    >
      <rect
        x="-42"
        y="-11"
        width="84"
        height="22"
        rx="11"
        :fill="isPathActive ? '#1C1B18' : '#FFFFFF'"
        :stroke="isPathActive ? typeConfig.stroke : '#CBD5E1'"
        stroke-width="1.8"
        class="shadow-md"
      />
      <circle cx="-28" cy="0" r="4" :fill="typeConfig.tagDot" />
      <text
        x="5"
        y="3.5"
        text-anchor="middle"
        :fill="isPathActive ? '#FFFFFF' : '#1C1B18'"
        class="text-[10px] font-mono font-extrabold uppercase tracking-wider"
      >
        Step {{ pathOrder }}
      </text>
    </g>

    <!-- FLOATING NAME & STAT TAG (Crisp, High-Contrast page2 Design) -->
    <g
      :transform="`translate(0, ${typeConfig.tagY})`"
      class="transition-transform duration-150 group-hover:scale-105 pointer-events-none"
    >
      <rect
        x="-70"
        y="-13"
        width="140"
        height="26"
        rx="13"
        fill="#FFFFFF"
        :stroke="typeConfig.stroke"
        stroke-width="2"
        class="shadow-md"
      />
      <!-- Type indicator dot -->
      <circle cx="-56" cy="0" r="4" :fill="typeConfig.tagDot" />
      <!-- Label text -->
      <text
        x="-46"
        y="4"
        :fill="typeConfig.text"
        class="text-[11px] font-mono font-bold tracking-tight"
      >
        {{ label.length > 13 ? label.slice(0, 11) + '..' : label }}
      </text>
      <!-- Sequence Step / Mention Count badge -->
      <rect
        v-if="pathOrder || mentionCount"
        x="36"
        y="-9"
        width="26"
        height="18"
        rx="9"
        fill="#F1F5F9"
      />
      <text
        v-if="pathOrder || mentionCount"
        x="49"
        y="4"
        text-anchor="middle"
        class="text-[9px] font-mono font-bold fill-[#64748B]"
      >
        {{ pathOrder ? '#' + pathOrder : `${mentionCount}×` }}
      </text>
    </g>
  </g>
</template>
