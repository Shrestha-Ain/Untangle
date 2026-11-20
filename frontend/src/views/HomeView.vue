<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentsStore } from '@/stores/documents'
import TopHudHeader from '@/components/home/TopHudHeader.vue'
import SourceUploadPanel from '@/components/home/SourceUploadPanel.vue'
import IngestionProgress from '@/components/home/IngestionProgress.vue'
import MapCard from '@/components/home/MapCard.vue'
import FilterChips from '@/components/home/FilterChips.vue'
import ExamGistModal from '@/components/hud/ExamGistModal.vue'
import InteractiveSparkles from '@/components/home/InteractiveSparkles.vue'
import DemoVideoModal from '@/components/home/DemoVideoModal.vue'

const router = useRouter()
const documentsStore = useDocumentsStore()

const currentFilter = ref<'all' | 'research' | 'study'>('all')
const searchQuery = ref('')
const isDemoVideoOpen = ref(false)

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

function launchDemoTown() {
  const targetId = documentsStore.documents.length > 0 ? documentsStore.documents[0].id : 'doc-attention-1706'
  router.push(`/town/${targetId}`)
}
</script>

<template>
  <div class="min-h-screen w-full bg-[#F0F4F8] dark:bg-[#0B1120] text-slate-900 dark:text-slate-100 flex flex-col selection:bg-blue-100 selection:text-blue-900 dark:selection:bg-blue-900/60 dark:selection:text-blue-100 relative overflow-x-hidden transition-colors duration-300">
    <!-- 🌟 Interactive Mouse Sparkle / Celestial Bluish Particle Trail Layer -->
    <InteractiveSparkles />

    <!-- Top Nav Header -->
    <TopHudHeader />

    <!-- Main Content Area -->
    <main class="flex-1 w-full max-w-7xl mx-auto px-6 py-8 space-y-10 relative z-20">
      <!-- 🚀 Eye-Catching, Focused Hero Section (Clean, Bluish, Not Overwhelming) -->
      <section class="text-center pt-2 pb-4 space-y-5 max-w-3xl mx-auto">
        <!-- Elegant Pill Badge -->
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 dark:bg-blue-950/70 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300 text-xs font-mono font-bold shadow-xs">
          <span class="w-2 h-2 rounded-full bg-blue-500 animate-ping"></span>
          <span>✦ 3D SPATIAL KNOWLEDGE REALMS • GRAPHRAG ATLAS</span>
        </div>

        <!-- Hero Headline -->
        <h1 class="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 dark:text-white leading-tight">
          Master Complex Literature in 3D
          <span class="block mt-1 text-blue-600 dark:text-sky-400">
            Navigate Living Concept Realms
          </span>
        </h1>

        <!-- Hero Subtitle (Crisp & Digestible) -->
        <p class="text-sm sm:text-base text-slate-600 dark:text-slate-300 max-w-2xl mx-auto leading-relaxed font-medium">
          Transform dense academic papers and textbooks into explorable 3D knowledge realms. Follow prerequisite energy highways, interact with stepped towers, and master topics effortlessly with Regulus AI.
        </p>

        <!-- Action CTAs -->
        <div class="flex flex-wrap items-center justify-center gap-3.5 pt-1">
          <!-- Main 3D Realm Explorer Button -->
          <button
            @click="launchDemoTown"
            class="px-6 py-3 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-sm shadow-[0_4px_0_#1D4ED8] active:translate-y-0.5 transition-all flex items-center gap-2 group cursor-pointer"
          >
            <span class="material-symbols-outlined text-lg group-hover:rotate-12 transition-transform">view_in_ar</span>
            <span>Explore 3D Realm</span>
          </button>

          <!-- Interactive Demo Video Button -->
          <button
            @click="isDemoVideoOpen = true"
            class="px-5 py-3 rounded-2xl bg-white dark:bg-slate-800/90 text-blue-600 dark:text-sky-400 border-2 border-blue-200 dark:border-blue-800/80 hover:border-blue-500 dark:hover:border-blue-500 font-extrabold text-sm shadow-xs transition-all flex items-center gap-2 group cursor-pointer"
          >
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="material-symbols-outlined text-lg group-hover:scale-110 transition-transform">play_circle</span>
            <span>Watch Demo Video</span>
          </button>

          <!-- Upload Document Anchor -->
          <a
            href="#upload-section"
            class="px-6 py-3 rounded-2xl bg-white dark:bg-slate-800/90 text-slate-800 dark:text-slate-200 border-2 border-slate-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 font-bold text-sm shadow-xs transition-all flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-lg text-blue-600 dark:text-blue-400">upload_file</span>
            <span>Upload Document</span>
          </a>
        </div>

        <!-- 3 Sleek Compact Pillars (Visual, Concise, Zero Clutter) -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3.5 pt-4 text-left">
          <!-- Pillar 1 -->
          <div class="p-4 rounded-2xl bg-white dark:bg-[#0F172A] border border-blue-100 dark:border-slate-800 shadow-xs space-y-1.5 transition-all hover:border-blue-400 dark:hover:border-blue-600">
            <div class="w-8 h-8 rounded-xl bg-blue-50 dark:bg-blue-950/80 text-blue-600 dark:text-blue-400 flex items-center justify-center">
              <span class="material-symbols-outlined text-lg">view_in_ar</span>
            </div>
            <h3 class="text-xs font-black uppercase tracking-wide text-slate-900 dark:text-white">3D Spatial Palaces</h3>
            <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
              Replace dense pages with physical towers you can orbit 360°, inspect, and remember visually.
            </p>
          </div>

          <!-- Pillar 2 -->
          <div class="p-4 rounded-2xl bg-white dark:bg-[#0F172A] border border-blue-100 dark:border-slate-800 shadow-xs space-y-1.5 transition-all hover:border-cyan-400 dark:hover:border-cyan-600">
            <div class="w-8 h-8 rounded-xl bg-cyan-50 dark:bg-cyan-950/80 text-cyan-600 dark:text-cyan-400 flex items-center justify-center">
              <span class="material-symbols-outlined text-lg">alt_route</span>
            </div>
            <h3 class="text-xs font-black uppercase tracking-wide text-slate-900 dark:text-white">Prerequisite Roads</h3>
            <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
              Directional energy viaducts guide you step-by-step from fundamental bases to apex milestones.
            </p>
          </div>

          <!-- Pillar 3 -->
          <div class="p-4 rounded-2xl bg-white dark:bg-[#0F172A] border border-blue-100 dark:border-slate-800 shadow-xs space-y-1.5 transition-all hover:border-indigo-400 dark:hover:border-indigo-600">
            <div class="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
              <span class="material-symbols-outlined text-lg">psychology</span>
            </div>
            <h3 class="text-xs font-black uppercase tracking-wide text-slate-900 dark:text-white">Regulus AI & Quizzes</h3>
            <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
              Learn through real analogies, formula derivations, interactive quizzes, and 2-min exam sheets.
            </p>
          </div>
        </div>

        <!-- 🎬 Interactive Video Walkthrough Banner Card -->
        <div
          @click="isDemoVideoOpen = true"
          class="mt-4 p-4 sm:p-5 rounded-3xl bg-gradient-to-r from-blue-900/40 via-indigo-900/30 to-slate-900/60 dark:from-blue-950/70 dark:via-indigo-950/50 dark:to-slate-900/90 border-2 border-blue-400/40 dark:border-blue-700/50 shadow-md hover:border-blue-400 hover:shadow-xl transition-all cursor-pointer flex flex-col sm:flex-row items-center justify-between gap-4 text-left group"
        >
          <div class="flex items-center gap-3.5">
            <div class="w-12 h-12 rounded-2xl bg-blue-600 group-hover:bg-blue-500 text-white flex items-center justify-center shadow-lg transition-transform group-hover:scale-105 shrink-0">
              <span class="material-symbols-outlined text-2xl ml-0.5">play_arrow</span>
            </div>
            <div class="space-y-0.5">
              <div class="flex items-center gap-2">
                <span class="text-xs font-mono font-bold text-sky-400">✦ NARRATED VIDEO TOUR</span>
                <span class="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-mono font-bold">1m 26s</span>
              </div>
              <h4 class="text-sm font-extrabold text-white">See Untangle in Action: 3D Palaces, Energy Viaducts & AI Guide</h4>
              <p class="text-xs text-slate-300">Click to watch an interactive walkthrough and live 3D animations.</p>
            </div>
          </div>

          <div class="px-4 py-2 rounded-xl bg-blue-600 group-hover:bg-blue-500 text-white text-xs font-bold flex items-center gap-1.5 transition-colors shrink-0">
            <span>Watch Demo</span>
            <span class="material-symbols-outlined text-sm">arrow_forward</span>
          </div>
        </div>
      </section>

      <!-- Ingestion Stepper Notification (if actively processing) -->
      <IngestionProgress />

      <!-- Dual Mode Upload Area -->
      <section id="upload-section">
        <SourceUploadPanel />
      </section>

      <!-- Knowledge Maps Library Section -->
      <section class="space-y-4 pt-2">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white">Your Knowledge Maps</h2>
              <span class="px-2 py-0.5 text-xs font-mono font-bold bg-blue-100 dark:bg-slate-800 text-blue-700 dark:text-blue-300 rounded-full">
                {{ filteredDocuments.length }}
              </span>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
              Interactive multi-hop entity graphs & structural textbook chapters.
            </p>
          </div>

          <!-- Search Input with Keyboard Shortcut Hint -->
          <div class="relative w-full sm:w-72">
            <span class="material-symbols-outlined absolute left-3.5 top-2.5 text-slate-400 text-base">search</span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search papers & books..."
              class="w-full pl-10 pr-9 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0F172A] text-slate-900 dark:text-white placeholder-slate-400 shadow-xs focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
            />
            <span class="absolute right-3 top-2.5 px-1.5 py-0.5 text-[9.5px] font-mono font-semibold bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 rounded">
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
          class="bg-white dark:bg-[#0F172A] rounded-3xl border-2 border-dashed border-slate-200 dark:border-slate-800 p-12 text-center space-y-3 shadow-xs"
        >
          <div class="w-14 h-14 mx-auto rounded-2xl bg-blue-50 dark:bg-slate-800 text-blue-600 dark:text-blue-400 flex items-center justify-center shadow-inner">
            <span class="material-symbols-outlined text-3xl">map</span>
          </div>
          <h3 class="text-sm font-bold text-slate-900 dark:text-white">No knowledge maps found</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
            Upload an academic paper on the left or a textbook on the right to generate your first interactive map.
          </p>
        </div>
      </section>
    </main>

    <!-- Document-Wide Exam Gist Modal -->
    <ExamGistModal />

    <!-- 🎬 Interactive Demo Video Walkthrough Modal (7-Stage Product Tour + 3D Animation) -->
    <DemoVideoModal :is-open="isDemoVideoOpen" @close="isDemoVideoOpen = false" />

    <!-- Footer -->
    <footer class="w-full border-t border-blue-100 dark:border-slate-800/80 bg-[#F0F4F8] dark:bg-[#0B1120] py-6 mt-12 transition-colors">
      <div class="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 dark:text-slate-400">
        <div class="flex items-center gap-2">
          <span class="font-bold text-slate-900 dark:text-white">Untangle</span>
          <span>•</span>
          <span>3D GraphRAG Spatial Knowledge Synthesis</span>
        </div>
        <p class="font-mono text-[11px]">Built on WebGL Three.js · Microsoft GraphRAG · Vue 3 · FastAPI · Neo4j</p>
      </div>
    </footer>
  </div>
</template>
