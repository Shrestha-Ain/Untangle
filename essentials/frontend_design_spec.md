# Untangle — Frontend Design Specification

**Companion to:** `graphrag_explorer_system_design.md` and `graphrag_implementation_deep_dive.md`

## 1. Design Philosophy & Brand

### Brand Identity: Untangle

Untangle is a knowledge mapping tool that helps researchers and students see structure inside dense academic material. The name reflects the product's core purpose: taking a tangled web of concepts, citations, and dependencies and making it navigable.

**What it isn't:** Untangle is not branded as a game. It uses a spatial, isometric map as a visual metaphor for knowledge graphs because spatial navigation is cognitively intuitive — not because it's a city-builder. The difference matters in copy, in color choices, and in how features are named.

### Brand Personality
- **Structured Clarity:** Dense material made legible. Every design decision earns its place.
- **Quiet Intelligence:** The interface feels considered, not busy. It surfaces information when relevant, stays out of the way when not.
- **Spatial Intuition:** The isometric map metaphor works because humans navigate space naturally. Towers closer together are more related. Bright roads mean active connections. This isn't decoration — it's communication.

### Design Movement: Muted Academic Spatial Tool
Muted, warm neutrals as the dominant surface. Desaturated accent colors with deliberate restraint. Crisp information hierarchy through typography and spacing rather than color intensity. No heavy gradients, no glow-heavy backgrounds, no game chrome. The one place vibrancy is allowed: the knowledge map canvas itself, where colored towers and glowing roads communicate structure.

### Rule: The Gradient Rule
At most one 2-stop gradient per component, no more than 10% brightness difference between stops. Most surfaces are flat muted colors. Gradients are used only for:
- Progress bar fills (single horizontal axis)
- The hero heading text on auth pages (single direction, very subtle)
- The isometric map canvas terrain (barely perceptible, top-to-bottom)

---

## 2. Design System Tokens

### 2.1 Color Palette

**Surface & Environmental**
| Token Name | Hex | Usage |
|---|---|---|
| `surface` | `#F7F6F3` | Warm off-white base — like a textbook page. Primary app background. |
| `surface-container-low` | `#EFEFED` | Slightly darker neutral. Card backgrounds, sidebar fills. |
| `surface-container` | `#E8E7E3` | Input backgrounds, secondary panels. |
| `surface-container-high` | `#DEDDD8` | Hover states on surface. |
| `canvas-bg` | `#EEF0EB` | Isometric map canvas background — sage-tinted parchment. |
| `zone-greenfield` | `#DFE8DA` | Park zones and open terrain on the map. Desaturated sage. |
| `road-track` | `#D8D6CF` | Road base lanes. Warm stone grey. |
| `border-default` | `#D4D3CE` | General borders, dividers. |
| `border-muted` | `#E4E3DF` | Subtle borders on cards. |

**Entity Node Colors (muted, perceptually balanced)**
| Token | Hex | Entity Type | Notes |
|---|---|---|---|
| `node-person` | `#7C6FA0` | Person / Author | Dusty lavender |
| `node-org` | `#C49A3C` | Organisation / Institution | Warm ochre |
| `node-concept` | `#4E9A7D` | Concept / Topic | Muted jade |
| `node-location` | `#A85A5A` | Location / Dataset | Dusty rose-red |
| `node-community` | `#4E8FA8` | Community / District | Dusty slate-blue |
| `node-chapter` | `#7A8C6A` | Chapter (Study Mode) | Olive sage |
| `node-section` | `#B8A87A` | Section (Study Mode) | Warm tan |

**Interactive & Accent Colors**
| Token | Hex | Usage |
|---|---|---|
| `primary` | `#3D6B5A` | Brand color — muted forest green. Primary buttons, active states, links. |
| `primary-dark` | `#2C5043` | Button press depth shadow. |
| `primary-light` | `#E8F0EC` | Primary-tinted backgrounds for selected states. |
| `beam-pulse` | `#6BA3BE` | Active traversal path glow on canvas. Soft steel blue. |
| `source-link` | `#B8A87A` | Dashed cross-source roads (outside context links). Warm tan. |
| `accent-amber` | `#B8924A` | Secondary accent — citations, markers. Muted amber. |
| `accent-amber-dark` | `#8C6A2C` | Amber button press depth. |

