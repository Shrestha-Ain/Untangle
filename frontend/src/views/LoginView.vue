<script setup lang="ts">
import { SignIn } from '@clerk/vue'
</script>

<template>
  <div
    class="relative min-h-screen w-full flex flex-col"
    style="background-color: #F7F6F3;"
  >
    <!-- Subtle dot grid — barely visible texture -->
    <div
      class="absolute inset-0 pointer-events-none"
      style="background-image: radial-gradient(rgba(28,27,24,0.07) 1px, transparent 1px); background-size: 24px 24px;"
    ></div>

    <!-- Minimal top nav -->
    <header class="relative z-10 w-full max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <!-- Logomark: simple knot/node icon -->
        <div
          class="w-8 h-8 rounded-lg flex items-center justify-center"
          style="background-color: #3D6B5A;"
        >
          <span class="material-symbols-outlined text-white" style="font-size: 18px;">hub</span>
        </div>
        <span class="font-bold text-base tracking-tight" style="color: #1C1B18;">Untangle</span>
      </div>

      <div class="flex items-center gap-3">
        <span class="text-sm" style="color: #8A877F;">New to Untangle?</span>
        <router-link
          to="/register"
          class="px-3 py-1.5 text-sm font-medium rounded-lg border transition-colors"
          style="color: #1C1B18; border-color: #D4D3CE; background: white;"
        >
          Create account
        </router-link>
      </div>
    </header>

    <!-- Main two-column layout -->
    <main class="relative z-10 flex-1 w-full max-w-6xl mx-auto px-6 py-10 flex items-center">
      <div class="w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

        <!-- Left: Brand & value proposition -->
        <div class="space-y-8">
          <div class="space-y-4">
            <h1 class="text-4xl font-bold tracking-tight leading-tight" style="color: #1C1B18;">
              Turn dense material<br />into navigable knowledge.
            </h1>
            <p class="text-base leading-relaxed" style="color: #5C5A54; max-width: 400px;">
              Untangle maps research papers and textbooks into an interactive knowledge graph you can explore, query, and extend.
            </p>
          </div>

          <!-- Feature list — clean, no game language -->
          <div class="space-y-3">
            <div class="flex items-start gap-3">
              <div
                class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                style="background-color: #E8F0EC;"
              >
                <span class="material-symbols-outlined" style="font-size: 16px; color: #3D6B5A;">account_tree</span>
              </div>
              <div>
                <p class="text-sm font-semibold" style="color: #1C1B18;">Research Mode</p>
                <p class="text-sm" style="color: #5C5A54;">Upload a paper — get a live, explorable entity-relationship map with multi-hop reasoning.</p>
              </div>
            </div>

            <div class="flex items-start gap-3">
              <div
                class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                style="background-color: #F5EFE3;"
              >
                <span class="material-symbols-outlined" style="font-size: 16px; color: #B8924A;">menu_book</span>
              </div>
              <div>
                <p class="text-sm font-semibold" style="color: #1C1B18;">Study Mode</p>
                <p class="text-sm" style="color: #5C5A54;">Upload a textbook — topics, subtopics, and chapter structures laid out spatially for exam prep.</p>
              </div>
            </div>

            <div class="flex items-start gap-3">
              <div
                class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                style="background-color: #EFEFED;"
              >
                <span class="material-symbols-outlined" style="font-size: 16px; color: #5C5A54;">link</span>
              </div>
              <div>
                <p class="text-sm font-semibold" style="color: #1C1B18;">Cross-source linking</p>
                <p class="text-sm" style="color: #5C5A54;">Regulus suggests related sources when a concept needs outside context. Link them with one click.</p>
              </div>
            </div>
          </div>

          <!-- Small map preview strip — shows the muted color palette in context -->
          <div
            class="rounded-xl p-3 border"
            style="background-color: #EEF0EB; border-color: #D4D3CE;"
          >
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xs font-mono font-semibold uppercase tracking-wider" style="color: #8A877F;">Sample map · Research Mode</span>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-mono" style="background: #EBE5F5; color: #7C6FA0; border: 1px solid #D5CCE8;">
                <span class="w-1.5 h-1.5 rounded-full inline-block" style="background: #7C6FA0;"></span>Vaswani et al.
              </span>
              <span class="text-xs" style="color: #B8A87A;">──</span>
              <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-mono" style="background: #E5F3EE; color: #4E9A7D; border: 1px solid #C4DDD4;">
                <span class="w-1.5 h-1.5 rounded-full inline-block" style="background: #4E9A7D;"></span>Attention Mechanism
              </span>
              <span class="text-xs" style="color: #B8A87A;">──</span>
              <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-mono" style="background: #EEE8DC; color: #C49A3C; border: 1px solid #DDD0B0;">
                <span class="w-1.5 h-1.5 rounded-full inline-block" style="background: #C49A3C;"></span>Google Brain
              </span>
            </div>
          </div>
        </div>

        <!-- Right: Clerk SignIn -->
        <div class="flex justify-center lg:justify-end">
          <div
            class="w-full rounded-2xl border overflow-hidden"
            style="max-width: 420px; background: white; border-color: #E4E3DF; box-shadow: 0 4px 20px rgba(28,27,24,0.08);"
          >
            <SignIn
              routing="path"
              path="/login"
              sign-up-url="/register"
              after-sign-in-url="/"
              after-sign-up-url="/"
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