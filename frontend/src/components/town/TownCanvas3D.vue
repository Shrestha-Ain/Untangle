<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { useGraphStore } from '@/stores/graph'
import { useThemeStore } from '@/stores/theme'

const props = withDefaults(
  defineProps<{
    activeTypeFilter?: string
    autoRotate?: boolean
    autoRotateSpeed?: number
    hideNavigationBadge?: boolean
  }>(),
  {
    activeTypeFilter: 'ALL',
    autoRotate: false,
    autoRotateSpeed: 1.2,
    hideNavigationBadge: false,
  }
)

const emit = defineEmits<{
  (e: 'buildingClick', id: string): void
}>()

const graphStore = useGraphStore()
const themeStore = useThemeStore()
const containerRef = ref<HTMLDivElement | null>(null)

// Solid Color Mapping (Strictly NO Gradients)
const TYPE_COLORS: Record<string, { main: number; light: number; dark: number; hex: string; bgClass: string; textClass: string }> = {
  CONCEPT: { main: 0x06B6D4, light: 0x22D3EE, dark: 0x0891B2, hex: '#06B6D4', bgClass: 'bg-cyan-500', textClass: 'text-cyan-950' },
  TOPIC: { main: 0x06B6D4, light: 0x22D3EE, dark: 0x0891B2, hex: '#06B6D4', bgClass: 'bg-cyan-500', textClass: 'text-cyan-950' },
  PERSON: { main: 0x8B5CF6, light: 0xA78BFA, dark: 0x7C3AED, hex: '#8B5CF6', bgClass: 'bg-purple-500', textClass: 'text-purple-950' },
  ORG: { main: 0x2563EB, light: 0x60A5FA, dark: 0x1D4ED8, hex: '#2563EB', bgClass: 'bg-blue-600', textClass: 'text-blue-950' },
  CHAPTER: { main: 0x10B981, light: 0x34D399, dark: 0x059669, hex: '#10B981', bgClass: 'bg-emerald-500', textClass: 'text-emerald-950' },
  SECTION: { main: 0xF59E0B, light: 0xFBBF24, dark: 0xD97706, hex: '#F59E0B', bgClass: 'bg-amber-500', textClass: 'text-amber-950' },
  LOCATION: { main: 0xEF4444, light: 0xF87171, dark: 0xDC2626, hex: '#EF4444', bgClass: 'bg-rose-500', textClass: 'text-rose-950' },
}

function getColor(type: string) {
  return TYPE_COLORS[type] || TYPE_COLORS.CONCEPT
}

// Three.js Core Variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let animationFrameId: number | null = null

// Scene Meshes & Lighting References
let groundMesh: THREE.Mesh | null = null
let gridMesh: THREE.GridHelper | null = null
let ambientLight: THREE.AmbientLight | null = null
let sunLight: THREE.DirectionalLight | null = null
let fillLight: THREE.DirectionalLight | null = null

const buildingMeshes = new Map<string, THREE.Group>()
const floatingEnergySlabs: Array<{ mesh: THREE.Mesh; basePosY: number; speed: number }> = []
const animatedRoadPhotons: Array<{ mesh: THREE.Mesh; curve: THREE.CatmullRomCurve3; speed: number; progress: number }> = []
let pulseRingMesh: THREE.Mesh | null = null
const roadGroup = new THREE.Group()

// Projected 2D Overlay Labels Data
interface ProjectedLabel {
  id: string
  name: string
  type: string
  stepIndex?: number
  isMain: boolean
  isSelected: boolean
  screenX: number
  screenY: number
  visible: boolean
}
const projectedLabels = ref<ProjectedLabel[]>([])

// Filtered Buildings
const buildings = computed(() => {
  const nodes = graphStore.townBuildings
  if (!props.activeTypeFilter || props.activeTypeFilter === 'ALL') {
    return nodes
  }
  return nodes.filter((b) => b.type === props.activeTypeFilter)
})

// World coordinate mapping
function to3DCoords(x: number, y: number): { x: number; z: number } {
  const centerX = 980
  const centerY = 560
  return {
    x: (x - centerX) * 0.92,
    z: (y - centerY) * 0.92,
  }
}

