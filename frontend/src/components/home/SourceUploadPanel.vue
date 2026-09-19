<script setup lang="ts">
import { ref } from 'vue'
import { useDocumentsStore } from '@/stores/documents'

const documentsStore = useDocumentsStore()

const arxivInput = ref('')
const isDraggingResearch = ref(false)
const isDraggingStudy = ref(false)

function onFileSelect(e: Event, mode: 'research' | 'study') {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    documentsStore.uploadDocument(target.files[0], null, mode)
    target.value = ''
  }
}

function onDrop(e: DragEvent, mode: 'research' | 'study') {
  if (mode === 'research') isDraggingResearch.value = false
  if (mode === 'study') isDraggingStudy.value = false

  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    documentsStore.uploadDocument(e.dataTransfer.files[0], null, mode)
  }
}

function submitArxiv() {
  const url = arxivInput.value.trim()
  if (!url) return
  documentsStore.uploadDocument(null, url, 'research')
  arxivInput.value = ''
}
</script>

<template>
  <div class="w-full relative overflow-hidden rounded-3xl bg-white border-2 border-[#D4D3CE] shadow-[0_4px_24px_rgba(28,27,24,0.06)] group">
    <!-- Ambient decorative soft glows (inspired by page1/code.html) -->
    <div class="absolute -top-24 -left-24 w-64 h-64 bg-emerald-100/60 rounded-full blur-3xl pointer-events-none transition-opacity duration-500 group-hover:opacity-80"></div>
    <div class="absolute -bottom-24 -right-24 w-64 h-64 bg-amber-100/50 rounded-full blur-3xl pointer-events-none transition-opacity duration-500 group-hover:opacity-80"></div>

    <!-- Header Strip -->
    <div class="relative px-8 py-5 border-b border-[#E4E3DF] bg-[#F7F6F3]/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
      <div>
        <div class="flex items-center gap-2">
          <h2 class="text-lg font-bold text-[#1C1B18] tracking-tight">Upload & Synthesize</h2>
          <span class="px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider bg-[#E8F0EC] text-[#3D6B5A] rounded-full border border-[#C4D8CC]">
            Dual Pipeline
          </span>
        </div>
        <p class="text-xs text-[#5C5A54] mt-0.5">Select a research paper or book to generate an explorable, multi-hop knowledge map.</p>
      </div>
    </div>

    <!-- Dual Column Upload Workflow -->
    <div class="relative grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-[#E4E3DF]">
      <!-- Column 1: Research Paper -->
      <div class="p-6 md:p-8 space-y-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <span class="w-2.5 h-2.5 rounded-full bg-[#4E9A7D] ring-4 ring-[#E8F0EC]"></span>
            <h3 class="text-sm font-bold text-[#1C1B18]">Map a Research Paper</h3>
          </div>
          <span class="px-2.5 py-1 text-[10px] font-mono font-bold uppercase tracking-wider bg-[#E8F0EC] text-[#3D6B5A] rounded-lg border border-[#C4D8CC] shadow-xs">
            Research Mode
          </span>
        </div>

        <p class="text-xs text-[#5C5A54] leading-relaxed">
          Extract named entities, relational triples, and community clusters. Generates a multi-hop traversal graph with grounded citations.
        </p>

        <!-- Dropzone -->
        <label
          class="relative flex flex-col items-center justify-center p-7 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-200"
          :class="[
            isDraggingResearch
              ? 'border-[#3D6B5A] bg-[#E8F0EC]/60 scale-[0.99]'
              : 'border-[#D4D3CE] bg-[#F7F6F3]/50 hover:bg-[#F7F6F3] hover:border-[#3D6B5A]/70 shadow-xs'
          ]"
          @dragover.prevent="isDraggingResearch = true"
          @dragleave.prevent="isDraggingResearch = false"
          @drop.prevent="onDrop($event, 'research')"
        >
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            class="sr-only"
            @change="onFileSelect($event, 'research')"
          />
          <div class="w-12 h-12 rounded-2xl bg-[#E8F0EC] text-[#3D6B5A] flex items-center justify-center mb-2 shadow-xs animate-float">
            <span class="material-symbols-outlined text-2xl">cloud_upload</span>
          </div>
          <span class="text-xs font-bold text-[#1C1B18]">Drop paper PDF or click to browse</span>
          <span class="text-[11px] text-[#8A877F] mt-0.5 font-medium">Supports PDF, DOCX, TXT (up to 50MB)</span>
        </label>

        <!-- arXiv Input -->
        <div class="space-y-1.5 pt-1">
          <label class="text-[11px] font-mono font-medium text-[#5C5A54] flex items-center gap-1.5">
            <span class="material-symbols-outlined text-[#3D6B5A]" style="font-size: 15px;">link</span>
            <span>Or import directly via arXiv identifier:</span>
          </label>
          <div class="flex items-center gap-2">
            <input
              v-model="arxivInput"
              type="text"
              placeholder="e.g. 1706.03762 or https://arxiv.org/abs/..."
              class="flex-1 px-3.5 py-2 text-xs rounded-xl border border-[#D4D3CE] bg-[#F7F6F3] text-[#1C1B18] placeholder-[#8A877F] focus:border-[#3D6B5A] focus:outline-none focus:ring-1 focus:ring-[#3D6B5A] transition-colors"
              @keydown.enter="submitArxiv"
            />
            <button
              @click="submitArxiv"
              class="px-4 py-2 text-xs font-bold text-white bg-[#3D6B5A] hover:bg-[#2C5043] rounded-xl shadow-[0_3px_0_#2C5043] active:translate-y-px transition-all flex-shrink-0"
            >
              Fetch & Build
            </button>
          </div>
        </div>
      </div>

      <!-- Column 2: Study Mode Book -->
      <div class="p-6 md:p-8 space-y-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <span class="w-2.5 h-2.5 rounded-full bg-[#C49A3C] ring-4 ring-[#F5EFE3]"></span>
            <h3 class="text-sm font-bold text-[#1C1B18]">Untangle a Book</h3>
          </div>
          <span class="px-2.5 py-1 text-[10px] font-mono font-bold uppercase tracking-wider bg-[#F5EFE3] text-[#8C6A2C] rounded-lg border border-[#DDD0B0] shadow-xs">
            Study Mode
          </span>
        </div>

        <p class="text-xs text-[#5C5A54] leading-relaxed">
          Deconstructs textbooks into hierarchical chapters, sections, and topics. Connects concepts in a guided learning sequence.
        </p>

        <!-- Dropzone -->
        <label
          class="relative flex flex-col items-center justify-center p-7 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-200"
          :class="[
            isDraggingStudy
              ? 'border-[#B8924A] bg-[#F5EFE3]/60 scale-[0.99]'
              : 'border-[#D4D3CE] bg-[#F7F6F3]/50 hover:bg-[#F7F6F3] hover:border-[#B8924A]/70 shadow-xs'
          ]"
          @dragover.prevent="isDraggingStudy = true"
          @dragleave.prevent="isDraggingStudy = false"
          @drop.prevent="onDrop($event, 'study')"
        >
          <input
            type="file"
            accept=".pdf,.epub,.txt"
            class="sr-only"
            @change="onFileSelect($event, 'study')"
          />
          <div class="w-12 h-12 rounded-2xl bg-[#F5EFE3] text-[#8C6A2C] flex items-center justify-center mb-2 shadow-xs animate-float">
            <span class="material-symbols-outlined text-2xl">auto_stories</span>
          </div>
          <span class="text-xs font-bold text-[#1C1B18]">Drop textbook, syllabus, or course notes</span>
          <span class="text-[11px] text-[#8A877F] mt-0.5 font-medium">Supports PDF, EPUB, TXT</span>
        </label>

        <!-- Cross-source Context Pill -->
        <div class="rounded-2xl p-3.5 bg-[#F5EFE3]/70 border border-[#DDD0B0] flex items-start gap-2.5 shadow-xs">
          <span class="material-symbols-outlined text-[#8C6A2C] text-base mt-0.5 flex-shrink-0">lightbulb</span>
          <p class="text-[11px] text-[#8C6A2C] leading-normal font-medium">
            <strong>Cross-Source Linking:</strong> When a textbook topic references outside material, Regulus will automatically flag it and suggest related papers or manual source imports.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
