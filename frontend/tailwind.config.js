/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],

  theme: {
    extend: {
      // ─── COLORS ──────────────────────────────────────────────────────────
      // Untangle muted palette — academic, warm, calm. No bright saturated hues.
      colors: {
        // Surfaces — warm off-white progression (like paper grades)
        surface:               '#F7F6F3',
        'surface-low':         '#EFEFED',
        'surface-mid':         '#E8E7E3',
        'surface-high':        '#DEDDD8',

        // Map canvas
        'canvas-bg':           '#EEF0EB',   // sage-parchment terrain
        'zone-greenfield':     '#DFE8DA',   // park zones on map
        'road-track':          '#D8D6CF',   // road base lanes

        // Borders
        'border-default':      '#D4D3CE',
        'border-muted':        '#E4E3DF',

        // Brand / primary (muted forest green)
        primary:               '#3D6B5A',
        'primary-dark':        '#2C5043',
        'primary-light':       '#E8F0EC',

        // Accent
        'accent-amber':        '#B8924A',
        'accent-amber-dark':   '#8C6A2C',
        'accent-amber-light':  '#F5EFE3',

        // Entity node colors — desaturated, perceptually balanced
        'node-person':         '#7C6FA0',   // dusty lavender — authors
        'node-org':            '#C49A3C',   // warm ochre — institutions
        'node-concept':        '#4E9A7D',   // muted jade — concepts/topics
        'node-location':       '#A85A5A',   // dusty rose-red — locations/datasets
        'node-community':      '#4E8FA8',   // dusty slate-blue — communities
        'node-chapter':        '#7A8C6A',   // olive sage — chapters (Study Mode)
        'node-section':        '#B8A87A',   // warm tan — sections (Study Mode)

        // Interactive canvas states
        'beam-pulse':          '#6BA3BE',   // soft steel-blue traversal glow
        'source-link':         '#B8A87A',   // dashed cross-source road color

        // Text
        'text-primary':        '#1C1B18',
        'text-secondary':      '#5C5A54',
        'text-muted':          '#8A877F',

        // Semantic states (reuse node colors for visual consistency)
        'state-success':       '#4E9A7D',
        'state-warning':       '#C49A3C',
        'state-error':         '#A85A5A',
        'state-info':          '#4E8FA8',
      },

      // ─── FONTS ───────────────────────────────────────────────────────────
      // Two-font system: Inter (all UI text) + JetBrains Mono (labels, data)
      // Fredoka removed — no game font in Untangle.
      fontFamily: {
        body: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },

      // ─── BOX SHADOWS ─────────────────────────────────────────────────────
      // Functional, calm shadows. No harsh colored offsets except btn depth.
      boxShadow: {
        'card':        '0 1px 3px rgba(28,27,24,0.08), 0 1px 2px rgba(28,27,24,0.04)',
        'card-hover':  '0 4px 12px rgba(28,27,24,0.10), 0 2px 4px rgba(28,27,24,0.05)',
        'panel':       '0 4px 20px rgba(28,27,24,0.08)',
        'panel-lg':    '0 8px 40px rgba(28,27,24,0.12)',
        // Button press depth — very subtle, just adds tactile feel
        'btn':         '0 3px 0 #2C5043',
        'btn-amber':   '0 3px 0 #8C6A2C',
        'btn-neutral': '0 3px 0 #A8A69F',
      },

      // ─── BORDER RADIUS ───────────────────────────────────────────────────
      borderRadius: {
        '2xl': '1.25rem',
        '3xl': '1.75rem',
      },

      // ─── KEYFRAMES ───────────────────────────────────────────────────────
      keyframes: {
        // Upload icon gentle float — softer and slower than before
        'float-soft': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-5px)' },
        },
        // Building base ring pulse — used for selected/highlighted node
        'pulse-ring': {
          '0%':   { transform: 'scale(0.95)', opacity: '0.7' },
          '50%':  { transform: 'scale(1.05)', opacity: '0.3' },
          '100%': { transform: 'scale(0.95)', opacity: '0.7' },
        },
        // Energy road particles (SVG animation)
        'particle-run': {
          '0%':   { strokeDashoffset: '60' },
          '100%': { strokeDashoffset: '0' },
        },
      },
      animation: {
        'float':      'float-soft 4s ease-in-out infinite',
        'pulse-ring': 'pulse-ring 2.5s ease infinite',
        'particle':   'particle-run 1.4s linear infinite',
      },
    },
  },

  plugins: [],
}