function initThree() {
  if (!containerRef.value) return

  const width = containerRef.value.clientWidth || window.innerWidth
  const height = containerRef.value.clientHeight || window.innerHeight

  const isDark = themeStore.isDark()

  // 1. Scene
  scene = new THREE.Scene()
  scene.background = new THREE.Color(isDark ? 0x0B1120 : 0xF0F4F8)

  // 2. Perspective Camera
  camera = new THREE.PerspectiveCamera(45, width / height, 1, 4000)
  camera.position.set(0, 520, 780)
  camera.lookAt(0, 0, 0)

  // 3. Renderer with crisp antialiasing
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  containerRef.value.appendChild(renderer.domElement)

  // 4. Orbit Controls (Freely move, rotate 360°, pan, and zoom!)
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.08
  controls.maxPolarAngle = Math.PI / 2.06
  controls.minDistance = 140
  controls.maxDistance = 2000
  controls.target.set(0, 0, 0)
  controls.autoRotate = props.autoRotate
  controls.autoRotateSpeed = props.autoRotateSpeed

  // 5. Solid Crisp Lighting
  ambientLight = new THREE.AmbientLight(0xFFFFFF, isDark ? 0.65 : 0.85)
  scene.add(ambientLight)

  sunLight = new THREE.DirectionalLight(0xFFFFFF, isDark ? 1.05 : 1.25)
  sunLight.position.set(400, 750, 400)
  sunLight.castShadow = true
  sunLight.shadow.mapSize.width = 2048
  sunLight.shadow.mapSize.height = 2048
  sunLight.shadow.camera.near = 50
  sunLight.shadow.camera.far = 1800
  const d = 750
  sunLight.shadow.camera.left = -d
  sunLight.shadow.camera.right = d
  sunLight.shadow.camera.top = d
  sunLight.shadow.camera.bottom = -d
  scene.add(sunLight)

  fillLight = new THREE.DirectionalLight(0xE2E8F0, isDark ? 0.35 : 0.45)
  fillLight.position.set(-400, 450, -400)
  scene.add(fillLight)

  scene.add(roadGroup)

  // 6. Build 3D Realm
  buildGroundAndGrid()
  buildDistricts()
  buildBuildings()
  buildRoadsAndPaths()
  buildSelectionPulseRing()

  // 7. Event Listeners
  renderer.domElement.addEventListener('pointerdown', onPointerDown)
  renderer.domElement.addEventListener('pointermove', onPointerMove)
  window.addEventListener('resize', onWindowResize)

  // 8. Animation loop
  animate()
  fitCameraToAll()
}

// 3D Ground & Crisp Solid Grid (Theme Aware)
function buildGroundAndGrid() {
  const isDark = themeStore.isDark()

  // Main Ground Platform (Solid Slab in Soothing Dark/Light Tone)
  const groundGeo = new THREE.CylinderGeometry(820, 840, 16, 64)
  const groundMat = new THREE.MeshStandardMaterial({
    color: isDark ? 0x0F172A : 0xFFFFFF,
    roughness: 0.6,
    metalness: 0.05,
  })
  groundMesh = new THREE.Mesh(groundGeo, groundMat)
  groundMesh.position.y = -8
  groundMesh.receiveShadow = true
  scene.add(groundMesh)

  // 3D Grid in Soothing Blue Tone
  gridMesh = new THREE.GridHelper(
    1600,
    40,
    0x2563EB,
    isDark ? 0x1E293B : 0xCBD5E1
  )
  gridMesh.position.y = 0.5
  scene.add(gridMesh)
}

function updateThemeVisuals() {
  if (!scene) return
  const isDark = themeStore.isDark()

  scene.background = new THREE.Color(isDark ? 0x0B1120 : 0xF0F4F8)

  if (groundMesh) {
    (groundMesh.material as THREE.MeshStandardMaterial).color.set(isDark ? 0x0F172A : 0xFFFFFF)
  }

  if (ambientLight) {
    ambientLight.intensity = isDark ? 0.65 : 0.85
  }

  if (sunLight) {
    sunLight.intensity = isDark ? 1.05 : 1.25
  }

  if (gridMesh) {
    scene.remove(gridMesh)
    gridMesh = new THREE.GridHelper(1600, 40, 0x2563EB, isDark ? 0x1E293B : 0xCBD5E1)
    gridMesh.position.y = 0.5
    scene.add(gridMesh)
  }
}

watch(() => themeStore.currentTheme, () => {
  updateThemeVisuals()
})

