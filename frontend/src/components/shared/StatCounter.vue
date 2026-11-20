<script setup lang="ts">
defineProps<{
  label: string
  value: number | string | undefined
}>()
</script>

<template>
  <div class="bg-slate-50 dark:bg-slate-800/80 rounded-xl p-2 border border-slate-200 dark:border-slate-700/80 flex flex-col justify-center transition-colors">
    <span class="text-[10px] uppercase font-mono tracking-wider text-slate-500 dark:text-slate-400 font-semibold truncate">
      {{ label }}
    </span>
    <span class="text-sm font-mono font-bold text-slate-900 dark:text-white mt-0.5">
      {{ value ?? '—' }}
    </span>
  </div>
</template>
