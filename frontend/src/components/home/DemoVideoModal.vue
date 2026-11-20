<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useGraphStore } from '@/stores/graph'
import { useThemeStore } from '@/stores/theme'
import TownCanvas3D from '@/components/town/TownCanvas3D.vue'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const router = useRouter()
const graphStore = useGraphStore()
const themeStore = useThemeStore()

// Reference to the Live 3D Town Canvas
const town3dRef = ref<InstanceType<typeof TownCanvas3D> | null>(null)

// Video interactive state
const videoAiTab = ref<'research' | 'study'>('research')
const videoDemoProgress = ref(67)
const videoDemoTopics = ref([
  { id: '1', name: 'Scaled Dot-Product', weight: 25, done: true },
  { id: '2', name: 'Multi-Head Attention', weight: 25, done: true },
  { id: '3', name: 'Positional Encoding', weight: 20, done: true },
  { id: '4', name: 'Feed-Forward Sublayers', weight: 15, done: false },
  { id: '5', name: 'Residual Normalization', weight: 15, done: false },
])

// Playback state
const isPlaying = ref(false)
const isMuted = ref(false)
const currentTime = ref(0) // seconds
const totalDuration = 110 // total seconds (~1m 50s)
const activeChapterIndex = ref(0)
const isVoiceSpeaking = ref(false)
let timerInterval: number | null = null

// Audio Context for ambient harmonic chimes
let audioCtx: AudioContext | null = null

export interface DemoChapter {
  id: number
  title: string
  subtitle: string
  startTime: number
  endTime: number
  narration: string
  visualPhase: 'signin' | 'upload' | 'town3d' | 'regulus' | 'slider' | 'progress' | 'quiz'
}

const chapters: DemoChapter[] = [
  {
    id: 1,
    title: 'Sign In & Dual-Mode Selection',
    subtitle: 'Secure authentication & personal knowledge library',
    startTime: 0,
    endTime: 12,
    narration:
      'Step 1: Sign in with Clerk to access your personal dashboard. Untangle provides dedicated workspaces for academic research papers and college course textbooks.',
    visualPhase: 'signin',
  },
  {
    id: 2,
    title: 'Document Upload & GraphRAG Pipeline',
    subtitle: 'Dual-mode processing for papers and textbooks',
    startTime: 12,
    endTime: 25,
    narration:
      'Step 2: Upload your PDF or paste an arXiv link. Untangle parses the document and extracts core concepts, formulas, and relationship networks with real-time GraphRAG clustering.',
    visualPhase: 'upload',
  },
  {
    id: 3,
    title: 'The Actual 3D Knowledge Realm',
    subtitle: '360-degree orbit, stepped architectural towers, and elevated highways',
    startTime: 25,
    endTime: 40,
    narration:
      'Step 3: Step directly into the actual 3D Knowledge Realm. Concepts emerge as physical stepped monoliths with flat architectural terraces, connected by elevated unidirectional energy viaducts. Left-drag to orbit in full 360 degrees.',
    visualPhase: 'town3d',
  },
  {
    id: 4,
    title: 'AI Replies: Research Papers vs College Study',
    subtitle: 'Novelty & math formulas for papers, analogies & exam traps for college',
    startTime: 40,
    endTime: 68,
    narration:
      'Step 4: Here is how Regulus AI answers after you upload a document. For research papers, it breaks down novel architectural breakthroughs, mathematical formulations, and ablation metrics with direct arXiv citations. For college study materials, it explains complex topics using real-world analogies, code snippets, and high-yield professor exam traps.',
    visualPhase: 'regulus',
  },
  {
    id: 5,
    title: 'Top Learning Path Slider & Auto-Zoom',
    subtitle: 'Sequential prerequisite traversal with auto-focus camera zoom',
    startTime: 68,
    endTime: 82,
    narration:
      'Step 5: Traverse your learning path sequentially with the top slider. Click next to move through prerequisites, and watch the 3D camera auto-zoom into each concept tower with a radiant radar ring.',
    visualPhase: 'slider',
  },
  {
    id: 6,
    title: 'Study Progress & Topic Completion Breakdown',
    subtitle: 'Track completion percentage and individual topic mastery',
    startTime: 82,
    endTime: 96,
    narration:
      'Step 6: Track your study progress in real time. The new Progress Tracker displays your overall completion percentage and a topic-by-topic breakdown. Mark topics as studied to track your journey to one hundred percent mastery.',
    visualPhase: 'progress',
  },
  {
    id: 7,
    title: 'Quiz Master, Notes & Launch 3D Realm',
    subtitle: 'Gamified quizzes, markdown notes, theme sync, and exploration',
    startTime: 96,
    endTime: 110,
    narration:
      'Step 7: Reinforce what you learned with gamified four-option quizzes, export personal Markdown notes, and toggle between soothing bluish dark and light modes. Click Launch 3D Realm to begin.',
    visualPhase: 'quiz',
  },
]

const currentChapter = computed(() => {
  return (
    chapters.find(
      (c) => currentTime.value >= c.startTime && currentTime.value < c.endTime
    ) || chapters[chapters.length - 1]
  )
})

const currentSubtitle = computed(() => currentChapter.value.narration)

const progressPercent = computed(() => {
  return (currentTime.value / totalDuration) * 100
})

function formatTime(secs: number): string {
  const m = Math.floor(secs / 60)
  const s = Math.floor(secs % 60)
  return `${m}:${s < 10 ? '0' : ''}${s}`
}

