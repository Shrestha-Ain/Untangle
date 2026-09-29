<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useGraphStore } from '@/stores/graph'
import { usePanZoom } from '@/composables/usePanZoom'
import { useTownLayout } from '@/composables/useTownLayout'
import DistrictTurf from './DistrictTurf.vue'
import EnergyRoad from './EnergyRoad.vue'
import TowerBuilding from './TowerBuilding.vue'
import TreeCluster from './TreeCluster.vue'

const props = defineProps<{
  activeTypeFilter?: string
}>()

const svgRef = ref<SVGSVGElement | null>(null)
const graphStore = useGraphStore()
const { translateX, translateY, scale, onMouseDown, onWheel, zoomIn, zoomOut, recenter } = usePanZoom()
const { layoutBuildings, layoutRoads, layoutDistricts } = useTownLayout()

// Compute positioned elements
const buildings = computed(() => {
  const list = layoutBuildings(graphStore.townBuildings)
  if (!props.activeTypeFilter || props.activeTypeFilter === 'ALL') {
    return list
  }
  return list.filter((b) => b.type === props.activeTypeFilter)
})

const roads = computed(() => layoutRoads(graphStore.energyRoads, buildings.value))
const districts = computed(() => layoutDistricts(graphStore.communities, buildings.value))

// Compute Learning Path sequential trail
const learningPathTrail = computed(() => {
  if (!graphStore.isPathModeActive || graphStore.learningPath.length < 2) {
    return ''
  }

  const posMap = new Map(buildings.value.map((b) => [b.id, { x: b.x, y: b.y }]))
  const points = graphStore.learningPath
    .map((id) => posMap.get(id))
    .filter((pos): pos is { x: number; y: number } => pos !== undefined)

  if (points.length < 2) return ''

  let d = `M ${points[0].x},${points[0].y}`
  for (let i = 1; i < points.length; i++) {
    const prev = points[i - 1]
    const curr = points[i]
    const midX = (prev.x + curr.x) / 2
    const midY = (prev.y + curr.y) / 2 - 35
    d += ` Q ${midX},${midY} ${curr.x},${curr.y}`
  }
  return d
})

function onBuildingClick(id: string) {
  graphStore.selectEntity(id)
}

// Watch highlighted subgraph from Regulus answers
watch(
  () => graphStore.highlightedSubgraph,
  (subgraph) => {
    if (!svgRef.value) return
    const allItems = svgRef.value.querySelectorAll('.town-building, .energy-road')

    if (!subgraph) {
      allItems.forEach((el) => {
        el.classList.remove('dimmed')
        el.classList.remove('highlighted')
      })
      return
    }

    // Dim everything by default
    allItems.forEach((el) => {
      el.classList.add('dimmed')
      el.classList.remove('highlighted')
    })

    // Highlight answer nodes
    subgraph.nodeIds.forEach((id) => {
      const nodeEl = svgRef.value?.querySelector(`#building-${id}`)
      if (nodeEl) {
        nodeEl.classList.remove('dimmed')
        nodeEl.classList.add('highlighted')
      }
    })

    // Highlight answer edges
    subgraph.edgeIds.forEach((id) => {
      const roadEl = svgRef.value?.querySelector(`#road-${id}`)
      if (roadEl) {
        roadEl.classList.remove('dimmed')
        roadEl.classList.add('highlighted')
      }
    })
  },
  { deep: true }
)

defineExpose({
  zoomIn,
  zoomOut,
  recenter,
})
</script>

