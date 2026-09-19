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
      class="px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5"
      :class="[
        modelValue === 'all'
          ? 'bg-[#1C1B18] text-white'
          : 'bg-white text-[#5C5A54] border border-[#D4D3CE] hover:bg-[#EFEFED]'
      ]"
    >
      <span>All Maps</span>
      <span
        class="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold"
        :class="modelValue === 'all' ? 'bg-white/20 text-white' : 'bg-[#EFEFED] text-[#5C5A54]'"
      >
        {{ allCount }}
      </span>
    </button>

    <button
      @click="emit('update:modelValue', 'research')"
      class="px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5"
      :class="[
        modelValue === 'research'
          ? 'bg-[#3D6B5A] text-white shadow-sm'
          : 'bg-white text-[#5C5A54] border border-[#D4D3CE] hover:bg-[#EFEFED]'
      ]"
    >
      <span class="w-1.5 h-1.5 rounded-full bg-[#4E9A7D] inline-block"></span>
      <span>Research Papers</span>
      <span
        class="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold"
        :class="modelValue === 'research' ? 'bg-white/20 text-white' : 'bg-[#EFEFED] text-[#5C5A54]'"
      >
        {{ researchCount }}
      </span>
    </button>

    <button
      @click="emit('update:modelValue', 'study')"
      class="px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5"
      :class="[
        modelValue === 'study'
          ? 'bg-[#8C6A2C] text-white shadow-sm'
          : 'bg-white text-[#5C5A54] border border-[#D4D3CE] hover:bg-[#EFEFED]'
      ]"
    >
      <span class="w-1.5 h-1.5 rounded-full bg-[#C49A3C] inline-block"></span>
      <span>Study Books</span>
      <span
        class="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold"
        :class="modelValue === 'study' ? 'bg-white/20 text-white' : 'bg-[#EFEFED] text-[#5C5A54]'"
      >
        {{ studyCount }}
      </span>
    </button>
  </div>
</template>