// 3D District Island Plates
function buildDistricts() {
  const communities = graphStore.communities
  const colorPalette = [0x06B6D4, 0x8B5CF6, 0x10B981, 0xF59E0B, 0x2563EB]

  communities.forEach((comm, idx) => {
    const memberNodes = graphStore.townBuildings.filter((b) => comm.entity_ids?.includes(b.id))
    if (memberNodes.length === 0) return

    let avgX = 0
    let avgY = 0
    memberNodes.forEach((n) => {
      avgX += n.x ?? 980
      avgY += n.y ?? 560
    })
    avgX /= memberNodes.length
    avgY /= memberNodes.length

    const coords = to3DCoords(avgX, avgY)
    const colorHex = colorPalette[idx % colorPalette.length]

    // Solid Elevated District Plateau Slab
    const radius = Math.max(120, memberNodes.length * 52)
    const plateGeo = new THREE.CylinderGeometry(radius, radius + 10, 6, 32)
    const plateMat = new THREE.MeshStandardMaterial({
      color: colorHex,
      roughness: 0.45,
      metalness: 0.1,
      transparent: true,
      opacity: 0.28,
    })
    const plate = new THREE.Mesh(plateGeo, plateMat)
    plate.position.set(coords.x, 2, coords.z)
    plate.receiveShadow = true
    scene.add(plate)

    // Solid Perimeter Ring
    const ringGeo = new THREE.RingGeometry(radius - 2, radius + 2, 32)
    const ringMat = new THREE.MeshBasicMaterial({ color: colorHex, side: THREE.DoubleSide })
    const ring = new THREE.Mesh(ringGeo, ringMat)
    ring.rotation.x = -Math.PI / 2
    ring.position.set(coords.x, 5.2, coords.z)
    scene.add(ring)
  })
}

