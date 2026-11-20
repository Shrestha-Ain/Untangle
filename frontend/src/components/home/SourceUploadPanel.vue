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
  <div class="w-full relative overflow-hidden rounded-3xl bg-white dark:bg-[#0F172A] border-2 border-blue-100 dark:border-slate-800 shadow-[0_8px_30px_rgba(15,23,42,0.06)] dark:shadow-[0_8px_30px_rgba(0,0,0,0.5)] transition-colors group">
    <!-- Ambient decorative soft glows in soothing bluish tones -->
    <div class="absolute -top-24 -left-24 w-72 h-72 bg-blue-200/40 dark:bg-blue-600/10 rounded-full blur-3xl pointer-events-none transition-opacity duration-500 group-hover:opacity-80"></div>
    <div class="absolute -bottom-24 -right-24 w-72 h-72 bg-cyan-200/40 dark:bg-cyan-600/10 rounded-full blur-3xl pointer-events-none transition-opacity duration-500 group-hover:opacity-80"></div>

    <!-- Header Strip -->
    <div class="relative px-8 py-5 border-b border-blue-100 dark:border-slate-800 bg-[#F0F4F8]/60 dark:bg-[#111C35]/70 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
      <div>
        <div class="flex items-center gap-2">
          <h2 class="text-lg font-bold text-slate-900 dark:text-white tracking-tight">Upload & Synthesize</h2>
          <span class="px-2.5 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider bg-blue-100 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 rounded-full border border-blue-200 dark:border-blue-800">
            Dual Pipeline
          </span>
        </div>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Select a research paper or book to generate an explorable, multi-hop knowledge map.</p>
      </div>
    </div>

    <!-- Dual Column Upload Workflow -->
    <div class="relative grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-blue-100 dark:divide-slate-800">
      <!-- Column 1: Research Paper -->
      <div class="p-6 md:p-8 space-y-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <span class="w-2.5 h-2.5 rounded-full bg-blue-500 ring-4 ring-blue-100 dark:ring-blue-950"></span>
            <h3 class="text-sm font-bold text-slate-900 dark:text-white">Map a Research Paper</h3>
          </div>
          <span class="px-2.5 py-1 text-[10px] font-mono font-bold uppercase tracking-wider bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 rounded-lg border border-blue-200 dark:border-blue-800 shadow-xs">
            Research Mode
          </span>
        </div>

        <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          Extract named entities, relational triples, and community clusters. Generates a multi-hop traversal graph with grounded citations.
        </p>

        <!-- Dropzone -->
        <label
          class="relative flex flex-col items-center justify-center p-7 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-200"
          :class="[
            isDraggingResearch
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/50 scale-[0.99]'
              : 'border-slate-300 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-900/60 hover:bg-blue-50/40 dark:hover:bg-slate-800/80 hover:border-blue-500/70 shadow-xs'
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
          <div class="w-12 h-12 rounded-2xl bg-blue-100 dark:bg-blue-950/80 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-2 shadow-xs animate-float">
            <span class="material-symbols-outlined text-2xl">cloud_upload</span>
          </div>
          <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Drop paper PDF or click to browse</span>
          <span class="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5 font-medium">Supports PDF, DOCX, TXT (up to 50MB)</span>
        </label>

        <!-- arXiv Input -->
        <div class="space-y-1.5 pt-1">
          <label class="text-[11px] font-mono font-medium text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
            <span class="material-symbols-outlined text-blue-600 dark:text-blue-400" style="font-size: 15px;">link</span>
            <span>Or import directly via arXiv identifier:</span>
          </label>
          <div class="flex items-center gap-2">
            <input
              v-model="arxivInput"
              type="text"
              placeholder="e.g. 1706.03762 or https://arxiv.org/abs/..."
              class="flex-1 px-3.5 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-colors"
              @keydown.enter="submitArxiv"
            />
            <button
              @click="submitArxiv"
              class="px-4 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 rounded-xl shadow-[0_3px_0_#1D4ED8] active:translate-y-px transition-all flex-shrink-0"
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
            <span class="w-2.5 h-2.5 rounded-full bg-cyan-500 ring-4 ring-cyan-100 dark:ring-cyan-950"></span>
            <h3 class="text-sm font-bold text-slate-900 dark:text-white">Untangle a Book</h3>
          </div>
          <span class="px-2.5 py-1 text-[10px] font-mono font-bold uppercase tracking-wider bg-cyan-50 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-300 rounded-lg border border-cyan-200 dark:border-cyan-800 shadow-xs">
            Study Mode
          </span>
        </div>

        <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          Deconstructs textbooks into hierarchical chapters, sections, and topics. Connects concepts in a guided learning sequence.
        </p>

        <!-- Dropzone -->
        <label
          class="relative flex flex-col items-center justify-center p-7 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-200"
          :class="[
            isDraggingStudy
              ? 'border-cyan-500 bg-cyan-50 dark:bg-cyan-950/50 scale-[0.99]'
              : 'border-slate-300 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-900/60 hover:bg-cyan-50/40 dark:hover:bg-slate-800/80 hover:border-cyan-500/70 shadow-xs'
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
          <div class="w-12 h-12 rounded-2xl bg-cyan-100 dark:bg-cyan-950/80 text-cyan-600 dark:text-cyan-400 flex items-center justify-center mb-2 shadow-xs animate-float">
            <span class="material-symbols-outlined text-2xl">auto_stories</span>
          </div>
          <span class="text-xs font-bold text-slate-800 dark:text-slate-200">Drop textbook, syllabus, or course notes</span>
          <span class="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5 font-medium">Supports PDF, EPUB, TXT</span>
        </label>

        <!-- Cross-source Context Pill -->
        <div class="rounded-2xl p-3.5 bg-blue-50/80 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800/60 flex items-start gap-2.5 shadow-xs">
          <span class="material-symbols-outlined text-blue-600 dark:text-blue-400 text-base mt-0.5 flex-shrink-0">lightbulb</span>
          <p class="text-[11px] text-blue-900 dark:text-blue-200 leading-normal font-medium">
            <strong>Cross-Source Linking:</strong> When a textbook topic references outside material, Regulus will automatically flag it and suggest related papers or manual source imports.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