// ── Web Audio Synth (Ambient Sci-Fi Harmonic Tones) ───────────────────
function initAudio() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext
    if (AudioContextClass) {
      audioCtx = new AudioContextClass()
    }
  }
}

function playChime(freq = 440) {
  if (isMuted.value || !audioCtx) return
  try {
    if (audioCtx.state === 'suspended') {
      audioCtx.resume()
    }
    const osc = audioCtx.createOscillator()
    const gain = audioCtx.createGain()

    osc.type = 'sine'
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime)
    osc.frequency.exponentialRampToValueAtTime(freq * 1.5, audioCtx.currentTime + 0.4)

    gain.gain.setValueAtTime(0.06, audioCtx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.5)

    osc.connect(gain)
    gain.connect(audioCtx.destination)

    osc.start()
    osc.stop(audioCtx.currentTime + 0.5)
  } catch (e) {
    // Ignore audio error if blocked
  }
}

// ── Web Speech API Soothing Voice Engine (Gentle Feminine Cadence) ──────
let speechUtterance: SpeechSynthesisUtterance | null = null
let cachedVoices: SpeechSynthesisVoice[] = []

function updateVoices() {
  if (typeof window !== 'undefined' && window.speechSynthesis) {
    cachedVoices = window.speechSynthesis.getVoices()
  }
}

if (typeof window !== 'undefined' && window.speechSynthesis) {
  updateVoices()
  if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = updateVoices
  }
}

function getSoothingFemaleVoice(): SpeechSynthesisVoice | null {
  if (typeof window === 'undefined' || !window.speechSynthesis) return null
  const voices = (cachedVoices.length > 0 ? cachedVoices : window.speechSynthesis.getVoices()) || []
  if (voices.length === 0) return null

  const englishVoices = voices.filter((v) => v.lang.startsWith('en'))
  const candidatePool = englishVoices.length > 0 ? englishVoices : voices

  // Priority 1: Top-tier natural neural female voices (Windows 11 / Edge / Azure Natural)
  const naturalFemale = candidatePool.find(
    (v) =>
      v.name.includes('Natural') &&
      /Jenny|Aria|Sonia|Ava|Emma|Ana|Maisie|Libby|Michelle|Clara|Steffi/i.test(v.name)
  )
  if (naturalFemale) return naturalFemale

  // Priority 2: Chrome / Google high-quality female voices
  const googleFemale = candidatePool.find(
    (v) => /Google UK English Female|Google US English/i.test(v.name)
  )
  if (googleFemale) return googleFemale

  // Priority 3: Apple / Safari high-quality female voices
  const appleFemale = candidatePool.find(
    (v) => /Samantha|Victoria|Karen|Moira|Tessa|Fiona|Nora|Serena/i.test(v.name)
  )
  if (appleFemale) return appleFemale

  // Priority 4: Standard Windows / SAPI female voices
  const desktopFemale = candidatePool.find(
    (v) => /Zira|Hazel|Susan|Catherine|Linda|Heera|Neerja/i.test(v.name)
  )
  if (desktopFemale) return desktopFemale

  // Priority 5: Any voice explicitly containing "female", "woman", or "girl"
  const anyFemale = candidatePool.find((v) => /Female|Woman|Girl/i.test(v.name))
  if (anyFemale) return anyFemale

  // Priority 6: Any English voice that is definitely NOT male
  const nonMale = candidatePool.find(
    (v) => !/David|Guy|Mark|George|Richard|Stefan|James|Paul|Ryan|Christopher|Brian|Eric|Martin|Tom|Male/i.test(v.name)
  )
  if (nonMale) return nonMale

  return candidatePool[0] || null
}

function speakCurrentChapter() {
  if (isMuted.value || !window.speechSynthesis) return

  window.speechSynthesis.cancel()

  const textToSpeak = currentChapter.value.narration
  speechUtterance = new SpeechSynthesisUtterance(textToSpeak)

  // Soothing feminine delivery settings:
  speechUtterance.rate = 0.96
  speechUtterance.pitch = 1.10
  speechUtterance.volume = 0.95

  const voice = getSoothingFemaleVoice()
  if (voice) {
    speechUtterance.voice = voice
  }

  speechUtterance.onstart = () => {
    isVoiceSpeaking.value = true
  }

  speechUtterance.onend = () => {
    isVoiceSpeaking.value = false
  }

  speechUtterance.onerror = () => {
    isVoiceSpeaking.value = false
  }

  window.speechSynthesis.speak(speechUtterance)
}

function stopVoice() {
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel()
  }
  isVoiceSpeaking.value = false
}

// ── Interactive 3D Video Actions ───────────────────────────────────────
function onVideoBuildingClick(nodeId: string) {
  graphStore.selectEntity(nodeId)
  town3dRef.value?.focusOnNode(nodeId)
}

function handleVideoStepClick(stepIdx: number) {
  if (graphStore.learningPath.length > stepIdx) {
    graphStore.setPathIndex(stepIdx)
    const nodeId = graphStore.learningPath[stepIdx]
    town3dRef.value?.focusOnNode(nodeId)
  }
}

function toggleVideoTopic(idx: number) {
  videoDemoTopics.value[idx].done = !videoDemoTopics.value[idx].done
  const doneCount = videoDemoTopics.value.filter((t) => t.done).length
  videoDemoProgress.value = Math.round((doneCount / videoDemoTopics.value.length) * 100)
}