// ════════════════════════════════════════════════════════════════════════════
// Build 3D Towers — Strictly FLAT Architectural Tops (NO Cones, NO Spheres, NO Pyramids!)
// ════════════════════════════════════════════════════════════════════════════
function buildBuildings() {
  buildingMeshes.forEach((group) => scene.remove(group))
  buildingMeshes.clear()
  floatingEnergySlabs.length = 0

  buildings.value.forEach((b) => {
    const coords = to3DCoords(b.x ?? 980, b.y ?? 560)
    const group = new THREE.Group()
    group.position.set(coords.x, 0, coords.z)
    group.userData = { nodeId: b.id, name: b.label, type: b.type }

    const colors = getColor(b.type)
    const isMain = (b.level ?? 1) >= 4 || b.type === 'CHAPTER' || b.type === 'ORG' || (b.mentionCount ?? 0) >= 20

    if (isMain) {
      // ══════════════════════════════════════════════════════════════
      // MAIN CITADEL TOWER: Rectilinear Stepped Skyscraper with Flat Helipad & Battlements
      // ══════════════════════════════════════════════════════════════
      // Foundation Base Slab: Flat Rectangular Stone Plinth
      const baseGeo = new THREE.BoxGeometry(72, 14, 72)
      const baseMat = new THREE.MeshStandardMaterial({ color: 0xE2E8F0, roughness: 0.5 })
      const baseMesh = new THREE.Mesh(baseGeo, baseMat)
      baseMesh.position.y = 7
      baseMesh.castShadow = true
      baseMesh.receiveShadow = true
      group.add(baseMesh)

      // Main High-Rise Shaft (Solid Vibrant Theme Color)
      const shaftGeo = new THREE.BoxGeometry(64, 110, 64)
      const shaftMat = new THREE.MeshStandardMaterial({
        color: colors.main,
        roughness: 0.35,
        metalness: 0.2,
      })
      const shaft = new THREE.Mesh(shaftGeo, shaftMat)
      shaft.position.y = 14 + 55
      shaft.castShadow = true
      shaft.receiveShadow = true
      group.add(shaft)

      // Solid Cyber Windows (Flat horizontal light bars)
      const windowGeo = new THREE.BoxGeometry(65, 8, 52)
      const windowMat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF })
      const win1 = new THREE.Mesh(windowGeo, windowMat)
      win1.position.y = 48
      group.add(win1)
      const win2 = new THREE.Mesh(windowGeo, windowMat)
      win2.position.y = 78
      group.add(win2)
      const win3 = new THREE.Mesh(windowGeo, windowMat)
      win3.position.y = 108
      group.add(win3)

      // Tier 2: Flat Mid-Level Observation Deck
      const deckGeo = new THREE.BoxGeometry(50, 20, 50)
      const deckMat = new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.3 })
      const deck = new THREE.Mesh(deckGeo, deckMat)
      deck.position.y = 14 + 110 + 10
      deck.castShadow = true
      group.add(deck)

      // Tier 3: Flat Cantilevered Roof Terrace / Helipad (Strictly FLAT, NOT ROUND OR TRIANGLE)
      const roofGeo = new THREE.BoxGeometry(58, 6, 58)
      const roofMat = new THREE.MeshStandardMaterial({ color: colors.dark, roughness: 0.2 })
      const roof = new THREE.Mesh(roofGeo, roofMat)
      roof.position.y = 14 + 110 + 20 + 3
      roof.castShadow = true
      group.add(roof)

      // Four Flat Corner Battlements / Parapets on Roof Corners
      const bGeo = new THREE.BoxGeometry(10, 8, 10)
      const bMat = new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.3 })
      const corners = [
        [-24, -24],
        [24, -24],
        [-24, 24],
        [24, 24],
      ]
      corners.forEach(([cx, cz]) => {
        const battlement = new THREE.Mesh(bGeo, bMat)
        battlement.position.set(cx, 14 + 110 + 20 + 6 + 4, cz)
        battlement.castShadow = true
        group.add(battlement)
      })

      // Tier 4: Hovering Flat Rectangular Energy Slab (Spins Horizontally — Flat Top and Bottom)
      const slabGeo = new THREE.BoxGeometry(22, 5, 22)
      const slabMat = new THREE.MeshStandardMaterial({
        color: colors.light,
        roughness: 0.2,
        metalness: 0.4,
        emissive: colors.main,
        emissiveIntensity: 0.4,
      })
      const slab = new THREE.Mesh(slabGeo, slabMat)
      const slabBaseY = 14 + 110 + 20 + 6 + 22
      slab.position.y = slabBaseY
      slab.castShadow = true
      group.add(slab)
      floatingEnergySlabs.push({ mesh: slab, basePosY: slabBaseY, speed: 0.02 + Math.random() * 0.01 })

      // Skyward Flat Rectangular Laser Pillar
      const beamGeo = new THREE.BoxGeometry(4, 380, 4)
      const beamMat = new THREE.MeshBasicMaterial({
        color: colors.main,
        transparent: true,
        opacity: 0.38,
      })
      const beam = new THREE.Mesh(beamGeo, beamMat)
      beam.position.y = slabBaseY + 190
      group.add(beam)
    } else {
      // ══════════════════════════════════════════════════════════════
      // SUB TOWER: Flat-Topped Modular Pavilion (Strictly NO Cones, NO Spheres, NO Pyramids)
      // ══════════════════════════════════════════════════════════════
      // Flat Stone Plinth Base
      const baseGeo = new THREE.BoxGeometry(50, 10, 50)
      const baseMat = new THREE.MeshStandardMaterial({ color: 0xE2E8F0, roughness: 0.5 })
      const baseMesh = new THREE.Mesh(baseGeo, baseMat)
      baseMesh.position.y = 5
      baseMesh.castShadow = true
      baseMesh.receiveShadow = true
      group.add(baseMesh)

      // Main Cubic Body
      const bodyGeo = new THREE.BoxGeometry(44, 70, 44)
      const bodyMat = new THREE.MeshStandardMaterial({
        color: colors.main,
        roughness: 0.4,
        metalness: 0.15,
      })
      const body = new THREE.Mesh(bodyGeo, bodyMat)
      body.position.y = 10 + 35
      body.castShadow = true
      body.receiveShadow = true
      group.add(body)

      // Flat Architectural Penthouse & Cornice Ledge (FLAT, NOT PYRAMIDAL)
      const corniceGeo = new THREE.BoxGeometry(48, 4, 48)
      const corniceMat = new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.3 })
      const cornice = new THREE.Mesh(corniceGeo, corniceMat)
      cornice.position.y = 10 + 70 + 2
      cornice.castShadow = true
      group.add(cornice)

      // Flat Recessed Upper Deck Room
      const upperRoomGeo = new THREE.BoxGeometry(32, 14, 32)
      const upperRoomMat = new THREE.MeshStandardMaterial({ color: colors.dark, roughness: 0.3 })
      const upperRoom = new THREE.Mesh(upperRoomGeo, upperRoomMat)
      upperRoom.position.y = 10 + 70 + 4 + 7
      upperRoom.castShadow = true
      group.add(upperRoom)

      // Flat Rooftop Mechanical Box / Terrace
      const roofCapGeo = new THREE.BoxGeometry(36, 3, 36)
      const roofCapMat = new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.3 })
      const roofCap = new THREE.Mesh(roofCapGeo, roofCapMat)
      roofCap.position.y = 10 + 70 + 4 + 14 + 1.5
      roofCap.castShadow = true
      group.add(roofCap)

      // Flat Square Rooftop Antenna Post with Flat Square Beacon
      const postGeo = new THREE.BoxGeometry(2.5, 22, 2.5)
      const postMat = new THREE.MeshStandardMaterial({ color: colors.dark, roughness: 0.2 })
      const post = new THREE.Mesh(postGeo, postMat)
      post.position.y = 10 + 70 + 18 + 11
      group.add(post)

      const beaconGeo = new THREE.BoxGeometry(7, 4, 7)
      const beaconMat = new THREE.MeshBasicMaterial({ color: colors.light })
      const beacon = new THREE.Mesh(beaconGeo, beaconMat)
      beacon.position.y = 10 + 70 + 18 + 22
      group.add(beacon)
    }

    scene.add(group)
    buildingMeshes.set(b.id, group)
  })
}

