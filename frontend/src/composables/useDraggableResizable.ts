import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

export type Placement = 'top-center' | 'bottom-left' | 'top-right' | 'top-left' | 'custom'

export interface DraggableResizableOptions {
  initialX?: number
  initialY?: number
  initialWidth?: number
  initialHeight?: number
  minWidth?: number
  maxWidth?: number
  minHeight?: number
  maxHeight?: number
  defaultPlacement?: Placement
  storageKey?: string
}

export function useDraggableResizable(options: DraggableResizableOptions = {}) {
  const {
    initialWidth = 520,
    initialHeight = 480,
    minWidth = 320,
    maxWidth = 980,
    minHeight = 180,
    maxHeight = 900,
    defaultPlacement = 'bottom-left',
    storageKey,
  } = options

  const width = ref(initialWidth)
  const height = ref(initialHeight)
  const x = ref(options.initialX ?? 20)
  const y = ref(options.initialY ?? 20)

  const isDragging = ref(false)
  const isResizing = ref(false)
  const resizeDirection = ref<string | null>(null)
  const isCustomPositioned = ref(false)

  // Track initial coordinates during drag/resize gesture
  let startMouseX = 0
  let startMouseY = 0
  let startPosX = 0
  let startPosY = 0
  let startWidth = 0
  let startHeight = 0

  function computeDefaultCoords(targetPlacement: Placement = defaultPlacement): { x: number; y: number } {
    const vw = typeof window !== 'undefined' ? window.innerWidth : 1280
    const vh = typeof window !== 'undefined' ? window.innerHeight : 800

    switch (targetPlacement) {
      case 'top-center':
        return {
          x: Math.max(10, Math.round((vw - width.value) / 2)),
          y: 76,
        }
      case 'top-right':
        return {
          x: Math.max(10, Math.round(vw - width.value - 24)),
          y: 80,
        }
      case 'top-left':
        return {
          x: 24,
          y: 80,
        }
      case 'bottom-left':
      default:
        return {
          x: 24,
          y: Math.max(10, Math.round(vh - height.value - 24)),
        }
    }
  }

  function applyPlacement(placement: Placement = defaultPlacement) {
    const coords = computeDefaultCoords(placement)
    x.value = coords.x
    y.value = coords.y
    clampToScreen()
  }

  function clampToScreen() {
    if (typeof window === 'undefined') return
    const vw = window.innerWidth
    const vh = window.innerHeight

    // Ensure dialog never exceeds current viewport
    if (width.value > vw - 20) width.value = Math.max(minWidth, vw - 20)
    if (height.value > vh - 20) height.value = Math.max(minHeight, vh - 20)

    // Clamp coordinates inside screen margins
    x.value = Math.min(Math.max(8, x.value), Math.max(8, vw - width.value - 8))
    y.value = Math.min(Math.max(8, y.value), Math.max(8, vh - height.value - 8))
  }

  // --- DRAG HANDLERS ---
  function onDragStart(event: MouseEvent | TouchEvent) {
    // Ignore if clicked on an input, button, or link
    const target = event.target as HTMLElement | null
    if (
      target &&
      (target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.tagName === 'BUTTON' ||
        target.closest('button') ||
        target.closest('input') ||
        target.closest('.no-drag'))
    ) {
      return
    }

    event.preventDefault()
    isDragging.value = true
    isCustomPositioned.value = true

    const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
    const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY

    startMouseX = clientX
    startMouseY = clientY
    startPosX = x.value
    startPosY = y.value

    window.addEventListener('mousemove', onDragMove)
    window.addEventListener('mouseup', onDragEnd)
    window.addEventListener('touchmove', onDragMove, { passive: false })
    window.addEventListener('touchend', onDragEnd)
  }

  function onDragMove(event: MouseEvent | TouchEvent) {
    if (!isDragging.value) return
    if ('touches' in event) event.preventDefault()

    const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
    const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY

    const dx = clientX - startMouseX
    const dy = clientY - startMouseY

    x.value = startPosX + dx
    y.value = startPosY + dy

    clampToScreen()
  }

  function onDragEnd() {
    if (!isDragging.value) return
    isDragging.value = false
    window.removeEventListener('mousemove', onDragMove)
    window.removeEventListener('mouseup', onDragEnd)
    window.removeEventListener('touchmove', onDragMove)
    window.removeEventListener('touchend', onDragEnd)
    saveState()
  }

  // --- RESIZE HANDLERS ---
  function onResizeStart(event: MouseEvent | TouchEvent, dir: string = 'se') {
    event.preventDefault()
    event.stopPropagation()
    isResizing.value = true
    resizeDirection.value = dir
    isCustomPositioned.value = true

    const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
    const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY

    startMouseX = clientX
    startMouseY = clientY
    startWidth = width.value
    startHeight = height.value
    startPosX = x.value
    startPosY = y.value

    window.addEventListener('mousemove', onResizeMove)
    window.addEventListener('mouseup', onResizeEnd)
    window.addEventListener('touchmove', onResizeMove, { passive: false })
    window.addEventListener('touchend', onResizeEnd)
  }

  function onResizeMove(event: MouseEvent | TouchEvent) {
    if (!isResizing.value) return
    if ('touches' in event) event.preventDefault()

    const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
    const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY

    const dx = clientX - startMouseX
    const dy = clientY - startMouseY
    const dir = resizeDirection.value || 'se'

    const vw = window.innerWidth
    const vh = window.innerHeight

    // Horizontal adjustments
    if (dir.includes('e')) {
      const newW = Math.min(maxWidth, Math.max(minWidth, startWidth + dx))
      width.value = Math.min(newW, vw - x.value - 8)
    } else if (dir.includes('w')) {
      const maxLeftExpansion = startPosX + startWidth - minWidth
      const proposedX = Math.max(8, Math.min(maxLeftExpansion, startPosX + dx))
      const newW = startWidth - (proposedX - startPosX)
      if (newW >= minWidth && newW <= maxWidth) {
        x.value = proposedX
        width.value = newW
      }
    }

    // Vertical adjustments
    if (dir.includes('s')) {
      const newH = Math.min(maxHeight, Math.max(minHeight, startHeight + dy))
      height.value = Math.min(newH, vh - y.value - 8)
    } else if (dir.includes('n')) {
      const maxTopExpansion = startPosY + startHeight - minHeight
      const proposedY = Math.max(8, Math.min(maxTopExpansion, startPosY + dy))
      const newH = startHeight - (proposedY - startPosY)
      if (newH >= minHeight && newH <= maxHeight) {
        y.value = proposedY
        height.value = newH
      }
    }
  }

  function onResizeEnd() {
    if (!isResizing.value) return
    isResizing.value = false
    resizeDirection.value = null
    window.removeEventListener('mousemove', onResizeMove)
    window.removeEventListener('mouseup', onResizeEnd)
    window.removeEventListener('touchmove', onResizeMove)
    window.removeEventListener('touchend', onResizeEnd)
    saveState()
  }

  function resetPlacement() {
    width.value = initialWidth
    height.value = initialHeight
    applyPlacement(defaultPlacement)
    isCustomPositioned.value = false
    if (storageKey) {
      try {
        localStorage.removeItem(`untangle_dialog_${storageKey}`)
      } catch {}
    }
  }

  function saveState() {
    if (!storageKey) return
    try {
      localStorage.setItem(
        `untangle_dialog_${storageKey}`,
        JSON.stringify({
          x: x.value,
          y: y.value,
          width: width.value,
          height: height.value,
          isCustom: isCustomPositioned.value,
        })
      )
    } catch {}
  }

  function loadSavedState() {
    if (!storageKey) return false
    try {
      const saved = localStorage.getItem(`untangle_dialog_${storageKey}`)
      if (saved) {
        const parsed = JSON.parse(saved)
        if (parsed && typeof parsed.x === 'number' && typeof parsed.y === 'number') {
          x.value = parsed.x
          y.value = parsed.y
          if (parsed.width) width.value = Math.min(maxWidth, Math.max(minWidth, parsed.width))
          if (parsed.height) height.value = Math.min(maxHeight, Math.max(minHeight, parsed.height))
          isCustomPositioned.value = parsed.isCustom || false
          clampToScreen()
          return true
        }
      }
    } catch {}
    return false
  }

  function onWindowResize() {
    clampToScreen()
  }

  onMounted(() => {
    const loaded = loadSavedState()
    if (!loaded) {
      applyPlacement(defaultPlacement)
    }
    window.addEventListener('resize', onWindowResize)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', onWindowResize)
    window.removeEventListener('mousemove', onDragMove)
    window.removeEventListener('mouseup', onDragEnd)
    window.removeEventListener('mousemove', onResizeMove)
    window.removeEventListener('mouseup', onResizeEnd)
  })

  const style = computed(() => ({
    position: 'fixed' as const,
    left: `${x.value}px`,
    top: `${y.value}px`,
    width: `${width.value}px`,
    height: `${height.value}px`,
    zIndex: isDragging.value || isResizing.value ? 45 : 30,
  }))

  return {
    x,
    y,
    width,
    height,
    isDragging,
    isResizing,
    isCustomPositioned,
    style,
    onDragStart,
    onResizeStart,
    resetPlacement,
    clampToScreen,
  }
}
