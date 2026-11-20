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
  isPunched?: boolean
}>()

const emit = defineEmits<{
  (e: 'click'): void
}>()

const isMain = computed(() => {
  return (props.level ?? 1) >= 4 || props.type === 'CHAPTER' || props.type === 'ORG' || (props.mentionCount ?? 0) >= 20
})

const typeConfig = computed(() => {
  const mainYOffset = isMain.value ? -230 : -154
  const beaconYOffset = isMain.value ? -265 : -186

  switch (props.type) {
    case 'PERSON':
      return {
        fillLeft: '#8B5CF6',
        fillRight: '#6D28D9',
        fillTop: '#C084FC',
        stroke: '#A855F7',
        accentGlow: '#DDD6FE',
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
        accentGlow: '#DBEAFE',
        text: '#1E3A8A',
        tagDot: '#3B82F6',
        badge: 'Org',
        tagY: mainYOffset,
        beaconY: beaconYOffset,
      }
    case 'LOCATION':
      return {
        fillLeft: '#E11D48',
        fillRight: '#BE123C',
        fillTop: '#FDA4AF',
        stroke: '#F43F5E',
        accentGlow: '#FFE4E6',
        text: '#881337',
        tagDot: '#F43F5E',
        badge: 'Benchmark',
        tagY: mainYOffset,
        beaconY: beaconYOffset,
      }
    case 'CHAPTER':
      return {
        fillLeft: '#059669',
        fillRight: '#047857',
        fillTop: '#6EE7B7',
        stroke: '#10B981',
        accentGlow: '#D1FAE5',
        text: '#064E3B',
        tagDot: '#10B981',
        badge: 'Chapter',
        tagY: mainYOffset,
        beaconY: beaconYOffset,
      }
    case 'SECTION':
      return {
        fillLeft: '#D97706',
        fillRight: '#B45309',
        fillTop: '#FCD34D',
        stroke: '#F59E0B',
        accentGlow: '#FEF3C7',
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
        accentGlow: '#CFFAFE',
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
    <!-- 1. Deep 3D Ground Cast Shadow (Elongated isometric shadow) -->
    <ellipse
      cx="20"
      cy="16"
      :rx="isMain ? 74 : 50"
      :ry="isMain ? 30 : 20"
      fill="#0F172A"
      :opacity="isMain ? 0.25 : 0.16"
      class="group-hover:opacity-35 group-hover:scale-110 transition-all duration-300"
    />

    <!-- 2. ACTIVE / FOCUSED TOPIC: Radiant 3D Neon Aura & Radar Ring -->
    <g v-if="isSelected || isPathActive || isPunched" class="pointer-events-none">
      <!-- Outer radiant glow disk -->
      <ellipse
        cx="0"
        cy="10"
        :rx="isMain ? 104 : 76"
        :ry="isMain ? 48 : 34"
        :fill="typeConfig.stroke"
        fill-opacity="0.25"
        class="animate-pulse"
      />

      <!-- Concentric animated radar waves -->
      <ellipse
        cx="0"
        cy="10"
        :rx="isMain ? 92 : 66"
        :ry="isMain ? 42 : 28"
        fill="none"
        :stroke="typeConfig.stroke"
        stroke-width="3.5"
        class="radar-ring-1"
      />
      <ellipse
        cx="0"
        cy="10"
        :rx="isMain ? 116 : 86"
        :ry="isMain ? 52 : 36"
        fill="none"
        :stroke="typeConfig.stroke"
        stroke-width="2"
        stroke-dasharray="6, 6"
        class="radar-ring-2"
      />

      <!-- Volumetric Skyward Laser Beam (Piercing the clouds) -->
      <linearGradient :id="'skyBeam-' + id" x1="0" y1="1" x2="0" y2="0">
        <stop offset="0%" :stop-color="typeConfig.stroke" stop-opacity="0.85" />
        <stop offset="40%" :stop-color="typeConfig.fillTop" stop-opacity="0.45" />
        <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0" />
      </linearGradient>
      <polygon
        :points="`${isMain ? '-20' : '-14'},10 ${isMain ? '20' : '14'},10 ${isMain ? '40' : '26'},-380 ${isMain ? '-40' : '-26'},-380`"
        :fill="'url(#skyBeam-' + id + ')'"
        class="animate-pulse"
      />
    </g>

    <!-- 3. 3D ISOMETRIC BUILDING CONTAINER (Dynamic levitation on hover) -->
    <g class="transition-transform duration-300 ease-out group-hover:-translate-y-3 group-hover:scale-[1.03]">
      <!-- ======================================================== -->
      <!-- OPTION A: GRAND 3D CITADEL / MONOLITH (MAIN TOWERS)      -->
      <!-- ======================================================== -->
      <g v-if="isMain">
        <!-- Tier 0: 3D Beveled Stepped Stone Plinth Base -->
        <polygon fill="#F1F5F9" points="0,20 68,-14 0,-44 -68,-14" />
        <polygon fill="#CBD5E1" points="-68,-14 0,20 0,10 -68,-24" />
        <polygon fill="#94A3B8" points="0,20 68,-14 68,-24 0,10" />

        <!-- Tier 1: Heavy Fortified Citadel Bastion -->
        <polygon :fill="typeConfig.fillLeft" points="-54,-16 0,8 0,-78 -54,-102" />
        <polygon :fill="typeConfig.fillRight" points="0,8 54,-16 54,-102 0,-78" />
        <polygon :fill="typeConfig.fillTop" stroke="#FFFFFF" stroke-width="1.2" points="0,-78 54,-102 0,-124 -54,-102" />

        <!-- Illuminated Cyber Matrix Windows (Left Facade) -->
        <line x1="-42" y1="-30" x2="-14" y2="-14" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.95" />
        <line x1="-42" y1="-50" x2="-14" y2="-34" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.95" />
        <line x1="-42" y1="-70" x2="-14" y2="-54" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.95" />
        <line x1="-42" y1="-90" x2="-14" y2="-74" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.95" />

        <!-- High-Tech Cooling Slits & Energy Channels (Right Facade) -->
        <line x1="14" y1="-14" x2="42" y2="-30" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.7" />
        <line x1="14" y1="-34" x2="42" y2="-50" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.7" />
        <line x1="14" y1="-54" x2="42" y2="-70" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.7" />
        <line x1="14" y1="-74" x2="42" y2="-90" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.7" />

        <!-- Tier 2: Mid-Level Observatory Spire -->
        <polygon :fill="typeConfig.fillLeft" points="-34,-102 0,-84 0,-152 -34,-170" />
        <polygon :fill="typeConfig.fillRight" points="0,-84 34,-102 34,-170 0,-152" />
        <polygon :fill="typeConfig.fillTop" stroke="#FFFFFF" stroke-width="1.5" points="0,-152 34,-170 0,-186 -34,-170" />

        <!-- Tier 3: Floating 3D Crystal Gem Spire (Hovering & Glowing) -->
        <g class="animate-float">
          <!-- Outer Holographic Spinning Diamond Ring -->
          <ellipse
            cx="0"
            cy="-214"
            rx="32"
            ry="12"
            fill="none"
            :stroke="typeConfig.stroke"
            stroke-width="1.8"
            stroke-dasharray="8, 6"
            class="animate-spin"
            opacity="0.85"
          />

          <!-- 3D Polyhedral Floating Crystal Apex -->
          <polygon
            points="0,-192 28,-214 0,-248 -28,-214"
            :fill="typeConfig.fillTop"
            filter="url(#softGlow)"
          />
          <polygon points="0,-192 28,-214 0,-206" fill="#FFFFFF" opacity="0.9" />
          <polygon points="-28,-214 0,-192 0,-206" :fill="typeConfig.fillLeft" opacity="0.8" />
          <circle cx="0" cy="-220" r="5" fill="#FFFFFF" />

          <!-- High Beacon Laser Beam -->
          <line
            x1="0"
            y1="-248"
            x2="0"
            y2="-296"
            :stroke="typeConfig.stroke"
            stroke-width="3.5"
            stroke-linecap="round"
            class="animate-pulse"
          />
        </g>
      </g>

      <!-- ======================================================== -->
      <!-- OPTION B: 3D PRISMATIC PAVILION (SUB TOWERS)             -->
      <!-- ======================================================== -->
      <g v-else>
        <!-- Ground Base Plinth -->
        <polygon fill="#F1F5F9" points="0,12 44,-8 0,-28 -44,-8" />
        <polygon fill="#CBD5E1" points="-44,-8 0,12 0,5 -44,-15" />
        <polygon fill="#94A3B8" points="0,12 44,-8 44,-15 0,5" />

        <!-- 3D Isometric Walls -->
        <polygon :fill="typeConfig.fillLeft" points="-38,-10 0,8 0,-62 -38,-78" />
        <polygon :fill="typeConfig.fillRight" points="0,8 38,-10 38,-78 0,-62" />

        <!-- Slanted Prismatic Glass Solar Roof -->
        <polygon :fill="typeConfig.fillTop" stroke="#FFFFFF" stroke-width="1.5" points="0,-62 38,-78 0,-102 -38,-78" />

        <!-- Luminous Energy Window Apertures -->
        <line x1="-26" y1="-30" x2="-10" y2="-18" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.95" />
        <line x1="-26" y1="-50" x2="-10" y2="-38" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.95" />
        <line x1="10" y1="-18" x2="26" y2="-30" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.7" />
        <line x1="10" y1="-38" x2="26" y2="-50" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.7" />

        <!-- Satellite Relay Spire at Apex with Orbiting Ring -->
        <line x1="0" y1="-102" x2="0" y2="-130" :stroke="typeConfig.stroke" stroke-width="3" stroke-linecap="round" />
        <circle cx="0" cy="-132" r="5" :fill="typeConfig.tagDot" stroke="#FFFFFF" stroke-width="1.5" />
        <circle cx="0" cy="-132" r="8" fill="none" :stroke="typeConfig.stroke" stroke-width="1.2" stroke-dasharray="3, 3" class="animate-spin" />
      </g>
    </g>

    <!-- 4. FLOATING LEARNING PATH STEP BEACON -->
    <g
      v-if="pathOrder !== undefined"
      :transform="`translate(0, ${typeConfig.beaconY})`"
      class="transition-transform duration-200 pointer-events-none"
    >
      <rect
        x="-44"
        y="-12"
        width="88"
        height="24"
        rx="12"
        :fill="isPathActive ? '#0F172A' : '#FFFFFF'"
        :stroke="isPathActive ? typeConfig.stroke : '#94A3B8'"
        stroke-width="2"
        class="shadow-md"
      />
      <circle cx="-28" cy="0" r="4.5" :fill="typeConfig.tagDot" />
      <text
        x="6"
        y="4"
        text-anchor="middle"
        :fill="isPathActive ? '#FFFFFF' : '#0F172A'"
        class="text-[10.5px] font-mono font-black uppercase tracking-wider"
      >
        Step {{ pathOrder }}
      </text>
    </g>

    <!-- 5. FLOATING 3D TOPIC BADGE (MAIN VS SUB) -->
    <g
      :transform="`translate(0, ${typeConfig.tagY})`"
      class="transition-transform duration-150 group-hover:scale-105 pointer-events-none"
    >
      <rect
        :x="isMain ? -82 : -72"
        y="-15"
        :width="isMain ? 164 : 144"
        height="30"
        rx="15"
        fill="#FFFFFF"
        :stroke="isMain ? '#F59E0B' : typeConfig.stroke"
        :stroke-width="isMain ? 2.5 : 2"
        class="shadow-lg"
      />

      <!-- Status dot -->
      <circle :cx="isMain ? -66 : -56" cy="0" :r="isMain ? 5 : 4.5" :fill="isMain ? '#F59E0B' : typeConfig.tagDot" />

      <!-- Label -->
      <text
        :x="isMain ? -54 : -46"
        y="4"
        :fill="typeConfig.text"
        class="text-[11px] font-mono font-black tracking-tight"
      >
        {{ label.length > (isMain ? 13 : 11) ? label.slice(0, isMain ? 12 : 10) + '..' : label }}
      </text>

      <!-- Pill Badge: MAIN vs SUB -->
      <rect
        :x="isMain ? 36 : 28"
        y="-9"
        :width="isMain ? 38 : 36"
        height="18"
        rx="9"
        :fill="isMain ? '#FEF3C7' : '#F1F5F9'"
      />
      <text
        :x="isMain ? 55 : 46"
        y="4"
        text-anchor="middle"
        :fill="isMain ? '#B45309' : '#475569'"
        class="text-[9px] font-mono font-black uppercase tracking-wider"
      >
        {{ isMain ? 'MAIN' : 'SUB' }}
      </text>
    </g>
  </g>
</template>

<style scoped>
@keyframes radarPulse {
  0% {
    transform: scale(0.9);
    opacity: 0.95;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.4;
  }
  100% {
    transform: scale(0.9);
    opacity: 0.95;
  }
}

.radar-ring-1 {
  animation: radarPulse 2.4s ease-in-out infinite;
  transform-origin: 0px 10px;
}

.radar-ring-2 {
  animation: radarPulse 2.4s ease-in-out infinite 0.6s;
  transform-origin: 0px 10px;
}

@keyframes floatBob {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-6px);
  }
}

.animate-float {
  animation: floatBob 3s ease-in-out infinite;
}
</style>
