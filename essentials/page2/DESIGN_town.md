---
name: Untangle
colors:
  surface: '#F7F6F3'
  surface-low: '#EFEFED'
  surface-mid: '#E8E7E3'
  surface-high: '#DEDDD8'
  canvas-bg: '#EEF0EB'
  zone-greenfield: '#DFE8DA'
  road-track: '#D8D6CF'
  border-default: '#D4D3CE'
  border-muted: '#E4E3DF'
  primary: '#3D6B5A'
  primary-dark: '#2C5043'
  primary-light: '#E8F0EC'
  accent-amber: '#B8924A'
  accent-amber-dark: '#8C6A2C'
  accent-amber-light: '#F5EFE3'
  node-person: '#7C6FA0'
  node-org: '#C49A3C'
  node-concept: '#4E9A7D'
  node-location: '#A85A5A'
  node-community: '#4E8FA8'
  node-chapter: '#7A8C6A'
  node-section: '#B8A87A'
  beam-pulse: '#6BA3BE'
  source-link: '#B8A87A'
  text-primary: '#1C1B18'
  text-secondary: '#5C5A54'
  text-muted: '#8A877F'
  hud-surface: 'rgba(247, 246, 243, 0.92)'
  hud-border: 'rgba(212, 211, 206, 0.80)'
  hud-surface-dark: '#1C1B18'
typography:
  display-hero:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '800'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 22px
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-code-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: -0.01em
  label-code-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
  label-badge:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-lg: 1.5rem
  margin: 1rem
  margin-desktop: 1.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
  space-2xl: 2rem
---

## Brand & Style

This design system reimagines complex academic synthesis and retrieval-augmented graph exploration (GraphRAG) through the metaphor of an isometric strategy simulation: "Untangle knowledge map." Complex entity networks, citation multi-hop paths, and community clusters are transformed from dry topological node-link diagrams into an engaging, explorable landscape of architectural districts, research towers, knowledge plazas, and radiant transit pathways.

### Brand Personality & Emotional Impact
- **Playfully Rigorous:** Academic depth disguised in crisp clarity. Users feel like city planners charting discoveries across multi-disciplinary territories rather than analysts wading through dense graph indexes.
- **Luminous Transparency:** Every multi-hop retrieval trajectory and extracted citation chunk is visually traceable through vibrant, high-luminance light pulses and trajectory beams.
- **Tactile Precision:** Combining crisp, structural developer-grade typography with soft parchment-hued cartographic bases and floating frosted HUD viewports.

### Design Movement
The design movement is **Technical Glassmorphism with Isometric Cartography**. It merges the clean lines and modular grids of developer tooling with the delightful spatial geography of isometric simulation. Floating head-up displays (HUDs), rounded status badges, neon-lit trajectory vectors, and parchment-grounded map tiles maintain high functional density without sacrificing joy.

## Colors

The color architecture bridges soft environmental cartography with vibrant, semantic district taxonomy. 

### Environmental Palette
- **Parchment Base & Greenfield (`#F4F7F4`, `#D9EDDF`):** Creates an inviting, low-fatigue map surface reminiscent of classic world-builder games and tactical cartography.
- **Road & District Grid (`#E2E8F0`):** Soft, neutral structural lanes that guide visual paths without competing with active node links.

### Entity & District Coding
- **Person / Author (`district-person` / `#7C6FA0`):** Dusty lavender, representing agency, scholarly authorship, and researcher profiles.
- **Org / Institution (`district-org` / `#C49A3C`):** Warm ochre, designating universities, labs, funding agencies, and editorial bodies.
- **Concept / Topic (`district-concept` / `#4E9A7D`):** Muted jade, symbolizing thriving core ideas, methodologies, and technical subjects.
- **Location / Dataset (`district-location` / `#A85A5A`):** Dusty rose-red, highlighting empirical corpora, geographical settings, and physical testbeds.
- **Community Hub / Cluster (`district-community` / `#4E8FA8`):** Dusty slate-blue, indicating high-density modular clusters, thematic neighborhoods, and synthesized answer regions.

### Interactive State Highlights
- **Sub-graph Beam Trajectory (`#6BA3BE`):** Soft steel blue gradient with ambient outer glow, illuminating the exact traversal paths executed during a multi-hop query.
- **Dimmed State:** Unselected entities and irrelevant architectural nodes reduce to 25% opacity with desaturated neutral tones (`#94A3B8`), allowing the relevant answer subgraph to pop into the foreground.

## Typography

Typography balances rapid academic scanning with the structural precision of technical telemetry.