<template>
  <div
    class="w-full h-full bg-[#EBF7F2] overflow-hidden cursor-grab active:cursor-grabbing select-none relative"
    @mousedown="onMouseDown"
    @wheel="onWheel"
  >
    <!-- Background subtle geometric dot grid -->
    <div
      class="absolute inset-0 pointer-events-none opacity-30"
      style="background-image: radial-gradient(rgba(13, 148, 136, 0.15) 1.5px, transparent 1.5px); background-size: 36px 36px;"
    ></div>

    <svg
      ref="svgRef"
      class="w-[2048px] h-[1400px] transform-gpu transition-transform duration-75"
      :style="{ transform: `translate3d(${translateX}px, ${translateY}px, 0) scale(${scale})` }"
      viewBox="0 0 2048 1400"
    >
      <defs>
        <!-- Soft Glow Filter for Floating Gems and Domes (page2 style) -->
        <filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="8" result="glow" />
          <feComposite in="SourceGraphic" in2="glow" operator="over" />
        </filter>

        <!-- Lush Grass Linear Gradient -->
        <linearGradient id="grassGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#E9F7EF" />
          <stop offset="50%" stop-color="#DEF3E7" />
          <stop offset="100%" stop-color="#D4ECE0" />
        </linearGradient>

        <!-- Vibrant Crystal & Roof Gradients -->
        <linearGradient id="cyanCrystalGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#67E8F9" />
          <stop offset="50%" stop-color="#06B6D4" />
          <stop offset="100%" stop-color="#0891B2" />
        </linearGradient>

        <linearGradient id="purpleRoofGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#C084FC" />
          <stop offset="100%" stop-color="#7E22CE" />
        </linearGradient>

        <linearGradient id="amberDomeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#FCD34D" />
          <stop offset="70%" stop-color="#F59E0B" />
          <stop offset="100%" stop-color="#D97706" />
        </linearGradient>

        <linearGradient id="pathTrailGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#06B6D4" />
          <stop offset="50%" stop-color="#10B981" />
          <stop offset="100%" stop-color="#F59E0B" />
        </linearGradient>
      </defs>

      <!-- Beautiful Lush Ground Base -->
      <rect fill="url(#grassGrad)" width="2048" height="1400" />

      <!-- District Turf Platforms (Rich Island Zones) -->
      <DistrictTurf
        v-for="d in districts"
        :key="d.id"
        :points="d.polygon"
        :fill="d.fill"
        :stroke="d.stroke"
        :text-color="d.textColor"
        :label="d.label"
        :center-x="d.centerX"
        :center-y="d.centerY"
      />

      <!-- Cheerful Foliage Tree Clusters -->
      <TreeCluster :x="360" :y="480" />
      <TreeCluster :x="760" :y="220" />
      <TreeCluster :x="1220" :y="260" />
      <TreeCluster :x="1560" :y="520" />
      <TreeCluster :x="680" :y="700" />
      <TreeCluster :x="1160" :y="760" />

      <!-- High-Fidelity Energy Roads Layer (rendered below buildings) -->
      <EnergyRoad
        v-for="r in roads"
        :id="`road-${r.id}`"
        :key="r.id"
        :path="r.svgPath"
        :relation-type="r.relationType"
        :is-cross-source="r.isCrossSource"
        :source-pos="r.sourcePos"
        :target-pos="r.targetPos"
      />

      <!-- SEQUENTIAL LEARNING PATH TRAIL (Illuminated Rainbow Guide) -->
      <g v-if="learningPathTrail" class="pointer-events-none">
        <!-- Trail glow halo -->
        <path
          :d="learningPathTrail"
          fill="none"
          stroke="#38BDF8"
          stroke-width="12"
          stroke-opacity="0.3"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <!-- Luminous pulsing stream -->
        <path
          :d="learningPathTrail"
          fill="none"
          stroke="url(#pathTrailGrad)"
          stroke-width="4.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-dasharray="10, 12"
          class="energy-stream"
        />
      </g>


      <!-- Tower Buildings Layer (Positioned with plenty of breathing room) -->
      <TowerBuilding
        v-for="b in buildings"
        :id="`building-${b.id}`"
        :key="b.id"
        :x="b.x"
        :y="b.y"
        :label="b.label"
        :type="b.type"
        :level="b.level"
        :mention-count="b.mentionCount"
        :path-order="b.pathOrder"
        :is-selected="graphStore.selectedEntityId === b.id"
        :is-path-active="graphStore.currentPathNodeId === b.id"
        @click="onBuildingClick(b.id)"
      />
    </svg>
  </div>
</template>

<style>
.town-building,
.energy-road {
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1), filter 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.dimmed {
  opacity: 0.2;
  filter: grayscale(0.85);
}

.highlighted {
  opacity: 1 !important;
  filter: drop-shadow(0 0 20px rgba(56, 189, 248, 0.65)) !important;
}

@keyframes particle-run {
  0% {
    stroke-dashoffset: 60;
  }
  100% {
    stroke-dashoffset: 0;
  }
}

.energy-stream {
  stroke-dasharray: 8, 12;
  animation: particle-run 1.4s linear infinite;
}

.source-link-stream {
  stroke-dasharray: 6, 6;
  animation: particle-run 2.2s linear infinite;
}

@keyframes floaty {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-8px);
  }
}

.animate-float {
  animation: floaty 3.5s ease-in-out infinite;
}

@keyframes pulse-ring {
  0% {
    transform: scale(0.92);
    opacity: 0.9;
  }
  50% {
    transform: scale(1.18);
    opacity: 0.35;
  }
  100% {
    transform: scale(0.92);
    opacity: 0.9;
  }
}

.animate-pulse-ring {
  animation: pulse-ring 2.6s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  transform-origin: center;
}
</style>
