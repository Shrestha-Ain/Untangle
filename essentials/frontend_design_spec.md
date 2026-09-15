# Research Realm — Frontend Design Specification

**Companion to:** `graphrag_explorer_system_design.md` and `graphrag_implementation_deep_dive.md`

## 1. Design Philosophy & Brand

This design system reimagines complex academic synthesis and retrieval-augmented graph exploration (GraphRAG) through the metaphor of an isometric strategy simulation: **"Citation City."** Complex entity networks, citation multi-hop paths, and community clusters are transformed from dry topological node-link diagrams into an engaging, explorable landscape of architectural districts, research towers, knowledge plazas, and radiant transit pathways.

### Brand Personality & Emotional Impact
- **Playfully Rigorous:** Academic depth disguised in crisp gamified clarity. Users feel like city planners charting discoveries across multi-disciplinary territories rather than analysts wading through dense graph indexes.
- **Luminous Transparency:** Every multi-hop retrieval trajectory and extracted citation chunk is visually traceable through vibrant, high-luminance light pulses and trajectory beams.
- **Tactile Precision:** Combining crisp, structural developer-grade typography with soft parchment-hued cartographic bases and floating frosted HUD viewports.

### Design Movement: Gamified Technical Glassmorphism with Isometric Cartography
It merges the clean lines and modular grids of developer tooling with the delightful spatial geography of isometric simulation games (SimCity, Pokémon GO, and strategic tower defenses). Floating head-up displays (HUDs), rounded status badges, neon-lit trajectory vectors, and parchment-grounded map tiles maintain high functional density without sacrificing joy.

### Why this is a strong portfolio signal
This design heavily differentiates from typical RAG UIs, which often look like standard chat interfaces or dry dashboards. By gamifying the experience and using a rich visual metaphor, it demonstrates the ability to translate highly technical and abstract backend processes (like graph traversal and community clustering) into an intuitive, delightful, and highly differentiated user experience.

---

## 2. Design System Tokens

### 2.1 Color Palette

**Surface & Environmental**
| Token Name | Hex / Value | Usage |
|---|---|---|
| `surface` / `surface-bright` / `background` | `#f8f9ff` | Base surface colors for UI elements |
| `surface-dim` | `#cbdbf5` | Dimmed surface state |
| `surface-container-lowest` | `#ffffff` | Lowest elevation container |
| `surface-container-low` | `#eff4ff` | Low elevation container |
| `surface-container` | `#e5eeff` | Base container |
| `surface-container-high` | `#dce9ff` | High elevation container |
| `surface-container-highest` / `surface-variant` | `#d3e4fe` | Highest elevation container / variant |
| `parchment-canvas` | `#F4F7F4` | Base canvas background for the map / world |
| `zone-greenfield` | `#D9EDDF` | Greenfield park zones on the map |
| `road-track` | `#E2E8F0` | Structural lanes on the isometric map |

**Entity District Colors**
| Token Name | Hex / Value | Usage |
|---|---|---|
| `district-person` | `#8B5CF6` | Royal Lilac, representing agency, scholarly authorship, and researcher profiles. |
| `district-org` | `#F59E0B` | Warm Amber, designating universities, labs, funding agencies, and editorial bodies. |
| `district-concept` | `#10B981` | Emerald Green, symbolizing thriving core ideas, methodologies, and technical subjects. |
| `district-location` | `#EF4444` | Coral Red, highlighting empirical corpora, geographical settings, and physical testbeds. |
| `district-community` | `#06B6D4` | Electric Cyan, indicating high-density modular clusters, thematic neighborhoods. |

**Interactive State Colors**
| Token Name | Hex / Value | Usage |
|---|---|---|
| `beam-pulse` | `#38BDF8` | Radiant cyan-blue gradient, illuminating traversal paths during queries. |
| `citation-gold` | `#D97706` | Highlight color for citations and important game markers (e.g., levels) |
| (Dimmed state) | `opacity: 25%` / `#94A3B8` | Desaturated neutral tones for non-relevant nodes during queries. |

**HUD & Glassmorphism**
| Token Name | Hex / Value | Usage |
|---|---|---|
| `hud-surface` | `rgba(255, 255, 255, 0.88)` | Background fill for floating HUD panels |
| `hud-border` | `rgba(226, 232, 240, 0.85)` | Hairline border for HUD panels |
| `hud-surface-dark` | `#0F172A` | Dark tag backgrounds, e.g., floating tower tags |

