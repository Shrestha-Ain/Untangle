import { defineStore } from 'pinia'
import { api } from '@/api/client'

export interface GraphNode {
  id: string
  name: string
  type: string // 'CONCEPT' | 'PERSON' | 'ORG' | 'LOCATION' | 'CHAPTER' | 'SECTION' | 'TOPIC'
  description?: string
  mention_count?: number
  level?: number
  path_order?: number // Step order in the sequential learning path (1, 2, 3...)
  x?: number
  y?: number
}

export interface GraphEdge {
  id: string
  source_id: string
  target_id: string
  relation_type: string
  is_cross_source?: boolean
}

export interface CommunityGroup {
  id: string
  title: string
  summary?: string
  entity_ids: string[]
  level: number
}

export interface ChunkExcerpt {
  chunk_id: string
  section_ref: string
  text: string
}

export interface ExamTakeaway {
  key_takeaways: string[]
  formula_to_memorize?: string
  likely_exam_question: string
  trap_to_avoid?: string
}

export interface TopicDossier {
  node_id: string
  name: string
  type: string
  path_step?: number
  summary: string
  key_formulas_or_code: string[]
  raw_chunks: ChunkExcerpt[]
  prerequisites: string[]
  next_concepts: string[]
  exam_gist?: ExamTakeaway
}

export interface HighYieldTopicGist {
  node_id: string
  name: string
  type: string
  high_yield_rank: number // 1, 2, 3...
  tagline: string
  summary: string
  key_formula_or_rule?: string
  likely_exam_question: string
  exam_trap: string
}

export interface ExamGistData {
  document_id: string
  document_title: string
  mode: 'research' | 'study'
  total_topics: number
  generated_at: string
  high_yield_topics: HighYieldTopicGist[]
}

