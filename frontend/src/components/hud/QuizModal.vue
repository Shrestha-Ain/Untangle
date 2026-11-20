<script setup lang="ts">
import { computed } from 'vue'
import { useQuizStore } from '@/stores/quiz'

const quizStore = useQuizStore()

const currentQ = computed(() => quizStore.currentQuestion)
const scorePercent = computed(() => {
  if (quizStore.totalQuestions === 0) return 0
  return Math.round((quizStore.score / quizStore.totalQuestions) * 100)
})

const performanceGrade = computed(() => {
  const p = scorePercent.value
  if (p === 100) return { title: '🏆 Perfect Mastery!', color: 'text-amber-600', badge: 'Grand Scholar', desc: 'You have flawlessly conquered these conceptual invariants!' }
  if (p >= 80) return { title: '🌟 Advanced Knowledge!', color: 'text-emerald-600', badge: 'High Yield Master', desc: 'Outstanding grasp of the core theory and edge cases.' }
  if (p >= 50) return { title: '👍 Solid Foundation!', color: 'text-teal-600', badge: 'Passing Grade', desc: 'Good baseline. Check the explanations to iron out the exam traps.' }
  return { title: '📖 Needs Review', color: 'text-rose-600', badge: 'Keep Practicing', desc: 'Use Regulus 🎯 Topic Focus to review this concept and re-try!' }
})
</script>

