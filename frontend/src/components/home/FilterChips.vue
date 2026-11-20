<script setup lang="ts">
defineProps<{
  modelValue: 'all' | 'research' | 'study'
  allCount: number
  researchCount: number
  studyCount: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: 'all' | 'research' | 'study'): void
}>()
</script>

<template>
  <div class="flex items-center gap-2 flex-wrap">
    <button
      @click="emit('update:modelValue', 'all')"
      class="px-3.5 py-1.5 text-xs font-bold rounded-xl transition-all flex items-center gap-1.5 active:scale-95 shadow-2xs"
      :class="[
        modelValue === 'all'
          ? 'bg-blue-600 text-white shadow-xs'
          : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
      ]"
    >
      <span>All Maps</span>
      <span
        class="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold"
        :class="modelValue === 'all' ? 'bg-white/25 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'"
      >
        {{ allCount }}
      </span>
    </button>

    <button
      @click="emit('update:modelValue', 'research')"
      class="px-3.5 py-1.5 text-xs font-bold rounded-xl transition-all flex items-center gap-1.5 active:scale-95 shadow-2xs"
      :class="[
        modelValue === 'research'
          ? 'bg-blue-700 text-white shadow-xs'
          : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
      ]"
    >
      <span class="w-1.5 h-1.5 rounded-full bg-blue-400 inline-block"></span>
      <span>Research Papers</span>
      <span
        class="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold"
        :class="modelValue === 'research' ? 'bg-white/25 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'"
      >
        {{ researchCount }}
      </span>
    </button>

    <button
      @click="emit('update:modelValue', 'study')"
      class="px-3.5 py-1.5 text-xs font-bold rounded-xl transition-all flex items-center gap-1.5 active:scale-95 shadow-2xs"
      :class="[
        modelValue === 'study'
          ? 'bg-cyan-600 text-white shadow-xs'
          : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
      ]"
    >
      <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 inline-block"></span>
      <span>Textbooks & Syllabi</span>
      <span
        class="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold"
        :class="modelValue === 'study' ? 'bg-white/25 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'"
      >
        {{ studyCount }}
      </span>
    </button>
  </div>
</template>
