<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDocumentsStore } from '@/stores/documents'
import TopHudHeader from '@/components/home/TopHudHeader.vue'
import SourceUploadPanel from '@/components/home/SourceUploadPanel.vue'
import IngestionProgress from '@/components/home/IngestionProgress.vue'
import MapCard from '@/components/home/MapCard.vue'
import FilterChips from '@/components/home/FilterChips.vue'
import ExamGistModal from '@/components/hud/ExamGistModal.vue'

const documentsStore = useDocumentsStore()

const currentFilter = ref<'all' | 'research' | 'study'>('all')
const searchQuery = ref('')

onMounted(() => {
  documentsStore.fetchDocuments()
})

const filteredDocuments = computed(() => {
  let docs = documentsStore.documents

  if (currentFilter.value === 'research') {
    docs = docs.filter((d) => d.source_mode === 'research')
  } else if (currentFilter.value === 'study') {
    docs = docs.filter((d) => d.source_mode === 'study')
  }

  const query = searchQuery.value.trim().toLowerCase()
  if (query) {
    docs = docs.filter(
      (d) =>
        d.title.toLowerCase().includes(query) ||
        (d.author && d.author.toLowerCase().includes(query))
    )
  }

  return docs
})

function handleDelete(id: string) {
  if (confirm('Delete this knowledge map?')) {
    documentsStore.deleteDocument(id)
  }
}
</script>

<template>
  <div class="min-h-screen w-full bg-[#F7F6F3] text-[#1C1B18] flex flex-col selection:bg-[#E8F0EC] selection:text-[#3D6B5A] relative overflow-x-hidden">
    <!-- Soft Page Ambient Glows (inspired by page1/code.html) -->
    <div class="absolute top-20 left-1/4 w-96 h-96 bg-emerald-100/40 rounded-full blur-3xl pointer-events-none -z-10"></div>
    <div class="absolute top-96 right-10 w-96 h-96 bg-amber-100/30 rounded-full blur-3xl pointer-events-none -z-10"></div>

    <!-- Top Nav Header -->
    <TopHudHeader />

    <!-- Main Content Area -->
    <main class="flex-1 w-full max-w-7xl mx-auto px-6 py-8 space-y-9">
      <!-- Ingestion Stepper Notification (if actively processing) -->
      <IngestionProgress />

      <!-- Dual Mode Upload Area -->
      <SourceUploadPanel />

      <!-- Knowledge Maps Library Section -->
      <section class="space-y-5 pt-2">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-extrabold tracking-tight text-[#1C1B18]">Your Knowledge Maps</h2>
              <span class="px-2 py-0.5 text-xs font-mono font-bold bg-[#EFEFED] text-[#5C5A54] rounded-full">
                {{ filteredDocuments.length }}
              </span>
            </div>
            <p class="text-xs text-[#5C5A54] mt-0.5 font-medium">
              Interactive multi-hop entity graphs & structural textbook chapters.
            </p>
          </div>

          <!-- Search Input with Keyboard Shortcut Hint -->
          <div class="relative w-full sm:w-72">
            <span class="material-symbols-outlined absolute left-3.5 top-2.5 text-[#8A877F] text-base">search</span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search papers & books..."
              class="w-full pl-10 pr-9 py-2 text-xs rounded-xl border border-[#D4D3CE] bg-white text-[#1C1B18] placeholder-[#8A877F] shadow-xs focus:border-[#3D6B5A] focus:outline-none focus:ring-2 focus:ring-[#3D6B5A]/20 transition-all"
            />
            <span class="absolute right-3 top-2.5 px-1.5 py-0.5 text-[9.5px] font-mono font-semibold bg-[#EFEFED] text-[#8A877F] rounded">
              ⌘K
            </span>
          </div>
        </div>

        <!-- Filter Chips -->
        <FilterChips
          v-model="currentFilter"
          :all-count="documentsStore.documents.length"
          :research-count="documentsStore.researchDocuments.length"
          :study-count="documentsStore.studyDocuments.length"
        />

        <!-- Maps Grid -->
        <div
          v-if="filteredDocuments.length > 0"
          class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-1"
        >
          <MapCard
            v-for="doc in filteredDocuments"
            :key="doc.id"
            :doc="doc"
            @delete="handleDelete"
          />
        </div>

        <!-- Empty State -->
        <div
          v-else
          class="bg-white rounded-3xl border-2 border-dashed border-[#D4D3CE] p-12 text-center space-y-3 shadow-xs"
        >
          <div class="w-14 h-14 mx-auto rounded-2xl bg-[#EFEFED] text-[#8A877F] flex items-center justify-center shadow-inner">
            <span class="material-symbols-outlined text-3xl">map</span>
          </div>
          <h3 class="text-sm font-bold text-[#1C1B18]">No knowledge maps found</h3>
          <p class="text-xs text-[#5C5A54] max-w-sm mx-auto">
            Upload an academic paper on the left or a textbook on the right to generate your first interactive map.
          </p>
        </div>
      </section>
    </main>

    <!-- Document-Wide Exam Gist Modal -->
    <ExamGistModal />

    <!-- Footer -->
    <footer class="w-full border-t border-[#D4D3CE] bg-[#F7F6F3] py-6 mt-12">
      <div class="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#8A877F]">
        <div class="flex items-center gap-2">
          <span class="font-bold text-[#1C1B18]">Untangle</span>
          <span>•</span>
          <span>Knowledge Graph Synthesis & Exploration</span>
        </div>
        <p class="font-mono text-[11px]">Built on Microsoft GraphRAG · Vue 3 · FastAPI · Neo4j · Qdrant</p>
      </div>
    </footer>
  </div>
</template>
