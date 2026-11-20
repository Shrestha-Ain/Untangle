<script setup lang="ts">
import { watch } from 'vue'
import { useUser, useClerk } from '@clerk/vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const { user, isSignedIn } = useUser()
const clerk = useClerk()
const authStore = useAuthStore()
const themeStore = useThemeStore()

watch(
  isSignedIn,
  (signedIn) => {
    if (signedIn) {
      authStore.syncWithBackend()
    } else {
      authStore.clearAuth()
    }
  },
  { immediate: true }
)

function handleSignOut() {
  authStore.clearAuth()
  if (clerk && 'value' in clerk && clerk.value) {
    clerk.value.signOut({ redirectUrl: '/login' })
  } else if (clerk && 'signOut' in clerk) {
    (clerk as any).signOut({ redirectUrl: '/login' })
  }
}
</script>

<template>
  <header class="w-full bg-[#F0F4F8]/90 dark:bg-[#0B1120]/95 backdrop-blur-md border-b border-blue-100 dark:border-slate-800/80 sticky top-0 z-40 transition-colors">
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <!-- Left: Logo, Wordmark & Live Indicator -->
      <div class="flex items-center gap-3.5">
        <router-link to="/" class="flex items-center gap-3 group">
          <div class="w-10 h-10 rounded-2xl bg-blue-600 shadow-sm flex items-center justify-center text-white transition-transform group-hover:scale-105">
            <span class="material-symbols-outlined text-xl">hub</span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="font-extrabold text-base tracking-tight text-slate-900 dark:text-white">Untangle</span>
              <span
                class="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider rounded-full border transition-all"
                :class="[
                  authStore.isBackendConnected
                    ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800'
                    : authStore.isSyncing
                    ? 'bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'
                ]"
              >
                <span
                  class="w-1.5 h-1.5 rounded-full"
                  :class="[
                    authStore.isBackendConnected
                      ? 'bg-blue-500 animate-pulse'
                      : authStore.isSyncing
                      ? 'bg-amber-500 animate-ping'
                      : 'bg-slate-400'
                  ]"
                ></span>
                {{ authStore.isBackendConnected ? 'Backend Synced' : authStore.isSyncing ? 'Connecting...' : 'Local Dev' }}
              </span>
            </div>
            <div class="hidden md:flex items-center gap-1.5 text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              <span>GraphRAG 3D Knowledge Realms</span>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Right: User Avatar & Session Controls & Dark/Light Toggle -->
      <div class="flex items-center gap-3">
        <!-- 🌓 Theme Toggle Button (Dark / Light Mode) -->
        <button
          @click="themeStore.toggleTheme"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs font-bold hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400 shadow-xs transition-all active:scale-95"
          :title="themeStore.currentTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
        >
          <span class="material-symbols-outlined text-[16px] text-amber-500 dark:text-yellow-400">
            {{ themeStore.currentTheme === 'dark' ? 'dark_mode' : 'light_mode' }}
          </span>
          <span class="hidden sm:inline font-mono text-[11px]">
            {{ themeStore.currentTheme === 'dark' ? 'Dark' : 'Light' }}
          </span>
        </button>

        <div v-if="isSignedIn && user" class="flex items-center gap-3">
          <div class="flex items-center gap-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 pl-1.5 pr-3 py-1 rounded-2xl shadow-xs">
            <img
              v-if="user.imageUrl"
              :src="user.imageUrl"
              :alt="user.fullName ?? 'User'"
              class="w-7 h-7 rounded-xl object-cover border border-slate-200 dark:border-slate-700"
            />
            <div
              v-else
              class="w-7 h-7 rounded-xl bg-blue-600 text-white text-xs font-bold flex items-center justify-center"
            >
              {{ user.firstName?.charAt(0) ?? 'U' }}
            </div>
            <div class="hidden sm:block text-left">
              <div class="flex items-center gap-1">
                <span class="text-xs font-bold text-slate-900 dark:text-white block leading-tight">
                  {{ user.fullName ?? 'Scholar' }}
                </span>
                <span
                  v-if="authStore.isBackendConnected"
                  class="material-symbols-outlined text-[13px] text-blue-500"
                  title="Backend DB Synced"
                >
                  check_circle
                </span>
              </div>
              <span class="text-[10px] font-mono text-slate-500 dark:text-slate-400 block leading-none mt-0.5">
                {{ user.primaryEmailAddress?.emailAddress ?? user.id }}
              </span>
            </div>
          </div>

          <button
            @click="handleSignOut"
            class="px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
            title="Sign Out"
          >
            Sign out
          </button>
        </div>

        <div v-else class="flex items-center gap-2.5">
          <div class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono font-bold uppercase tracking-wider bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 rounded-xl shadow-xs">
            <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
            Guest Dev
          </div>
          <router-link
            to="/login"
            class="px-3.5 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 rounded-xl shadow-[0_3px_0_#1D4ED8] active:translate-y-px transition-all"
          >
            Sign In Screen
          </router-link>
        </div>
      </div>
    </div>
  </header>
</template>
