---
name: Research Realm
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#3d4947'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#6d7a77'
  outline-variant: '#bcc9c6'
  surface-tint: '#006a61'
  primary: '#00685f'
  on-primary: '#ffffff'
  primary-container: '#008378'
  on-primary-container: '#f4fffc'
  inverse-primary: '#6bd8cb'
  secondary: '#6b38d4'
  on-secondary: '#ffffff'
  secondary-container: '#8455ef'
  on-secondary-container: '#fffbff'
  tertiary: '#825100'
  on-tertiary: '#ffffff'
  tertiary-container: '#a36700'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#89f5e7'
  primary-fixed-dim: '#6bd8cb'
  on-primary-fixed: '#00201d'
  on-primary-fixed-variant: '#005049'
  secondary-fixed: '#e9ddff'
  secondary-fixed-dim: '#d0bcff'
  on-secondary-fixed: '#23005c'
  on-secondary-fixed-variant: '#5516be'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
  district-person: '#8B5CF6'
  district-org: '#F59E0B'
  district-concept: '#10B981'
  district-location: '#EF4444'
  district-community: '#06B6D4'
  parchment-canvas: '#F4F7F4'
  road-track: '#E2E8F0'
  zone-greenfield: '#D9EDDF'
  beam-pulse: '#38BDF8'
  hud-surface: rgba(255, 255, 255, 0.88)
  hud-border: rgba(226, 232, 240, 0.85)
  hud-surface-dark: '#0F172A'
  citation-gold: '#D97706'
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

This design system reimagines complex academic synthesis and retrieval-augmented graph exploration (GraphRAG) through the metaphor of an isometric strategy simulation: "Citation City." Complex entity networks, citation multi-hop paths, and community clusters are transformed from dry topological node-link diagrams into an engaging, explorable landscape of architectural districts, research towers, knowledge plazas, and radiant transit pathways.

### Brand Personality & Emotional Impact
- **Playfully Rigorous:** Academic depth disguised in crisp gamified clarity. Users feel like city planners charting discoveries across multi-disciplinary territories rather than analysts wading through dense graph indexes.
- **Luminous Transparency:** Every multi-hop retrieval trajectory and extracted citation chunk is visually traceable through vibrant, high-luminance light pulses and trajectory beams.
- **Tactile Precision:** Combining crisp, structural developer-grade typography with soft parchment-hued cartographic bases and floating frosted HUD viewports.

### Design Movement
The design movement is **Gamified Technical Glassmorphism with Isometric Cartography**. It merges the clean lines and modular grids of developer tooling with the delightful spatial geography of isometric simulation games (SimCity, Pokémon GO, and strategic tower defenses). Floating head-up displays (HUDs), rounded status badges, neon-lit trajectory vectors, and parchment-grounded map tiles maintain high functional density without sacrificing joy.

## Colors

The color architecture bridges soft environmental cartography with vibrant, semantic district taxonomy. 

### Environmental Palette
- **Parchment Base & Greenfield (`#F4F7F4`, `#D9EDDF`):** Creates an inviting, low-fatigue map surface reminiscent of classic world-builder games and tactical cartography.
- **Road & District Grid (`#E2E8F0`):** Soft, neutral structural lanes that guide visual paths without competing with active node links.

### Entity & District Coding
- **Person / Author (`district-person` / `#8B5CF6`):** Royal Lilac, representing agency, scholarly authorship, and researcher profiles.
- **Org / Institution (`district-org` / `#F59E0B`):** Warm Amber, designating universities, labs, funding agencies, and editorial bodies.
- **Concept / Topic (`district-concept` / `#10B981`):** Emerald Green, symbolizing thriving core ideas, methodologies, and technical subjects.
- **Location / Dataset (`district-location` / `#EF4444`):** Coral Red, highlighting empirical corpora, geographical settings, and physical testbeds.
- **Community Hub / Cluster (`district-community` / `#06B6D4`):** Electric Cyan, indicating high-density modular clusters, thematic neighborhoods, and synthesized answer regions.

### Interactive State Highlights
- **Sub-graph Beam Trajectory (`#38BDF8`):** Radiant cyan-blue gradient with ambient outer glow, illuminating the exact traversal paths executed during a multi-hop query.
- **Dimmed State:** Unselected entities and irrelevant architectural nodes reduce to 25% opacity with desaturated neutral tones (`#94A3B8`), allowing the relevant answer subgraph to pop into the foreground.

## Typography

Typography balances rapid academic scanning with the structural precision of technical telemetry.

### Font Hierarchy
- **Primary & Interface Font (`Inter`):** Handles all application surfaces, chat conversations, panel titles, drawer metadata, and system navigation. High x-height ensures crisp legibility across variable-density isometric map viewports.
- **Technical & Gamified Monospace (`JetBrains Mono`):** Applied to relationship edge labels (e.g., `WORKS_FOR`, `LOCATED_IN`, `CITES`), community ID counters, citation references, latency telemetry, and code or raw chunk excerpts.

### Styling & Micro-copy Principles
- Entity badges on isometric buildings use uppercase monospaced labels (`label-badge`) with deliberate character tracking for rapid glanceability.
- In-chat reasoning traces render chunk IDs and multi-hop hops as monospaced inline chips that link bidirectionally to nodes in the viewport.

## Layout & Spacing

The layout is built around a full-canvas spatial viewport bordered by floating HUD (Heads-Up Display) modules and dockable drawers.

