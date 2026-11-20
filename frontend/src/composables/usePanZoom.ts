import { ref } from 'vue'

export function usePanZoom() {
  const translateX = ref(-180)
  const translateY = ref(-160)
  const scale = ref(1)

  const isDragging = ref(false)
  let startX = 0
  let startY = 0

  function onMouseDown(e: MouseEvent) {
    // Prevent panning when clicking buttons, inputs, or HUD cards
    if ((e.target as HTMLElement).closest('button, input, [data-no-pan], .glass-panel, .hud-card')) {
      return
    }

    isDragging.value = true
    startX = e.clientX - translateX.value
    startY = e.clientY - translateY.value

    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('mouseup', onMouseUp)
  }

  function onMouseMove(e: MouseEvent) {
    if (!isDragging.value) return
    translateX.value = e.clientX - startX
    translateY.value = e.clientY - startY
  }

  function onMouseUp() {
    isDragging.value = false
    window.removeEventListener('mousemove', onMouseMove)
    window.removeEventListener('mouseup', onMouseUp)
  }

  function onWheel(e: WheelEvent) {
    // Only zoom when scrolling over canvas, not over scrollable HUDs
    if ((e.target as HTMLElement).closest('.regulus-scroll, .drawer-scroll')) {
      return
    }
    e.preventDefault()
    const zoomFactor = -e.deltaY * 0.001
    const newScale = Math.max(0.4, Math.min(2.2, scale.value + zoomFactor))
    scale.value = newScale
  }

  function zoomIn() {
    scale.value = Math.min(2.2, scale.value + 0.15)
  }

  function zoomOut() {
    scale.value = Math.max(0.4, scale.value - 0.15)
  }

  function recenter() {
    translateX.value = -180
    translateY.value = -160
    scale.value = 0.85
  }

  function fitTown(buildingsList: Array<{ x: number; y: number }>) {
    if (!buildingsList || buildingsList.length === 0) {
      recenter()
      return
    }

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
    buildingsList.forEach((b) => {
      if (b.x !== undefined && b.y !== undefined) {
        minX = Math.min(minX, b.x)
        maxX = Math.max(maxX, b.x)
        minY = Math.min(minY, b.y)
        maxY = Math.max(maxY, b.y)
      }
    })

    if (!isFinite(minX) || !isFinite(maxX)) {
      recenter()
      return
    }

    const vw = typeof window !== 'undefined' ? window.innerWidth : 1200
    const vh = typeof window !== 'undefined' ? window.innerHeight : 800

    // Reserve comfortable margins so no buildings are occluded by top stepper or side panels
    // We reserve ~340px on the right for the topic drawer and ~80px on the left
    const availableW = Math.max(320, vw - 360)
    const availableH = Math.max(300, vh - 180)

    const townW = Math.max(200, maxX - minX + 280)
    const townH = Math.max(200, maxY - minY + 320)

    // Calculate optimal scale so that ALL buildings are 100% visible
    const fitScale = Math.min(0.88, Math.max(0.42, Math.min(availableW / townW, availableH / townH)))
    scale.value = Number(fitScale.toFixed(2))

    const centerX = (minX + maxX) / 2
    const centerY = (minY + maxY) / 2

    // Center in the visible viewport (offset slightly to the left to give comfortable breathing room from the right card)
    const viewportCenterX = (vw - 160) / 2
    translateX.value = Math.round(viewportCenterX - centerX * scale.value)
    translateY.value = Math.round(vh / 2 - centerY * scale.value + 40)
  }

  function focusOn(targetX: number, targetY: number, targetScale = 1.15) {
    scale.value = targetScale
    const vw = typeof window !== 'undefined' ? window.innerWidth : 1200
    const vh = typeof window !== 'undefined' ? window.innerHeight : 800
    // Center (targetX, targetY) inside the viewport with comfortable padding
    translateX.value = Math.round(vw / 2 - targetX * targetScale)
    translateY.value = Math.round(vh / 2 - targetY * targetScale + 40)
  }

  return {
    translateX,
    translateY,
    scale,
    isDragging,
    onMouseDown,
    onWheel,
    zoomIn,
    zoomOut,
    recenter,
    fitTown,
    focusOn,
  }
}