**Text Colors**
| Token | Hex | Usage |
|---|---|---|
| `text-primary` | `#1C1B18` | Primary body text |
| `text-secondary` | `#5C5A54` | Secondary text, labels |
| `text-muted` | `#8A877F` | Placeholder text, metadata |
| `text-inverse` | `#F7F6F3` | Text on dark/colored backgrounds |

**HUD & Glassmorphism**
| Token | Value | Usage |
|---|---|---|
| `hud-surface` | `rgba(247, 246, 243, 0.92)` | Floating HUD panel backgrounds |
| `hud-border` | `rgba(212, 211, 206, 0.80)` | HUD panel borders — warm stone |
| `hud-surface-dark` | `#1C1B18` | Dark tag backgrounds on canvas |

**Semantic States**
| Token | Hex | Usage |
|---|---|---|
| `state-success` | `#4E9A7D` | (Shares with `node-concept`) Success states, completed steps |
| `state-warning` | `#C49A3C` | Warning states, in-progress steps |
| `state-error` | `#A85A5A` | Error states |
| `state-info` | `#4E8FA8` | Informational states |

---

### 2.2 Typography Scale

Two fonts only. No game font (Fredoka removed).

| Token | Font | Size | Weight | Line height | Letter spacing | Usage |
|---|---|---|---|---|---|---|
| `display-hero` | Inter | 36px | 800 | 44px | -0.025em | Auth page headings |
| `headline-lg` | Inter | 24px | 700 | 32px | -0.02em | Section headers |
| `headline-md` | Inter | 18px | 600 | 26px | -0.01em | Card headers, panel titles |
| `headline-sm` | Inter | 15px | 600 | 22px | normal | Small section titles |
| `body-lg` | Inter | 15px | 400 | 24px | normal | Primary body text |
| `body-md` | Inter | 13px | 400 | 20px | normal | Secondary body, Regulus chat text |
| `body-sm` | Inter | 12px | 400 | 18px | normal | Fine print, metadata |
| `label-code-lg` | JetBrains Mono | 13px | 600 | 18px | -0.01em | Chunk text, code, map building labels |
| `label-code-md` | JetBrains Mono | 11px | 500 | 16px | normal | Edge relations, telemetry |
| `label-badge` | JetBrains Mono | 10px | 700 | 14px | 0.04em | Node badges, counters |

---

### 2.3 Spacing & Layout

| Token | Value |
|---|---|
| `space-xs` | 0.25rem |
| `space-sm` | 0.5rem |
| `space-md` | 0.75rem |
| `space-lg` | 1rem |
| `space-xl` | 1.5rem |
| `space-2xl` | 2rem |
| `gutter` | 1rem |
| `gutter-lg` | 1.5rem |

---

### 2.4 Border Radius

| Token | Value | Usage |
|---|---|---|
| `rounded` | 0.375rem | Input fields, small chips |
| `rounded-md` | 0.5rem | Buttons, small cards |
| `rounded-lg` | 0.75rem | Medium panels |
| `rounded-xl` | 1rem | Cards, form containers |
| `rounded-2xl` | 1.25rem | HUD panels, larger cards |
| `rounded-3xl` | 1.75rem | Auth panels, modals |
| `rounded-full` | 9999px | Pills, avatars |

---

### 2.5 Elevation & Shadows

**The 5 Planes:**
1. **Plane 0 (Map Canvas):** Terrain tiles, park zones, roads. No shadow.
2. **Plane 1 (Buildings & Roads):** Node buildings and relationship roads on the SVG canvas. Buildings: `drop-shadow(0 2px 4px rgba(28,27,24,0.12))`. Highlighted buildings: `drop-shadow(0 0 16px rgba(107,163,190,0.35))`.
3. **Plane 2 (Floating Labels):** Entity labels above buildings. `0 1px 3px rgba(28,27,24,0.10)`.
4. **Plane 3 (HUD Panels):** Frosted glass panels. `backdrop-filter: blur(10px)`, `rgba(247,246,243,0.92)` fill, `0 4px 20px rgba(28,27,24,0.08)`.
5. **Plane 4 (Drawers & Modals):** Deep shadow. `0 8px 40px rgba(28,27,24,0.12)`.

