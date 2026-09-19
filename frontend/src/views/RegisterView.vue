<script setup lang="ts">
import { SignUp } from '@clerk/vue'
</script>

<template>
  <div class="relative min-h-screen w-full bg-[#F4F7F4] text-slate-800 flex flex-col justify-between overflow-x-hidden selection:bg-emerald-200 selection:text-emerald-900">
    <!-- Ambient background dots & glow orbs -->
    <div
      class="absolute inset-0 pointer-events-none opacity-60"
      style="background-image: radial-gradient(rgba(0, 104, 95, 0.12) 1.2px, transparent 1.2px); background-size: 28px 28px;"
    ></div>
    <div class="absolute -top-32 -left-32 w-96 h-96 bg-purple-300/25 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-32 -right-32 w-96 h-96 bg-emerald-300/30 rounded-full blur-3xl pointer-events-none"></div>

    <!-- Top Branding Navbar -->
    <header class="relative z-10 w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
      <router-link to="/" class="flex items-center gap-3 group">
        <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-700 flex items-center justify-center text-white shadow-game-btn transition-transform group-hover:scale-105">
          <span class="material-symbols-outlined text-2xl">account_balance</span>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="font-extrabold text-lg tracking-tight text-slate-900">Research Realm</span>
            <span class="hidden sm:inline-flex px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-emerald-100 text-emerald-800 rounded-full border border-emerald-200">
              New Scholar
            </span>
          </div>
          <p class="text-xs text-slate-500 font-medium">Citation Archipelago • Academy Enrollment</p>
        </div>
      </router-link>

      <div class="flex items-center gap-2">
        <span class="text-xs text-slate-500 hidden sm:inline">Already enrolled?</span>
        <router-link
          to="/login"
          class="px-3.5 py-1.5 text-xs font-bold text-slate-800 bg-white hover:bg-slate-50 border border-slate-200 rounded-xl transition-colors shadow-sm"
        >
          Sign In 📜
        </router-link>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="relative z-10 flex-1 w-full max-w-7xl mx-auto px-6 py-8 flex items-center justify-center">
      <div class="w-full grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
        
        <!-- Left Column: Scholarship Perks & Academy Lore -->
        <div class="lg:col-span-6 space-y-6">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-900 border border-emerald-200 shadow-sm">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>COMMENCE YOUR SCHOLARSHIP</span>
          </div>

          <div class="space-y-3">
            <h1 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
              Begin your journey as a <br />
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600">
                Master Cartographer.
              </span>
            </h1>
            <p class="text-slate-600 text-base leading-relaxed max-w-lg">
              Enlist in the Research Realm to turn any research paper into an interactive, multi-agent knowledge town with automated graph indexing.
            </p>
          </div>

          <!-- Scholar Perks Grid -->
          <div class="space-y-3 pt-1">
            <div class="flex items-start gap-3.5 p-3.5 rounded-2xl bg-white/80 backdrop-blur-md border border-white/80 shadow-sm">
              <div class="w-9 h-9 rounded-xl bg-purple-100 text-purple-800 flex items-center justify-center flex-shrink-0">
                <span class="material-symbols-outlined text-xl">auto_awesome</span>
              </div>
              <div>
                <h4 class="text-sm font-bold text-slate-900">Level 1 Apprentice Scholar Card</h4>
                <p class="text-xs text-slate-500 mt-0.5">Receive 100 Energy sparks and start unlocking research badges with each paper you ingest.</p>
              </div>
            </div>

            <div class="flex items-start gap-3.5 p-3.5 rounded-2xl bg-white/80 backdrop-blur-md border border-white/80 shadow-sm">
              <div class="w-9 h-9 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center flex-shrink-0">
                <span class="material-symbols-outlined text-xl">account_tree</span>
              </div>
              <div>
                <h4 class="text-sm font-bold text-slate-900">Leiden Community Clustering</h4>
                <p class="text-xs text-slate-500 mt-0.5">Automatic hierarchical clustering that partitions concepts into named thematic districts.</p>
              </div>
            </div>

            <div class="flex items-start gap-3.5 p-3.5 rounded-2xl bg-white/80 backdrop-blur-md border border-white/80 shadow-sm">
              <div class="w-9 h-9 rounded-xl bg-cyan-100 text-cyan-800 flex items-center justify-center flex-shrink-0">
                <span class="material-symbols-outlined text-xl">psychology</span>
              </div>
              <div>
                <h4 class="text-sm font-bold text-slate-900">Professor Archimedes AI Companion</h4>
                <p class="text-xs text-slate-500 mt-0.5">Stream citations with formula clues, grounded in verifiable knowledge graph subgraphs.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Clerk Sign Up Component -->
        <div class="lg:col-span-6 flex justify-center lg:justify-end">
          <div class="w-full max-w-md bg-white/95 backdrop-blur-xl p-2 sm:p-4 rounded-3xl border border-white shadow-hud-lg">
            <SignUp
              routing="path"
              path="/register"
              sign-in-url="/login"
              after-sign-up-url="/"
              after-sign-in-url="/"
              :appearance="{
                variables: {
                  colorPrimary: '#00685f',
                  colorBackground: '#ffffff',
                  colorText: '#0f172a',
                  colorTextSecondary: '#64748b',
                  colorInputBackground: '#f8fafc',
                  colorInputBorder: '#e2e8f0',
                  borderRadius: '0.875rem',
                  fontFamily: 'Inter, sans-serif',
                },
                elements: {
                  card: 'shadow-none border-0 bg-transparent',
                  headerTitle: 'text-xl font-extrabold text-slate-900',
                  headerSubtitle: 'text-xs text-slate-500',
                  formButtonPrimary: 'bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-[0_4px_0_#004d46] hover:translate-y-[-1px] active:translate-y-[2px] transition-all text-xs tracking-wider uppercase',
                  formFieldInput: 'rounded-xl border-slate-200 focus:border-emerald-500 focus:ring-emerald-500 text-sm bg-slate-50',
                  footerActionLink: 'text-emerald-700 hover:text-emerald-800 font-bold',
                  socialButtonsBlockButton: 'rounded-xl border-slate-200 hover:bg-slate-50 font-medium text-xs',
                  dividerLine: 'bg-slate-200',
                  dividerText: 'text-slate-400 text-xs font-semibold',
                }
              }"
            />
          </div>
        </div>

      </div>
    </main>

    <!-- Footer -->
    <footer class="relative z-10 w-full max-w-7xl mx-auto px-6 py-6 text-center text-xs text-slate-400 font-medium">
      Research Realm • GraphRAG Exploration Architecture • Powered by Microsoft GraphRAG & Vue 3
    </footer>
  </div>
</template>

