/** @type {import('tailwindcss').Config} */
export default {
  // "content" tells Tailwind which files to scan for class names.
  // In production, it strips out any class that doesn't appear here → tiny CSS bundle.
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],

  theme: {
    extend: {
      // ─── COLORS ────────────────────────────────────────────────────────────
      // All tokens from frontend_design_spec.md §2.1
      colors: {
        // Primary brand (teal/emerald)
        primary:            "#00685f",
        "primary-container":"#008378",

        // Map canvas & surface
        surface:            "#F4F7F4",   // parchment base
        "zone-greenfield":  "#D9EDDF",   // park zones
        "road-track":       "#E2E8F0",   // road lanes

        // Entity District colors — each entity type gets its own hue
        // PERSON → Royal Lilac
        "district-person":    "#8B5CF6",
        // ORGANIZATION → Warm Amber
        "district-org":       "#F59E0B",
        // CONCEPT/TOPIC → Emerald Green
        "district-concept":   "#10B981",
        // LOCATION/DATASET → Coral Red
        "district-location":  "#EF4444",
        // COMMUNITY CLUSTER → Electric Cyan
        "district-community": "#06B6D4",

        // Interactive states
        "beam-pulse":   "#38BDF8",   // active traversal path glow
        "citation-gold":"#D97706",   // citation references
      },

      // ─── FONTS ─────────────────────────────────────────────────────────────
      // Three-font system from the design spec:
      // 1. Inter      → all UI surfaces, chat, navigation
      // 2. Fredoka    → game headings on the Town Explorer page (playful, rounded)
      // 3. JetBrains Mono → edge labels, chunk IDs, latency telemetry, code
      fontFamily: {
        body: ["Inter", "sans-serif"],
        game: ["Fredoka", "Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },

      // ─── BOX SHADOWS ───────────────────────────────────────────────────────
      // "Game shadows" — a bottom-heavy dark offset gives buttons a 3D press feel.
      // The card shadows use a subtle spread for floaty glassmorphic panels.
      boxShadow: {
        // Cards & panels
        "game-sm":  "0 4px 0 rgba(0,0,0,0.06), 0 8px 16px -4px rgba(0,0,0,0.04)",
        "game":     "0 6px 0 rgba(0,0,0,0.06), 0 12px 24px -4px rgba(0,0,0,0.06)",
        // Buttons — solid bottom offset by accent color, creates a "physical" press depth
        "game-btn":   "0 4px 0 #004d46",   // primary teal button depth
        "game-amber": "0 4px 0 #B45309",   // amber/gold button depth
        "game-purple":"0 4px 0 #6D28D9",   // purple button depth
        "game-sky":   "0 4px 0 #0284c7",   // sky blue button depth
        // Glassmorphic HUD panels
        "hud-sm":   "0 4px 20px rgba(0,0,0,0.08)",
        "hud":      "0 12px 40px rgba(0,0,0,0.12)",
        "hud-lg":   "0 12px 48px rgba(0,0,0,0.14)",
      },

      // ─── BORDER RADIUS ─────────────────────────────────────────────────────
      // The design uses very rounded corners (cozy game aesthetic).
      // Tailwind already has 2xl/3xl but we extend for 4xl used in some panels.
      borderRadius: {
        "2xl": "1.25rem",  // 20px — HUD cards, realm cards
        "3xl": "1.75rem",  // 28px — large panels, summon portal
        "4xl": "2.25rem",  // 36px — modal overlays
      },

      // ─── KEYFRAME ANIMATIONS ───────────────────────────────────────────────
      // Custom animations from the design spec §6 Animation Catalog.
      // These go in keyframes here; then you reference them in `animation` below.
      keyframes: {
        // Gentle float — used for: upload icon, floating crystal gems, mascot drone
        "float-soft": {
          "0%, 100%": { transform: "translateY(0px) rotate(0deg)" },
          "50%":       { transform: "translateY(-6px) rotate(1deg)" },
        },
        // Tower base ring pulse — used for: active entity beacon rings
        "pulse-ring": {
          "0%":   { transform: "scale(0.95)", opacity: "0.8" },
          "50%":  { transform: "scale(1.05)", opacity: "0.4" },
          "100%": { transform: "scale(0.95)", opacity: "0.8" },
        },
        // Energy road particles — SVG stroke-dashoffset animation
        // (applied directly on SVG elements, defined here for reference)
        "particle-run": {
          "0%":   { strokeDashoffset: "60" },
          "100%": { strokeDashoffset: "0" },
        },
      },
      animation: {
        "float":      "float-soft 3.5s ease-in-out infinite",
        "float-slow": "float-soft 5s ease-in-out infinite",
        "pulse-ring": "pulse-ring 2.5s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "particle":   "particle-run 1.4s linear infinite",
      },
    },
  },

  plugins: [],
}
