<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'

const props = defineProps<{
  documentId: string
  mode: 'research' | 'study'
}>()

const chatStore = useChatStore()
const queryInput = ref('')
const isExpanded = ref(true)
const scrollContainer = ref<HTMLDivElement | null>(null)
const expandedCitations = ref<Record<string, boolean>>({})

function toggleCitation(msgId: string) {
  expandedCitations.value[msgId] = !expandedCitations.value[msgId]
}

async function handleSend() {
  const q = queryInput.value.trim()
  if (!q || chatStore.isStreaming) return
  queryInput.value = ''
  await chatStore.sendMessage(q, props.documentId, props.mode)
}

watch(
  () => chatStore.messages.length,
  async () => {
    await nextTick()
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  }
)
</script>

<template>
  <div
    class="absolute bottom-4 left-4 z-20 w-[92vw] sm:w-[500px] bg-white/95 backdrop-blur-xl rounded-2xl border border-[#E4E3DF] shadow-[0_8px_40px_rgba(28,27,24,0.12)] flex flex-col overflow-hidden transition-all duration-200"
    :class="isExpanded ? 'h-[440px]' : 'h-14'"
  >
    <!-- Top Header Bar -->
    <div
      class="px-4 py-3 bg-[#F7F6F3]/80 border-b border-[#E4E3DF] flex items-center justify-between cursor-pointer select-none"
      @click="isExpanded = !isExpanded"
    >
      <div class="flex items-center gap-2.5">
        <div class="w-7 h-7 rounded-full bg-[#1C1B18] text-white font-bold text-xs flex items-center justify-center">
          R
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-[#1C1B18]">Regulus</span>
            <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#E8F0EC] text-[#3D6B5A] border border-[#C4D8CC]">
              {{ mode === 'study' ? 'Study Guide' : 'Research Guide' }}
            </span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click.stop="chatStore.clearChat"
          class="text-[10px] text-[#8A877F] hover:text-[#1C1B18] px-2 py-0.5 rounded hover:bg-[#EFEFED] transition-colors"
          title="Clear Conversation"
        >
          Clear
        </button>
        <button
          class="w-6 h-6 rounded flex items-center justify-center text-[#5C5A54] hover:bg-[#EFEFED] transition-colors"
        >
          <span class="material-symbols-outlined text-sm">
            {{ isExpanded ? 'expand_more' : 'expand_less' }}
          </span>
        </button>
      </div>
    </div>

    <!-- Messages Container (when expanded) -->
    <div
      v-show="isExpanded"
      ref="scrollContainer"
      class="flex-1 p-4 overflow-y-auto space-y-4 regulus-scroll text-xs"
    >
      <!-- Welcome Message if empty -->
      <div
        v-if="chatStore.messages.length === 0"
        class="text-center py-8 space-y-2 text-[#8A877F]"
      >
        <span class="material-symbols-outlined text-2xl text-[#3D6B5A]">psychology</span>
        <p class="text-xs font-medium text-[#5C5A54]">
          Ask Regulus anything about this {{ mode === 'study' ? 'textbook' : 'paper' }}.
        </p>
        <p class="text-[11px]">
          {{ mode === 'study'
            ? 'Try: "Explain how locks prevent race conditions" or "What are the key concepts in Chapter 2?"'
            : 'Try: "How does Multi-Head Attention relate to Scaled Dot-Product?"'
          }}
        </p>
      </div>

      <!-- Message History -->
      <div
        v-for="msg in chatStore.messages"
        :key="msg.id"
        class="space-y-2"
      >
        <!-- User bubble -->
        <div
          v-if="msg.role === 'user'"
          class="ml-auto max-w-[85%] bg-[#EFEFED] text-[#1C1B18] p-3 rounded-2xl rounded-tr-sm border border-[#D4D3CE] font-medium"
        >
          {{ msg.content }}
        </div>

        <!-- Assistant bubble -->
        <div
          v-else
          class="mr-auto max-w-[92%] bg-white p-3.5 rounded-2xl rounded-tl-sm border border-[#E4E3DF] shadow-sm space-y-2 text-[#1C1B18]"
        >
          <p class="leading-relaxed whitespace-pre-line">{{ msg.content }}</p>

          <!-- Streaming cursor -->
          <span
            v-if="msg.isStreaming"
            class="inline-block w-1.5 h-3 bg-[#3D6B5A] animate-pulse ml-0.5"
          ></span>

          <!-- Citations / Clues Accordion -->
          <div
            v-if="msg.citations && msg.citations.length > 0"
            class="pt-2 border-t border-[#EFEFED]"
          >
            <button
              @click="toggleCitation(msg.id)"
              class="flex items-center gap-1.5 text-[11px] font-mono font-semibold text-[#3D6B5A] hover:underline"
            >
              <span class="material-symbols-outlined text-xs">find_in_page</span>
              <span>Grounded Citations ({{ msg.citations.length }})</span>
              <span class="material-symbols-outlined text-xs">
                {{ expandedCitations[msg.id] ? 'expand_less' : 'expand_more' }}
              </span>
            </button>

            <div
              v-show="expandedCitations[msg.id]"
              class="mt-2 space-y-1.5 p-2.5 bg-[#F7F6F3] rounded-lg border border-[#E4E3DF]"
            >
              <div
                v-for="c in msg.citations"
                :key="c.chunk_id"
                class="space-y-0.5"
              >
                <div class="font-mono text-[10px] text-[#8A877F] font-bold">
                  {{ c.title ?? c.chunk_id }}
                </div>
                <p class="font-mono text-[10.5px] text-[#5C5A54] italic bg-white p-1.5 rounded border border-[#E4E3DF]">
                  "{{ c.snippet }}"
                </p>
              </div>
            </div>
          </div>

          <!-- Suggested External Sources (Study Mode Cross-Source) -->
          <div
            v-if="msg.suggestedSources && msg.suggestedSources.length > 0"
            class="mt-2 p-2.5 rounded-xl bg-[#F5EFE3] border border-[#DDD0B0] space-y-1.5"
          >
            <div class="flex items-center gap-1 text-[11px] font-bold text-[#8C6A2C]">
              <span class="material-symbols-outlined text-sm">link</span>
              <span>Suggested External Context</span>
            </div>
            <div
              v-for="s in msg.suggestedSources"
              :key="s.id"
              class="space-y-1"
            >
              <p class="text-[11px] text-[#1C1B18] font-semibold">{{ s.title }}</p>
              <p class="text-[10px] text-[#5C5A54]">{{ s.reason }}</p>
              <button
                class="mt-1 px-2.5 py-1 text-[10px] font-bold text-white bg-[#8C6A2C] hover:bg-[#6D5220] rounded shadow-sm transition-colors"
              >
                + Import Source into Map
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Bar (when expanded) -->
    <div
      v-show="isExpanded"
      class="p-3 bg-[#F7F6F3] border-t border-[#E4E3DF] flex items-center gap-2"
    >
      <input
        v-model="queryInput"
        type="text"
        :placeholder="`Ask Regulus about this ${mode === 'study' ? 'textbook' : 'paper'}...`"
        class="flex-1 px-3 py-2 text-xs rounded-xl border border-[#D4D3CE] bg-white text-[#1C1B18] placeholder-[#8A877F] focus:border-[#3D6B5A] focus:outline-none focus:ring-1 focus:ring-[#3D6B5A]"
        :disabled="chatStore.isStreaming"
        @keydown.enter="handleSend"
      />
      <button
        @click="handleSend"
        :disabled="chatStore.isStreaming || !queryInput.trim()"
        class="px-3.5 py-2 text-xs font-semibold text-white bg-[#3D6B5A] hover:bg-[#2C5043] disabled:opacity-50 disabled:cursor-not-allowed rounded-xl shadow-[0_3px_0_#2C5043] active:translate-y-px transition-all"
      >
        Ask
      </button>
    </div>
  </div>
</template>

