<script setup lang="ts">
// App.vue is the root component. It only renders <RouterView />,
// which is the slot where Vue Router injects the current page component
// (LoginView, HomeView, or TownExplorerView).
// Global layout elements (if any) would go here.
import { RouterView } from 'vue-router'
</script>

<template>
  <!-- RouterView renders whichever View component matches the current URL -->
  <RouterView />
</template>