### Font Hierarchy
- **Primary & Interface Font (`Inter`):** Handles all application surfaces, chat conversations, panel titles, drawer metadata, and system navigation. High x-height ensures crisp legibility across variable-density isometric map viewports.
- **Technical Monospace (`JetBrains Mono`):** Applied to relationship edge labels (e.g., `WORKS_FOR`, `LOCATED_IN`, `CITES`), community ID counters, citation references, latency telemetry, and code or raw chunk excerpts.

### Styling & Micro-copy Principles
- Entity badges on isometric buildings use uppercase monospaced labels (`label-badge`) with deliberate character tracking for rapid glanceability.
- In-chat reasoning traces render chunk IDs and multi-hop hops as monospaced inline chips that link bidirectionally to nodes in the viewport.

## Layout & Spacing

The layout is built around a full-canvas spatial viewport bordered by floating HUD (Heads-Up Display) modules and dockable drawers.

### Split-Screen & Viewport Anatomy
1. **Full-Bleed Map Canvas:** Serves as the continuous interactive backdrop spanning 100% of the viewport.
2. **Floating HUD Controls:** Anchored with `1rem` margins to the viewport corners:
   - **Top Bar:** Navigation pills, query search bar, mode toggles (`3D Rotate`, `View Community Districts`), and ingestion upload triggers.
   - **Bottom-Left Regulus Panel:** Suspended floating conversational panel (`380px` to `440px` width) with internal scrolling and prompt dock.
   - **Right Side Dock / Drawer:** Collapsible contextual inspector (`340px` width) showcasing building details, community district tree lists, and raw source chunks.
3. **Responsive Adaptation:**
   - **Desktop (>1280px):** Simultaneous open state for the floating Regulus Panel, map canvas, and Entity Drawer without canvas occlusion.
   - **Tablet / Small Desktop (1024px–1279px):** Entity Drawer automatically docks as a slide-out overlay; Regulus Panel scales to `340px`.
   - **Mobile (<1024px):** Single active mode (Full Map or Full Chat), toggled via an anchored bottom navigation bar.

## Elevation & Depth

Visual depth establishes a clear cognitive separation between the underlying cartographic plane and the analytic tooling floating above it.

### Elevation Layers
- **Plane 0 (The map):** The isometric canvas displaying terrain tiles, streets, park greenfields, and road networks.
- **Plane 1 (Architectural Structures & Beams):** 2.5D building sprites, community towers, and glowing neon trajectory lines. Active nodes emit a localized circular halo blur (`0 0 16px rgba(107, 163, 190, 0.35)`).
- **Plane 2 (Floating Labels & Waypoints):** Crisp entity badges and relationship pills floating directly above roofs and along vector edges with subtle drops (`0 2px 4px rgba(15, 23, 42, 0.12)`).
- **Plane 3 (HUD Panels & Chat Console):** Frosted glass panels using `backdrop-filter: blur(10px)`, `rgba(247, 246, 243, 0.92)` fill, hairline border `rgba(212, 211, 206, 0.80)`, and soft ambient shadow (`0 8px 30px -4px rgba(15, 23, 42, 0.08)`).
- **Plane 4 (Drawers & Modal Overlays):** Grounded contextual drawers featuring crisp edge separation with deeper elevation shadows (`-4px 0 24px rgba(15, 23, 42, 0.08)`).

## Shapes

The design system uses a friendly, ergonomic rounded aesthetic that matches playful isometric views while retaining software utility.

### Geometry Specifications
- **HUD Panels & Cards:** Medium rounded corners (`12px` to `16px`) creating soft pebble-like consoles floating on the canvas.
- **Entity Tags & Road Badges:** Pill-shaped (`9999px`) badges for entity labels, community clusters, and traversal edge tags, preventing sharp corner collision on busy maps.
- **Buttons & Input Elements:** `8px` corner radius for structured, tactile form controls.
- **Miniature Node Bases:** Isometric octagons and rounded diamond plinths supporting each building asset, grounding the structure onto the terrain grid.

## Components

### Canvas Semantics — Dual Mode
The canvas seamlessly adapts its semantic mapping based on the active mode while maintaining the same underlying spatial architecture:

| Visual Element | Research Mode | Study Mode |
|---|---|---|
| District (colored polygon) | Community cluster | Chapter |
| Large tower | High-mention entity | Section / Major topic |
| Small tower | Low-mention entity | Sub-topic |
| Normal road | Relationship | Conceptual link |
| Highlighted road (glowing) | Retrieved traversal path | Exam-relevant concept path |
| Dashed road | Cross-paper citation link | Cross-book context link |
| District label | Community name | Chapter title |
| Tower label | Entity name | Section / Topic name |