<template>
  <div
    v-if="quizStore.isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in select-none"
  >
    <div
      class="w-full max-w-xl bg-white rounded-3xl shadow-[0_24px_64px_rgba(0,0,0,0.22)] border border-slate-200 overflow-hidden flex flex-col max-h-[90vh] transition-all"
    >
      <!-- Modal Header -->
      <div class="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-2xl bg-[#00685F] text-white flex items-center justify-center font-bold text-lg shadow-sm">
            <span class="material-symbols-outlined text-xl">quiz</span>
          </div>
          <div>
            <h3 class="text-sm font-extrabold text-slate-800 flex items-center gap-2">
              <span>Untangle Knowledge Quiz</span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold uppercase">
                Active
              </span>
            </h3>
            <p class="text-[11px] text-slate-500">
              Interactive test for topic retention & exam preparation
            </p>
          </div>
        </div>

        <button
          @click="quizStore.closeQuiz"
          class="w-8 h-8 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-colors"
          title="Close Quiz"
        >
          <span class="material-symbols-outlined text-lg">close</span>
        </button>
      </div>

      <!-- Mode Selector Tabs (Topic vs Whole Document) -->
      <div class="px-6 py-2.5 bg-slate-100/70 border-b border-slate-200 flex items-center justify-between gap-2 text-xs">
        <div class="flex items-center gap-1.5 bg-slate-200/80 p-1 rounded-xl">
          <button
            @click="quizStore.setQuizMode('topic')"
            class="px-3 py-1 rounded-lg font-bold transition-all flex items-center gap-1.5"
            :class="[
              quizStore.quizMode === 'topic'
                ? 'bg-white text-slate-800 shadow-xs'
                : 'text-slate-600 hover:text-slate-900',
            ]"
          >
            <span>🎯</span>
            <span>Topic: {{ quizStore.selectedTopicName }}</span>
          </button>

          <button
            @click="quizStore.setQuizMode('document')"
            class="px-3 py-1 rounded-lg font-bold transition-all flex items-center gap-1.5"
            :class="[
              quizStore.quizMode === 'document'
                ? 'bg-white text-slate-800 shadow-xs'
                : 'text-slate-600 hover:text-slate-900',
            ]"
          >
            <span>📚</span>
            <span>Whole PDF Exam</span>
          </button>
        </div>

        <!-- Progress Counter -->
        <div v-if="!quizStore.isFinished" class="text-right">
          <span class="text-[11px] font-mono font-bold text-slate-500">
            Question {{ quizStore.currentIndex + 1 }} of {{ quizStore.totalQuestions }}
          </span>
        </div>
      </div>

      <!-- Modal Body (Questions or Score Finish) -->
      <div class="p-6 overflow-y-auto space-y-5 regulus-scroll">
        <!-- ========================================================= -->
        <!-- STATE A: ACTIVE QUIZ QUESTIONS                            -->
        <!-- ========================================================= -->
        <div v-if="!quizStore.isFinished && currentQ" class="space-y-4">
          <!-- Question Banner -->
          <div class="p-4 rounded-2xl bg-teal-50/60 border border-teal-100 space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-mono font-extrabold uppercase tracking-wider text-teal-800 px-2 py-0.5 rounded bg-teal-100">
                {{ currentQ.topicName || 'Conceptual Principle' }}
              </span>
              <span class="text-xs font-mono font-bold text-slate-500">
                Score: {{ quizStore.score }}
              </span>
            </div>
            <p class="text-sm font-bold text-slate-800 leading-snug">
              {{ currentQ.question }}
            </p>
          </div>

          <!-- Options Grid -->
          <div class="space-y-2.5">
            <button
              v-for="(opt, idx) in currentQ.options"
              :key="idx"
              @click="quizStore.submitAnswer(idx)"
              :disabled="quizStore.hasAnswered"
              class="w-full text-left p-3.5 rounded-2xl border text-xs font-medium transition-all flex items-start gap-3 relative select-none"
              :class="[
                !quizStore.hasAnswered
                  ? 'bg-white border-slate-200 hover:border-teal-500 hover:bg-teal-50/30 text-slate-800 active:scale-[0.99] cursor-pointer shadow-2xs'
                  : idx === currentQ.correctIndex
                  ? 'bg-emerald-50 border-emerald-500 text-emerald-900 font-bold ring-2 ring-emerald-200'
                  : idx === quizStore.selectedOptionIndex
                  ? 'bg-rose-50 border-rose-500 text-rose-900 ring-2 ring-rose-200'
                  : 'bg-slate-50 border-slate-200 text-slate-400 opacity-60',
              ]"
            >
              <div
                class="w-6 h-6 rounded-xl flex items-center justify-center shrink-0 font-mono font-bold text-[11px]"
                :class="[
                  quizStore.hasAnswered && idx === currentQ.correctIndex
                    ? 'bg-emerald-500 text-white'
                    : quizStore.hasAnswered && idx === quizStore.selectedOptionIndex
                    ? 'bg-rose-500 text-white'
                    : 'bg-slate-100 text-slate-600',
                ]"
              >
                {{ ['A', 'B', 'C', 'D'][idx] }}
              </div>
              <div class="flex-1 leading-relaxed">
                {{ opt.replace(/^[A-D]\)\s*/, '') }}
              </div>

              <!-- Status Icon Badge -->
              <span
                v-if="quizStore.hasAnswered && idx === currentQ.correctIndex"
                class="material-symbols-outlined text-emerald-600 text-lg shrink-0"
              >
                check_circle
              </span>
              <span
                v-else-if="quizStore.hasAnswered && idx === quizStore.selectedOptionIndex"
                class="material-symbols-outlined text-rose-600 text-lg shrink-0"
              >
                cancel
              </span>
            </button>
          </div>

          <!-- Explanation Callout upon Answering -->
          <div
            v-if="quizStore.hasAnswered"
            class="p-4 rounded-2xl border transition-all animate-fade-in space-y-1.5"
            :class="[
              quizStore.selectedOptionIndex === currentQ.correctIndex
                ? 'bg-emerald-50/80 border-emerald-200 text-emerald-900'
                : 'bg-amber-50/80 border-amber-200 text-amber-900',
            ]"
          >
            <div class="flex items-center gap-1.5 text-xs font-extrabold">
              <span class="material-symbols-outlined text-base">
                {{ quizStore.selectedOptionIndex === currentQ.correctIndex ? 'verified' : 'info' }}
              </span>
              <span>
                {{ quizStore.selectedOptionIndex === currentQ.correctIndex ? 'Excellent deduction!' : 'Key Conceptual Takeaway:' }}
              </span>
            </div>
            <p class="text-[11.5px] leading-relaxed">
              {{ currentQ.explanation }}
            </p>
          </div>
        </div>

        <!-- ========================================================= -->
        <!-- STATE B: QUIZ FINISHED / SUMMARY CELEBRATION CARD        -->
        <!-- ========================================================= -->
        <div v-else-if="quizStore.isFinished" class="text-center py-6 space-y-5 animate-fade-in">
          <div class="w-20 h-20 rounded-3xl mx-auto flex items-center justify-center bg-teal-50 border border-teal-200 shadow-inner">
            <span class="material-symbols-outlined text-4xl text-[#00685F]">
              {{ scorePercent >= 80 ? 'workspace_premium' : scorePercent >= 50 ? 'school' : 'psychology' }}
            </span>
          </div>

          <div class="space-y-1">
            <h4 class="text-xl font-extrabold" :class="performanceGrade.color">
              {{ performanceGrade.title }}
            </h4>
            <p class="text-xs text-slate-600 max-w-sm mx-auto">
              {{ performanceGrade.desc }}
            </p>
          </div>

          <!-- Score Card Pill -->
          <div class="inline-flex items-center gap-3 px-5 py-2.5 rounded-2xl bg-slate-100 border border-slate-200 font-mono">
            <span class="text-xs text-slate-500 uppercase font-bold">Your Score:</span>
            <span class="text-base font-extrabold text-slate-800">
              {{ quizStore.score }} / {{ quizStore.totalQuestions }} ({{ scorePercent }}%)
            </span>
          </div>

          <div class="flex items-center justify-center gap-3 pt-2">
            <button
              @click="quizStore.restartQuiz"
              class="px-4 py-2.5 rounded-xl bg-[#00685F] text-white font-bold text-xs hover:bg-[#005149] active:scale-95 transition-all shadow-sm flex items-center gap-1.5"
            >
              <span class="material-symbols-outlined text-base">replay</span>
              <span>Retake Quiz</span>
            </button>

            <button
              @click="quizStore.closeQuiz"
              class="px-4 py-2.5 rounded-xl bg-slate-200 text-slate-700 font-bold text-xs hover:bg-slate-300 active:scale-95 transition-all"
            >
              Back to Realm Map
            </button>
          </div>
        </div>
      </div>

      <!-- Modal Footer (Next Button) -->
      <div v-if="!quizStore.isFinished" class="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
        <div class="text-[11px] text-slate-500">
          {{ quizStore.hasAnswered ? 'Answer registered.' : 'Select the most accurate answer above.' }}
        </div>

        <button
          @click="quizStore.nextQuestion"
          :disabled="!quizStore.hasAnswered"
          class="px-5 py-2 rounded-xl bg-[#00685F] text-white font-bold text-xs disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#005149] active:scale-95 transition-all shadow-sm flex items-center gap-1.5"
        >
          <span>{{ quizStore.currentIndex < quizStore.totalQuestions - 1 ? 'Next Question' : 'View Results' }}</span>
          <span class="material-symbols-outlined text-sm">arrow_forward</span>
        </button>
      </div>
    </div>
  </div>
</template>