export const useGraphStore = defineStore('graph', {
  state: () => ({
    nodes: [] as GraphNode[],
    edges: [] as GraphEdge[],
    communityData: [] as CommunityGroup[],
    selectedEntityId: null as string | null,
    highlightedSubgraph: null as { nodeIds: string[]; edgeIds: string[] } | null,
    // Learning path state
    learningPath: [] as string[], // Ordered array of node IDs
    currentPathIndex: 0,
    isPathModeActive: true,
    // Topic reader state
    activeDossier: null as TopicDossier | null,
    isReaderOpen: false,
    // Exam Gist state
    examGistData: null as ExamGistData | null,
    isExamGistOpen: false,
    isLoading: false,
    currentDocumentId: null as string | null,
  }),

  getters: {
    selectedEntity: (state) =>
      state.nodes.find((n) => n.id === state.selectedEntityId) ?? null,

    townBuildings: (state) =>
      state.nodes.map((n) => ({
        id: n.id,
        label: n.name,
        type: n.type || 'CONCEPT',
        mentionCount: n.mention_count || 1,
        level: n.level ?? Math.min(Math.ceil((n.mention_count || 1) / 5), 5),
        pathOrder: n.path_order,
        description: n.description,
        x: n.x,
        y: n.y,
      })),

    energyRoads: (state) =>
      state.edges.map((e) => ({
        id: e.id,
        sourceId: e.source_id,
        targetId: e.target_id,
        relationType: e.relation_type || 'RELATES_TO',
        isCrossSource: e.is_cross_source || false,
      })),

    communities: (state) => state.communityData,

    currentPathNodeId: (state): string | null => {
      if (state.learningPath.length === 0) return null
      return state.learningPath[state.currentPathIndex] ?? null
    },

    currentPathNode(state): GraphNode | null {
      const id = this.currentPathNodeId
      if (!id) return null
      return state.nodes.find((n) => n.id === id) ?? null
    },
  },

  actions: {
    async loadGraph(documentId: string, mode: 'research' | 'study' = 'research') {
      this.currentDocumentId = documentId
      this.isLoading = true

      try {
        const endpoint = mode === 'study' ? `/graph/${documentId}/study-map` : `/graph/${documentId}/town`
        const { data } = await api.get(endpoint)
        if (data && data.nodes) {
          // Normalize nodes — backend may not include mention_count or path_order
          this.nodes = (data.nodes || []).map((n: any) => ({
            id: n.id,
            name: n.name || n.id,
            type: n.type || 'CONCEPT',
            description: n.description || '',
            mention_count: n.mention_count || n.level || 1,
            level: n.level || 1,
            path_order: n.path_order,
            x: n.x,
            y: n.y,
          }))

          // Normalize edges — backend uses {source, target, relation},
          // frontend expects {source_id, target_id, relation_type, id}
          this.edges = (data.edges || []).map((e: any, idx: number) => ({
            id: e.id || `edge-${e.source || e.source_id}-${e.target || e.target_id}-${idx}`,
            source_id: e.source_id || e.source || '',
            target_id: e.target_id || e.target || '',
            relation_type: e.relation_type || e.relation || 'RELATES_TO',
            is_cross_source: e.is_cross_source || false,
          }))

          this.communityData = data.communities || []

          // Try to get learning path from backend
          try {
            const pathRes = await api.get(`/graph/${documentId}/learning-path`)
            const pathData = pathRes.data
            if (Array.isArray(pathData)) {
              // Direct array of IDs
              this.learningPath = pathData
            } else if (pathData?.steps && Array.isArray(pathData.steps)) {
              // Backend returns { document_id, steps: [{step_index, id, name, ...}] }
              this.learningPath = pathData.steps.map((s: any) => s.id)
            } else {
              this.computeDefaultLearningPath()
            }
          } catch {
            // Compute fallback learning path from nodes sorted by path_order
            this.computeDefaultLearningPath()
          }
          this.isLoading = false
          return
        }
      } catch (err) {
        console.warn('Backend graph data unavailable, generating seed map for:', documentId, err)
      }

      // Generate realistic mock graph if offline / demo
      this.generateMockGraph(documentId, mode)
      this.isLoading = false
    },

    computeDefaultLearningPath() {
      const sorted = [...this.nodes].sort((a, b) => (a.path_order ?? 99) - (b.path_order ?? 99))
      this.learningPath = sorted.map((n) => n.id)
      this.currentPathIndex = 0
    },

    generateMockGraph(_documentId: string, mode: 'research' | 'study') {
      if (mode === 'study') {
        // Study Mode Hierarchy (OSTEP book style - clean, spacious cartography)
        this.nodes = [
          { id: 'sec-1-1', name: 'Process API', type: 'SECTION', description: 'Core system calls: fork(), exec(), and wait().', mention_count: 18, level: 4, path_order: 1, x: 580, y: 320 },
          { id: 'top-1-1-1', name: 'Fork Call', type: 'TOPIC', description: 'Creates a child process that is an almost exact clone of the caller.', mention_count: 14, level: 3, path_order: 2, x: 500, y: 520 },
          { id: 'top-1-1-2', name: 'Context Switch', type: 'TOPIC', description: 'Mechanism to save register state and restore another process.', mention_count: 16, level: 3, path_order: 3, x: 920, y: 360 },
          { id: 'chap-2', name: 'Concurrency', type: 'CHAPTER', description: 'Managing multi-threaded access to shared variables and critical sections.', mention_count: 22, level: 5, path_order: 4, x: 980, y: 580 },
          { id: 'sec-2-1', name: 'Locks & Mutexes', type: 'SECTION', description: 'Hardware and software primitives for mutual exclusion.', mention_count: 17, level: 4, path_order: 5, x: 1380, y: 400 },
          { id: 'top-2-1-1', name: 'Compare-And-Swap', type: 'TOPIC', description: 'Atomic hardware instruction utilized for building spinlocks.', mention_count: 12, level: 2, path_order: 6, x: 1280, y: 660 },
          { id: 'top-ext-paper', name: 'Amdahl Law', type: 'CONCEPT', description: 'Theoretical bound on parallel speedup (Cross-source link).', mention_count: 9, level: 2, path_order: 7, x: 940, y: 800 },
        ]
        this.edges = [
          { id: 'e-1', source_id: 'sec-1-1', target_id: 'top-1-1-1', relation_type: 'HAS_TOPIC' },
          { id: 'e-2', source_id: 'sec-1-1', target_id: 'top-1-1-2', relation_type: 'HAS_TOPIC' },
          { id: 'e-3', source_id: 'top-1-1-2', target_id: 'chap-2', relation_type: 'LEADS_TO' },
          { id: 'e-4', source_id: 'chap-2', target_id: 'sec-2-1', relation_type: 'CONTAINS' },
          { id: 'e-5', source_id: 'sec-2-1', target_id: 'top-2-1-1', relation_type: 'HAS_TOPIC' },
          { id: 'e-6', source_id: 'top-2-1-1', target_id: 'top-ext-paper', relation_type: 'NEEDS_CONTEXT', is_cross_source: true },
        ]
        this.communityData = [
          { id: 'c-1', title: 'Chapter 1: Virtualization', entity_ids: ['sec-1-1', 'top-1-1-1', 'top-1-1-2'], level: 1 },
          { id: 'c-2', title: 'Chapter 2: Concurrency', entity_ids: ['chap-2', 'sec-2-1', 'top-2-1-1', 'top-ext-paper'], level: 2 },
        ]
        this.learningPath = ['sec-1-1', 'top-1-1-1', 'top-1-1-2', 'chap-2', 'sec-2-1', 'top-2-1-1', 'top-ext-paper']
      } else {
        // Research Mode Graph (Attention Is All You Need - spacious page2 layout)
        this.nodes = [
          { id: 'n-attn', name: 'Multi-Head Attention', type: 'CONCEPT', description: 'Mechanism computing joint information across distinct representation subspaces.', mention_count: 38, level: 5, path_order: 2, x: 980, y: 440 },
          { id: 'n-pe', name: 'Positional Encoding', type: 'CONCEPT', description: 'Injected sine/cosine frequencies providing sequence order awareness.', mention_count: 18, level: 3, path_order: 3, x: 980, y: 220 },
          { id: 'n-vaswani', name: 'Ashish Vaswani', type: 'PERSON', description: 'Lead author of Attention Is All You Need, Google Brain.', mention_count: 14, level: 3, path_order: 4, x: 580, y: 460 },
          { id: 'n-sdpa', name: 'Scaled Dot-Product', type: 'LOCATION', description: 'Core matrix attention equation: softmax(QK^T / sqrt(d_k))V.', mention_count: 28, level: 4, path_order: 1, x: 960, y: 680 },
          { id: 'n-brain', name: 'Google Brain', type: 'ORG', description: 'Deep learning research team where the Transformer was invented.', mention_count: 20, level: 4, path_order: 5, x: 1380, y: 420 },
          { id: 'n-bert', name: 'BERT Architecture', type: 'CONCEPT', description: 'Bidirectional encoder representations developed from transformers.', mention_count: 12, level: 2, path_order: 6, x: 1420, y: 640 },
        ]
        this.edges = [
          { id: 'e-1', source_id: 'n-sdpa', target_id: 'n-attn', relation_type: 'FOUNDATION_OF' },
          { id: 'e-2', source_id: 'n-attn', target_id: 'n-pe', relation_type: 'COMBINED_WITH' },
          { id: 'e-3', source_id: 'n-vaswani', target_id: 'n-attn', relation_type: 'PROPOSED' },
          { id: 'e-4', source_id: 'n-vaswani', target_id: 'n-brain', relation_type: 'WORKS_FOR' },
          { id: 'e-5', source_id: 'n-attn', target_id: 'n-bert', relation_type: 'INFLUENCED' },
        ]
        this.communityData = [
          { id: 'c-1', title: 'Attention Core Architecture', entity_ids: ['n-sdpa', 'n-attn', 'n-pe'], level: 1 },
          { id: 'c-2', title: 'Research Genesis & Impact', entity_ids: ['n-vaswani', 'n-brain', 'n-bert'], level: 2 },
        ]
        this.learningPath = ['n-sdpa', 'n-attn', 'n-pe', 'n-vaswani', 'n-brain', 'n-bert']
      }
      this.currentPathIndex = 0
    },

    selectEntity(entityId: string | null) {
      this.selectedEntityId = entityId
      if (entityId) {
        // Sync learning path index if selected node is on the path
        const idx = this.learningPath.indexOf(entityId)
        if (idx !== -1) {
          this.currentPathIndex = idx
        }
      }
    },

    highlightSubgraph(subgraph: { nodeIds: string[]; edgeIds: string[] } | null) {
      this.highlightedSubgraph = subgraph
    },

    // Learning Path Traversal Actions
    setPathIndex(index: number) {
      if (index >= 0 && index < this.learningPath.length) {
        this.currentPathIndex = index
        const nodeId = this.learningPath[index]
        this.selectEntity(nodeId)
      }
    },

    nextPathStep() {
      if (this.currentPathIndex < this.learningPath.length - 1) {
        this.setPathIndex(this.currentPathIndex + 1)
      }
    },

    prevPathStep() {
      if (this.currentPathIndex > 0) {
        this.setPathIndex(this.currentPathIndex - 1)
      }
    },

    togglePathMode() {
      this.isPathModeActive = !this.isPathModeActive
      if (this.isPathModeActive && this.learningPath.length > 0) {
        this.selectEntity(this.learningPath[this.currentPathIndex])
      }
    },

    // Deep Topic Reader
    async openTopicDossier(nodeId: string) {
      this.isLoading = true
      this.isReaderOpen = true

      try {
        const { data } = await api.get(`/graph/${this.currentDocumentId}/nodes/${nodeId}/dossier`)
        if (data) {
          // Normalize backend NodeDossierResponse → frontend TopicDossier
          // Backend: { text_chunks, description, incoming_relations, outgoing_relations }
          // Frontend: { raw_chunks, summary, prerequisites, next_concepts, exam_gist }
          this.activeDossier = {
            node_id: data.node_id,
            name: data.name,
            type: data.type || 'CONCEPT',
            path_step: data.path_step,
            summary: data.summary || data.description || '',
            key_formulas_or_code: data.key_formulas_or_code || [],
            raw_chunks: (data.raw_chunks || data.text_chunks || []).map((c: any) => ({
              chunk_id: c.chunk_id || c.id || `chunk-${Math.random().toString(36).slice(2, 8)}`,
              section_ref: c.section_ref || c.metadata?.section || 'Source Document',
              text: c.text || c.content || c.payload?.text || '',
            })),
            prerequisites: data.prerequisites ||
              (data.incoming_relations || [])
                .map((r: any) => r.source || r.name || '')
                .filter(Boolean)
                .slice(0, 5),
            next_concepts: data.next_concepts ||
              (data.outgoing_relations || [])
                .map((r: any) => r.target || r.name || '')
                .filter(Boolean)
                .slice(0, 5),
            exam_gist: data.exam_gist || undefined,
          }
          this.isLoading = false
          return
        }
      } catch {
        // Fallback to rich mock dossier for demo
      }

      const node = this.nodes.find((n) => n.id === nodeId)
      if (!node) {
        this.isLoading = false
        return
      }

      this.activeDossier = this.buildMockDossier(node)
      this.isLoading = false
    },

    closeTopicReader() {
      this.isReaderOpen = false
    },

    // Exam Gist & High-Yield Revision Sheet Actions
    async openExamGist(documentId?: string) {
      const docId = documentId || this.currentDocumentId || 'doc-attention-1706'
      this.isLoading = true
      this.isExamGistOpen = true

      try {
        const { data } = await api.get(`/graph/${docId}/exam-gist`)
        if (data && data.high_yield_topics) {
          this.examGistData = data
          this.isLoading = false
          return
        }
      } catch {
        // Fallback to rich mock exam gist
      }

      this.examGistData = this.buildMockExamGist(docId)
      this.isLoading = false
    },

    closeExamGist() {
      this.isExamGistOpen = false
    },

    buildMockExamGist(documentId: string): ExamGistData {
      const isStudy = documentId.includes('ostep') || documentId.includes('book')
      if (isStudy) {
        return {
          document_id: documentId,
          document_title: 'Operating Systems: Three Easy Pieces (OSTEP)',
          mode: 'study',
          total_topics: 7,
          generated_at: '2026-09-20',
          high_yield_topics: [
            {
              node_id: 'top-1-1-1',
              name: 'Fork System Call',
              type: 'TOPIC',
              high_yield_rank: 1,
              tagline: 'Process Creation & Virtual Memory Duplication',
              summary:
                'Primary UNIX mechanism to spawn processes. Creates an exact duplicate of the caller with identical memory image, file descriptors, and CPU registers, but a distinct PID.',
              key_formula_or_rule: 'pid_t rc = fork(); // returns 0 in child, child_pid in parent, <0 on failure',
              likely_exam_question:
                'Explain what fork() returns in the child vs. parent process and whether global variable modifications in the child affect the parent.',
              exam_trap:
                'Exam Trap: Students assume memory is shared. After fork(), the child has its own copy-on-write virtual address space. Mutating variables in the child does NOT alter the parent!',
            },
            {
              node_id: 'top-1-1-2',
              name: 'Context Switch',
              type: 'TOPIC',
              high_yield_rank: 2,
              tagline: 'CPU Time-Sharing & Register State Transition',
              summary:
                'Low-level assembly mechanism to pause one running process and resume another. Involves saving hardware registers to the kernel stack and restoring the target process registers.',
              key_formula_or_rule:
                'Cost: Register Save/Restore + TLB Flush (Cache Misses overhead: ~1-10 microseconds)',
              likely_exam_question:
                'What hardware and software state must be saved and restored during a context switch, and why is it expensive?',
              exam_trap:
                'Exam Trap: Context switch overhead is not just register swapping—the hidden cost is indirect overhead from cold CPU caches and TLB invalidation!',
            },
            {
              node_id: 'top-2-1-1',
              name: 'Compare-And-Swap (CAS)',
              type: 'TOPIC',
              high_yield_rank: 3,
              tagline: 'Hardware Mutual Exclusion Primitive',
              summary:
                'Atomic hardware instruction testing if memory holds an expected value; if true, updates to new value. Fundamental building block for non-blocking locks and synchronization.',
              key_formula_or_rule: 'int CAS(int *ptr, int expected, int new_val) // atomic hardware test-and-set',
              likely_exam_question:
                'How is Compare-And-Swap used to build a basic spinlock, and what is its main drawback under heavy contention?',
              exam_trap:
                'Exam Trap: Spinlocks with CAS waste CPU cycles spinning in a loop while waiting. On single-CPU systems, a pure spinlock without yielding will deadlock until timer interrupt!',
            },
          ],
        }
      }

      // Research Mode Exam Gist (Attention Is All You Need)
      return {
        document_id: documentId,
        document_title: 'Attention Is All You Need (Vaswani et al.)',
        mode: 'research',
        total_topics: 6,
        generated_at: '2026-09-20',
        high_yield_topics: [
          {
            node_id: 'n-attn',
            name: 'Multi-Head Attention',
            type: 'CONCEPT',
            high_yield_rank: 1,
            tagline: 'Parallel Subspace Attention Mechanism',
            summary:
              'Linearly projects Queries, Keys, and Values into h lower-dimensional subspaces, computes Scaled Dot-Product Attention in parallel, and concatenates the resulting projections.',
            key_formula_or_rule:
              'MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W^O\nwhere head_i = Attention(Q W_i^Q, K W_i^K, V W_i^V)',
            likely_exam_question:
              'Why does Transformer use Multi-Head Attention instead of a single large attention head?',
            exam_trap:
              'Exam Trap: Students often believe multi-head attention increases model FLOPs. Because d_k = d_v = d_model / h = 64, total computational cost is equivalent to single-head full-dim attention!',
          },
          {
            node_id: 'n-sdpa',
            name: 'Scaled Dot-Product Attention',
            type: 'LOCATION',
            high_yield_rank: 2,
            tagline: 'Softmax Matrix Attention Equation',
            summary:
              'Computes dot products of query with all keys, divides by √d_k, applies softmax to obtain weights, and multiplies by values. Scaling prevents vanishing gradients.',
            key_formula_or_rule: 'Attention(Q, K, V) = softmax( (Q K^T) / √d_k ) V',
            likely_exam_question:
              'Why is the scaling factor 1/√d_k necessary in Scaled Dot-Product Attention?',
            exam_trap:
              'Exam Trap: For large d_k, dot products grow large in magnitude, pushing softmax into extreme regions with near-zero gradients. Scaling by √d_k restores unit variance!',
          },
          {
            node_id: 'n-pe',
            name: 'Positional Encoding',
            type: 'CONCEPT',
            high_yield_rank: 3,
            tagline: 'Sinusoidal Sequence Order Injection',
            summary:
              'Adds fixed sinusoidal functions of varying frequencies to input embeddings to inject positional information since self-attention contains no recurrence or convolution.',
            key_formula_or_rule:
              'PE(pos, 2i)   = sin( pos / 10000^{2i / d_model} )\nPE(pos, 2i+1) = cos( pos / 10000^{2i / d_model} )',
            likely_exam_question:
              'How do Positional Encodings allow the model to generalize to sequence lengths longer than those seen during training?',
            exam_trap:
              'Exam Trap: Positional encodings are ADDED elementwise to word embeddings, not concatenated, to avoid expanding model dimension!',
          },
        ],
      }
    },

    buildMockDossier(node: GraphNode): TopicDossier {
      const idx = this.learningPath.indexOf(node.id)
      const prereq = idx > 0 ? [this.nodes.find((n) => n.id === this.learningPath[idx - 1])?.name ?? ''] : []
      const nextC = idx < this.learningPath.length - 1 ? [this.nodes.find((n) => n.id === this.learningPath[idx + 1])?.name ?? ''] : []

      if (node.id === 'n-attn') {
        return {
          node_id: node.id,
          name: node.name,
          type: node.type,
          path_step: node.path_order ?? 2,
          summary:
            'Multi-Head Attention extends standard self-attention by linearly projecting Queries, Keys, and Values h times with distinct learned parameter matrices. Each projection is then processed in parallel by Scaled Dot-Product attention, concatenated, and projected once more into the output dimension.',
          key_formulas_or_code: [
            'MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W^O',
            'where head_i = Attention(Q W_i^Q, K W_i^K, V W_i^V)',
            'Parameter matrices: W_i^Q ∈ ℝ^{d_model × d_k}, W_i^K ∈ ℝ^{d_model × d_k}, W_i^V ∈ ℝ^{d_model × d_v}, W^O ∈ ℝ^{hd_v × d_model}',
          ],
          raw_chunks: [
            {
              chunk_id: 'chunk-attention-1',
              section_ref: 'Vaswani et al. §3.2.2 Multi-Head Attention',
              text: 'Instead of performing a single attention function with d_model-dimensional queries, keys and values, we found it beneficial to linearly project the queries, keys and values h times with different, learned linear projections to d_k, d_k and d_v dimensions, respectively.',
            },
            {
              chunk_id: 'chunk-attention-2',
              section_ref: 'Vaswani et al. §3.2.2 Intuition & Parallelism',
              text: 'Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this.',
            },
            {
              chunk_id: 'chunk-attention-3',
              section_ref: 'Vaswani et al. §5.3 Dimension Configuration',
              text: 'In this work we employ h = 8 parallel attention layers, or heads. For each of these we use d_k = d_v = d_model / h = 64. Due to the reduced dimension of each head, the total computational cost is similar to that of single-head attention with full dimensionality.',
            },
          ],
          prerequisites: prereq.filter(Boolean),
          next_concepts: nextC.filter(Boolean),
          exam_gist: {
            key_takeaways: [
              'Computes attention over h separate representation subspaces in parallel.',
              'Uses d_k = d_v = d_model / h = 64 (for d_model = 512, h = 8).',
              'Total compute cost is identical to single-head attention of full dimensionality.',
            ],
            formula_to_memorize: 'MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W^O',
            likely_exam_question: 'Why is Multi-Head Attention beneficial over single-head attention?',
            trap_to_avoid:
              'Do not confuse multi-head projection with increasing total parameters; each head works on down-projected subspaces, keeping total FLOPs constant.',
          },
        }
      } else if (node.id === 'top-1-1-1') {
        return {
          node_id: node.id,
          name: 'Fork System Call',
          type: 'TOPIC',
          path_step: node.path_order ?? 2,
          summary:
            'The fork() system call creates an exact duplicate of the calling process. The new child process runs concurrently with the parent, having its own separate address space, file descriptor table, and register states.',
          key_formulas_or_code: [
            '#include <unistd.h>\npid_t rc = fork();\nif (rc < 0) {\n    fprintf(stderr, "fork failed\\n");\n} else if (rc == 0) {\n    printf("hello from child (pid:%d)\\n", (int) getpid());\n} else {\n    printf("parent of %d (pid:%d)\\n", rc, (int) getpid());\n}',
          ],
          raw_chunks: [
            {
              chunk_id: 'chunk-ostep-fork-1',
              section_ref: 'OSTEP §5.1 The fork() System Call',
              text: 'The fork() system call is the primary mechanism in UNIX for creating new processes. When fork() completes, two processes return from the call. To the child process, fork() returns 0; to the parent process, fork() returns the PID of the newly created child.',
            },
            {
              chunk_id: 'chunk-ostep-fork-2',
              section_ref: 'OSTEP §5.2 Determinism & CPU Scheduling',
              text: 'Notice that the output of a program calling fork() is not deterministic. Once the child is created, the OS CPU scheduler decides which process (parent or child) runs first on the CPU.',
            },
          ],
          prerequisites: prereq.filter(Boolean),
          next_concepts: nextC.filter(Boolean),
          exam_gist: {
            key_takeaways: [
              'fork() creates an exact duplicate process with distinct address space and PID.',
              'Returns 0 to child, child PID to parent, negative on failure.',
              'Execution order between parent and child is non-deterministic (OS CPU scheduler decision).',
            ],
            formula_to_memorize: 'pid_t rc = fork(); // 0 = child, >0 = parent',
            likely_exam_question: 'What is the return value of fork() in parent vs child?',
            trap_to_avoid:
              'Child processes share open file descriptors, but have independent address spaces—modifying variables in child does NOT change parent state!',
          },
        }
      }

      // Generic dossier with auto-generated exam takeaway
      return {
        node_id: node.id,
        name: node.name,
        type: node.type,
        path_step: node.path_order,
        summary: node.description ?? 'A key concept extracted during knowledge graph analysis.',
        key_formulas_or_code: [],
        raw_chunks: [
          {
            chunk_id: `chunk-${node.id}-1`,
            section_ref: 'Primary Source Section',
            text: `Detailed discussion and contextual usage of ${node.name}. This section establishes its relational importance and dependencies within the surrounding domain hierarchy.`,
          },
        ],
        prerequisites: prereq.filter(Boolean),
        next_concepts: nextC.filter(Boolean),
        exam_gist: {
          key_takeaways: [
            `Core concept within domain hierarchy: ${node.name}.`,
            'Directly connected along critical relationship pathways.',
          ],
          likely_exam_question: `Explain the architectural role of ${node.name} in this system.`,
          trap_to_avoid: `Confusing ${node.name} with adjacent or prerequisite modules.`,
        },
      }
    },
  },
})