// ════════════════════════════════════════════════════════════════════════════
// 3D Directional Arrow Helper (Elevated above Road Surface, Unidirectional / Bidirectional)
// ════════════════════════════════════════════════════════════════════════════
function create3DArrow(pos: THREE.Vector3, dir: THREE.Vector3, colorHex: number, scale = 1.0): THREE.Group {
  const arrowGroup = new THREE.Group()
  arrowGroup.position.copy(pos)
  arrowGroup.position.y += 6.5 // Elevated above tube surface so it is prominently visible and NEVER hides

  // Forward Arrowhead
  const headGeo = new THREE.ConeGeometry(7 * scale, 15 * scale, 8)
  const headMat = new THREE.MeshStandardMaterial({
    color: colorHex,
    roughness: 0.2,
    metalness: 0.3,
  })
  const head = new THREE.Mesh(headGeo, headMat)
  head.rotation.x = Math.PI / 2
  head.castShadow = true
  arrowGroup.add(head)

  // White High-Contrast Collar Band at arrow base
  const collarGeo = new THREE.CylinderGeometry(4.5 * scale, 4.5 * scale, 3.5 * scale, 8)
  const collarMat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF })
  const collar = new THREE.Mesh(collarGeo, collarMat)
  collar.rotation.x = Math.PI / 2
  collar.position.z = -7.5 * scale
  arrowGroup.add(collar)

  // Align orientation with direction vector
  const lookTarget = pos.clone().add(dir)
  arrowGroup.lookAt(lookTarget)
  return arrowGroup
}

