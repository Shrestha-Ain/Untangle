<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useDocumentsStore } from '@/stores/documents'
import { useGraphStore } from '@/stores/graph'
import TownNavBar from '@/components/hud/TownNavBar.vue'
import TownCanvas3D from '@/components/town/TownCanvas3D.vue'
import BuildingInfoCard from '@/components/hud/BuildingInfoCard.vue'
import RegulusPanel from '@/components/hud/RegulusPanel.vue'
import LearningPathStepper from '@/components/hud/LearningPathStepper.vue'
import TopicReaderModal from '@/components/hud/TopicReaderModal.vue'
import ExamGistModal from '@/components/hud/ExamGistModal.vue'
import QuizModal from '@/components/hud/QuizModal.vue'
import NotesDrawer from '@/components/hud/NotesDrawer.vue'
import StudyProgressModal from '@/components/hud/StudyProgressModal.vue'
import { useProgressStore } from '@/stores/progress'

const route = useRoute()
const documentsStore = useDocumentsStore()
const graphStore = useGraphStore()
const progressStore = useProgressStore()

const canvasRef = ref<InstanceType<typeof TownCanvas3D> | null>(null)
const activeFilter = ref('ALL')

const documentId = computed(() => (route.params.documentId as string) || 'default-doc')

const currentDoc = computed(() => {
  return (
    documentsStore.documents.find((d) => d.id === documentId.value) ?? {
      id: documentId.value,
      title: 'Knowledge Map Explorer',
      source_mode: 'research' as const,
      filename: 'document.pdf',
    }
  )
})

const mode = computed<'research' | 'study'>(() => {
  return currentDoc.value?.source_mode ?? 'research'
})

async function initializeMap(docId: string, currentMode: 'research' | 'study') {
  await graphStore.loadGraph(docId, currentMode)
  // Select first step in store, but fit all buildings in view so map is completely visible
  if (graphStore.learningPath.length > 0) {
    graphStore.currentPathIndex = 0
  }
  setTimeout(() => {
    canvasRef.value?.recenter()
  }, 100)
}

onMounted(async () => {
  progressStore.initProgress()
  if (documentsStore.documents.length === 0) {
    await documentsStore.fetchDocuments()
  }
  await initializeMap(documentId.value, mode.value)
})

watch(
  () => route.params.documentId,
  async (newDocId: string | string[] | undefined) => {
    if (newDocId && typeof newDocId === 'string') {
      await initializeMap(newDocId, mode.value)
    }
  }
)

function handleZoomIn() {
  canvasRef.value?.zoomIn()
}

function handleZoomOut() {
  canvasRef.value?.zoomOut()
}

function handleRecenter() {
  canvasRef.value?.recenter()
}

function handleSetIsometric() {
  canvasRef.value?.setCameraIsometric()
}

function handleSetTopDown() {
  canvasRef.value?.setCameraTopDown()
}

const is3DActive = computed(() => true)

function handleToggle3D() {
  canvasRef.value?.setCameraIsometric()
}
</script>

<template>
  <div class="relative w-screen h-screen overflow-hidden bg-[#F0F4F8] dark:bg-[#0B1120]">
    <!-- Top HUD Navigation (Solid Colors, No Gradients) -->
    <TownNavBar
      :title="currentDoc.title"
      :mode="mode"
      :is-3-d-active="is3DActive"
      v-model:active-filter="activeFilter"
      @zoom-in="handleZoomIn"
      @zoom-out="handleZoomOut"
      @recenter="handleRecenter"
      @toggle-3-d="handleToggle3D"
      @set-camera-isometric="handleSetIsometric"
      @set-camera-top-down="handleSetTopDown"
    />

    <!-- Guided Learning Path Stepper (Movable & Resizable, Sleek Top Center) -->
    <LearningPathStepper />

    <!-- True 3D WebGL Three.js Town Canvas (Interactive Orbit, 360 Rotation, Pan & Zoom) -->
    <TownCanvas3D
      ref="canvasRef"
      :active-type-filter="activeFilter"
      @building-click="(id) => graphStore.selectEntity(id)"
    />

    <!-- Movable & Resizable Topic Detail Inspector -->
    <BuildingInfoCard :mode="mode" />

    <!-- Deep Topic Reader Modal / Slide-Over Pane -->
    <TopicReaderModal />

    <!-- Exam Gist & High-Yield Revision Sheet Modal -->
    <ExamGistModal />

    <!-- Interactive Quiz Master Modal (Topic & Document) -->
    <QuizModal />

    <!-- Study Progress & Topic Completion Breakdown Modal -->
    <StudyProgressModal :mode="mode" />

    <!-- Personal Notes Slide-Over Drawer -->
    <NotesDrawer :document-id="documentId" />

    <!-- Movable & Resizable Regulus AI Chat Window (Docked capsule initially, full screen visibility) -->
    <RegulusPanel
      :document-id="documentId"
      :mode="mode"
    />
  </div>
</template>
