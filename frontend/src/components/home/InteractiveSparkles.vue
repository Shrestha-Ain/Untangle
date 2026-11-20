<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvasRef = ref<HTMLCanvasElement | null>(null)

interface Sparkle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  maxLife: number
  life: number
  color: string
  rotation: number
  rotSpeed: number
  type: 'star' | 'diamond' | 'spark'
}

const COLORS = [
  '#3B82F6', // Royal Sapphire Blue
  '#60A5FA', // Vibrant Sky Blue
  '#38BDF8', // Electric Cyan
  '#06B6D4', // Deep Ocean Cyan
  '#818CF8', // Soft Indigo-Blue
  '#93C5FD', // Icy Frost Blue
]

let animationFrameId: number | null = null
const sparkles: Sparkle[] = []
let lastX = 0
let lastY = 0

function spawnSparkle(x: number, y: number, isBurst = false) {
  const count = isBurst ? 24 : 3
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2
    const speed = isBurst ? (2 + Math.random() * 4.5) : (0.5 + Math.random() * 2)
    const color = COLORS[Math.floor(Math.random() * COLORS.length)]
    const types: Array<'star' | 'diamond' | 'spark'> = ['star', 'diamond', 'spark']

    sparkles.push({
      x: x + (Math.random() - 0.5) * 8,
      y: y + (Math.random() - 0.5) * 8,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 0.3, // slight upward float
      size: isBurst ? (3 + Math.random() * 5) : (2 + Math.random() * 3.5),
      maxLife: isBurst ? (40 + Math.random() * 30) : (25 + Math.random() * 20),
      life: 0,
      color,
      rotation: Math.random() * Math.PI,
      rotSpeed: (Math.random() - 0.5) * 0.15,
      type: types[Math.floor(Math.random() * types.length)],
    })
  }

  // Cap max sparkles for performance
  if (sparkles.length > 300) {
    sparkles.splice(0, sparkles.length - 300)
  }
}

function onPointerMove(e: PointerEvent) {
  const dx = e.clientX - lastX
  const dy = e.clientY - lastY
  const dist = Math.sqrt(dx * dx + dy * dy)

  // Only spawn if moved sufficiently
  if (dist > 6) {
    spawnSparkle(e.clientX, e.clientY, false)
    lastX = e.clientX
    lastY = e.clientY
  }
}

function onPointerDown(e: PointerEvent) {
  spawnSparkle(e.clientX, e.clientY, true)
}

function drawStar(ctx: CanvasRenderingContext2D, cx: number, cy: number, spikes: number, outerRadius: number, innerRadius: number) {
  let rot = (Math.PI / 2) * 3
  let x = cx
  let y = cy
  const step = Math.PI / spikes

  ctx.beginPath()
  ctx.moveTo(cx, cy - outerRadius)
  for (let i = 0; i < spikes; i++) {
    x = cx + Math.cos(rot) * outerRadius
    y = cy + Math.sin(rot) * outerRadius
    ctx.lineTo(x, y)
    rot += step

    x = cx + Math.cos(rot) * innerRadius
    y = cy + Math.sin(rot) * innerRadius
    ctx.lineTo(x, y)
    rot += step
  }
  ctx.lineTo(cx, cy - outerRadius)
  ctx.closePath()
  ctx.fill()
}

function render() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  for (let i = sparkles.length - 1; i >= 0; i--) {
    const s = sparkles[i]
    s.life++
    s.x += s.vx
    s.y += s.vy
    s.rotation += s.rotSpeed
    s.vx *= 0.96
    s.vy *= 0.96

    const progress = s.life / s.maxLife
    if (progress >= 1) {
      sparkles.splice(i, 1)
      continue
    }

    const alpha = Math.max(0, 1 - progress)
    ctx.save()
    ctx.globalAlpha = alpha
    ctx.fillStyle = s.color
    ctx.translate(s.x, s.y)
    ctx.rotate(s.rotation)

    if (s.type === 'star') {
      drawStar(ctx, 0, 0, 4, s.size * 1.5, s.size * 0.4)
    } else if (s.type === 'diamond') {
      ctx.beginPath()
      ctx.moveTo(0, -s.size * 1.2)
      ctx.lineTo(s.size * 0.8, 0)
      ctx.lineTo(0, s.size * 1.2)
      ctx.lineTo(-s.size * 0.8, 0)
      ctx.closePath()
      ctx.fill()
    } else {
      ctx.beginPath()
      ctx.arc(0, 0, s.size * 0.8, 0, Math.PI * 2)
      ctx.fill()
    }

    ctx.restore()
  }

  animationFrameId = requestAnimationFrame(render)
}

function resizeCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
}

onMounted(() => {
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)
  window.addEventListener('pointermove', onPointerMove, { passive: true })
  window.addEventListener('pointerdown', onPointerDown, { passive: true })
  animationFrameId = requestAnimationFrame(render)
})

onBeforeUnmount(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  window.removeEventListener('resize', resizeCanvas)
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('pointerdown', onPointerDown)
})
</script>

<template>
  <canvas
    ref="canvasRef"
    class="fixed inset-0 pointer-events-none z-30"
  ></canvas>
</template>