**Semantic Colors**
| Token Name | Hex / Value | Usage |
|---|---|---|
| `primary` | `#00685f` | Primary branding color |
| `primary-container` | `#008378` | Primary container background |
| `secondary` | `#6b38d4` | Secondary branding color |
| `tertiary` | `#825100` | Tertiary branding color |
| `error` | `#ba1a1a` | Error state color |

### 2.2 Typography Scale

| Token name | Font family | Size | Weight | Line height | Letter spacing | Usage |
|---|---|---|---|---|---|---|
| `font-game` | Fredoka, Inter | - | 400, 500, 600, 700 | - | - | Page 2 explorer headings, immersive gamified UI text |
| `display-hero` | Inter | 36px | 800 | 44px | -0.025em | Main page headers, big stats |
| `headline-lg` | Inter | 24px | 700 | 32px | -0.02em | Section headers |
| `headline-md` | Inter | 18px | 600 | 26px | -0.01em | Card headers, panel titles |
| `headline-sm` | Inter | 15px | 600 | 22px | normal | Small section titles |
| `body-lg` | Inter | 15px | 400 | 24px | normal | Primary body text |
| `body-md` | Inter | 13px | 400 | 20px | normal | Secondary body text, chat text |
| `body-sm` | Inter | 12px | 400 | 18px | normal | Tertiary body text, fine print |
| `label-code-lg` | JetBrains Mono | 13px | 600 | 18px | -0.01em | Primary monospace labels (code, chunks) |
| `label-code-md` | JetBrains Mono | 11px | 500 | 16px | normal | Edge relationships, telemetry data |
| `label-badge` | JetBrains Mono | 10px | 700 | 14px | 0.04em | Entity badges on isometric buildings, counters |

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
| `margin` | 1rem |
| `margin-desktop` | 1.5rem |

### 2.4 Border Radius

| Token | Value |
|---|---|
| `rounded-sm` | 0.25rem |
| `rounded` | 0.5rem |
| `rounded-md` | 0.75rem |
| `rounded-lg` | 1rem |
| `rounded-xl` | 1.5rem |
| `rounded-2xl` | 1.25rem (custom) |
| `rounded-3xl` | 1.75rem (custom) |
| `rounded-4xl` | 2.25rem (custom) |
| `rounded-full` | 9999px |

### 2.5 Elevation & Shadows

**The 5 Planes:**
1. **Plane 0 (The Realm):** The isometric canvas displaying terrain tiles, streets, park greenfields, and road networks.
2. **Plane 1 (Architectural Structures & Beams):** 2.5D building sprites, community towers, and glowing neon trajectory lines. Active nodes emit a localized circular halo blur (`0 0 24px rgba(56, 189, 248, 0.45)`).
3. **Plane 2 (Floating Labels & Waypoints):** Crisp entity badges and relationship pills floating directly above roofs and along vector edges with subtle drops (`0 2px 4px rgba(15, 23, 42, 0.12)`).
4. **Plane 3 (HUD Panels & Chat Console):** Frosted glass panels using `backdrop-filter: blur(12px)`, `rgba(255, 255, 255, 0.88)` fill, hairline border `rgba(226, 232, 240, 0.85)`, and soft ambient shadow (`0 8px 30px -4px rgba(15, 23, 42, 0.08)`).
5. **Plane 4 (Drawers & Modal Overlays):** Grounded contextual drawers featuring crisp edge separation with deeper elevation shadows (`-4px 0 24px rgba(15, 23, 42, 0.08)`).

**Game Shadows (CSS Custom Values):**
- `shadow-game-sm`: `0 4px 0 rgba(0,0,0,0.06), 0 8px 16px -4px rgba(0,0,0,0.04)`
- `shadow-game`: `0 6px 0 rgba(0,0,0,0.06), 0 12px 24px -4px rgba(0,0,0,0.06)`
- `shadow-game-btn`: `0 4px 0 #004d46`
- `shadow-game-amber`: `0 4px 0 #B45309`
- `shadow-game-purple`: `0 4px 0 #6D28D9`

---

## 3. Page Specifications

### 3.1 Page 1: Home / Dashboard ('Research Realm')

**Layout:** Max-width container, sticky top HUD header, main content area with two-section grid.

**Components:**