**Functional Shadows (CSS Custom Values):**
- `shadow-card`: `0 1px 3px rgba(28,27,24,0.08), 0 1px 2px rgba(28,27,24,0.04)`
- `shadow-card-hover`: `0 4px 12px rgba(28,27,24,0.10), 0 2px 4px rgba(28,27,24,0.05)`
- `shadow-panel`: `0 4px 20px rgba(28,27,24,0.08)`
- `shadow-panel-lg`: `0 8px 40px rgba(28,27,24,0.12)`
- `shadow-btn`: `0 3px 0 #2C5043` (primary button press depth)
- `shadow-btn-amber`: `0 3px 0 #8C6A2C` (amber button press depth)

---

## 3. Page Specifications

### 3.1 Home / Dashboard

**Layout:** Max-width container, sticky top navigation bar, main content area with soft ambient warmth and lively interactive cards.

**Components:**

#### 3.1.1 Top Navigation Bar
- **Left:** Untangle wordmark + node logomark + live status indicator pill (`● Live Sync`).
- **Right:** User avatar (Clerk integration), dev guest chip if unauthenticated, and session controls.
- Style: `bg-surface/95 backdrop-blur-md border-b border-border-default`, height 56px.

#### 3.1.2 Source Upload Panel (dual-mode)
Lively, tactile card with soft ambient decorative glows (`bg-emerald-50/50` and `bg-amber-50/40`), subtle float animation on upload icons (`animate-float`), and dual-column workflow:

**Left — "Map a Research Paper"**
- Label: `RESEARCH MODE` badge (muted jade, uppercase, JetBrains Mono)
- Heading: "Map a Research Paper"
- Subtext: "Extract entities, relationships, and communities from an academic paper."
- Drag-and-drop zone: dashed tactile border (`border-2 border-dashed border-[#D4D3CE]`), `bg-[#F7F6F3]/60 hover:bg-[#F7F6F3]`
- Floating upload icon with subtle soft float animation, "Drop paper PDF or click to browse", or paste arXiv URL input.
- Supported: PDF, DOCX, TXT

**Right — "Untangle a Book"**
- Label: `STUDY MODE` badge (muted ochre, uppercase, JetBrains Mono)
- Heading: "Untangle a Book"
- Subtext: "Break down a textbook or study book into an explorable knowledge map."
- Same drag-and-drop zone style with book icon and warm tan accents.
- Supported: PDF, EPUB, TXT
- Interactive Callout: Explains automatic cross-source context detection and manual outside source import.

#### 3.1.3 Ingestion Progress Panel
Shown when a document is being processed. Displays live progression:
- **Header:** Live pulsing dot + document title + stage explanation.
- **Progress bar:** Smooth animated fill with mode-specific tinting.
- **3-step stepper:** Mode-aware stages with spin and checkmark status.

#### 3.1.4 Knowledge Maps Section
- **Header:** "Your Knowledge Maps" + search input with live keyword filtering.
- **Filter tabs:** All Maps | Research Papers | Study Books with interactive numeric badges.
- **Grid:** 3–4 column responsive grid of tactile map cards.

#### 3.1.5 Map Card
- Background: White card with `rounded-2xl`, tactile border `border border-[#E4E3DF]`, and smooth hover lift (`hover:-translate-y-1 hover:shadow-card-hover`).
- **Top row:** ModeBadge (`Research` / `Study`), live status tag, and subtle delete icon on hover.
- **Title & Author:** Crisp typography with 2-line clamp.
- **Stats ribbon:** 3-column pill grid (Entities/Roads/Districts or Chapters/Sections/Topics).
- **Interactive Mini-Tag Preview Strip:** Displays preview badges of top concepts or chapters.
- **Action:** Tactile **"Open Map →"** button with 3D press depth (`shadow-btn active:translate-y-px`).

---

### 3.2 Knowledge Map Explorer (Isometric Canvas)

**Layout:** Full-viewport SVG canvas backdrop (`2048x1400` viewBox), floating glassmorphic HUD panels on all corners.