// ════════════════════════════════════════════════════════════════════════════
// Build 3D Energy Viaduct Roads with UNIDIRECTIONAL Step Arrows (Bidirectional if Interchangeable)
// ════════════════════════════════════════════════════════════════════════════
function buildRoadsAndPaths() {
  // Clear previous roads
  while (roadGroup.children.length > 0) {
    const obj = roadGroup.children[0]
    roadGroup.remove(obj)
  }
  animatedRoadPhotons.length = 0

  // 1. Regular Cross-Entity Roads with Directed Arrows
  graphStore.edges.forEach((edge) => {
    const srcNode = graphStore.townBuildings.find((n) => n.id === edge.source_id)
    const tgtNode = graphStore.townBuildings.find((n) => n.id === edge.target_id)
    if (!srcNode || !tgtNode) return

    const p1 = to3DCoords(srcNode.x ?? 980, srcNode.y ?? 560)
    const p2 = to3DCoords(tgtNode.x ?? 980, tgtNode.y ?? 560)

    const v1 = new THREE.Vector3(p1.x, 10, p1.z)
    const v2 = new THREE.Vector3(p2.x, 10, p2.z)
    const mid = new THREE.Vector3((p1.x + p2.x) / 2, 28, (p1.z + p2.z) / 2)

    const curve = new THREE.CatmullRomCurve3([v1, mid, v2])
    const tubeGeo = new THREE.TubeGeometry(curve, 24, 3.5, 8, false)
    const tubeMat = new THREE.MeshStandardMaterial({
      color: 0x06B6D4,
      roughness: 0.3,
      metalness: 0.2,
    })
    const tube = new THREE.Mesh(tubeGeo, tubeMat)
    tube.castShadow = true
    roadGroup.add(tube)

    // Directed Arrow at Midpoint: Pointing strictly from source to target
    const pArrow = curve.getPointAt(0.52)
    const dirArrow = curve.getTangentAt(0.52).normalize()
    roadGroup.add(create3DArrow(pArrow, dirArrow, 0x06B6D4, 0.9))
  })

  // 2. Sequential Learning Path Highway with PROMINENT UNIDIRECTIONAL ARROWS
  if (graphStore.learningPath.length > 1) {
    for (let i = 0; i < graphStore.learningPath.length - 1; i++) {
      const srcId = graphStore.learningPath[i]
      const tgtId = graphStore.learningPath[i + 1]
      const srcNode = graphStore.townBuildings.find((n) => n.id === srcId)
      const tgtNode = graphStore.townBuildings.find((n) => n.id === tgtId)
      // DO NOT RETURN from the loop if a node is missing! Use CONTINUE!
      if (!srcNode || !tgtNode) continue

      const p1 = to3DCoords(srcNode.x ?? 980, srcNode.y ?? 560)
      const p2 = to3DCoords(tgtNode.x ?? 980, tgtNode.y ?? 560)
      const isInterchangeable = graphStore.isStepPairInterchangeable(srcId, tgtId)
      const roadColor = isInterchangeable ? 0xF59E0B : 0x10B981

      const v1 = new THREE.Vector3(p1.x, 14, p1.z)
      const v2 = new THREE.Vector3(p2.x, 14, p2.z)
      const mid = new THREE.Vector3((p1.x + p2.x) / 2, 38, (p1.z + p2.z) / 2)

      const curve = new THREE.CatmullRomCurve3([v1, mid, v2])
      const tubeGeo = new THREE.TubeGeometry(curve, 32, 5.5, 8, false)
      const tubeMat = new THREE.MeshStandardMaterial({
        color: roadColor,
        roughness: 0.2,
        metalness: 0.3,
      })
      const tube = new THREE.Mesh(tubeGeo, tubeMat)
      tube.castShadow = true
      roadGroup.add(tube)

      if (!isInterchangeable) {
        // ─── STRICTLY UNIDIRECTIONAL: Lower Step (i) ➔ Higher Step (i+1) ───
        // Two prominent elevated directional arrowheads pointing forward
        const t1 = 0.38
        const pArrow1 = curve.getPointAt(t1)
        const dir1 = curve.getTangentAt(t1).normalize()
        roadGroup.add(create3DArrow(pArrow1, dir1, 0x10B981, 1.25))

        const t2 = 0.72
        const pArrow2 = curve.getPointAt(t2)
        const dir2 = curve.getTangentAt(t2).normalize()
        roadGroup.add(create3DArrow(pArrow2, dir2, 0x10B981, 1.25))
      } else {
        // ─── INTERCHANGEABLE: Bidirectional Sibling Steps ───
        // Forward arrow pointing to i+1
        const tFwd = 0.68
        const pFwd = curve.getPointAt(tFwd)
        const dirFwd = curve.getTangentAt(tFwd).normalize()
        roadGroup.add(create3DArrow(pFwd, dirFwd, 0xF59E0B, 1.15))

        // Opposing reverse arrow pointing back to i
        const tBwd = 0.32
        const pBwd = curve.getPointAt(tBwd)
        const dirBwd = curve.getTangentAt(tBwd).negate().normalize()
        roadGroup.add(create3DArrow(pBwd, dirBwd, 0xF59E0B, 1.15))
      }

      // Animated 3D Traveling Energy Photon Particle
      const photonGeo = new THREE.BoxGeometry(6, 6, 6)
      const photonMat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF })
      const photon = new THREE.Mesh(photonGeo, photonMat)
      roadGroup.add(photon)
      animatedRoadPhotons.push({
        mesh: photon,
        curve,
        speed: 0.007,
        progress: Math.random(),
      })
    }
  }
}

// 3D Animated Selection Ring at Tower Base
function buildSelectionPulseRing() {
  const ringGeo = new THREE.RingGeometry(58, 66, 32)
  const ringMat = new THREE.MeshBasicMaterial({
    color: 0x10B981,
    side: THREE.DoubleSide,
  })
  pulseRingMesh = new THREE.Mesh(ringGeo, ringMat)
  pulseRingMesh.rotation.x = -Math.PI / 2
  pulseRingMesh.position.y = 1.2
  pulseRingMesh.visible = false
  scene.add(pulseRingMesh)
}

// Camera Presets
function setCameraIsometric() {
  if (!controls || !camera) return
  controls.reset()
  camera.position.set(540, 520, 540)
  controls.target.set(0, 0, 0)
  controls.update()
}

function setCameraTopDown() {
  if (!controls || !camera) return
  controls.reset()
  camera.position.set(0, 920, 10)
  controls.target.set(0, 0, 0)
  controls.update()
}

function zoomIn() {
  if (!camera) return
  const factor = 0.85
  camera.position.multiplyScalar(factor)
  controls.update()
}

function zoomOut() {
  if (!camera) return
  const factor = 1.15
  camera.position.multiplyScalar(factor)
  controls.update()
}

function fitCameraToAll() {
  if (!controls || !camera) return
  camera.position.set(0, 560, 820)
  controls.target.set(0, 0, 0)
  controls.update()
}

