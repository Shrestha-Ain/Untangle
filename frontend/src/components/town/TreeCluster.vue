<script setup lang="ts">
defineProps<{
  x: number
  y: number
}>()
</script>

<template>
  <g :transform="`translate(${x}, ${y})`" class="pointer-events-none select-none">
    <!-- Soft ground shadow for foliage -->
    <ellipse cx="2" cy="14" rx="28" ry="12" fill="#0F172A" opacity="0.08" />

    <!-- Varied vibrant tree circles (page2 style) -->
    <circle cx="-12" cy="2" r="18" fill="#86EFAC" />
    <circle cx="-16" cy="-2" r="13" fill="#BBF7D0" />
    <circle cx="12" cy="6" r="16" fill="#4ADE80" />
    <circle cx="2" cy="-8" r="19" fill="#86EFAC" />
    <circle cx="-1" cy="-12" r="14" fill="#BBF7D0" />
    <circle cx="16" cy="-4" r="13" fill="#A7F3D0" />
  </g>
</template>
