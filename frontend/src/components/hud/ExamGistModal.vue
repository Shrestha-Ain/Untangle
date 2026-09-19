<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useGraphStore } from '@/stores/graph'
import ModeBadge from '@/components/shared/ModeBadge.vue'

const graphStore = useGraphStore()
const router = useRouter()
const route = useRoute()

const searchQuery = ref('')

const gistData = computed(() => graphStore.examGistData)

const filteredTopics = computed(() => {
  if (!gistData.value) return []
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return gistData.value.high_yield_topics
  return gistData.value.high_yield_topics.filter(
    (t) =>
      t.name.toLowerCase().includes(query) ||
      t.tagline.toLowerCase().includes(query) ||
      t.summary.toLowerCase().includes(query) ||
      (t.key_formula_or_rule && t.key_formula_or_rule.toLowerCase().includes(query))
  )
})

function close() {
  graphStore.closeExamGist()
}

function spotlightOnMap(nodeId: string) {
  close()
  // If we are already on the town explorer view, select node directly
  if (route.name === 'town-explorer' || route.params.documentId) {
    graphStore.selectEntity(nodeId)
  } else if (gistData.value) {
    // If opened from HomeView, navigate to the map with node selected
    router.push(`/realm/${gistData.value.document_id}`)
    setTimeout(() => {
      graphStore.selectEntity(nodeId)
    }, 400)
  }
}

function openTopicDossier(nodeId: string) {
  close()
  graphStore.openTopicDossier(nodeId)
}
</script>

