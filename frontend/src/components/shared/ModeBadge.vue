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
      'bg-[#E8F0EC] text-[#3D6B5A] border-[#C4D8CC]'
    ]"
  >
    <span class="w-1.5 h-1.5 rounded-full bg-[#4E9A7D] inline-block"></span>
    Research
  </span>
  <span
    v-else
    :class="[
      'inline-flex items-center gap-1.5 font-mono font-bold tracking-wider uppercase rounded-md border transition-colors',
      size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-1 text-xs',
      'bg-[#F5EFE3] text-[#8C6A2C] border-[#DDD0B0]'
    ]"
  >
    <span class="w-1.5 h-1.5 rounded-full bg-[#C49A3C] inline-block"></span>
    Study
  </span>
</template>

