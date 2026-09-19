import { ref } from 'vue'

export function usePanZoom() {
  const translateX = ref(-180)
  const translateY = ref(-160)
  const scale = ref(1)

  let isDragging = false
  let startX = 0
  let startY = 0

  function onMouseDown(e: MouseEvent) {
    // Prevent panning when clicking buttons, inputs, or HUD cards
    if ((e.target as HTMLElement).closest('button, input, [data-no-pan], .glass-panel, .hud-card')) {
      return
    }

    isDragging = true
    startX = e.clientX - translateX.value
    startY = e.clientY - translateY.value

    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('mouseup', onMouseUp)
  }

  function onMouseMove(e: MouseEvent) {
    if (!isDragging) return
    translateX.value = e.clientX - startX
    translateY.value = e.clientY - startY
  }

  function onMouseUp() {
    isDragging = false
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
    scale.value = 1
  }

  return {
    translateX,
    translateY,
    scale,
    onMouseDown,
    onWheel,
    zoomIn,
    zoomOut,
    recenter,
  }
}