<template>
  <div
    v-if="graphStore.isExamGistOpen && gistData"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/40 backdrop-blur-xs transition-opacity"
    @click.self="close"
  >
    <!-- Modal Container -->
    <div
      class="w-full max-w-4xl max-h-[90vh] bg-white rounded-3xl shadow-2xl border-2 border-[#D4D3CE] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200"
    >
      <!-- Modal Header -->
      <div class="px-6 py-5 bg-[#F7F6F3] border-b border-[#E4E3DF] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="space-y-1">
          <div class="flex items-center gap-2.5">
            <span class="w-7 h-7 rounded-lg bg-[#C49A3C] text-white flex items-center justify-center font-bold shadow-xs">
              <span class="material-symbols-outlined text-base">bolt</span>
            </span>
            <h2 class="text-lg font-extrabold text-[#1C1B18] tracking-tight">
              Exam Gist & High-Yield Revision Sheet
            </h2>
            <ModeBadge :mode="gistData.mode" size="sm" />
          </div>
          <p class="text-xs text-[#5C5A54] line-clamp-1 font-medium">
            {{ gistData.document_title }} — Rapid concept synthesis, core formulas & exam traps
          </p>
        </div>

        <div class="flex items-center gap-2">
          <!-- Search input -->
          <div class="relative w-48 sm:w-56">
            <span class="material-symbols-outlined absolute left-2.5 top-2 text-[#8A877F] text-sm">search</span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Filter topics..."
              class="w-full pl-8 pr-3 py-1.5 text-xs rounded-xl border border-[#D4D3CE] bg-white text-[#1C1B18] placeholder-[#8A877F] focus:border-[#C49A3C] focus:outline-none focus:ring-2 focus:ring-[#C49A3C]/20 transition-all"
            />
          </div>

          <!-- Close button -->
          <button
            @click="close"
            class="w-8 h-8 rounded-full flex items-center justify-center text-[#5C5A54] hover:text-[#1C1B18] hover:bg-[#EFEFED] transition-colors"
            title="Close"
          >
            <span class="material-symbols-outlined text-lg">close</span>
          </button>
        </div>
      </div>

      <!-- Quick Exam Stats Banner -->
      <div class="px-6 py-2.5 bg-[#FFFDF9] border-b border-[#DDD0B0] flex items-center justify-between text-xs text-[#8C6A2C]">
        <div class="flex items-center gap-2 font-mono font-medium">
          <span class="w-2 h-2 rounded-full bg-[#C49A3C] animate-ping"></span>
          <span>{{ gistData.high_yield_topics.length }} High-Yield Core Topics Ranked by Exam Importance</span>
        </div>
        <span class="font-mono text-[11px] text-[#A68032] hidden sm:inline">
          Last updated: {{ gistData.generated_at }}
        </span>
      </div>

      <!-- Scrollable Topics Sheet -->
      <div class="flex-1 p-6 overflow-y-auto space-y-6">
        <div
          v-for="topic in filteredTopics"
          :key="topic.node_id"
          class="rounded-2xl border-2 border-[#E4E3DF] bg-white hover:border-[#DDD0B0] p-5 shadow-xs transition-all space-y-4"
        >
          <!-- Card Header: Rank + Title + Type + Actions -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#EFEFED] pb-3">
            <div class="flex items-center gap-3 flex-wrap">
              <span class="px-2.5 py-1 text-xs font-mono font-extrabold rounded-lg bg-[#C49A3C] text-white shadow-xs">
                #{{ topic.high_yield_rank }} High-Yield
              </span>
              <h3 class="text-base font-bold text-[#1C1B18]">
                {{ topic.name }}
              </h3>
              <span class="px-2 py-0.5 text-[10px] font-mono font-semibold uppercase bg-[#EFEFED] text-[#5C5A54] rounded-md">
                {{ topic.type }}
              </span>
            </div>

            <!-- Navigation Buttons -->
            <div class="flex items-center gap-2">
              <button
                @click="openTopicDossier(topic.node_id)"
                class="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-[#5C5A54] hover:text-[#1C1B18] hover:bg-[#EFEFED] rounded-lg border border-[#D4D3CE] transition-colors"
                title="Read complete raw chunks dossier"
              >
                <span class="material-symbols-outlined text-xs text-[#3D6B5A]">menu_book</span>
                <span>Deep Dossier</span>
              </button>

              <button
                @click="spotlightOnMap(topic.node_id)"
                class="inline-flex items-center gap-1 px-3 py-1 text-xs font-bold text-white bg-[#3D6B5A] hover:bg-[#2C5043] rounded-lg shadow-[0_2px_0_#2C5043] active:translate-y-px transition-all"
                title="Spotlight concept on knowledge map"
              >
                <span class="material-symbols-outlined text-xs">near_me</span>
                <span>Spotlight on Map</span>
              </button>
            </div>
          </div>

          <!-- Tagline & 2-Sentence Core Summary -->
          <div class="space-y-1">
            <div class="text-[11px] font-mono font-semibold text-[#8C6A2C]">
              // {{ topic.tagline }}
            </div>
            <p class="text-xs leading-relaxed text-[#2C2922] font-medium bg-[#F7F6F3] p-3 rounded-xl border border-[#E4E3DF]">
              {{ topic.summary }}
            </p>
          </div>

          <!-- Key Formula or Rule to Memorize -->
          <div v-if="topic.key_formula_or_rule" class="space-y-1.5">
            <div class="flex items-center gap-1 text-[11px] font-mono font-bold uppercase tracking-wider text-[#8C6A2C]">
              <span class="material-symbols-outlined text-xs">functions</span>
              <span>Core Formula / Rule to Memorize</span>
            </div>
            <div class="p-3 bg-[#1C1B18] text-[#E5F3EE] font-mono text-xs rounded-xl shadow-inner overflow-x-auto whitespace-pre leading-relaxed">
              {{ topic.key_formula_or_rule }}
            </div>
          </div>

          <!-- Exam Question & Common Pitfall/Trap -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
            <!-- Likely Exam Question -->
            <div class="p-3.5 bg-[#FFFDF9] rounded-xl border border-[#DDD0B0] space-y-1.5">
              <div class="flex items-center gap-1.5 text-xs font-bold text-[#8C6A2C]">
                <span class="material-symbols-outlined text-sm">help_outline</span>
                <span>Classic Exam Question</span>
              </div>
              <p class="text-xs text-[#2C2922] italic font-medium leading-relaxed">
                "{{ topic.likely_exam_question }}"
              </p>
            </div>

            <!-- Exam Trap to Avoid -->
            <div class="p-3.5 bg-[#A85A5A]/10 rounded-xl border border-[#A85A5A]/25 space-y-1.5">
              <div class="flex items-center gap-1.5 text-xs font-bold text-[#A85A5A]">
                <span class="material-symbols-outlined text-sm">warning_amber</span>
                <span>Common Exam Trap / Misconception</span>
              </div>
              <p class="text-xs text-[#4A2020] leading-relaxed">
                {{ topic.exam_trap }}
              </p>
            </div>
          </div>
        </div>

        <div v-if="filteredTopics.length === 0" class="py-12 text-center text-sm text-[#8A877F]">
          No high-yield topics matched "{{ searchQuery }}".
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-3.5 bg-[#F7F6F3] border-t border-[#E4E3DF] flex items-center justify-between text-xs text-[#5C5A54]">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-sm text-[#3D6B5A]">check_circle</span>
          <span>Curated for time-pressured pre-exam review</span>
        </div>
        <button
          @click="close"
          class="px-4 py-1.5 text-xs font-bold text-[#1C1B18] hover:bg-[#EFEFED] rounded-xl border border-[#D4D3CE] transition-colors"
        >
          Close Review Sheet
        </button>
      </div>
    </div>
  </div>
</template>