// ── Playback Controls ──────────────────────────────────────────────────
function togglePlay() {
  if (isPlaying.value) {
    pause()
  } else {
    play()
  }
}

function play() {
  initAudio()
  isPlaying.value = true
  playChime(523.25) // C5 chime

  if (!isMuted.value) {
    speakCurrentChapter()
  }

  if (timerInterval) clearInterval(timerInterval)
  timerInterval = window.setInterval(() => {
    if (currentTime.value < totalDuration) {
      currentTime.value += 0.5

      // Check if transitioned to a new chapter
      const newIndex = chapters.findIndex(
        (c) => currentTime.value >= c.startTime && currentTime.value < c.endTime
      )
      if (newIndex !== -1 && newIndex !== activeChapterIndex.value) {
        activeChapterIndex.value = newIndex
        playChime(659.25) // E5 transition chime
        if (!isMuted.value) {
          speakCurrentChapter()
        }
      }
    } else {
      pause()
      currentTime.value = totalDuration
    }
  }, 500)
}

function pause() {
  isPlaying.value = false
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  stopVoice()
}

function restart() {
  currentTime.value = 0
  activeChapterIndex.value = 0
  play()
  town3dRef.value?.recenter()
}

function seekTo(targetSeconds: number) {
  currentTime.value = Math.max(0, Math.min(totalDuration, targetSeconds))
  const newIndex = chapters.findIndex(
    (c) => currentTime.value >= c.startTime && currentTime.value < c.endTime
  )
  if (newIndex !== -1) {
    activeChapterIndex.value = newIndex
  }
  if (isPlaying.value) {
    stopVoice()
    if (!isMuted.value) {
      speakCurrentChapter()
    }
  }
}

function toggleMute() {
  isMuted.value = !isMuted.value
  if (isMuted.value) {
    stopVoice()
  } else if (isPlaying.value) {
    speakCurrentChapter()
  }
}

function jumpToChapter(index: number) {
  const ch = chapters[index]
  if (ch) {
    seekTo(ch.startTime)
  }
}

function handleClose() {
  pause()
  stopVoice()
  emit('close')
}

function exploreRealmNow() {
  handleClose()
  router.push('/realm/doc-attention-1706')
}

// Watch chapter changes to synchronize 3D camera navigation
watch(
  () => activeChapterIndex.value,
  (newIdx) => {
    const ch = chapters[newIdx]
    if (!ch) return

    if (ch.visualPhase === 'town3d') {
      town3dRef.value?.recenter()
      town3dRef.value?.setCameraIsometric()
    } else if (ch.visualPhase === 'regulus') {
      // In Regulus showcase, alternate or default to research paper view
      videoAiTab.value = 'research'
      if (graphStore.learningPath.length > 1) {
        const step2Id = graphStore.learningPath[1]
        town3dRef.value?.focusOnNode(step2Id)
      }
    } else if (ch.visualPhase === 'slider') {
      if (graphStore.learningPath.length > 1) {
        graphStore.setPathIndex(1)
        const step2Id = graphStore.learningPath[1]
        town3dRef.value?.focusOnNode(step2Id)
      }
    } else if (ch.visualPhase === 'progress') {
      town3dRef.value?.recenter()
    } else if (ch.visualPhase === 'quiz') {
      town3dRef.value?.recenter()
    }
  }
)

watch(
  () => props.isOpen,
  async (open) => {
    if (open) {
      if (graphStore.nodes.length === 0) {
        await graphStore.loadGraph('doc-attention-1706', 'research')
      }
      setTimeout(() => {
        play()
        town3dRef.value?.recenter()
      }, 200)
    } else {
      pause()
    }
  }
)

onMounted(async () => {
  if (props.isOpen) {
    if (graphStore.nodes.length === 0) {
      await graphStore.loadGraph('doc-attention-1706', 'research')
    }
    play()
  }
})

onUnmounted(() => {
  pause()
})
</script>