#### 3.1.1 Top HUD Header
- **Brand badge:** Castle icon, 'Research Realm' title, 'Cozy Builder' tag.
- **World indicator:** 'Citation Archipelago' with live pulse dot (`animate-ping`).
- **Center (Active Quest):** Amber card with quest step progress ('Active Quest').
- **Right (Gamified Resources):**
  - Sparks gem badge (💎 count)
  - Energy badge (⚡ with fraction)
  - Player profile card: avatar with level badge, name, verified icon, XP progress bar

#### 3.1.2 Summon Portal (Upload Card)
- **Container:** Left column (`lg:col-span-5`), `shadow-game`, decorative background glows.
- **Header:** 'Town Altar' badge, heading 'Summon a New Knowledge Town ✨'.
- **Dropzone:** Dashed border, floating upload icon (`animate-float`), text prompts.
- **Button:** 'Browse Scrolls' with `shadow-game-btn`.
- **Quick Teleport:** arXiv input with link icon, 'Build ⚡' button with `shadow-game-amber`.

#### 3.1.3 Construction Pipeline (Active Build Card)
- **Container:** Right column (`lg:col-span-7`), `shadow-game`.
- **Header:** Live indicator dot + 'Active Town Construction' label + percentage badge.
- **Current project:** Name, domain, author, and emoji avatar (e.g., 🏰).
- **Master progress bar:** Gradient fill with pulse indicator at the leading edge.
- **3-step quest cards (Grid):**
  - **Step 1 (Deconstruct Paper):** Completed state (green check, emerald theme).
  - **Step 2 (Build Entity Towers):** Active state (blue/sky theme, `animate-bounce` icon, ring highlight).
  - **Step 3 (Light Up Roads):** Upcoming state (gray theme, dashed border, reduced opacity).
- **Footer:** Wizard emoji + status text + 'Watch Live Build' link with chevron.

#### 3.1.4 Knowledge Realms Section
- **Header:** Section title, count badge, description text.
- **Filter chips:** 'All Realms' (active, emerald), 'NLP', 'Vision', 'Systems'.
- **Grid:** 4-column realm card grid.

#### 3.1.5 Realm Card
- **Structure:**
  - **Top badges:** Category tag + emoji.
  - **Visual badge area:** Gradient background, center emoji, JetBrains Mono town name, level badge. Group hover effects transition the gradient.
  - **Paper title:** Extrabold, hover color transition to primary color. Author line below.
  - **Stats ribbon:** 3-col grid (Districts, Towers, Scholars) with monospace numbers.
  - **Button:** 'Enter Realm' with game shadow and play arrow icon.
- **Under Construction Variant:** Amber theme, 🚧 icon (`animate-bounce`), 'Constructing' badge with pulsing dot, disabled 'Finishing Spire...' button with spinning sync icon.

### 3.2 Page 2: Town Explorer ('Citation City')

**Layout:** Full-viewport SVG canvas as backdrop, fixed floating HUD panels on all sides. Pointer events are handled carefully so the canvas can be dragged while HUDs remain interactive.

**Components:**

#### 3.2.1 Top Navigation HUD
- **Left (Player Profile):** Glassmorphic card, pointer-events-auto, avatar with level, name, XP bar.
- **Center (Realm Badge & Filters):** Realm badge (e.g., Transformer Citadel) + tower filter pills (All Towers, Concepts, Scholars, Arenas with count badges).
- **Right (Controls):** Recenter, Zoom In, Zoom Out icon buttons + 'Daily Quest' gradient button.

#### 3.2.2 Isometric Town Canvas (SVG)
- **Viewport:** Full viewport SVG with 1920x1280 viewbox, draggable/zoomable.
- **Background:** Grass gradient (`grassGrad`).
- **Districts:** Colored polygons with text labels floating in the ground.
- **Road System:** Gray stroke underlays → white surface → neon energy stream overlays with stroke-dasharray animation (`particle-run`).
- **Foliage:** Decorative green circle clusters for trees.
- **Floating Mascot:** Cute blue circle drone with eyes and propeller (`animate-float`).

#### 3.2.3 Tower Buildings
- **Multi-Head Attention Spire (Concept):** Cyan crystal with stepped 3D body, floating gem with glow filter, light beam shooting upward, pulsing base rings.
- **Vaswani Research Lodge (Person):** Purple lodge with steeple roof, arch door, flag on pole.
- **Scaled Dot-Product Arena (Location):** Amber/gold tiered base with dome, glow filter.
- **Q,K,V Subspace Pylons (Concept):** Three floating colored crystal pylons (pink, teal, amber).
- **Google Brain Lab (Org):** Blue modern building with solar roof panel.
- **Common Features:** Ground shadow ellipse, hover scale transition on floating tag. Click handler to select. Floating game tag (dark rounded rect with colored dot, name, and level badge).

