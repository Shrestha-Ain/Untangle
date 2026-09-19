<script setup lang="ts">
import { computed } from 'vue'
import { useGraphStore } from '@/stores/graph'

const graphStore = useGraphStore()
const dossier = computed(() => graphStore.activeDossier)

function close() {
  graphStore.closeTopicReader()
}

function proceedNext() {
  close()
  graphStore.nextPathStep()
}
</script>

<template>
  <div
    v-if="graphStore.isReaderOpen && dossier"
    class="fixed inset-0 z-50 flex items-center justify-end bg-black/30 backdrop-blur-xs transition-opacity"
    @click.self="close"
  >
    <!-- Slide-over Deep Reading Pane -->
    <div
      class="w-full max-w-2xl h-full bg-white shadow-2xl border-l border-[#D4D3CE] flex flex-col overflow-hidden animate-in slide-in-from-right duration-300"
    >
      <!-- Reader Header -->
      <div class="px-6 py-4 bg-[#F7F6F3] border-b border-[#E4E3DF] flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <span class="px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider bg-[#E8F0EC] text-[#3D6B5A] rounded border border-[#C4D8CC]">
            {{ dossier.type }}
          </span>
          <span
            v-if="dossier.path_step"
            class="px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider bg-[#F5EFE3] text-[#8C6A2C] rounded border border-[#DDD0B0]"
          >
            Curriculum Step {{ dossier.path_step }}
          </span>
        </div>

        <button
          @click="close"
          class="w-8 h-8 rounded-full flex items-center justify-center text-[#5C5A54] hover:text-[#1C1B18] hover:bg-[#EFEFED] transition-colors"
          title="Close Reader"
        >
          <span class="material-symbols-outlined text-lg">close</span>
        </button>
      </div>

      <!-- Scrollable Reading Content -->
      <div class="flex-1 p-6 md:p-8 overflow-y-auto space-y-6 text-sm">
        <!-- Title & Badges -->
        <div class="space-y-1">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-extrabold text-[#1C1B18] tracking-tight">
              {{ dossier.name }}
            </h2>
            <button
              @click="graphStore.openExamGist()"
              class="hidden sm:inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold text-[#8C6A2C] bg-[#F5EFE3] hover:bg-[#EBDDBF] border border-[#DDD0B0] rounded-lg transition-colors"
              title="View full exam revision sheet"
            >
              <span class="material-symbols-outlined text-xs text-[#C49A3C]">bolt</span>
              <span>All Exam Gists</span>
            </button>
          </div>
        </div>

        <!-- ⚡ 2-Minute High-Yield Exam Gist Card (Exam Rush Takeaway) -->
        <div
          v-if="dossier.exam_gist"
          class="rounded-2xl border-2 border-[#DDD0B0] bg-gradient-to-br from-[#FFFDF9] to-[#F7F2E7] p-5 shadow-xs space-y-3.5"
        >
          <div class="flex items-center justify-between border-b border-[#DDD0B0]/60 pb-2.5">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-md bg-[#C49A3C] text-white flex items-center justify-center font-bold shadow-xs">
                <span class="material-symbols-outlined text-sm">bolt</span>
              </span>
              <div>
                <span class="text-xs font-mono font-extrabold uppercase tracking-wider text-[#8C6A2C]">
                  2-Minute Exam Gist
                </span>
                <span class="text-[10px] text-[#A68032] ml-2 font-medium">High-Yield Takeaways</span>
              </div>
            </div>
            <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-[#C49A3C]/15 text-[#8C6A2C]">
              EXAM READY
            </span>
          </div>

          <!-- Bullet takeaways -->
          <ul class="space-y-1.5 text-xs text-[#3E382E] list-disc list-inside leading-relaxed font-medium">
            <li v-for="(takeaway, i) in dossier.exam_gist.key_takeaways" :key="i" class="marker:text-[#C49A3C]">
              {{ takeaway }}
            </li>
          </ul>

          <!-- Formula to memorize if present -->
          <div v-if="dossier.exam_gist.formula_to_memorize" class="space-y-1 pt-1">
            <span class="text-[10.5px] font-mono font-bold uppercase tracking-wider text-[#8C6A2C] flex items-center gap-1">
              <span class="material-symbols-outlined text-xs">edit_note</span>
              <span>Formula to Memorize</span>
            </span>
            <div class="p-2.5 bg-[#1C1B18] text-[#E5F3EE] font-mono text-xs rounded-xl shadow-inner overflow-x-auto whitespace-pre">
              {{ dossier.exam_gist.formula_to_memorize }}
            </div>
          </div>

          <!-- Likely exam question & trap -->
          <div class="grid grid-cols-1 gap-2 pt-1">
            <div class="p-3 bg-white/90 rounded-xl border border-[#DDD0B0] space-y-1">
              <div class="flex items-center gap-1 text-[11px] font-bold text-[#8C6A2C]">
                <span class="material-symbols-outlined text-xs">help</span>
                <span>Likely Exam Question</span>
              </div>
              <p class="text-xs text-[#2C2922] italic font-medium">
                "{{ dossier.exam_gist.likely_exam_question }}"
              </p>
            </div>

            <div v-if="dossier.exam_gist.trap_to_avoid" class="p-3 bg-[#A85A5A]/10 rounded-xl border border-[#A85A5A]/25 space-y-1">
              <div class="flex items-center gap-1 text-[11px] font-bold text-[#A85A5A]">
                <span class="material-symbols-outlined text-xs">warning</span>
                <span>Common Exam Trap to Avoid</span>
              </div>
              <p class="text-xs text-[#4A2020] leading-relaxed">
                {{ dossier.exam_gist.trap_to_avoid }}
              </p>
            </div>
          </div>
        </div>

        <!-- Executive Overview -->
        <div class="space-y-2">
          <h3 class="text-xs font-mono font-bold uppercase tracking-wider text-[#8A877F] flex items-center gap-1.5">
            <span class="material-symbols-outlined text-sm text-[#3D6B5A]">menu_book</span>
            <span>Comprehensive Concept Synthesis</span>
          </h3>
          <p class="text-sm leading-relaxed text-[#5C5A54] bg-[#F7F6F3] p-4 rounded-xl border border-[#E4E3DF]">
            {{ dossier.summary }}
          </p>
        </div>

        <!-- Key Equations, Mathematical Formulations or Code Snippets -->
        <div v-if="dossier.key_formulas_or_code && dossier.key_formulas_or_code.length > 0" class="space-y-2">
          <h3 class="text-xs font-mono font-bold uppercase tracking-wider text-[#8A877F] flex items-center gap-1.5">
            <span class="material-symbols-outlined text-sm text-[#3D6B5A]">functions</span>
            <span>Mathematical & Formal Definitions</span>
          </h3>
          <div class="space-y-2">
            <div
              v-for="(formula, idx) in dossier.key_formulas_or_code"
              :key="idx"
              class="p-3.5 bg-[#1C1B18] text-[#E5F3EE] font-mono text-xs rounded-xl shadow-inner overflow-x-auto whitespace-pre leading-relaxed"
            >
              {{ formula }}
            </div>
          </div>
        </div>

        <!-- All Extracted Verbatim Chunks from Source Material -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-mono font-bold uppercase tracking-wider text-[#8A877F] flex items-center gap-1.5">
              <span class="material-symbols-outlined text-sm text-[#3D6B5A]">article</span>
              <span>All Source Passages & Chunks ({{ dossier.raw_chunks.length }})</span>
            </h3>
            <span class="text-[11px] font-mono text-[#8A877F]">Direct Grounded Quotes</span>
          </div>

          <div class="space-y-3">
            <div
              v-for="chunk in dossier.raw_chunks"
              :key="chunk.chunk_id"
              class="p-4 bg-[#F7F6F3]/70 rounded-xl border border-[#E4E3DF] space-y-1.5"
            >
              <div class="flex items-center justify-between text-[11px] font-mono text-[#3D6B5A] font-bold">
                <span>{{ chunk.section_ref }}</span>
                <span class="text-[#8A877F] font-normal">ID: {{ chunk.chunk_id }}</span>
              </div>
              <p class="text-xs text-[#2C302E] leading-relaxed italic bg-white p-3 rounded-lg border border-[#E4E3DF]">
                "{{ chunk.text }}"
              </p>
            </div>
          </div>
        </div>

        <!-- Prerequisites & Next Concepts in Curriculum -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
          <!-- Prerequisites -->
          <div class="p-3.5 rounded-xl border border-[#E4E3DF] bg-[#F7F6F3]">
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-[#8A877F] block mb-1">
              Foundational Prerequisites
            </span>
            <div v-if="dossier.prerequisites.length > 0" class="flex flex-wrap gap-1.5">
              <span
                v-for="p in dossier.prerequisites"
                :key="p"
                class="px-2 py-0.5 text-xs font-mono rounded bg-white border border-[#D4D3CE] text-[#1C1B18]"
              >
                {{ p }}
              </span>
            </div>
            <span v-else class="text-xs text-[#8A877F] italic">No prior prerequisites required.</span>
          </div>

          <!-- Next Concepts -->
          <div class="p-3.5 rounded-xl border border-[#E4E3DF] bg-[#F7F6F3]">
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-[#8A877F] block mb-1">
              Next in Learning Sequence
            </span>
            <div v-if="dossier.next_concepts.length > 0" class="flex flex-wrap gap-1.5">
              <span
                v-for="n in dossier.next_concepts"
                :key="n"
                class="px-2 py-0.5 text-xs font-mono rounded bg-white border border-[#D4D3CE] text-[#3D6B5A] font-medium"
              >
                {{ n }}
              </span>
            </div>
            <span v-else class="text-xs text-[#8A877F] italic">Final synthesis milestone.</span>
          </div>
        </div>
      </div>

      <!-- Reader Footer Actions -->
      <div class="p-4 bg-[#F7F6F3] border-t border-[#E4E3DF] flex items-center justify-between">
        <button
          @click="close"
          class="px-4 py-2 text-xs font-semibold text-[#5C5A54] hover:text-[#1C1B18] rounded-xl hover:bg-[#EFEFED] transition-colors"
        >
          Return to Map
        </button>

        <button
          v-if="dossier.next_concepts.length > 0"
          @click="proceedNext"
          class="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-[#3D6B5A] hover:bg-[#2C5043] rounded-xl shadow-[0_3px_0_#2C5043] active:translate-y-px transition-all"
        >
          <span>Mark Understood & Next Concept</span>
          <span class="material-symbols-outlined text-xs">arrow_forward</span>
        </button>
      </div>
    </div>
  </div>
</template>

