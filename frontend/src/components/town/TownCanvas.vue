<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
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
const { translateX, translateY, scale, isDragging, onMouseDown, onWheel, zoomIn, zoomOut, fitTown, focusOn } = usePanZoom()
const { layoutBuildings, layoutRoads, layoutDistricts } = useTownLayout()

// Compute positioned elements
const buildings = computed(() => {
  const list = layoutBuildings(graphStore.townBuildings)
  if (!props.activeTypeFilter || props.activeTypeFilter === 'ALL') {
    return list
  }
  return list.filter((b) => b.type === props.activeTypeFilter)
})

// Depth-sorted buildings for true 3D isometric layering (back-to-front rendering)
const sortedBuildings = computed(() => {
  return [...buildings.value].sort((a, b) => (a.y ?? 0) - (b.y ?? 0))
})

const activePunchedNodeId = ref<string | null>(null)

const roads = computed(() => layoutRoads(graphStore.energyRoads, buildings.value))
const districts = computed(() => layoutDistricts(graphStore.communities, buildings.value))

export interface LearningPathSegment {
  id: string
  sourceId: string
  targetId: string
  sourceStep: number
  targetStep: number
  pathD: string
  midX: number
  midY: number
  isInterchangeable: boolean
  isCurrent: boolean
}

// Compute Learning Path sequential directional segments (Unidirectional vs. Interchangeable)
const learningPathSegments = computed<LearningPathSegment[]>(() => {
  if (!graphStore.isPathModeActive || graphStore.learningPath.length < 2) {
    return []
  }

  const posMap = new Map(buildings.value.map((b) => [b.id, { x: b.x, y: b.y }]))
  const segs: LearningPathSegment[] = []

  for (let i = 0; i < graphStore.learningPath.length - 1; i++) {
    const srcId = graphStore.learningPath[i]
    const tgtId = graphStore.learningPath[i + 1]
    const p1 = posMap.get(srcId)
    const p2 = posMap.get(tgtId)

    if (!p1 || !p2) continue

    const dx = p2.x - p1.x
    const dy = p2.y - p1.y
    const dist = Math.sqrt(dx * dx + dy * dy) || 1
    const nx = dx / dist
    const ny = dy / dist

    // Trim endpoints cleanly outside building foundations so arrowheads are 100% visible
    const startX = Math.round(p1.x + nx * 44)
    const startY = Math.round(p1.y + ny * 44)
    const endX = Math.round(p2.x - nx * 54)
    const endY = Math.round(p2.y - ny * 54)

    // Gentle curved path arc
    const ctrlX = Math.round((p1.x + p2.x) / 2 - ny * 32)
    const ctrlY = Math.round((p1.y + p2.y) / 2 + nx * 32 - 28)

    const pathD = `M ${startX},${startY} Q ${ctrlX},${ctrlY} ${endX},${endY}`

    // Midpoint of quadratic Bezier at t=0.5
    const midX = Math.round(0.25 * startX + 0.5 * ctrlX + 0.25 * endX)
    const midY = Math.round(0.25 * startY + 0.5 * ctrlY + 0.25 * endY)

    const isInterchangeable = graphStore.isStepPairInterchangeable(srcId, tgtId)
    const isCurrent = graphStore.currentPathIndex === i || graphStore.currentPathIndex === i + 1

    segs.push({
      id: `${srcId}->${tgtId}`,
      sourceId: srcId,
      targetId: tgtId,
      sourceStep: i + 1,
      targetStep: i + 2,
      pathD,
      midX,
      midY,
      isInterchangeable,
      isCurrent,
    })
  }

  return segs
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

const isInitialMapLoad = ref(true)
const is3DMode = ref(true)

function toggle3DMode() {
  is3DMode.value = !is3DMode.value
}

function focusOnNode(id: string, targetZoom = 1.05) {
  const b = buildings.value.find((item) => item.id === id)
  if (b && b.x !== undefined && b.y !== undefined) {
    // Smooth camera navigation centered on the tower with gentle focus (1.05x) so context is not lost
    focusOn(b.x, b.y - 50, targetZoom)
    activePunchedNodeId.value = id
    setTimeout(() => {
      if (activePunchedNodeId.value === id) {
        activePunchedNodeId.value = null
      }
    }, 2400)
  }
}

// Automatically navigate and focus canvas on selected step / building
watch(
  () => graphStore.selectedEntityId,
  (newId) => {
    if (!newId) return

    if (isInitialMapLoad.value) {
      // On initial map load, do not jerk zoom into 1.25x and hide other buildings!
      // Instead, frame the full realm so every single building is 100% visible!
      isInitialMapLoad.value = false
      nextTick(() => {
        fitTownView()
      })
      // Highlight the first building briefly without camera disruption
      activePunchedNodeId.value = newId
      setTimeout(() => {
        if (activePunchedNodeId.value === newId) {
          activePunchedNodeId.value = null
        }
      }, 2000)
    } else {
      // Subsequent selections (user clicking Next/Prev or clicking a tower):
      focusOnNode(newId, 1.05)
    }
  }
)

function fitTownView() {
  fitTown(buildings.value)
}

watch(
  () => graphStore.nodes.length,
  () => {
    nextTick(() => {
      fitTownView()
    })
  }
)

onMounted(() => {
  nextTick(() => {
    setTimeout(() => {
      fitTownView()
    }, 150)
  })
})

defineExpose({
  zoomIn,
  zoomOut,
  recenter: fitTownView,
  fitTownView,
  focusOnNode,
  is3DMode,
  toggle3DMode,
})
</script>

<template>
  <div
    class="w-full h-full overflow-hidden cursor-grab active:cursor-grabbing select-none relative bg-gradient-to-br from-[#E0F2FE] via-[#F0FDF4] to-[#FAF5FF]"
    @mousedown="onMouseDown"
    @wheel="onWheel"
  >
    <!-- Radiant daylight sunbeam overlay -->
    <div
      class="absolute inset-0 pointer-events-none"
      style="background: radial-gradient(circle at 50% 12%, rgba(254, 240, 138, 0.25) 0%, rgba(56, 189, 248, 0.14) 45%, transparent 75%);"
    ></div>

    <!-- Soft floating 3D ambient cloud layers -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden opacity-40">
      <div class="cloud-drift-1 absolute w-[600px] h-[220px] rounded-full bg-white/60 blur-3xl -top-12 left-[10%]"></div>
      <div class="cloud-drift-2 absolute w-[720px] h-[260px] rounded-full bg-white/50 blur-3xl top-1/3 -right-24"></div>
    </div>

    <!-- 3D Perspective Frustum Stage -->
    <div
      class="w-full h-full flex items-center justify-center pointer-events-none"
      :style="{
        perspective: '1400px',
        perspectiveOrigin: '50% 42%',
      }"
    >
      <div
        class="w-[2048px] h-[1400px] pointer-events-auto transition-transform"
        :class="isDragging ? 'duration-0' : 'duration-500 ease-out'"
        :style="{
          transformStyle: 'preserve-3d',
          transform: is3DMode ? 'rotateX(24deg) rotateZ(-6deg)' : 'none',
          transformOrigin: '50% 50%',
          filter: is3DMode ? 'drop-shadow(0 35px 50px rgba(15, 23, 42, 0.18))' : 'none',
        }"
      >
        <svg
          ref="svgRef"
          class="w-[2048px] h-[1400px] transform-gpu transition-transform"
          :class="isDragging ? 'duration-0' : 'duration-300 ease-out'"
          :style="{ transform: `translate3d(${translateX}px, ${translateY}px, 0) scale(${scale})` }"
          viewBox="0 0 2048 1400"
        >
          <defs>
            <!-- Soft Glow Filter for Floating Gems and Domes -->
            <filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="8" result="glow" />
              <feComposite in="SourceGraphic" in2="glow" operator="over" />
            </filter>

            <!-- 3D Isometric Diamond Terrain Grid -->
            <pattern id="isoGrid" width="64" height="36.95" patternUnits="userSpaceOnUse">
              <path d="M 32 0 L 64 18.475 L 32 36.95 L 0 18.475 Z" fill="none" stroke="#059669" stroke-width="0.85" stroke-opacity="0.16" />
            </pattern>

            <!-- 3D Plateau Cliff Face Vertical Gradient -->
            <linearGradient id="cliffGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#94A3B8" />
              <stop offset="50%" stop-color="#64748B" />
              <stop offset="100%" stop-color="#334155" />
            </linearGradient>

            <!-- Unidirectional Forward Arrowhead (lower to higher step) - Crisp, elevated & high-visibility -->
            <marker
              id="pathArrowEnd"
              viewBox="0 0 16 16"
              refX="13"
              refY="8"
              markerWidth="13"
              markerHeight="13"
              orient="auto"
            >
              <path d="M 2 2 L 14 8 L 2 14 L 5 8 Z" fill="#0D9488" stroke="#FFFFFF" stroke-width="1.2" />
            </marker>

            <!-- Interchangeable Forward Arrowhead (Two-way flex order) -->
            <marker
              id="pathArrowInterchangeableEnd"
              viewBox="0 0 16 16"
              refX="13"
              refY="8"
              markerWidth="13"
              markerHeight="13"
              orient="auto"
            >
              <path d="M 2 2 L 14 8 L 2 14 L 5 8 Z" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.2" />
            </marker>

            <!-- Interchangeable Backward Arrowhead (Two-way flex order) -->
            <marker
              id="pathArrowInterchangeableStart"
              viewBox="0 0 16 16"
              refX="3"
              refY="8"
              markerWidth="13"
              markerHeight="13"
              orient="auto"
            >
              <path d="M 14 2 L 2 8 L 14 14 L 11 8 Z" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.2" />
            </marker>

            <!-- Vibrant Lush Grass Linear Gradient -->
            <linearGradient id="grassGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#F0FDF4" />
              <stop offset="40%" stop-color="#DCFCE7" />
              <stop offset="100%" stop-color="#BBF7D0" />
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

      <!-- Beautiful Lush Ground Base & 3D Isometric Diamond Terrain -->
      <rect fill="url(#grassGrad)" width="2048" height="1400" />
      <rect fill="url(#isoGrid)" width="2048" height="1400" />

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

      <!-- Tower Buildings Layer (Rendered with 3D Depth Sorting: Back-to-Front) -->
      <TowerBuilding
        v-for="b in sortedBuildings"
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
        :is-punched="activePunchedNodeId === b.id"
        @click="onBuildingClick(b.id)"
      />

      <!-- ELEVATED SEQUENTIAL LEARNING PATH TRAIL (Arrows & Badges Never Hide Behind Buildings) -->
      <g v-if="learningPathSegments.length > 0" class="pointer-events-none">
        <g v-for="seg in learningPathSegments" :key="seg.id">
          <!-- Outer glow halo -->
          <path
            :d="seg.pathD"
            fill="none"
            :stroke="seg.isInterchangeable ? '#F59E0B' : '#38BDF8'"
            :stroke-width="seg.isCurrent ? 14 : 9"
            :stroke-opacity="seg.isCurrent ? 0.4 : 0.22"
            stroke-linecap="round"
            stroke-linejoin="round"
          />

          <!-- Luminous animated stream with crisp elevated directional markers -->
          <path
            :d="seg.pathD"
            fill="none"
            :stroke="seg.isInterchangeable ? '#F59E0B' : '#0D9488'"
            :stroke-width="seg.isCurrent ? 5.5 : 4"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="energy-stream"
            :marker-end="seg.isInterchangeable ? 'url(#pathArrowInterchangeableEnd)' : 'url(#pathArrowEnd)'"
            :marker-start="seg.isInterchangeable ? 'url(#pathArrowInterchangeableStart)' : undefined"
          />

          <!-- Midpoint Indicator Badge -->
          <g :transform="`translate(${seg.midX}, ${seg.midY})`">
            <rect
              :x="seg.isInterchangeable ? -50 : -40"
              y="-11"
              :width="seg.isInterchangeable ? 100 : 80"
              height="22"
              rx="11"
              :fill="seg.isInterchangeable ? '#78350F' : '#042F2E'"
              :stroke="seg.isInterchangeable ? '#F59E0B' : '#0D9488'"
              stroke-width="1.4"
              class="shadow-md"
            />
            <text
              x="0"
              y="4"
              text-anchor="middle"
              class="text-[9.5px] font-mono font-extrabold fill-white tracking-wider uppercase select-none"
            >
              {{ seg.isInterchangeable ? `⇄ ${seg.sourceStep} & ${seg.targetStep} Flex` : `Step ${seg.sourceStep} → ${seg.targetStep}` }}
            </text>
          </g>
        </g>
      </g>
      </svg>
      </div>
    </div>
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

@keyframes cloudDrift1 {
  0%, 100% {
    transform: translateX(0px) translateY(0px);
  }
  50% {
    transform: translateX(80px) translateY(20px);
  }
}

@keyframes cloudDrift2 {
  0%, 100% {
    transform: translateX(0px) translateY(0px);
  }
  50% {
    transform: translateX(-100px) translateY(-30px);
  }
}

.cloud-drift-1 {
  animation: cloudDrift1 26s ease-in-out infinite;
}

.cloud-drift-2 {
  animation: cloudDrift2 32s ease-in-out infinite;
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