#### 3.2.1 Top Navigation HUD (`TownNavBar.vue`)
- Floating frosted bar across top:
  - **Left:** Back button to dashboard + document title + mode badge (with clean `hub` icon).
  - **Center:** Quick type filter pills with live count badges and Material Symbols (All Nodes, Concepts, Authors, Organizations, Benchmarks or All Elements, Chapters, Sections, Topics).
  - **Right:** "⚡ Exam Gist" rapid review button, recenter button, zoom controls.

#### 3.2.2 Isometric Map Canvas (`TownCanvas.vue`)
- **Cartographic Layout & Spacing**: Generous isometric tile spacing (`TILE_W: 380`, `TILE_H: 200`, `250px - 450px` breathing room between towers) ensuring zero visual congestion or overlapping tags.
- **Background**: Lush, clean cartographic linear gradient (`grassGrad`: `#E9F7EF` → `#DEF3E7` → `#D4ECE0`) with subtle geometric grid texture and vibrant decorative greenery clusters (`TreeCluster.vue`).
- **Districts (`DistrictTurf.vue`):** Multi-polygon solid pastel turf island platforms (`#CEEFE2` with `#B4E5D1` border, `#E8EDF9` with `#CCD8F4` border, `#F4E9F7` with `#E3CCE9` border, `#FDF1DF` with `#F8DFBC` border) with embedded territory banners in the ground plane.
- **Road Network (`EnergyRoad.vue`):** High-fidelity triple-layer highways:
  - Cobblestone underlay track (`stroke="#CBD5E1" stroke-width="24"`).
  - Clean surface lane (`stroke="#FFFFFF" stroke-width="14"`).
  - Luminous animated energy stream (`stroke-dasharray` flowing particles):
    - Radiant cyan (`#38BDF8`), rich purple (`#A855F7`), deep cyan (`#06B6D4`), and emerald (`#10B981`).
    - Cross-source links: Animated amber stream (`#F59E0B`).
  - Midpoint relation pill badge with uppercase monospace text and relation color dot.
- **Sequential Learning Path Trail:** An illuminated gradient ribbon (`#06B6D4` → `#10B981` → `#F59E0B`) with soft glow halo that visually weaves through nodes in recommended curriculum sequence.

#### 3.2.3 Building Styles by Node Type (Inspired by `page2/code.html`, strictly NO flags or game emojis)
Every tower is an elaborate 2.5D architectural sprite:
1. **Concept / Spire (e.g. Multi-Head Attention):**
   - 3D stepped faceted crystal body.
   - Central floating crystal gem with soft glow filter (`filter="url(#softGlow)"`) and gentle float animation.
   - Pulsing ground plinth ring (`animate-pulse-ring`).
   - Sky light beam shooting upward from the spire apex (`line class="animate-pulse"`).
2. **Author / Research Lodge (e.g. Vaswani Lodge):**
   - Cozy academic lodge with shaded isometric wall polygons.
   - Steepled cozy roof with rich lavender-to-purple gradient.
   - Warm arch entry door.
   - Architectural finial at apex (strictly **NO flags**).
3. **Location / Training Arena (e.g. Scaled Dot-Product Arena):**
   - Multi-tiered isometric base plinth.
   - Golden training dome with radial ambient highlight (`path d="M... Q... Z"`).
4. **Chapter / Citadel (Study Mode):**
   - Grand multi-tiered academic citadel with fortress towers and wide base.
5. **Section / Modern Lab Block (Study Mode & Orgs):**
   - Layered tech block with solar/glass panels and beveled corners.

All towers feature:
- Ground shadow ellipse (`fill="#1C1B18" fill-opacity="0.14"`).
- Selection pulse ring when clicked.
- High-contrast floating pill tag with type dot, title, and academic sequence / mention badge (strictly no RPG levels or game emojis).
- Floating sequence badge (`#1`, `#2`) when Learning Path mode is active.

#### 3.2.4 Building Detail Panel (`BuildingInfoCard.vue`)
- Fixed right side drawer (`width: 320px`). Glassmorphic container with close button.
- Clean Material Symbol avatar icon, node type badge, entity name, and 3-column telemetry grid (Type, Mentions/Depth, Connections). Zero game levels or RPG terminology.
- Executive summary text block.
- Action Buttons:
  - **"Read Everything on This Topic"**: Opens the full-screen Topic Reader Modal.
  - **"Highlight Connections"**: Pulses 1-hop neighborhood on canvas.
  - **"Find External References"** (Study Mode): Queries user library for related sources.

