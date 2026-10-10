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

const isMain = computed(() => {
  return (props.level ?? 1) >= 4 || props.type === 'CHAPTER' || props.type === 'ORG' || (props.mentionCount ?? 0) >= 20
})

const typeConfig = computed(() => {
  const mainYOffset = isMain.value ? -225 : -148
  const beaconYOffset = isMain.value ? -258 : -180

  switch (props.type) {
    case 'PERSON':
      return {
        fillLeft: '#7C3AED',
        fillRight: '#6D28D9',
        fillTop: '#C084FC',
        stroke: '#A855F7',
        text: '#4C1D95',
        tagDot: '#8B5CF6',
        badge: 'Author',
        tagY: mainYOffset,
        beaconY: beaconYOffset,
      }
    case 'ORG':
      return {
        fillLeft: '#2563EB',
        fillRight: '#1D4ED8',
        fillTop: '#93C5FD',
        stroke: '#3B82F6',
        text: '#1E3A8A',
        tagDot: '#3B82F6',
        badge: 'Org',
        tagY: mainYOffset,
        beaconY: beaconYOffset,
      }
    case 'LOCATION':
      return {
        fillLeft: '#D97706',
        fillRight: '#B45309',
        fillTop: '#FDE68A',
        stroke: '#F59E0B',
        text: '#78350F',
        tagDot: '#F59E0B',
        badge: 'Benchmark',
        tagY: mainYOffset,
        beaconY: beaconYOffset,
      }
    case 'CHAPTER':
      return {
        fillLeft: '#059669',
        fillRight: '#047857',
        fillTop: '#A7F3D0',
        stroke: '#10B981',
        text: '#064E3B',
        tagDot: '#10B981',
        badge: 'Chapter',
        tagY: mainYOffset,
        beaconY: beaconYOffset,
      }
    case 'SECTION':
      return {
        fillLeft: '#D97706',
        fillRight: '#92400E',
        fillTop: '#FCD34D',
        stroke: '#F59E0B',
        text: '#78350F',
        tagDot: '#F59E0B',
        badge: 'Section',
        tagY: mainYOffset,
        beaconY: beaconYOffset,
      }
    case 'TOPIC':
    case 'CONCEPT':
    default:
      return {
        fillLeft: '#0891B2',
        fillRight: '#0E7490',
        fillTop: '#67E8F9',
        stroke: '#06B6D4',
        text: '#155E75',
        tagDot: '#06B6D4',
        badge: 'Concept',
        tagY: mainYOffset,
        beaconY: beaconYOffset,
      }
  }
})
</script>

