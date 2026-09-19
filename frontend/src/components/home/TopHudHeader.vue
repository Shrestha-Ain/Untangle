<script setup lang="ts">
import { watch } from 'vue'
import { useUser, useClerk } from '@clerk/vue'
import { useAuthStore } from '@/stores/auth'

const { user, isSignedIn } = useUser()
const clerk = useClerk()
const authStore = useAuthStore()

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
  <header class="w-full bg-[#F7F6F3]/90 backdrop-blur-md border-b border-[#D4D3CE] sticky top-0 z-30 transition-all">
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <!-- Left: Logo, Wordmark & Live Indicator -->
      <div class="flex items-center gap-3.5">
        <router-link to="/" class="flex items-center gap-3 group">
          <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-[#2C5043] to-[#4E9A7D] p-0.5 shadow-sm flex items-center justify-center text-white transition-transform group-hover:scale-105">
            <span class="material-symbols-outlined text-xl">hub</span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="font-extrabold text-base tracking-tight text-[#1C1B18]">Untangle</span>
              <span
                class="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider rounded-full border transition-all"
                :class="[
                  authStore.isBackendConnected
                    ? 'bg-[#E8F0EC] text-[#3D6B5A] border-[#C4D8CC]'
                    : authStore.isSyncing
                    ? 'bg-[#FDF6E2] text-[#B8924A] border-[#E8DAB2]'
                    : 'bg-[#EFEFED] text-[#5C5A54] border-[#D4D3CE]'
                ]"
              >
                <span
                  class="w-1.5 h-1.5 rounded-full"
                  :class="[
                    authStore.isBackendConnected
                      ? 'bg-[#4E9A7D] animate-pulse'
                      : authStore.isSyncing
                      ? 'bg-[#B8924A] animate-ping'
                      : 'bg-[#8A877F]'
                  ]"
                ></span>
                {{ authStore.isBackendConnected ? 'Backend Synced' : authStore.isSyncing ? 'Connecting...' : 'Local Dev' }}
              </span>
            </div>
            <div class="hidden md:flex items-center gap-1.5 text-[11px] text-[#8A877F] font-medium">
              <span>GraphRAG Knowledge Engine</span>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Right: User Avatar & Session Controls -->
      <div class="flex items-center gap-4">
        <div v-if="isSignedIn && user" class="flex items-center gap-3">
          <div class="flex items-center gap-2.5 bg-white border border-[#D4D3CE] pl-1.5 pr-3 py-1 rounded-2xl shadow-xs">
            <img
              v-if="user.imageUrl"
              :src="user.imageUrl"
              :alt="user.fullName ?? 'User'"
              class="w-7 h-7 rounded-xl object-cover border border-[#E4E3DF]"
            />
            <div
              v-else
              class="w-7 h-7 rounded-xl bg-[#3D6B5A] text-white text-xs font-bold flex items-center justify-center"
            >
              {{ user.firstName?.charAt(0) ?? 'U' }}
            </div>
            <div class="hidden sm:block text-left">
              <div class="flex items-center gap-1">
                <span class="text-xs font-bold text-[#1C1B18] block leading-tight">
                  {{ user.fullName ?? 'Scholar' }}
                </span>
                <span
                  v-if="authStore.isBackendConnected"
                  class="material-symbols-outlined text-[13px] text-[#4E9A7D]"
                  title="Backend DB Synced"
                >
                  check_circle
                </span>
              </div>
              <span class="text-[10px] font-mono text-[#8A877F] block leading-none mt-0.5">
                {{ user.primaryEmailAddress?.emailAddress ?? user.id }}
              </span>
            </div>
          </div>

          <button
            @click="handleSignOut"
            class="px-3 py-1.5 text-xs font-medium text-[#5C5A54] hover:text-[#1C1B18] hover:bg-[#EFEFED] rounded-xl transition-colors"
            title="Sign Out"
          >
            Sign out
          </button>
        </div>

        <div v-else class="flex items-center gap-2.5">
          <div class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono font-bold uppercase tracking-wider bg-[#F5EFE3] text-[#8C6A2C] border border-[#DDD0B0] rounded-xl shadow-xs">
            <span class="w-1.5 h-1.5 rounded-full bg-[#C49A3C]"></span>
            Guest Dev
          </div>
          <router-link
            to="/login"
            class="px-3.5 py-1.5 text-xs font-semibold text-white bg-[#3D6B5A] hover:bg-[#2C5043] rounded-xl shadow-[0_3px_0_#2C5043] active:translate-y-px transition-all"
          >
            Sign In Screen
          </router-link>
        </div>
      </div>
    </div>
  </header>
</template>