function focusOnNode(nodeId: string) {
  const group = buildingMeshes.get(nodeId)
  if (!group || !controls || !camera) return

  const targetX = group.position.x
  const targetZ = group.position.z

  controls.target.set(targetX, 40, targetZ)
  camera.position.set(targetX, 260, targetZ + 360)
  controls.update()
}

// Raycasting (Clicking 3D Buildings)
const raycaster = new THREE.Raycaster()
const mouse = new THREE.Vector2()
let pointerDownTime = 0

function onPointerDown(_event: MouseEvent) {
  pointerDownTime = Date.now()
}

function onPointerMove(event: MouseEvent) {
  if (!containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(scene.children, true)
  let found = false
  for (const hit of intersects) {
    let p: THREE.Object3D | null = hit.object
    while (p && p !== scene) {
      if (p.userData?.nodeId) {
        found = true
        break
      }
      p = p.parent
    }
    if (found) break
  }
  containerRef.value.style.cursor = found ? 'pointer' : 'grab'
}

function onPointerClick(_event: MouseEvent) {
  if (Date.now() - pointerDownTime > 250) return
  if (!containerRef.value) return

  const rect = containerRef.value.getBoundingClientRect()
  mouse.x = ((_event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((_event.clientY - rect.top) / rect.height) * 2 + 1

  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(scene.children, true)

  for (const hit of intersects) {
    let p: THREE.Object3D | null = hit.object
    while (p && p !== scene) {
      if (p.userData?.nodeId) {
        const id = p.userData.nodeId
        graphStore.selectEntity(id)
        emit('buildingClick', id)
        return
      }
      p = p.parent
    }
  }
}

// Project 3D Buildings into 2D HTML/CSS Holographic Labels
function updateProjectedLabels() {
  if (!containerRef.value || !camera) return
  const width = containerRef.value.clientWidth
  const height = containerRef.value.clientHeight

  const labels: ProjectedLabel[] = []
  const tempVec = new THREE.Vector3()

  buildings.value.forEach((b) => {
    const group = buildingMeshes.get(b.id)
    if (!group) return

    const isMain = (b.level ?? 1) >= 4 || b.type === 'CHAPTER' || b.type === 'ORG' || (b.mentionCount ?? 0) >= 20
    const labelAltitude = isMain ? 220 : 135

    tempVec.set(group.position.x, labelAltitude, group.position.z)
    tempVec.project(camera)

    if (tempVec.z > 1) return

    const screenX = (tempVec.x * 0.5 + 0.5) * width
    const screenY = (-(tempVec.y * 0.5) + 0.5) * height

    const stepIndex = graphStore.learningPath.indexOf(b.id)
    labels.push({
      id: b.id,
      name: b.label,
      type: b.type,
      stepIndex: stepIndex !== -1 ? stepIndex + 1 : undefined,
      isMain,
      isSelected: graphStore.selectedEntityId === b.id,
      screenX: Math.round(screenX),
      screenY: Math.round(screenY),
      visible: true,
    })
  })

  projectedLabels.value = labels
}

// Animation Loop
let clock = 0
function animate() {
  animationFrameId = requestAnimationFrame(animate)
  clock += 0.016

  if (controls) controls.update()

  // 1. Rotate Floating Flat Energy Slabs
  floatingEnergySlabs.forEach((item) => {
    item.mesh.rotation.y += item.speed
    item.mesh.position.y = item.basePosY + Math.sin(clock * 3) * 2.5
  })

  // 2. Animate Traveling Energy Photons along Road Viaducts
  animatedRoadPhotons.forEach((item) => {
    item.progress += item.speed
    if (item.progress > 1) item.progress = 0
    const pt = item.curve.getPointAt(item.progress)
    item.mesh.position.set(pt.x, pt.y + 4, pt.z)
    item.mesh.rotation.y += 0.05
    item.mesh.rotation.x += 0.05
  })

  // 3. Selection Pulse Ring
  if (pulseRingMesh && graphStore.selectedEntityId) {
    const selectedGroup = buildingMeshes.get(graphStore.selectedEntityId)
    if (selectedGroup) {
      pulseRingMesh.visible = true
      pulseRingMesh.position.x = selectedGroup.position.x
      pulseRingMesh.position.z = selectedGroup.position.z
      const pulseScale = 1 + Math.sin(clock * 4) * 0.08
      pulseRingMesh.scale.set(pulseScale, pulseScale, pulseScale)
    } else {
      pulseRingMesh.visible = false
    }
  } else if (pulseRingMesh) {
    pulseRingMesh.visible = false
  }

  // 4. Update Projected 2D Overlay Labels
  updateProjectedLabels()

  if (renderer && scene && camera) {
    renderer.render(scene, camera)
  }
}

function onWindowResize() {
  if (!containerRef.value || !camera || !renderer) return
  const width = containerRef.value.clientWidth
  const height = containerRef.value.clientHeight
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

watch(
  () => buildings.value.length,
  () => {
    nextTick(() => {
      buildBuildings()
      buildRoadsAndPaths()
    })
  }
)

watch(
  () => graphStore.selectedEntityId,
  (newId) => {
    if (newId) {
      focusOnNode(newId)
    }
  }
)

watch(
  () => graphStore.learningPath.length,
  () => {
    nextTick(() => {
      buildRoadsAndPaths()
    })
  }
)

watch(
  () => props.autoRotate,
  (val) => {
    if (controls) {
      controls.autoRotate = Boolean(val)
    }
  }
)

watch(
  () => props.autoRotateSpeed,
  (speed) => {
    if (controls && speed !== undefined) {
      controls.autoRotateSpeed = speed
    }
  }
)

let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  nextTick(() => {
    initThree()
    if (containerRef.value && typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => {
        onWindowResize()
      })
      resizeObserver.observe(containerRef.value)
    }
  })
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  window.removeEventListener('resize', onWindowResize)
  if (renderer && renderer.domElement) {
    renderer.domElement.removeEventListener('pointerdown', onPointerDown)
    renderer.domElement.removeEventListener('pointermove', onPointerMove)
  }
  if (renderer) renderer.dispose()
})

defineExpose({
  zoomIn,
  zoomOut,
  recenter: fitCameraToAll,
  fitTownView: fitCameraToAll,
  focusOnNode,
  setCameraIsometric,
  setCameraTopDown,
  is3DMode: true,
  toggle3DMode: setCameraIsometric,
})
</script>

<template>
  <div
    ref="containerRef"
    class="w-full h-full relative overflow-hidden select-none bg-[#F8FAFC] dark:bg-[#090D16] transition-colors"
    @click="onPointerClick"
  >
    <!-- Crisp 3D Orbital Navigation Helper Badge in Canvas -->
    <div
      v-if="!hideNavigationBadge"
      class="absolute bottom-5 left-1/2 -translate-x-1/2 pointer-events-none z-10 flex items-center gap-2 px-3 py-1.5 bg-[#0F172A] dark:bg-slate-900 text-white rounded-full text-[11px] font-mono shadow-md border border-slate-700"
    >
      <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
      <span class="font-bold">3D Orbit: Left-Click Drag</span>
      <span class="text-slate-400">•</span>
      <span>Pan: Right-Click</span>
      <span class="text-slate-400">•</span>
      <span>Zoom: Scroll</span>
    </div>

    <!-- 2D Razor-Sharp Holographic Badges Projected in 3D Space -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden z-20">
      <div
        v-for="lbl in projectedLabels"
        :key="lbl.id"
        class="absolute -translate-x-1/2 -translate-y-full transition-transform pointer-events-auto cursor-pointer group"
        :style="{ left: `${lbl.screenX}px`, top: `${lbl.screenY}px` }"
        @click.stop="graphStore.selectEntity(lbl.id)"
      >
        <!-- Crisp Floating Topic Capsule (Solid Colors, No Gradients!) -->
        <div
          class="flex items-center gap-1.5 px-3 py-1 rounded-full shadow-md border-2 transition-all active:scale-95"
          :class="[
            lbl.isSelected
              ? 'bg-[#0F172A] text-white border-emerald-400 ring-4 ring-emerald-400/30 scale-105'
              : 'bg-white dark:bg-slate-900 text-[#0F172A] dark:text-slate-100 border-slate-900 dark:border-slate-600 hover:border-emerald-500 hover:scale-105'
          ]"
        >
          <!-- Step Number Pill -->
          <span
            v-if="lbl.stepIndex"
            class="px-1.5 py-0.2 rounded-full text-[9px] font-mono font-black"
            :class="lbl.isSelected ? 'bg-emerald-500 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200'"
          >
            Step {{ lbl.stepIndex }}
          </span>

          <!-- Node Name -->
          <span class="text-[11px] font-mono font-black tracking-tight truncate max-w-[120px]">
            {{ lbl.name }}
          </span>

          <!-- Solid Main / Sub Pill -->
          <span
            class="text-[8.5px] font-mono font-black px-1.5 py-0.2 rounded uppercase"
            :class="lbl.isMain ? 'bg-amber-400 text-slate-900 font-bold' : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300'"
          >
            {{ lbl.isMain ? 'MAIN' : 'SUB' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