<template>
  <!-- Fullscreen Modal Backdrop -->
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-950/85 backdrop-blur-xl animate-in fade-in duration-200 select-none"
    @click.self="handleClose"
  >
    <!-- Modal Container -->
    <div
      class="relative w-full max-w-4xl bg-[#0B1120] rounded-3xl border-2 border-slate-700/80 shadow-[0_24px_64px_rgba(0,0,0,0.6)] flex flex-col overflow-hidden text-white"
    >
      <!-- Header Bar -->
      <div
        class="px-5 py-3.5 bg-[#0F172A] border-b border-slate-800 flex items-center justify-between"
      >
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-xs">
            <span class="material-symbols-outlined text-lg">smart_display</span>
          </div>
          <div class="flex flex-col text-left">
            <div class="flex items-center gap-2">
              <span class="font-extrabold text-sm tracking-tight text-white">Untangle Feature Walkthrough</span>
              <span class="px-2 py-0.5 rounded-full bg-blue-950 text-sky-400 border border-blue-800 text-[10px] font-mono font-bold">
                Live 3D Product Journey
              </span>
            </div>
            <span class="text-[11px] text-slate-400 font-medium">
              Step {{ currentChapter.id }} of 7: {{ currentChapter.title }}
            </span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- Voice Narration Active Indicator -->
          <div
            v-if="!isMuted && isVoiceSpeaking"
            class="hidden sm:flex items-center gap-0.5 px-2.5 py-1 rounded-lg bg-blue-950/80 border border-blue-800 text-[10px] font-mono text-sky-400"
            title="Narrator Voice Speaking"
          >
            <span class="w-1 h-3 bg-sky-400 animate-pulse rounded-full"></span>
            <span class="w-1 h-4 bg-blue-400 animate-bounce rounded-full"></span>
            <span class="w-1 h-2 bg-sky-400 animate-pulse rounded-full"></span>
            <span class="ml-1 font-bold">Voice Active</span>
          </div>

          <!-- Close Modal -->
          <button
            @click="handleClose"
            class="w-8 h-8 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white flex items-center justify-center transition-colors cursor-pointer"
            title="Close video"
          >
            <span class="material-symbols-outlined text-lg">close</span>
          </button>
        </div>
      </div>

      <!-- Main Video Stage (Live True 3D WebGL Town Engine + Interactive Product Simulation) -->
      <div class="relative w-full aspect-video bg-[#070C18] overflow-hidden flex items-center justify-center">
        <!-- 🌟 ACTUAL LIVE 3D WEBGL TOWN ENGINE (Interactive Three.js Canvas) -->
        <TownCanvas3D
          ref="town3dRef"
          :auto-rotate="currentChapter.visualPhase === 'town3d' || currentChapter.visualPhase === 'quiz'"
          :auto-rotate-speed="1.4"
          active-type-filter="ALL"
          class="absolute inset-0 w-full h-full"
          @building-click="onVideoBuildingClick"
        />

        <!-- Soft translucent backdrop scrim for Scene 1 & 2 only, so signin/upload cards stand out -->
        <div
          v-if="currentChapter.visualPhase === 'signin' || currentChapter.visualPhase === 'upload' || currentChapter.visualPhase === 'progress'"
          class="absolute inset-0 bg-[#070C18]/85 backdrop-blur-[2px] transition-all duration-300 pointer-events-none z-10"
        ></div>

        <!-- Chapter Pill Tag (Top-Left of Screen) -->
        <div class="absolute top-4 left-4 z-30 flex flex-col gap-1 pointer-events-none text-left">
          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-900/90 backdrop-blur-md border border-slate-700 text-sky-300 text-xs font-mono font-bold shadow-md">
            <span>✦ Step {{ currentChapter.id }}</span>
            <span class="text-slate-400">•</span>
            <span>{{ currentChapter.title }}</span>
          </div>
          <span class="text-[11px] text-slate-300 font-medium drop-shadow-md max-w-sm">
            {{ currentChapter.subtitle }}
          </span>
        </div>

        <!-- ═════════════════════════════════════════════════════════════ -->
        <!-- REAL PRODUCT SIMULATION FRAMES (Changes based on chapter)    -->
        <!-- ═════════════════════════════════════════════════════════════ -->

        <!-- SCENE 1: Sign-In & Workspace Setup -->
        <div
          v-if="currentChapter.visualPhase === 'signin'"
          class="relative z-20 w-full max-w-md p-6 bg-[#0F172A]/95 backdrop-blur-xl rounded-3xl border-2 border-slate-700 shadow-2xl animate-in fade-in zoom-in-95 duration-300 text-center space-y-4"
        >
          <div class="w-12 h-12 mx-auto rounded-2xl bg-blue-600 text-white flex items-center justify-center shadow-lg font-black text-xl">
            U
          </div>
          <div>
            <h3 class="text-base font-extrabold text-white">Sign In to Untangle</h3>
            <p class="text-xs text-slate-400 mt-0.5">Clerk Authentication • Google OAuth & Email</p>
          </div>

          <div class="space-y-2 text-left">
            <div class="p-2.5 rounded-xl bg-slate-800/90 border border-slate-700 flex items-center justify-between text-xs text-white">
              <span class="flex items-center gap-2">
                <span class="material-symbols-outlined text-sm text-blue-400">mail</span>
                <span>scholar@research.edu</span>
              </span>
              <span class="text-emerald-400 font-bold text-[10px]">Verified ✓</span>
            </div>
            <div class="w-full py-2.5 rounded-xl bg-blue-600 text-white font-bold text-xs text-center shadow-md flex items-center justify-center gap-1.5">
              <span>Entering Dashboard...</span>
              <span class="material-symbols-outlined text-sm animate-spin">refresh</span>
            </div>
          </div>

          <div class="pt-2 border-t border-slate-800 flex items-center justify-around text-[10px] font-mono text-slate-400">
            <span>Library: Research & Study</span>
            <span>•</span>
            <span>Scholar XP: 450</span>
          </div>
        </div>

        <!-- SCENE 2: Document Upload & GraphRAG Pipeline -->
        <div
          v-else-if="currentChapter.visualPhase === 'upload'"
          class="relative z-20 w-full max-w-lg p-5 bg-[#0F172A]/95 backdrop-blur-xl rounded-3xl border-2 border-slate-700 shadow-2xl animate-in fade-in zoom-in-95 duration-300 space-y-3.5 text-left"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-blue-400">cloud_upload</span>
              <span class="text-xs font-black text-white">Document Ingestion Pipeline</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="px-2 py-0.5 rounded bg-blue-900/60 text-sky-400 border border-blue-800 text-[10px] font-mono font-bold">
                Research Mode
              </span>
              <span class="px-2 py-0.5 rounded bg-amber-950/60 text-amber-400 border border-amber-800 text-[10px] font-mono font-bold">
                Study Mode
              </span>
            </div>
          </div>

          <!-- Active PDF Item -->
          <div class="p-3 rounded-2xl bg-blue-950/40 border border-blue-500/40 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-xl bg-rose-600/20 border border-rose-500/30 text-rose-400 flex items-center justify-center font-bold text-xs font-mono">
                PDF
              </div>
              <div class="flex flex-col">
                <span class="text-xs font-bold text-white">vaswani2017_attention.pdf</span>
                <span class="text-[10px] text-slate-400">2.2 MB • Academic Paper</span>
              </div>
            </div>
            <span class="px-2 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-bold animate-pulse">
              Processing 85%
            </span>
          </div>

          <!-- 4-Step Pipeline Stepper -->
          <div class="space-y-1.5 pt-1">
            <div class="flex items-center justify-between text-[11px] text-slate-300">
              <span class="flex items-center gap-1.5 text-emerald-400 font-bold">
                <span>✓</span> 1. PDF Parser & Chunking
              </span>
              <span class="text-[10px] font-mono text-emerald-400 font-bold">Done</span>
            </div>
            <div class="flex items-center justify-between text-[11px] text-slate-300">
              <span class="flex items-center gap-1.5 text-emerald-400 font-bold">
                <span>✓</span> 2. GraphRAG Entity & Relation Extraction
              </span>
              <span class="text-[10px] font-mono text-emerald-400 font-bold">64 Entities</span>
            </div>
            <div class="flex items-center justify-between text-[11px] text-slate-300">
              <span class="flex items-center gap-1.5 text-sky-400 font-bold">
                <span class="animate-spin inline-block">⚙</span> 3. Leiden Graph Community Partitioning
              </span>
              <span class="text-[10px] font-mono text-sky-400 font-bold">8 Clusters</span>
            </div>
            <div class="flex items-center justify-between text-[11px] text-slate-400">
              <span class="flex items-center gap-1.5">
                <span>○</span> 4. 3D Knowledge Town Construction
              </span>
              <span class="text-[10px] font-mono text-slate-500">Generating Realm</span>
            </div>
          </div>
        </div>

        <!-- SCENE 3: The 3D Knowledge Realm — 100% Unobstructed Actual 3D WebGL Map View! -->
        <div
          v-else-if="currentChapter.visualPhase === 'town3d'"
          class="absolute inset-0 pointer-events-none z-20 p-4 flex flex-col justify-between"
        >
          <!-- Top Right Controls overlay -->
          <div class="flex items-center justify-end gap-2 pointer-events-auto">
            <div class="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/90 border border-slate-700/80 backdrop-blur-md shadow-xl text-[11px] font-mono">
              <button
                @click.stop="town3dRef?.setCameraIsometric()"
                class="px-2.5 py-1 rounded-lg font-bold bg-blue-600 text-white transition-colors cursor-pointer"
              >
                3D Isometric
              </button>
              <button
                @click.stop="town3dRef?.setCameraTopDown()"
                class="px-2.5 py-1 rounded-lg text-slate-300 hover:text-white transition-colors cursor-pointer"
              >
                Top-Down
              </button>
              <button
                @click.stop="town3dRef?.recenter()"
                class="px-2.5 py-1 rounded-lg text-slate-300 hover:text-white transition-colors cursor-pointer"
              >
                Recenter
              </button>
            </div>
          </div>

          <!-- Bottom Status Badges -->
          <div class="flex items-center justify-between pointer-events-auto">
            <!-- Left Info Pill -->
            <div class="flex items-center gap-2 px-3.5 py-2 rounded-2xl bg-slate-900/90 border border-slate-700/80 backdrop-blur-md text-xs font-mono text-slate-200 shadow-xl">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
              <span class="text-sky-300 font-bold">Attention Is All You Need • 3D Town</span>
              <span class="text-slate-400">•</span>
              <span class="text-amber-400 font-bold">Flat Architectural Roofs</span>
              <span class="text-slate-400">•</span>
              <span class="text-cyan-400 font-bold">Unidirectional Viaducts ➔</span>
            </div>

            <!-- Right Interactive Pill -->
            <div class="hidden sm:flex items-center gap-2 px-3.5 py-2 rounded-full bg-blue-950/90 border border-blue-700/80 backdrop-blur-md text-[11px] font-mono text-sky-200 shadow-xl">
              <span class="material-symbols-outlined text-sm text-sky-400">orbit</span>
              <span>Left-Drag to Orbit 360° • Scroll to Zoom</span>
            </div>
          </div>
        </div>

        <!-- SCENE 4: CORE FOCUS — Regulus AI Replies for Research Papers vs College Study -->
        <div
          v-else-if="currentChapter.visualPhase === 'regulus'"
          class="absolute inset-0 pointer-events-none z-20 p-4 flex items-center justify-start"
        >
          <div class="w-full max-w-lg pointer-events-auto p-4 bg-[#0F172A]/95 backdrop-blur-xl rounded-3xl border-2 border-slate-700 shadow-2xl space-y-2.5 text-left animate-in fade-in slide-in-from-left-4 duration-300">
            <!-- Chat Header with Differentiated Mode Tabs -->
            <div class="flex items-center justify-between pb-2 border-b border-slate-800">
              <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded-lg bg-emerald-500 text-white font-black text-xs flex items-center justify-center">R</div>
                <span class="text-xs font-bold text-white">Regulus AI Guide</span>
              </div>

              <!-- Interactive Tab Switcher demonstrating Research vs College Study Replies -->
              <div class="flex items-center gap-1 bg-slate-900 p-0.5 rounded-xl border border-slate-700 text-[10px] font-mono font-bold">
                <button
                  @click="videoAiTab = 'research'"
                  class="px-2 py-0.5 rounded-lg transition-colors cursor-pointer"
                  :class="videoAiTab === 'research' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'"
                >
                  🔬 Research Paper
                </button>
                <button
                  @click="videoAiTab = 'study'"
                  class="px-2 py-0.5 rounded-lg transition-colors cursor-pointer"
                  :class="videoAiTab === 'study' ? 'bg-amber-600 text-white' : 'text-slate-400 hover:text-white'"
                >
                  🎓 College Study
                </button>
              </div>
            </div>

            <!-- Tab 1: Research Paper Mode Reply -->
            <div v-if="videoAiTab === 'research'" class="space-y-2">
              <div class="ml-auto max-w-[85%] p-2 rounded-xl bg-blue-600 text-white text-xs font-medium">
                What is the novel contribution of Multi-Head Attention?
              </div>

              <!-- Research Structured Reply Cards -->
              <div class="space-y-1.5">
                <div class="p-2.5 rounded-xl bg-blue-950/60 border border-blue-600/40 text-sky-200 text-[11px] leading-relaxed">
                  <strong class="text-sky-300 block mb-0.5">🔬 Novel Architectural Innovation:</strong>
                  Replaces sequential $O(N)$ RNN recurrence with parallel $O(1)$ multi-head projections, unlocking massive GPU training parallelism.
                </div>

                <div class="p-2.5 rounded-xl bg-emerald-950/40 border border-emerald-600/40 text-emerald-200 text-[11px] font-mono leading-relaxed">
                  <strong class="text-emerald-400 block mb-0.5">⚙️ Mathematical Formulation:</strong>
                  MultiHead(Q,K,V) = Concat(head₁...headₕ)Wᴼ • d_k = d_model / h
                </div>

                <div class="p-2.5 rounded-xl bg-purple-950/40 border border-purple-600/40 text-purple-200 text-[11px] leading-relaxed">
                  <strong class="text-purple-300 block mb-0.5">📊 Empirical Ablation Metrics:</strong>
                  WMT 2014 English-to-German BLEU score reaches 28.4 (+2.0 over SOTA ensemble) with 3.5× faster training time.
                </div>

                <div class="px-3 py-1.5 rounded-xl bg-blue-950 border border-blue-800 text-sky-300 text-[10.5px] font-bold flex items-center justify-between cursor-pointer hover:bg-blue-900/80">
                  <span>👉 "How does Positional Encoding prevent order permutation?"</span>
                  <span class="material-symbols-outlined text-xs">arrow_forward</span>
                </div>
              </div>
            </div>

            <!-- Tab 2: College Study Mode Reply -->
            <div v-else class="space-y-2">
              <div class="ml-auto max-w-[85%] p-2 rounded-xl bg-amber-600 text-white text-xs font-medium">
                Explain the fork-exec pattern and process virtualization
              </div>

              <!-- Study Structured Reply Cards -->
              <div class="space-y-1.5">
                <div class="p-2.5 rounded-xl bg-amber-950/40 border border-amber-600/40 text-amber-200 text-[11px] leading-relaxed">
                  <strong class="text-amber-300 block mb-0.5">💡 Real-World Analogy:</strong>
                  Imagine a worker cloning themselves completely (fork), taking on a brand new job assignment (exec), while the supervisor waits for completion (wait).
                </div>

                <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-[10.5px] font-mono leading-relaxed">
                  <strong class="text-teal-400 block mb-0.5">⚙️ C Kernel System Calls:</strong>
                  pid_t rc = fork(); if (rc == 0) { execvp(args[0], args); } else { wait(NULL); }
                </div>

                <div class="p-2.5 rounded-xl bg-rose-950/40 border border-rose-600/40 text-rose-200 text-[11px] leading-relaxed">
                  <strong class="text-rose-400 block mb-0.5">⚠️ High-Yield Professor Exam Trap:</strong>
                  Fork does NOT restart from main()! Both parent and child resume execution immediately *after* the fork call, distinguished only by the return value.
                </div>

                <div class="px-3 py-1.5 rounded-xl bg-emerald-950 border border-emerald-800 text-emerald-300 text-[10.5px] font-bold flex items-center justify-between cursor-pointer hover:bg-emerald-900/80">
                  <span>👉 "Calculate total processes generated by nested fork() loops"</span>
                  <span class="material-symbols-outlined text-xs">arrow_forward</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- SCENE 5: Top Learning Path Slider (Prerequisite Stepper on top of 3D Map) -->
        <div
          v-else-if="currentChapter.visualPhase === 'slider'"
          class="absolute inset-0 pointer-events-none z-20 p-4 flex flex-col justify-between"
        >
          <!-- Movable Stepper at Top Center -->
          <div class="w-full max-w-lg mx-auto pointer-events-auto p-4 bg-[#0F172A]/95 backdrop-blur-xl rounded-2xl border-2 border-slate-700 shadow-2xl space-y-2 text-left animate-in fade-in slide-in-from-top-4 duration-300">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-blue-400">linear_scale</span>
                <span class="text-xs font-extrabold text-white">Top Learning Path Slider</span>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-900/60 text-sky-400 border border-blue-800 font-bold">
                Step 2 of 6 • Active
              </span>
            </div>

            <div class="p-2.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
              <div class="flex items-center justify-between text-xs">
                <button
                  @click="handleVideoStepClick(0)"
                  class="px-2 py-0.5 rounded bg-slate-800 text-slate-400 hover:text-white text-[10px] font-mono cursor-pointer"
                >
                  ← Prev: Scaled Dot-Product
                </button>
                <span class="font-extrabold text-sky-400 text-xs">Multi-Head Attention</span>
                <button
                  @click="handleVideoStepClick(2)"
                  class="px-2 py-0.5 rounded bg-blue-600 text-white text-[10px] font-mono font-bold cursor-pointer"
                >
                  Next: Positional Encoding →
                </button>
              </div>
              <!-- Track -->
              <div class="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div class="w-2/6 h-full bg-blue-500 rounded-full"></div>
              </div>
            </div>
          </div>

          <!-- Bottom Camera Auto-Zoom Badge -->
          <div class="self-center pointer-events-auto p-2.5 px-4 rounded-2xl bg-blue-950/90 border border-blue-500/60 backdrop-blur-md shadow-2xl flex items-center gap-2.5 text-xs text-white">
            <span class="w-2.5 h-2.5 rounded-full bg-blue-400 animate-ping"></span>
            <span class="font-bold">Camera Auto-Focus Zoom: Centered on Tower 02 (Multi-Head Attention)</span>
            <span class="text-[10px] font-mono text-sky-300">Radar Halo Active 🎯</span>
          </div>
        </div>

        <!-- SCENE 6: NEW FEATURE — Study Progress & Topic Completion Breakdown -->
        <div
          v-else-if="currentChapter.visualPhase === 'progress'"
          class="relative z-20 w-full max-w-lg p-5 bg-[#0F172A]/95 backdrop-blur-xl rounded-3xl border-2 border-slate-700 shadow-2xl animate-in fade-in zoom-in-95 duration-300 space-y-3.5 text-left"
        >
          <!-- Header -->
          <div class="flex items-center justify-between pb-2 border-b border-slate-800">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-emerald-400 text-lg">donut_large</span>
              <span class="text-xs font-black text-white">Curriculum Study Progress Tracker</span>
            </div>
            <span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px] font-mono font-bold">
              Live Percentage
            </span>
          </div>

          <!-- Overall Completion Metric -->
          <div class="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div class="space-y-0.5">
              <span class="text-[10px] font-mono font-bold text-slate-400 uppercase">Overall Syllabus Completion</span>
              <div class="text-2xl font-black text-emerald-400">{{ videoDemoProgress }}% Mastered</div>
              <span class="text-[10.5px] text-slate-400">3 of 5 topics completed</span>
            </div>
            <div class="w-28 space-y-1">
              <div class="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <div class="h-full bg-emerald-500 rounded-full transition-all duration-300" :style="{ width: `${videoDemoProgress}%` }"></div>
              </div>
              <span class="text-[9.5px] font-mono text-right text-slate-400 block">Target: 100%</span>
            </div>
          </div>

          <!-- Topic-by-Topic Breakdown Table with Percentages -->
          <div class="space-y-1.5 max-h-40 overflow-y-auto regulus-scroll pr-1">
            <div
              v-for="(t, idx) in videoDemoTopics"
              :key="t.id"
              class="p-2 rounded-xl border flex items-center justify-between text-xs transition-colors"
              :class="t.done ? 'bg-emerald-950/30 border-emerald-800/60' : 'bg-slate-900/60 border-slate-800'"
            >
              <div class="flex items-center gap-2">
                <button
                  @click="toggleVideoTopic(idx)"
                  class="w-5 h-5 rounded-md flex items-center justify-center transition-colors border cursor-pointer"
                  :class="t.done ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-slate-600 hover:border-blue-400'"
                >
                  <span class="material-symbols-outlined text-xs">check</span>
                </button>
                <span :class="t.done ? 'text-emerald-200 line-through opacity-80' : 'text-white font-medium'">
                  Step {{ idx + 1 }}: {{ t.name }}
                </span>
              </div>
              <span class="font-mono text-[10px] font-bold" :class="t.done ? 'text-emerald-400' : 'text-slate-400'">
                {{ t.weight }}% weight
              </span>
            </div>
          </div>
        </div>

        <!-- SCENE 7: Quiz Master, Notes, Theme Sync & Launch 3D Realm -->
        <div
          v-else-if="currentChapter.visualPhase === 'quiz'"
          class="relative z-20 w-full max-w-lg p-5 bg-[#0F172A]/95 backdrop-blur-xl rounded-3xl border-2 border-slate-700 shadow-2xl animate-in fade-in zoom-in-95 duration-300 space-y-3 text-left"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-emerald-400">quiz</span>
              <span class="text-xs font-black text-white">Interactive Quizzes & Theme Sync</span>
            </div>
            <span class="px-2 py-0.5 rounded bg-emerald-900/60 text-emerald-400 border border-emerald-800 text-[10px] font-mono font-bold">
              Score: 100% 🏆
            </span>
          </div>

          <!-- Question Card -->
          <div class="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
            <span class="text-xs font-bold text-white">Q: Why scale dot-products by 1/√d_k?</span>
            <div class="grid grid-cols-2 gap-1.5 text-[10.5px]">
              <div class="p-2 rounded-lg bg-slate-800/80 text-slate-400 border border-slate-700">A. Doubling parameters</div>
              <div class="p-2 rounded-lg bg-emerald-950/80 text-emerald-300 border-2 border-emerald-500 font-bold flex items-center justify-between">
                <span>B. Prevent vanishing gradients</span>
                <span>✓</span>
              </div>
              <div class="p-2 rounded-lg bg-slate-800/80 text-slate-400 border border-slate-700">C. Lower GPU memory</div>
              <div class="p-2 rounded-lg bg-slate-800/80 text-slate-400 border border-slate-700">D. Enforce causality</div>
            </div>
          </div>

          <!-- Theme Toggle Preview Button -->
          <button
            @click.stop="themeStore.toggleTheme()"
            class="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-mono font-bold text-slate-200 border border-slate-700 flex items-center justify-center gap-2 cursor-pointer transition-colors"
          >
            <span class="material-symbols-outlined text-sm text-amber-400">
              {{ themeStore.isDark() ? 'light_mode' : 'dark_mode' }}
            </span>
            <span>Toggle {{ themeStore.isDark() ? 'Light Mode' : 'Dark Mode' }} Preview</span>
          </button>

          <!-- Launch Button -->
          <button
            @click="exploreRealmNow"
            class="w-full py-3 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-sm shadow-[0_4px_0_#1D4ED8] active:translate-y-0.5 transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <span>Launch 3D Knowledge Realm</span>
            <span class="material-symbols-outlined text-lg">arrow_forward</span>
          </button>
        </div>
      </div>

      <!-- Live Word-by-Word Synchronized Subtitle Drawer -->
      <div
        class="px-5 py-3 bg-[#0F172A] border-t border-slate-800/80 flex items-center gap-3.5 min-h-[58px]"
      >
        <div class="w-7 h-7 rounded-lg bg-blue-900/60 border border-blue-700/60 text-sky-400 flex items-center justify-center shrink-0">
          <span class="material-symbols-outlined text-sm">closed_caption</span>
        </div>
        <p class="text-xs sm:text-[13px] text-slate-200 font-medium leading-relaxed text-left flex-1">
          {{ currentSubtitle }}
        </p>
      </div>

      <!-- Scrubber Timeline & Playback Controller -->
      <div class="p-4 bg-[#0B1120] border-t border-slate-800 flex flex-col gap-3">
        <!-- Interactive Progress Scrubber -->
        <div
          class="relative w-full h-2 bg-slate-800 rounded-full cursor-pointer group flex items-center"
          @click="(e) => {
            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
            const ratio = (e.clientX - rect.left) / rect.width
            seekTo(ratio * totalDuration)
          }"
        >
          <div
            class="h-full bg-blue-600 rounded-full transition-all duration-100 relative"
            :style="{ width: `${progressPercent}%` }"
          >
            <span
              class="absolute right-0 top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full bg-white shadow-md border-2 border-blue-600 scale-0 group-hover:scale-100 transition-transform"
            ></span>
          </div>
        </div>

        <!-- Controls Row -->
        <div class="flex items-center justify-between text-xs">
          <!-- Play/Pause, Rewind, Mute -->
          <div class="flex items-center gap-2.5">
            <button
              @click="togglePlay"
              class="w-9 h-9 rounded-xl bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center shadow-md transition-all active:scale-95 cursor-pointer"
              :title="isPlaying ? 'Pause' : 'Play'"
            >
              <span class="material-symbols-outlined text-xl">
                {{ isPlaying ? 'pause' : 'play_arrow' }}
              </span>
            </button>

            <button
              @click="restart"
              class="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors cursor-pointer"
              title="Restart video"
            >
              <span class="material-symbols-outlined text-base">replay</span>
            </button>

            <button
              @click="toggleMute"
              :class="[
                'px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer border',
                isMuted
                  ? 'bg-rose-950/60 border-rose-800 text-rose-300 hover:bg-rose-900/70'
                  : 'bg-slate-800 border-slate-700 text-slate-200 hover:bg-slate-700',
              ]"
              :title="isMuted ? 'Unmute Audio Narration' : 'Mute Audio Narration'"
            >
              <span class="material-symbols-outlined text-base">
                {{ isMuted ? 'volume_off' : 'volume_up' }}
              </span>
              <span>{{ isMuted ? 'Narration Muted' : 'Narration ON' }}</span>
            </button>
          </div>

          <!-- Chapter Quick Jump Pills -->
          <div class="hidden lg:flex items-center gap-1 bg-slate-800/80 p-1 rounded-xl border border-slate-700/80 text-[10.5px]">
            <button
              v-for="(ch, idx) in chapters"
              :key="ch.id"
              @click="jumpToChapter(idx)"
              :class="[
                'px-2 py-0.5 rounded-lg font-medium transition-all cursor-pointer',
                activeChapterIndex === idx
                  ? 'bg-blue-600 text-white font-bold shadow-xs'
                  : 'text-slate-400 hover:text-white',
              ]"
            >
              {{ ch.id }}. {{ ch.title }}
            </button>
          </div>

          <!-- Time & Direct Launch Pill -->
          <div class="flex items-center gap-3">
            <span class="font-mono text-slate-400 text-xs font-bold">
              {{ formatTime(currentTime) }} / {{ formatTime(totalDuration) }}
            </span>

            <button
              @click="exploreRealmNow"
              class="hidden sm:flex px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs items-center gap-1 transition-colors cursor-pointer shadow-xs"
            >
              <span>Explore 3D Realm</span>
              <span class="material-symbols-outlined text-xs">arrow_forward</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