#### 3.2.5 Regulus Panel (`RegulusPanel.vue`)
- Fixed bottom-left glassmorphic panel (`width: 500px`).
- Header with Regulus avatar and mode badge.
- Conversational streaming text with grounded citation chunk clues.
- Outside-source suggestion banners with "+ Import Source" triggers.

#### 3.2.6 Learning Path Stepper (`LearningPathStepper.vue`)
- Top-center floating HUD widget for guided curriculum traversal:
  - **Mode Toggle**: "Guided Journey" vs "Free Network".
  - **Step Navigator**: `[◀ Prev Concept]  Step 2 of 6: Multi-Head Attention  [Next Concept ▶]`.
  - Clicking next/prev auto-selects that building on the canvas, lights up the path, and updates Regulus context!

#### 3.2.7 Deep Topic Reader Modal (`TopicReaderModal.vue`)
- Triggered by "Read Full Topic Dossier" from the building info card.
- Full slide-over reader pane for exhaustive study:
  - **Header**: Topic Name, Type, Path Step, Close button.
  - **⚡ 2-Min Exam Gist (Top Banner)**: Prominent high-yield takeaway card at the very top of the dossier featuring key takeaway bullets, core formula/definition to memorize, and likely exam questions/traps. Designed specifically for students reviewing right before an exam.
  - **Synthesis**: Comprehensive explanation of the concept.
  - **Key Equations & Code**: Syntax-highlighted formulas and implementation snippets.
  - **Verbatim Source Passages**: All text chunks from the document that mention or define this concept, complete with section numbers and chunk IDs.
  - **Prerequisites & Next Steps**: Direct links to navigate to related concepts along the learning path.

#### 3.2.8 Exam Gist Modal & High-Yield Review Sheet (`ExamGistModal.vue`)
- Triggered globally via the **"⚡ Exam Gist"** button in `TownNavBar.vue` (top HUD) and quick-action on `MapCard.vue` (dashboard).
- Centered modal / full-height drawer containing an elaborate, document-wide high-yield revision sheet:
  - **Header**: Document Title, Mode Badge, "⚡ High-Yield Exam Gist", Quick Search & Filter bar, and Close button.
  - **Topic Cheat Sheet Cards**:
    - High-yield priority rank (e.g. `Rank 1: Core Foundation`, `Rank 2: Critical Mechanism`).
    - 2-sentence executive definition.
    - Memorization box: core formula (LaTeX/Monospace) or fundamental rule.
    - Likely Exam Question / Common Pitfall: exact question archetype with concise model answer.
    - **"Jump to Tower on Map"** button: instantly closes the modal, flies to the node on the isometric canvas, and pulses its 1-hop connections.

---

### 3.3 Login

- **Layout:** Centered content, two-column on desktop (left: brand/feature overview; right: Clerk `<SignIn />`)
- **Background:** Flat `#F7F6F3`. Dot grid at 8% opacity (`rgba(28,27,24,0.08)`). No colored orbs or glows.
- **Brand block:** Untangle wordmark + logomark. Tagline: "Turn dense material into navigable knowledge."
- **Feature list:** Two or three short feature bullets. Clean icon + text, no gamification language.
- **Clerk component:** Wrapped in a white card (`bg-white rounded-2xl shadow-panel border border-border-muted`). Custom appearance matching the muted palette.
- **Auth link:** "Don't have an account? Sign up" below the Clerk component.

---

### 3.4 Register

- **Layout:** Mirror of Login — two-column, same calm aesthetic.
- **Left column:** "Start mapping your knowledge." Heading. Two mode previews: small Research Mode callout + Study Mode callout, side by side.
- **Right column:** Clerk `<SignUp />` wrapped in the same white card.
- **Auth link:** "Already have an account? Sign in"

---

### 3.5 Evaluation Report (planned for later)

- Header: "GraphRAG vs Vector RAG — Benchmark Report"
- Two metric columns: GraphRAG (primary muted green) vs. Vector RAG (muted slate)
- Flat horizontal bars for accuracy, latency. No victory banners, no game chrome.
- Run history table at the bottom.

---

## 4. Regulus AI Guide

Regulus is Untangle's AI guide. Named neutrally, works across both modes.

