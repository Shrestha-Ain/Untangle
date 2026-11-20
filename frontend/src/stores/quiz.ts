import { defineStore } from 'pinia'
import { useGraphStore } from './graph'

export interface QuizQuestion {
  id: string
  topicId?: string
  topicName?: string
  question: string
  options: string[]
  correctIndex: number
  explanation: string
}

export const QUIZ_BANK: Record<string, QuizQuestion[]> = {
  // =========================================================================
  // OPERATING SYSTEMS TOPIC QUESTIONS
  // =========================================================================
  'sec-1-1': [
    {
      id: 'q-papi-1',
      topicId: 'sec-1-1',
      topicName: 'Process API',
      question: 'In Unix systems, what is the primary role of the wait() system call?',
      options: [
        'A) It puts the CPU into low-power sleep mode for 10 seconds.',
        'B) It pauses the parent until a child process terminates, reaping its exit status.',
        'C) It pauses the child until the parent sends a SIGKILL signal.',
        'D) It allocates a new process control block in swap memory.',
      ],
      correctIndex: 1,
      explanation:
        'Correct! wait() suspends the parent process until one of its children finishes, preventing the child from becoming a permanent "zombie" process in the kernel process table.',
    },
    {
      id: 'q-papi-2',
      topicId: 'sec-1-1',
      topicName: 'Process API',
      question: 'What happens to the current process memory when execvp() succeeds?',
      options: [
        'A) It spawns a parallel thread within the existing address space.',
        'B) It overwrites the code text, heap, and stack with the new executable program.',
        'C) It merges both executable binaries into a hybrid memory container.',
        'D) It returns the child PID to the parent process.',
      ],
      correctIndex: 1,
      explanation:
        'Correct! When exec() succeeds, it completely replaces the calling process’s address space with the new program code and initializes fresh stack and heap pointers.',
    },
  ],

  'top-1-1-1': [
    {
      id: 'q-fork-1',
      topicId: 'top-1-1-1',
      topicName: 'Fork Call',
      question: 'What is the return value of fork() in the newly created child process?',
      options: [
        'A) The parent process PID',
        'B) -1 on success',
        'C) 0',
        'D) A pointer to the Process Control Block',
      ],
      correctIndex: 2,
      explanation:
        'Correct! fork() returns 0 to the child process and the child’s newly assigned PID to the parent, allowing the program to differentiate roles via an if-else statement.',
    },
    {
      id: 'q-fork-2',
      topicId: 'top-1-1-1',
      topicName: 'Fork Call',
      question: 'How many total processes exist after running: for (int i = 0; i < 3; i++) fork(); ?',
      options: [
        'A) 3 processes',
        'B) 4 processes',
        'C) 6 processes',
        'D) 8 processes',
      ],
      correctIndex: 3,
      explanation:
        'Correct! Each loop iteration doubles the number of active processes: 2^3 = 8 total processes (1 original parent + 7 children).',
    },
  ],

  'top-1-1-2': [
    {
      id: 'q-ctx-1',
      topicId: 'top-1-1-2',
      topicName: 'Context Switch',
      question: 'Why is a context switch considered pure system overhead?',
      options: [
        'A) It permanently decreases the clock frequency of the CPU cores.',
        'B) It executes zero application instructions while consuming CPU cycles saving/restoring registers.',
        'C) It forces the operating system to reboot its virtual memory page tables.',
        'D) It corrupts the kernel stack pointer during hardware interrupts.',
      ],
      correctIndex: 1,
      explanation:
        'Correct! The CPU is completely consumed saving old registers and loading new registers during a context switch; no useful application payload computation occurs.',
    },
  ],

  'chap-2': [
    {
      id: 'q-conc-1',
      topicId: 'chap-2',
      topicName: 'Concurrency',
      question: 'Why is a simple C statement like `counter++` NOT thread-safe?',
      options: [
        'A) Modern compilers translate it into 3 machine instructions: Load, Modify, and Store.',
        'B) C does not permit variables named counter in multithreaded programs.',
        'C) The CPU cache refuses to write integer values across different L1 lines.',
        'D) It automatically invokes a mutex lock that deadlocks single threads.',
      ],
      correctIndex: 0,
      explanation:
        'Correct! `counter++` breaks down into `mov (Load)`, `add (Modify)`, and `mov (Store)`. If a context switch occurs between Load and Store, an update is lost (race condition).',
    },
  ],

  'sec-2-1': [
    {
      id: 'q-locks-1',
      topicId: 'sec-2-1',
      topicName: 'Locks & Mutexes',
      question: 'When is a Spinlock appropriate compared to a Sleeping Mutex?',
      options: [
        'A) On single-core uniprocessors running long database queries.',
        'B) On multicore processors where critical sections are held for only a few CPU cycles.',
        'C) When disk I/O operations take hundreds of milliseconds to complete.',
        'D) Only when user-space programs disable timer interrupts.',
      ],
      correctIndex: 1,
      explanation:
        'Correct! On multicore systems, spinning for a few nanoseconds avoids the high overhead of putting a thread to sleep and triggering full context switches.',
    },
  ],

  'top-2-1-1': [
    {
      id: 'q-cas-1',
      topicId: 'top-2-1-1',
      topicName: 'Compare-And-Swap',
      question: 'What is the "ABA problem" in lock-free CAS data structures?',
      options: [
        'A) Two threads attempt to acquire lock A then lock B in reverse order.',
        'B) A memory location changes from A to B and back to A, tricking CAS into believing nothing changed.',
        'C) The CPU memory bus overheats from excessive atomic bus-locking signals.',
        'D) A pointer is cast between ASCII characters A and B.',
      ],
      correctIndex: 1,
      explanation:
        'Correct! CAS only checks equality of value. If value A was modified to B and restored to A, CAS succeeds, even though pointer nodes or referenced structures may have been deallocated.',
    },
  ],

  'top-ext-paper': [
    {
      id: 'q-amdahl-1',
      topicId: 'top-ext-paper',
      topicName: 'Amdahl Law',
      question: 'If 90% of a program is parallelizable (P = 0.9), what is the MAXIMUM theoretical speedup with infinite CPU cores?',
      options: [
        'A) 100x',
        'B) 90x',
        'C) 10x',
        'D) 9x',
      ],
      correctIndex: 2,
      explanation:
        'Correct! By Amdahl’s Law: Limit = 1 / (1 - P) = 1 / (1 - 0.9) = 1 / 0.1 = 10x. Even with an infinite number of processors, the serial 10% strictly caps maximum speedup at 10x!',
    },
  ],

  // =========================================================================
  // TRANSFORMER / RESEARCH PAPER TOPIC QUESTIONS
  // =========================================================================
  'n-sdpa': [
    {
      id: 'q-sdpa-1',
      topicId: 'n-sdpa',
      topicName: 'Scaled Dot-Product',
      question: 'Why does Scaled Dot-Product Attention scale the dot products by 1 / sqrt(d_k)?',
      options: [
        'A) To double the memory throughput of GPU high-bandwidth memory (HBM).',
        'B) To prevent large dot product magnitudes from pushing the softmax into regions with vanishing gradients.',
        'C) To convert word embeddings from float32 into int8 quantization.',
        'D) To ensure queries and keys have identical vocabulary dimensions.',
      ],
      correctIndex: 1,
      explanation:
        'Correct! For large vector dimensions d_k, dot products grow large, causing softmax to yield extremely small gradients (vanishing gradient problem). Dividing by sqrt(d_k) stabilizes variance to 1.',
    },
  ],

  'n-attn': [
    {
      id: 'q-mha-1',
      topicId: 'n-attn',
      topicName: 'Multi-Head Attention',
      question: 'Does Multi-Head Attention with 8 heads require 8x more FLOP computation than single-head attention?',
      options: [
        'A) Yes, because each head calculates the full d_model matrix attention.',
        'B) No, because each head operates on a reduced dimension d_k = d_model / 8, keeping total computational cost identical.',
        'C) Yes, because every head requires separate positional encodings.',
        'D) No, because attention is only computed on the first head and cached for the rest.',
      ],
      correctIndex: 1,
      explanation:
        'Correct! Since d_k = d_model / h, each head operates in a smaller subspace. The concatenated multi-head computation has approximately the exact same FLOP cost as single-head full-dimension attention.',
    },
  ],

  'n-pe': [
    {
      id: 'q-pe-1',
      topicId: 'n-pe',
      topicName: 'Positional Encoding',
      question: 'Why do Transformers require Positional Encoding in the first place?',
      options: [
        'A) Because GPUs cannot multiply matrices without coordinate indices.',
        'B) Because self-attention is permutation-invariant and has no built-in awareness of token sequence order.',
        'C) To normalize token embeddings so their L2 norm equals 1.',
        'D) To compress the vocabulary size before embedding lookup.',
      ],
      correctIndex: 1,
      explanation:
        'Correct! Unlike RNNs that process tokens sequentially, self-attention treats tokens as an unordered set (bag of words). Positional encodings inject essential word-order frequencies.',
    },
  ],

  'n-bert': [
    {
      id: 'q-bert-1',
      topicId: 'n-bert',
      topicName: 'BERT Architecture',
      question: 'How does BERT differ architecturally from standard autoregressive models like GPT?',
      options: [
        'A) BERT uses Decoder blocks with causal masking to generate text left-to-right.',
        'B) BERT is an Encoder-only model with bidirectional attention, trained via Masked Language Modeling.',
        'C) BERT avoids using matrix multiplications and relies solely on convolutional layers.',
        'D) BERT cannot process natural language text.',
      ],
      correctIndex: 1,
      explanation:
        'Correct! BERT uses bidirectional Transformer encoder blocks to attend to context from both left and right simultaneously, making it ideal for classification and understanding rather than generation.',
    },
  ],
}

