<script setup lang="ts">
import { SignUp } from '@clerk/vue'
</script>

<template>
  <div
    class="relative min-h-screen w-full flex flex-col"
    style="background-color: #F7F6F3;"
  >
    <!-- Subtle dot grid texture -->
    <div
      class="absolute inset-0 pointer-events-none"
      style="background-image: radial-gradient(rgba(28,27,24,0.07) 1px, transparent 1px); background-size: 24px 24px;"
    ></div>

    <!-- Minimal top nav -->
    <header class="relative z-10 w-full max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div
          class="w-8 h-8 rounded-lg flex items-center justify-center"
          style="background-color: #3D6B5A;"
        >
          <span class="material-symbols-outlined text-white" style="font-size: 18px;">hub</span>
        </div>
        <span class="font-bold text-base tracking-tight" style="color: #1C1B18;">Untangle</span>
      </div>

      <div class="flex items-center gap-3">
        <span class="text-sm" style="color: #8A877F;">Already have an account?</span>
        <router-link
          to="/login"
          class="px-3 py-1.5 text-sm font-medium rounded-lg border transition-colors"
          style="color: #1C1B18; border-color: #D4D3CE; background: white;"
        >
          Sign in
        </router-link>
      </div>
    </header>

    <!-- Main two-column layout -->
    <main class="relative z-10 flex-1 w-full max-w-6xl mx-auto px-6 py-10 flex items-center">
      <div class="w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

        <!-- Left: What you get with Untangle -->
        <div class="space-y-8">
          <div class="space-y-4">
            <h1 class="text-4xl font-bold tracking-tight leading-tight" style="color: #1C1B18;">
              Start mapping<br />your knowledge.
            </h1>
            <p class="text-base leading-relaxed" style="color: #5C5A54; max-width: 400px;">
              Create an account to upload research papers, textbooks, or any academic material and turn them into an interactive, queryable knowledge graph.
            </p>
          </div>

          <!-- Two mode cards, side by side -->
          <div class="grid grid-cols-2 gap-3">
            <!-- Research Mode -->
            <div
              class="rounded-xl p-4 border space-y-2"
              style="background-color: #E8F0EC; border-color: #C4D8CC;"
            >
              <div class="flex items-center gap-1.5">
                <span class="material-symbols-outlined" style="font-size: 16px; color: #3D6B5A;">description</span>
                <span class="text-xs font-mono font-bold uppercase tracking-wider" style="color: #3D6B5A;">Research</span>
              </div>
              <p class="text-xs leading-relaxed" style="color: #2C5043;">
                Papers → entity maps, relationship roads, community clusters, cross-paper context linking.
              </p>
            </div>

            <!-- Study Mode -->
            <div
              class="rounded-xl p-4 border space-y-2"
              style="background-color: #F5EFE3; border-color: #DDD0B0;"
            >
              <div class="flex items-center gap-1.5">
                <span class="material-symbols-outlined" style="font-size: 16px; color: #B8924A;">menu_book</span>
                <span class="text-xs font-mono font-bold uppercase tracking-wider" style="color: #B8924A;">Study</span>
              </div>
              <p class="text-xs leading-relaxed" style="color: #8C6A2C;">
                Books → chapter districts, topic towers, subtopic structures, exam-ready concept paths.
              </p>
            </div>
          </div>

          <!-- Regulus guide callout -->
          <div
            class="flex items-start gap-3 p-4 rounded-xl border"
            style="background: white; border-color: #E4E3DF;"
          >
            <div
              class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-bold text-sm"
              style="background-color: #EFEFED; color: #5C5A54;"
            >
              R
            </div>
            <div>
              <p class="text-sm font-semibold" style="color: #1C1B18;">Regulus, your AI guide</p>
              <p class="text-xs leading-relaxed mt-0.5" style="color: #5C5A54;">
                Ask questions about your material. Regulus answers with citations and highlights the exact paths through the knowledge map it used to reason.
              </p>
            </div>
          </div>

          <!-- Node type legend — shows off the muted color palette -->
          <div>
            <p class="text-xs font-mono uppercase tracking-wider mb-2" style="color: #8A877F;">Node types on your map</p>
            <div class="flex flex-wrap gap-2">
              <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-mono" style="background: #EBE5F5; color: #7C6FA0;">
                <span class="w-1.5 h-1.5 rounded-full inline-block flex-shrink-0" style="background: #7C6FA0;"></span>Person
              </span>
              <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-mono" style="background: #EEE8DC; color: #C49A3C;">
                <span class="w-1.5 h-1.5 rounded-full inline-block flex-shrink-0" style="background: #C49A3C;"></span>Organisation
              </span>
              <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-mono" style="background: #E5F3EE; color: #4E9A7D;">
                <span class="w-1.5 h-1.5 rounded-full inline-block flex-shrink-0" style="background: #4E9A7D;"></span>Concept
              </span>
              <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-mono" style="background: #F2E8E8; color: #A85A5A;">
                <span class="w-1.5 h-1.5 rounded-full inline-block flex-shrink-0" style="background: #A85A5A;"></span>Location
              </span>
              <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-mono" style="background: #E5EEF3; color: #4E8FA8;">
                <span class="w-1.5 h-1.5 rounded-full inline-block flex-shrink-0" style="background: #4E8FA8;"></span>Community
              </span>
              <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-mono" style="background: #EDF0EA; color: #7A8C6A;">
                <span class="w-1.5 h-1.5 rounded-full inline-block flex-shrink-0" style="background: #7A8C6A;"></span>Chapter
              </span>
            </div>
          </div>
        </div>

        <!-- Right: Clerk SignUp -->
        <div class="flex justify-center lg:justify-end">
          <div
            class="w-full rounded-2xl border overflow-hidden"
            style="max-width: 420px; background: white; border-color: #E4E3DF; box-shadow: 0 4px 20px rgba(28,27,24,0.08);"
          >
            <SignUp
              routing="path"
              path="/register"
              sign-in-url="/login"
              after-sign-up-url="/"
              after-sign-in-url="/"
              :appearance="{
                variables: {
                  colorPrimary: '#3D6B5A',
                  colorBackground: '#ffffff',
                  colorText: '#1C1B18',
                  colorTextSecondary: '#5C5A54',
                  colorInputBackground: '#F7F6F3',
                  colorInputBorder: '#D4D3CE',
                  borderRadius: '0.75rem',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '14px',
                },
                elements: {
                  card: 'shadow-none border-0 bg-white',
                  headerTitle: 'text-lg font-bold text-[#1C1B18]',
                  headerSubtitle: 'text-xs text-[#8A877F]',
                  formButtonPrimary: 'bg-[#3D6B5A] hover:bg-[#2C5043] text-white font-semibold rounded-lg text-sm shadow-[0_3px_0_#2C5043] active:translate-y-px transition-all',
                  formFieldInput: 'rounded-lg border-[#D4D3CE] bg-[#F7F6F3] focus:border-[#3D6B5A] text-sm',
                  footerActionLink: 'text-[#3D6B5A] hover:text-[#2C5043] font-semibold',
                  socialButtonsBlockButton: 'rounded-lg border-[#D4D3CE] hover:bg-[#EFEFED] text-sm',
                  dividerLine: 'bg-[#E4E3DF]',
                  dividerText: 'text-[#8A877F] text-xs',
                }
              }"
            />
          </div>
        </div>

      </div>
    </main>

    <!-- Minimal footer -->
    <footer class="relative z-10 w-full max-w-6xl mx-auto px-6 py-5">
      <p class="text-xs text-center" style="color: #8A877F;">Untangle — Built on Microsoft GraphRAG · Vue 3 · FastAPI</p>
    </footer>
  </div>
</template>