#### 3.2.4 Building Info Card (Right Sidebar)
- **Position:** Fixed top-right.
- **Styling:** Glassmorphic (`bg-white/95`, `backdrop-blur-xl`), `shadow-[0_12px_40px_rgba(0,0,0,0.12)]`.
- **Header:** Close button, Icon, type badge, title.
- **Stats:** 3-col grid: Level, Mentions, Roads in big fun numbers.
- **Description:** Slate-50 background text block.
- **Actions:** 'Study Connections' (gradient teal) + Bookmark icon button.
- **Animation:** Slide-out/in via `translate-x-96` and `opacity-0` toggle.

#### 3.2.5 Quest Dialogue Box (Bottom-Left)
- **Position:** Fixed bottom-left, responsive width (full on mobile, 580px on desktop).
- **Styling:** Glassmorphic container.
- **Header:** Owl emoji avatar + 'Professor Archimedes' + 'Quest Guide' badge + paper reference. 'Inspect Quest Clue' toggle button.
- **Dialogue:** Text area for streaming text responses.
- **Clue Box:** Expandable accordion (teal background, formula display, JetBrains Mono font).
- **Input:** Search input + 'Ask 🏹' submit button (teal gradient).

### 3.3 Page 3: Login / Registration (Suggested)

- **Layout:** Clean centered card on the parchment background. Optional tiny realm preview silhouette in the background.
- **Header:** 'Enter the Research Academy' heading with castle icon.
- **Form:** Email + password fields with `rounded-xl` styling.
- **Action:** 'Begin Journey' primary button (emerald, game shadow).
- **Link:** 'New Scholar? Create Account' link.
- **Vibe:** Keep it simple — this page should not be visually heavy.

### 3.4 Page 4: Evaluation Report (Suggested)

- **Header:** '⚔️ Battle Report: GraphRAG vs Vector RAG'
- **Combatant Cards:** Two cards side-by-side (teal for GraphRAG, slate for Vector RAG) showing aggregate scores.
- **Metrics Section:**
  - Multi-hop Accuracy comparison (emerald vs slate bars/rings).
  - Single-hop Accuracy comparison.
  - Faithfulness Score (circular progress rings).
  - Latency p50/p95 comparison (horizontal bars).
  - Cost per query comparison.
- **Run History:** Results table at the bottom.
- **Victory Banner:** 'GraphRAG wins on multi-hop by X%!' with confetti emoji. Use game shadow and badge styling.

---

## 4. Gamification Model

| Action | XP Earned | Sparks | Notes |
|---|---|---|---|
| Upload & ingest a document | 50 XP | +10 | Quest auto-created |
| Ask a question (any mode) | 10 XP | +2 | |
| Explore a community district | 5 XP | +1 | First visit only |
| Complete an ingestion quest | 100 XP | +25 | Bonus |
| Complete a daily quest | 75 XP | +15 | |

**Level Thresholds:**
| Level | XP Required | Title |
|---|---|---|
| 1 | 0 | Apprentice Scholar |
| 2 | 100 | Research Assistant |
| 3 | 250 | Junior Fellow |
| 4 | 500 | Fellow |
| 5 | 1,000 | Senior Fellow |
| 6 | 2,000 | Distinguished Fellow |
| 7 | 3,500 | Research Director |
| 8 | 5,500 | Dean |
| 9 | 8,000 | Grand Scholar |
| 10 | 12,000 | Realm Master |

**Energy System:**
- Max 100 energy, regenerates 1 per minute.
- Each LLM query costs 5 energy (prevents API cost overruns).
- Document upload costs 20 energy.
- Shows as ⚡ badge in header.