### Split-Screen & Viewport Anatomy
1. **Full-Bleed Map Canvas:** Serves as the continuous interactive backdrop spanning 100% of the viewport.
2. **Floating HUD Controls:** Anchored with `1rem` margins to the viewport corners:
   - **Top Bar:** Navigation pills, query search bar, mode toggles (`3D Rotate`, `View Community Districts`), and ingestion upload triggers.
   - **Bottom-Left Chat HUD:** Suspended floating conversational panel (`380px` to `440px` width) with internal scrolling and prompt dock.
   - **Right Side Dock / Drawer:** Collapsible contextual inspector (`340px` width) showcasing building details, community district tree lists, and raw source chunks.
3. **Responsive Adaptation:**
   - **Desktop (>1280px):** Simultaneous open state for the floating Chat HUD, map canvas, and Entity Drawer without canvas occlusion.
   - **Tablet / Small Desktop (1024px–1279px):** Entity Drawer automatically docks as a slide-out overlay; Chat HUD scales to `340px`.
   - **Mobile (<1024px):** Single active mode (Full Map or Full Chat), toggled via an anchored bottom navigation bar.

## Elevation & Depth

Visual depth establishes a clear cognitive separation between the underlying cartographic game plane and the analytic tooling floating above it.

### Elevation Layers
- **Plane 0 (The Realm):** The isometric canvas displaying terrain tiles, streets, park greenfields, and road networks.
- **Plane 1 (Architectural Structures & Beams):** 2.5D building sprites, community towers, and glowing neon trajectory lines. Active nodes emit a localized circular halo blur (`0 0 24px rgba(56, 189, 248, 0.45)`).
- **Plane 2 (Floating Labels & Waypoints):** Crisp entity badges and relationship pills floating directly above roofs and along vector edges with subtle drops (`0 2px 4px rgba(15, 23, 42, 0.12)`).
- **Plane 3 (HUD Panels & Chat Console):** Frosted glass panels using `backdrop-filter: blur(12px)`, `rgba(255, 255, 255, 0.88)` fill, hairline border `rgba(226, 232, 240, 0.85)`, and soft ambient shadow (`0 8px 30px -4px rgba(15, 23, 42, 0.08)`).
- **Plane 4 (Drawers & Modal Overlays):** Grounded contextual drawers featuring crisp edge separation with deeper elevation shadows (`-4px 0 24px rgba(15, 23, 42, 0.08)`).

## Shapes

The design system uses a friendly, ergonomic rounded aesthetic that matches playful isometric video games while retaining software utility.

### Geometry Specifications
- **HUD Panels & Cards:** Medium rounded corners (`12px` to `16px`) creating soft pebble-like consoles floating on the canvas.
- **Entity Tags & Road Badges:** Pill-shaped (`9999px`) badges for entity labels, community clusters, and traversal edge tags, preventing sharp corner collision on busy maps.
- **Buttons & Input Elements:** `8px` corner radius for structured, tactile form controls.
- **Miniature Node Bases:** Isometric octagons and rounded diamond plinths supporting each building asset, grounding the structure onto the terrain grid.

## Components

### 1. Isometric Node Buildings & Towers
- **Visual Structure:** 2.5D miniature architectural models styled per entity type:
  - *Person:* Cozy Victorian townhouse or studio tower with Lilac trim.
  - *Organization:* Multi-story modern corporate headquarters with Warm Amber glazing.
  - *Concept:* Crystalline spire or obsidian obelisk with glowing Emerald energy core.
  - *Location:* Red-domed capitol or transit pavilion.
- **States:**
  - *Default:* Full color, gentle ambient shadow.
  - *Dimmed:* 25% opacity, grayscale wash.
  - *Active Query Hit:* Dynamic vertical pulse animation and neon radial beacon beam rising from the roof.

### 2. Trajectory Edge Beams
- **Visuals:** Illuminated animated energy ribbons traversing roads between buildings.
- **Tokens:** `district-community` and `beam-pulse` linear gradient with SVG dash-array marching ants during active traversal queries.
- **Metadata Badges:** Inline centered pill displaying the edge relation (`WORKS_FOR`, `MENTIONS`) in `label-code-md`.

### 3. Floating Chat HUD Panel
- **Container:** Glassmorphic card fixed at the lower left of the screen.
- **Header:** Title bar with query state indicators, clear button, and collapse trigger.
- **Message Bubbles:**
  - *User:* Soft slate background (`#F1F5F9`) with right alignment.
  - *Assistant:* Clean white card with subtle green/teal indicator avatar, streaming text updates, and interactive inline citation pills (`[Chunk #102]`, `[Davis et al.]`). Clicking an inline citation pans the isometric camera directly to that building.

### 4. Entity Detail Drawer
- **Location:** Anchored right sidebar.
- **Sections:**
  - *Building Header:* District category badge, entity name in `headline-md`, and mention frequency count.
  - *Community Summary:* Thematic overview of the cluster containing this entity.
  - *Extracted Source Chunks:* Collapsible parchment cards displaying verbatim text, highlighting retrieved entities with their corresponding district color.

### 5. District Filter Chips & Community Browser
- **Design:** Compact horizontal list or expandable tree with color-coded dot indicators.
- **Interaction:** Toggling a district chip highlights all corresponding buildings in the realm while dimming the remainder of the city. Includes numeric badges representing node cardinality.

### 6. Interactive Telemetry & Stat Counters
- **Design:** Game-styled stat trackers situated at the top HUD bar. Displays GraphRAG performance metrics:
  - *Nodes Active:* Total highlighted entities in answer.
  - *Hops Traversed:* Path depth indicator (e.g., `2-Hop Path`).
  - *Faithfulness Score:* Mini circular progress ring in Emerald green.