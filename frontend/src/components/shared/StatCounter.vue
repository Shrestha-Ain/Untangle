<script setup lang="ts">
defineProps<{
  label: string
  value: number | string | undefined
}>()
</script>

<template>
  <div class="bg-[#F7F6F3] rounded-lg p-2 border border-[#E4E3DF] flex flex-col justify-center">
    <span class="text-[10px] uppercase font-mono tracking-wider text-[#8A877F] font-semibold truncate">
      {{ label }}
    </span>
    <span class="text-sm font-mono font-bold text-[#1C1B18] mt-0.5">
      {{ value ?? '—' }}
    </span>
  </div>
</template>

