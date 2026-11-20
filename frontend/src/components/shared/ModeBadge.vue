<script setup lang="ts">
defineProps<{
  mode: 'research' | 'study'
  size?: 'sm' | 'md'
}>()
</script>

<template>
  <span
    v-if="mode === 'research'"
    :class="[
      'inline-flex items-center gap-1.5 font-mono font-bold tracking-wider uppercase rounded-md border transition-colors',
      size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-1 text-xs',
      'bg-blue-50 dark:bg-blue-950/70 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800'
    ]"
  >
    <span class="w-1.5 h-1.5 rounded-full bg-blue-500 inline-block"></span>
    Research
  </span>
  <span
    v-else
    :class="[
      'inline-flex items-center gap-1.5 font-mono font-bold tracking-wider uppercase rounded-md border transition-colors',
      size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-1 text-xs',
      'bg-cyan-50 dark:bg-cyan-950/70 text-cyan-700 dark:text-cyan-300 border-cyan-200 dark:border-cyan-800'
    ]"
  >
    <span class="w-1.5 h-1.5 rounded-full bg-cyan-500 inline-block"></span>
    Study
  </span>
</template>
