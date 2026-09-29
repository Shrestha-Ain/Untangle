<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDocumentsStore } from '@/stores/documents'
import { useGraphStore } from '@/stores/graph'
import TownNavBar from '@/components/hud/TownNavBar.vue'
import TownCanvas from '@/components/town/TownCanvas.vue'
import BuildingInfoCard from '@/components/hud/BuildingInfoCard.vue'
import RegulusPanel from '@/components/hud/RegulusPanel.vue'
import LearningPathStepper from '@/components/hud/LearningPathStepper.vue'
import TopicReaderModal from '@/components/hud/TopicReaderModal.vue'
import ExamGistModal from '@/components/hud/ExamGistModal.vue'

const route = useRoute()
const documentsStore = useDocumentsStore()
const graphStore = useGraphStore()

const canvasRef = ref<InstanceType<typeof TownCanvas> | null>(null)
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

onMounted(async () => {
  if (documentsStore.documents.length === 0) {
    await documentsStore.fetchDocuments()
  }
  await graphStore.loadGraph(documentId.value, mode.value)

  // REQUIREMENT 2: Whenever we open the map, it will open with the first step automatically selected
  if (graphStore.learningPath.length > 0) {
    graphStore.setPathIndex(0)
    canvasRef.value?.focusOnNode(graphStore.learningPath[0])
  } else if (graphStore.nodes.length > 0) {
    graphStore.selectEntity(graphStore.nodes[0].id)
    canvasRef.value?.focusOnNode(graphStore.nodes[0].id)
  }
})

function handleZoomIn() {
  canvasRef.value?.zoomIn()
}

function handleZoomOut() {
  canvasRef.value?.zoomOut()
}

function handleRecenter() {
  canvasRef.value?.recenter()
}
</script>

<template>
  <div class="relative w-screen h-screen overflow-hidden bg-[#EBF7F2]">
    <!-- Top HUD Navigation -->
    <TownNavBar
      :title="currentDoc.title"
      :mode="mode"
      v-model:active-filter="activeFilter"
      @zoom-in="handleZoomIn"
      @zoom-out="handleZoomOut"
      @recenter="handleRecenter"
    />

    <!-- Guided Learning Path Stepper (Top Center) -->
    <LearningPathStepper />

    <!-- Interactive SVG Isometric Canvas -->
    <TownCanvas
      ref="canvasRef"
      :active-type-filter="activeFilter"
    />

    <!-- Right Building / Topic Detail Drawer -->
    <BuildingInfoCard :mode="mode" />

    <!-- Deep Topic Reader Modal / Slide-Over Pane -->
    <TopicReaderModal />

    <!-- Exam Gist & High-Yield Revision Sheet Modal -->
    <ExamGistModal />

    <!-- Bottom-Left Regulus AI Guide Panel -->
    <RegulusPanel
      :document-id="documentId"
      :mode="mode"
    />
  </div>
</template>