**Quest Types:**
- **Ingestion Quest:** auto-created on upload, 3 steps (parse → extract → cluster).
- **Exploration Quest:** 'Visit 3 districts' or 'Ask 5 questions'.
- **Daily Quest:** rotated randomly ('Upload a new paper', 'Explore a community you haven't visited').

---

## 5. Responsive Behavior

| Breakpoint | Page 1 (Home) | Page 2 (Explorer) |
|---|---|---|
| Desktop (≥1280px) | Full layout, 4-col realm grid, side-by-side upload+pipeline | Full canvas, all HUDs visible simultaneously |
| Tablet (1024-1279px) | 2-col realm grid, stacked upload+pipeline | Canvas + bottom dialogue, info card as slide-over |
| Mobile (<1024px) | 1-col realm grid, stacked everything | Single mode toggle: Full Map OR Full Chat |

---

## 6. Animation & Microinteraction Catalog

| Name | CSS | Duration | Usage |
|---|---|---|---|
| `float-soft` / `floaty` | `translateY(0→-6/7px→0) rotate(0→1deg→0)` | 3.5s ease-in-out infinite | Upload icon, floating crystals, mascot drone |
| `pulse-ring` | `scale(0.9/0.95→1.05/1.15→0.9/0.95), opacity(0.8→0.3/0.4→0.8)` | 2.5s cubic-bezier | Tower base rings |
| `particle-run` (energy-stream) | `stroke-dashoffset: 60→0` | 1.4s linear infinite | Energy road particle flow |
| `animate-ping` | Tailwind built-in | - | Live dot indicators, tower base highlight |
| `animate-pulse` | Tailwind built-in | - | Progress bar glow, light beams |
| `animate-bounce` | Tailwind built-in | - | Active step icon, construction emoji |
| `animate-spin` | Tailwind built-in | - | Sync icon on constructing card |
| hover `-translate-y-1.5` | `transform: translateY(-6px)` | 300ms | Realm card lift-on-hover |
| `active:translate-y-0.5` | `transform: translateY(2px)` | instant | Button press-down feel |
| `active:scale-95` | `transform: scale(0.95)` | instant | Button press-down feel (explorer) |
| `.dimmed` | `opacity: 0.15; filter: grayscale(0.8)` | 400ms ease | Non-relevant town buildings |
| `.highlighted` | `opacity: 1; filter: drop-shadow(...)` | 400ms ease | Query-relevant town buildings |

---

## 7. Component Library

### 7.1 GameBadge
- **Style:** Pill-shaped (`rounded-full` or `rounded-xl`).
- **Variants:** filled (`bg-{color}-100`, `text-{color}-800`, `border-{color}-200`), active (`bg-{color}-600`, `text-white`), outline (`border-dashed`).
- **Optional:** leading dot indicator (animated or static), leading icon.

### 7.2 StatCounter
- **Usage:** Used in realm cards and building info cards.
- **Structure:** label (10px uppercase bold) + value (monospace bold).
- **Container:** `bg-slate-50`, `rounded-2xl`, `p-2.5`, `border slate-100`.

### 7.3 XpBar
- **Container:** Full-width progress bar (`bg-slate-100`, `h-1.5` to `h-4`, `rounded-full`).
- **Fill:** Gradient `from-{color}-400` to `to-{color}-500`, `rounded-full`.
- **Optional:** Animated pulse indicator at fill edge.

### 7.4 GameButton
- **Variants:**
  - **Primary:** `bg-emerald-600`, `shadow-game-btn (0 4px 0 #004d46)`
  - **Amber:** `bg-amber-400`, `shadow-game-amber (0 4px 0 #B45309)`
  - **Purple:** `bg-purple-600`, `shadow-game-purple (0 4px 0 #6D28D9)`
  - **Sky:** `bg-sky-600`, `shadow-[0_4px_0_#0284c7]`
  - **Gradient:** `from-teal-600` to `to-emerald-600`
- **Common Styles:** `active:translate-y-0.5`, `font-extrabold`, `text-xs`, uppercase, `tracking-wider`, `rounded-xl`.

### 7.5 GlassmorphicPanel
- **Container:**
  - `bg-white/90` to `bg-white/95`
  - `backdrop-blur-md` to `backdrop-blur-xl`
  - `rounded-2xl` to `rounded-3xl`
  - `shadow-[0_4px_20px_rgba(0,0,0,0.08)]` to `shadow-[0_12px_48px_rgba(0,0,0,0.14)]`
  - `border border-white/60` to `border-white/80`
  - `pointer-events-auto` (when floating over canvas)

### 7.6 TowerTag
- **Usage:** Floating label above SVG buildings.
- **Style:** Dark `rounded-full` rect (`bg-[#0F172A]`) or white bordered pill.
- **Content:** Contains: colored dot + game-font label + optional level badge (smaller rounded rect).
- **Animation:** Scale transition on parent group hover.