### 1. Isometric Node Buildings & Towers (High-Fidelity 2.5D, No Flags)
- **Visual Structure:** High-fidelity 2.5D miniature architectural models styled per entity type (inspired by the Page 2 prototype):
  - *Concept / Spire (e.g. Multi-Head Attention):* 3D stepped faceted crystal body, floating central gem with soft glow filter (`filter="url(#softGlow)"`), pulsing ground ring plinth, and upward sky light beam (`animate-pulse`).
  - *Person / Author (e.g. Vaswani Lodge):* Cozy Victorian academic lodge with shaded isometric wall polygons, steepled roof, and warm arch entry door. (Architectural finial at apex, strictly **NO flags**).
  - *Location / Arena (e.g. Scaled Dot-Product Arena):* Multi-tiered isometric base plinth supporting a gleaming golden training dome (`path d="M 915,595 Q 960,500 1005,595 Z"`).
  - *Chapter / Citadel (Study Mode):* Grand multi-tiered academic citadel with fortress towers and wide base.
  - *Section / Modern Lab Block (Study Mode & Orgs):* Layered tech block with solar/glass panels and beveled corners.
- **States:**
  - *Default:* Full color, gentle ground shadow ellipse (`fill="#1C1B18" fill-opacity="0.14"`).
  - *Dimmed:* 18% opacity, grayscale wash (0.75).
  - *Active Query Hit:* Radial drop shadow (`0 0 14px rgba(107, 163, 190, 0.40)`).
  - *Learning Path Step Badge:* Floating step pill (e.g. `① Step 1`) indicating recommended curriculum order.

### 2. Trajectory Edge Beams
- **Visuals:** High-fidelity triple-layered roads:
  - Wide underlay track (`stroke="#D8D6CF" stroke-width="28"`).
  - Pastel white surface lane (`stroke="#FFFFFF" stroke-width="18"`).
  - Animated particle streams (`stroke-dasharray`):
    - Normal relations: Soft steel blue (`#6BA3BE`).
    - Cross-source links: Dashed warm tan (`#B8A87A`).
- **Metadata Badges:** Inline centered pill displaying the edge relation in `label-code-md`.

### 3. Learning Path Stepper & Curriculum Trail
- **Trail:** Illuminated dashed guide line linking Step 1 → Step 2 → Step 3 in topological dependency sequence.
- **HUD Stepper:** Floating control bar providing next/prev navigation (`[◀ Prev] Step X of N: Concept [Next ▶]`).
- Auto-selects and centers the active concept, spotlighting its position in the curriculum.

### 4. Deep Topic Reader Dossier
- Accessible from the building detail card via **"📖 Read Full Topic Dossier"**.
- Opens a dedicated full-reader drawer providing:
  - Executive concept synthesis.
  - Extracted mathematical formulas and code blocks.
  - Verbatim raw source chunks from the document with section citations.
  - Prerequisite and next-step links along the learning path.

### 3. Regulus Panel
- **Container:** Glassmorphic card fixed at the lower left of the screen.
- **Header:** Title bar with query state indicators, clear button, and collapse trigger.
- **Behavior:** Mode-aware AI guide (Regulus):
  - *Research Mode:* Focuses on citation-focused answers. Shows citation pills linking to source chunks.
  - *Study Mode:* Focuses on concept explanation and outside source suggestions. Shows concept breadcrumbs (chapter → section → topic path), and when Regulus detects outside-context needs, shows a source suggestion card with "Import source →" action.

### 4. Entity Detail Drawer
- **Location:** Anchored right sidebar.
- **Sections:**
  - *Building Header:* District category badge, entity name in `headline-md`, and mention frequency count.
  - *Community Summary:* Thematic overview of the cluster containing this entity.
  - *Extracted Source Chunks:* Collapsible parchment cards displaying verbatim text, highlighting retrieved entities with their corresponding district color.

### 5. District Filter Chips & Community Browser
- **Design:** Compact horizontal list or expandable tree with color-coded dot indicators.
- **Interaction:** Toggling a district chip highlights all corresponding buildings in the knowledge map while dimming the remainder of the city. Includes numeric badges representing node cardinality.

### 6. Interactive Telemetry & Counters
- **Design:** Telemetry stat trackers situated at the top HUD bar. Displays GraphRAG performance metrics:
  - *Nodes Active:* Total highlighted entities in answer.
  - *Hops Traversed:* Path depth indicator (e.g., `2-Hop Path`).
  - *Faithfulness Score:* Mini circular progress ring in Emerald green.