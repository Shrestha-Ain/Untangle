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

This design system reimagines complex academic synthesis and retrieval-augmented graph exploration (GraphRAG) through the metaphor of an isometric strategy simulation: "the Knowledge Map." Complex entity networks, citation multi-hop paths, and community clusters are transformed from dry topological node-link diagrams into an engaging, explorable landscape of architectural districts, research towers, knowledge plazas, and radiant transit pathways.

### Brand Personality & Emotional Impact
- **Structured Clarity:** Dense material made legible. Every design decision earns its place.
- **Quiet Intelligence:** The interface surfaces information when relevant, stays out of the way when not.
- **Spatial Intuition:** The isometric map works because humans navigate space naturally. This isn't decoration — it's communication.

### Design Movement
The design movement is **Lively & Tactile Academic Cartography**. Combining warm off-white neutrals with soft atmospheric glows (`blur-3xl`), tactile card borders (`border-2 border-[#D4D3CE]`), animated micro-interactions (soft icon floating, live pulse status indicators), and interactive preview ribbons. This keeps the dashboard smooth, engaging, and lively without visual clutter.

## Colors

The color architecture bridges soft environmental cartography with vibrant, semantic district taxonomy. 

### Environmental Palette
- **Parchment Base & Greenfield (`#EEF0EB`, `#DFE8DA`):** Creates an inviting, low-fatigue map surface reminiscent of classic world-builder games and tactical cartography.
- **Road & District Grid (`#D8D6CF`):** Soft, neutral structural lanes that guide visual paths without competing with active node links.

### Entity & District Coding
- **Person / Author (`node-person` / `#7C6FA0`):** Dusty lavender, representing agency, scholarly authorship, and researcher profiles.
- **Org / Institution (`node-org` / `#C49A3C`):** Warm ochre, designating universities, labs, funding agencies, and editorial bodies.
- **Concept / Topic (`node-concept` / `#4E9A7D`):** Muted jade, symbolizing thriving core ideas, methodologies, and technical subjects.
- **Location / Dataset (`node-location` / `#A85A5A`):** Dusty rose-red, highlighting empirical corpora, geographical settings, and physical testbeds.
- **Community Hub / Cluster (`node-community` / `#4E8FA8`):** Dusty slate-blue, indicating high-density modular clusters, thematic neighborhoods, and synthesized answer regions.
- **Chapter (`node-chapter` / `#7A8C6A`):** Olive sage, structuring major divisions in Study Mode.
- **Section (`node-section` / `#B8A87A`):** Warm tan, representing detailed sub-topics in Study Mode.

### Interactive State Highlights
- **Sub-graph Beam Trajectory (`#6BA3BE`):** Soft steel blue gradient with ambient outer glow, illuminating the exact traversal paths executed during a multi-hop query.
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
- **Plane 1 (Architectural Structures & Beams):** 2.5D building sprites, community towers, and glowing neon trajectory lines. Active nodes emit a localized circular halo blur (`0 0 16px rgba(107, 163, 190, 0.35)`).
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
  - *Person:* Cozy Victorian townhouse or studio tower with dusty lavender trim.
  - *Organization:* Multi-story modern corporate headquarters with warm ochre glazing.
  - *Concept:* Crystalline spire or obsidian obelisk with muted jade energy core.
  - *Location:* Red-domed capitol or transit pavilion with dusty rose-red accents.
  - *Chapter:* Large district polygon, olive sage (`#7A8C6A`) (Study Mode).
  - *Section:* Medium tower, warm tan (`#B8A87A`) (Study Mode).
  - *Sub-topic:* Small tower adjacent to parent (Study Mode).
- **States:**
  - *Default:* Full color, gentle ambient shadow.
  - *Dimmed:* 25% opacity, grayscale wash.
  - *Active Query Hit:* Dynamic vertical pulse animation and neon radial beacon beam rising from the roof.

### 2. Trajectory Edge Beams
- **Visuals:** Illuminated animated energy ribbons traversing roads between buildings.
- **Tokens:** `district-community` and `beam-pulse` linear gradient with SVG dash-array marching ants during active traversal queries.
- **Metadata Badges:** Inline centered pill displaying the edge relation (`WORKS_FOR`, `MENTIONS`) in `label-code-md`.

### 3. Regulus Panel
- **Container:** Glassmorphic card fixed at the lower left of the screen.
- **Header:** Title bar referencing "Regulus" with query state indicators, clear button, and collapse trigger.
- **Message Bubbles:**
  - *User:* Soft slate background (`#F1F5F9`) with right alignment.
  - *Assistant:* Clean white card with subtle green/teal indicator avatar. Streaming text updates are mode-aware: Research Mode shows citation pills; Study Mode shows concept breadcrumbs and outside source suggestion cards. Clicking an inline citation pans the isometric camera directly to that building.

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
- **Design:** Metric trackers situated at the top HUD bar. Displays GraphRAG performance metrics:
  - *Nodes Active:* Total highlighted entities in answer.
  - *Hops Traversed:* Path depth indicator (e.g., `2-Hop Path`).
  - *Faithfulness Score:* Mini circular progress ring in muted jade.

### 7. Mode Badge
- **Design:** Pill-shaped JetBrains Mono badge indicating Research or Study mode.
- **Variants:** 
  - *Research Mode:* Muted jade background.
  - *Study Mode:* Warm ochre background.