<template>
  <g
    :id="id"
    :transform="`translate(${x}, ${y})`"
    class="town-building cursor-pointer group select-none transition-all"
    :class="{ selected: isSelected }"
    @click.stop="emit('click')"
  >
    <!-- Ground Shadow (Isometric Depth) -->
    <ellipse
      cx="14"
      cy="10"
      :rx="isMain ? 68 : 46"
      :ry="isMain ? 28 : 18"
      fill="#0F172A"
      :opacity="isMain ? 0.22 : 0.14"
      class="group-hover:opacity-30 group-hover:scale-105 transition-all duration-300"
    />

    <!-- Active / Path Selection Pulse Halo -->
    <ellipse
      v-if="isSelected || isPathActive"
      cx="0"
      cy="6"
      :rx="isMain ? 84 : 58"
      :ry="isMain ? 36 : 24"
      fill="none"
      :stroke="typeConfig.stroke"
      stroke-width="3"
      stroke-dasharray="8, 6"
      class="animate-pulse-ring"
    />

    <!-- 3D ISOMETRIC ARCHITECTURE CONTAINER (Animated hover elevation) -->
    <g class="transition-transform duration-300 group-hover:-translate-y-2.5">
      <!-- ======================================================== -->
      <!-- OPTION A: GRAND 3D MAIN TOWER (CITADEL / MONOLITH)       -->
      <!-- ======================================================== -->
      <g v-if="isMain">
        <!-- Tier 0: Stepped Plinth Foundation -->
        <polygon fill="#E2E8F0" points="0,16 64,-16 0,-44 -64,-16" />
        <polygon fill="#CBD5E1" points="-64,-16 0,16 0,6 -64,-24" />
        <polygon fill="#94A3B8" points="0,16 64,-16 64,-24 0,6" />

        <!-- Tier 1: Heavy Fortress Base (Left lit, Right shaded) -->
        <polygon :fill="typeConfig.fillLeft" points="-50,-18 0,4 0,-76 -50,-98" />
        <polygon :fill="typeConfig.fillRight" points="0,4 50,-18 50,-98 0,-76" />
        <polygon :fill="typeConfig.fillTop" points="0,-76 50,-98 0,-118 -50,-98" />

        <!-- Cyber Energy Window Slits (Left & Right Faces) -->
        <line x1="-36" y1="-32" x2="-14" y2="-18" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.85" />
        <line x1="-36" y1="-50" x2="-14" y2="-36" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.85" />
        <line x1="-36" y1="-68" x2="-14" y2="-54" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.85" />

        <line x1="14" y1="-18" x2="36" y2="-32" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.65" />
        <line x1="14" y1="-36" x2="36" y2="-50" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.65" />
        <line x1="14" y1="-54" x2="36" y2="-68" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.65" />

        <!-- Tier 2: Mid Spires & High Observatory -->
        <polygon :fill="typeConfig.fillLeft" points="-30,-98 0,-82 0,-146 -30,-162" />
        <polygon :fill="typeConfig.fillRight" points="0,-82 30,-98 30,-162 0,-146" />
        <polygon :fill="typeConfig.fillTop" stroke="#FFFFFF" stroke-width="1.2" points="0,-146 30,-162 0,-176 -30,-162" />

        <!-- Tier 3: Floating 3D Crystal Gem Spire (Hovering and Glowing) -->
        <g class="animate-float">
          <polygon
            points="0,-184 24,-204 0,-236 -24,-204"
            fill="url(#cyanCrystalGrad)"
            filter="url(#softGlow)"
          />
          <polygon points="0,-184 24,-204 0,-196" fill="#FFFFFF" opacity="0.8" />
          <circle cx="0" cy="-210" r="4.5" fill="#FFFFFF" />

          <!-- High Beacon Laser Beam -->
          <line
            x1="0"
            y1="-236"
            x2="0"
            y2="-280"
            :stroke="typeConfig.stroke"
            stroke-width="3"
            stroke-linecap="round"
            class="animate-pulse"
          />
        </g>
      </g>

      <!-- ======================================================== -->
      <!-- OPTION B: SLEEK 3D SUB TOWER (PAVILION / SATELLITE OUTPOST)-->
      <!-- ======================================================== -->
      <g v-else>
        <!-- Ground Base Plinth -->
        <polygon fill="#E2E8F0" points="0,10 40,-8 0,-26 -40,-8" />
        <polygon fill="#94A3B8" points="-40,-8 0,10 0,4 -40,-14" />
        <polygon fill="#64748B" points="0,10 40,-8 40,-14 0,4" />

        <!-- Compact Isometric Walls -->
        <polygon :fill="typeConfig.fillLeft" points="-34,-10 0,6 0,-56 -34,-70" />
        <polygon :fill="typeConfig.fillRight" points="0,6 34,-10 34,-70 0,-56" />

        <!-- Slanted Prismatic Solar Roof -->
        <polygon :fill="typeConfig.fillTop" stroke="#FFFFFF" stroke-width="1" points="0,-56 34,-70 0,-92 -34,-70" />

        <!-- Glowing Single Energy Window Slit -->
        <line x1="-22" y1="-28" x2="-8" y2="-18" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.85" />
        <line x1="8" y1="-18" x2="22" y2="-28" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" opacity="0.6" />

        <!-- Satellite Relay Spire at Apex -->
        <line x1="0" y1="-92" x2="0" y2="-118" :stroke="typeConfig.stroke" stroke-width="2.5" stroke-linecap="round" />
        <circle cx="0" cy="-120" r="4.5" :fill="typeConfig.tagDot" stroke="#FFFFFF" stroke-width="1.2" />
        <circle cx="0" cy="-120" r="7" fill="none" :stroke="typeConfig.stroke" stroke-width="1" stroke-dasharray="3, 3" class="animate-spin" />
      </g>
    </g>

    <!-- FLOATING LEARNING PATH STEP BEACON -->
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
        :fill="isPathActive ? '#0F172A' : '#FFFFFF'"
        :stroke="isPathActive ? typeConfig.stroke : '#CBD5E1'"
        stroke-width="1.8"
        class="shadow-md"
      />
      <circle cx="-28" cy="0" r="4" :fill="typeConfig.tagDot" />
      <text
        x="5"
        y="3.5"
        text-anchor="middle"
        :fill="isPathActive ? '#FFFFFF' : '#0F172A'"
        class="text-[10px] font-mono font-extrabold uppercase tracking-wider"
      >
        Step {{ pathOrder }}
      </text>
    </g>

    <!-- FLOATING NAME & TIER CLASSIFICATION TAG (MAIN VS SUB) -->
    <g
      :transform="`translate(0, ${typeConfig.tagY})`"
      class="transition-transform duration-150 group-hover:scale-105 pointer-events-none"
    >
      <rect
        :x="isMain ? -78 : -68"
        y="-14"
        :width="isMain ? 156 : 136"
        height="28"
        rx="14"
        fill="#FFFFFF"
        :stroke="isMain ? '#F59E0B' : typeConfig.stroke"
        :stroke-width="isMain ? 2.2 : 1.8"
        class="shadow-lg"
      />

      <!-- Left Type/Status Indicator Icon/Dot -->
      <circle :cx="isMain ? -64 : -54" cy="0" :r="isMain ? 5 : 4" :fill="isMain ? '#F59E0B' : typeConfig.tagDot" />

      <!-- Node Name -->
      <text
        :x="isMain ? -54 : -44"
        y="4"
        :fill="typeConfig.text"
        class="text-[11px] font-mono font-extrabold tracking-tight"
      >
        {{ label.length > (isMain ? 12 : 10) ? label.slice(0, isMain ? 11 : 9) + '..' : label }}
      </text>

      <!-- Main vs Sub Pill Badge -->
      <rect
        :x="isMain ? 34 : 26"
        y="-9"
        :width="isMain ? 36 : 34"
        height="18"
        rx="9"
        :fill="isMain ? '#FEF3C7' : '#F1F5F9'"
      />
      <text
        :x="isMain ? 52 : 43"
        y="4"
        text-anchor="middle"
        :fill="isMain ? '#B45309' : '#64748B'"
        class="text-[8.5px] font-mono font-extrabold uppercase tracking-wider"
      >
        {{ isMain ? 'MAIN' : 'SUB' }}
      </text>
    </g>
  </g>
</template>