export const useQuizStore = defineStore('quiz', {
  state: () => ({
    isOpen: false,
    quizMode: 'topic' as 'topic' | 'document',
    selectedTopicId: null as string | null,
    selectedTopicName: null as string | null,
    questions: [] as QuizQuestion[],
    currentIndex: 0,
    selectedOptionIndex: null as number | null,
    hasAnswered: false,
    score: 0,
    isFinished: false,
  }),

  getters: {
    currentQuestion: (state) => state.questions[state.currentIndex] ?? null,
    totalQuestions: (state) => state.questions.length,
    progressPercentage: (state) => {
      if (state.questions.length === 0) return 0
      return Math.round(((state.currentIndex + (state.hasAnswered ? 1 : 0)) / state.questions.length) * 100)
    },
  },

  actions: {
    openQuiz(mode: 'topic' | 'document' = 'topic', topicId?: string) {
      const graphStore = useGraphStore()
      this.quizMode = mode
      this.isOpen = true
      this.isFinished = false
      this.currentIndex = 0
      this.selectedOptionIndex = null
      this.hasAnswered = false
      this.score = 0

      const targetId = topicId || graphStore.selectedEntityId || (graphStore.nodes[0]?.id ?? 'sec-1-1')
      this.selectedTopicId = targetId
      const node = graphStore.nodes.find((n) => n.id === targetId)
      this.selectedTopicName = node?.name || targetId

      this.generateQuestions(mode, targetId)
    },

    closeQuiz() {
      this.isOpen = false
    },

    setQuizMode(mode: 'topic' | 'document') {
      this.openQuiz(mode, this.selectedTopicId || undefined)
    },

    generateQuestions(mode: 'topic' | 'document', topicId: string) {
      if (mode === 'topic') {
        const topicQs = QUIZ_BANK[topicId]
        if (topicQs && topicQs.length > 0) {
          this.questions = [...topicQs]
        } else {
          // Fallback to nearest questions
          const allQs = Object.values(QUIZ_BANK).flat()
          this.questions = allQs.slice(0, 3)
        }
      } else {
        // Document-wide comprehensive quiz (mix across topics)
        const allQs = Object.values(QUIZ_BANK).flat()
        // Shuffle & pick 5 questions
        const shuffled = [...allQs].sort(() => 0.5 - Math.random())
        this.questions = shuffled.slice(0, Math.min(5, shuffled.length))
      }
    },

    submitAnswer(optionIndex: number) {
      if (this.hasAnswered || !this.currentQuestion) return

      this.selectedOptionIndex = optionIndex
      this.hasAnswered = true

      if (optionIndex === this.currentQuestion.correctIndex) {
        this.score++
      }
    },

    nextQuestion() {
      if (this.currentIndex < this.questions.length - 1) {
        this.currentIndex++
        this.selectedOptionIndex = null
        this.hasAnswered = false
      } else {
        this.isFinished = true
      }
    },

    restartQuiz() {
      this.openQuiz(this.quizMode, this.selectedTopicId || undefined)
    },
  },
})