**Research Mode behavior:**
- Answers questions about entities, relationships, and communities in the paper.
- Grounds every answer with the exact subgraph and chunk passage used.
- Detects when a question requires outside context and suggests related papers.

**Study Mode behavior:**
- Answers concept questions, explains topics and sub-topics.
- Can traverse hierarchically ("explain this topic's parent chapter for more context").
- Flags when a concept assumes knowledge from outside the current book.
- Presents auto-suggested external sources inside the panel for one-click import.

**Tone:** Clear and direct. Academic but not stiff. Does not use game language ("quest", "exploring the realm", etc.).

---

## 5. Responsive Behavior

| Breakpoint | Dashboard | Map Explorer |
|---|---|---|
| Desktop (≥1280px) | Full layout, 3–4 col map grid, side-by-side upload panel | Full canvas, all HUDs visible simultaneously |
| Tablet (1024–1279px) | 2-col map grid, stacked upload panel | Canvas + bottom Regulus, detail panel as slide-over |
| Mobile (<1024px) | 1-col map grid, stacked everything | Toggle: Full Map OR Full Regulus Chat |

---

## 6. Animation & Microinteraction Catalog

| Name | CSS | Duration | Usage |
|---|---|---|---|
| `float-soft` | `translateY(0→-5px→0)` | 4s ease-in-out infinite | Upload drop zone icon only |
| `pulse-ring` | `scale(0.95→1.05→0.95), opacity(0.7→0.3→0.7)` | 2.5s ease infinite | Active building base ring (selected state) |
| `particle-run` | `stroke-dashoffset: 60→0` | 1.4s linear infinite | Road traversal particle flow |
| `animate-pulse` | Tailwind built-in | — | Ingestion progress dot, pending state |
| `animate-spin` | Tailwind built-in | — | Loading spinner on async actions |
| hover `-translate-y-0.5` | `translateY(-2px)` | 200ms | Map card hover lift |
| `active:translate-y-px` | `translateY(1px)` | instant | Button press depth |
| `.dimmed` | `opacity: 0.18; filter: grayscale(0.75)` | 350ms ease | Non-relevant buildings during Regulus answer |
| `.highlighted` | `opacity: 1; filter: drop-shadow(0 0 14px rgba(107,163,190,0.40))` | 350ms ease | Answer-relevant buildings |

---

## 7. Component Library

### 7.1 ModeBadge
- Pill shaped. JetBrains Mono, 10px, uppercase, letter-spacing 0.06em.
- Research: `bg-[#E8F0EC] text-[#3D6B5A] border border-[#C4D8CC]`
- Study: `bg-[#F5EFE3] text-[#8C6A2C] border border-[#DDD0B0]`

### 7.2 StatCounter
- Usage: Map cards, building detail panel.
- Structure: label (10px uppercase, `text-text-muted`, JetBrains Mono) + value (14px bold, `text-text-primary`, JetBrains Mono)
- Container: `bg-surface-container rounded-lg p-2.5 border border-border-muted`

### 7.3 ProgressBar
- Full-width. `bg-surface-container rounded-full h-1.5` outer.
- Fill: flat color (no gradient). Color matches mode.
- No animated pulse edge — just a plain filled bar.

### 7.4 PrimaryButton
- `bg-primary text-white font-semibold text-sm rounded-lg px-4 py-2 shadow-btn active:translate-y-px`
- Hover: `bg-primary/90`
- Disabled: `bg-surface-container-high text-text-muted cursor-not-allowed shadow-none`

### 7.5 SecondaryButton
- `bg-transparent text-text-secondary font-medium text-sm rounded-lg px-4 py-2 border border-border-default`
- Hover: `bg-surface-container-low`

### 7.6 GlassmorphicPanel
- `bg-[rgba(247,246,243,0.92)] backdrop-blur-[10px] border border-[rgba(212,211,206,0.80)]`
- `rounded-2xl shadow-panel pointer-events-auto`

### 7.7 BuildingTag (SVG canvas label)
- Dark pill: `fill="#1C1B18"`, `rx="10"`, with centered white monospace text.
- Colored dot prefix: `fill={nodeColor}`, radius 4.
- Scale on parent group hover: `transform: scale(1.05)` with 150ms transition.
