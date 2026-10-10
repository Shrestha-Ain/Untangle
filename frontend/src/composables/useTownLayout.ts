export interface BuildingLayoutInput {
  id: string
  label: string
  type: string
  mentionCount: number
  level: number
  pathOrder?: number
  description?: string
  x?: number
  y?: number
}

export interface RoadLayoutInput {
  id: string
  sourceId: string
  targetId: string
  relationType: string
  isCrossSource?: boolean
}

export interface CommunityLayoutInput {
  id: string
  title: string
  entity_ids: string[]
  level: number
}

// Generous spacing constants matching page2 cartography
const TILE_W = 380
const TILE_H = 200
const CENTER_X = 980
const CENTER_Y = 460

function isoProject(gx: number, gy: number) {
  return {
    x: (gx - gy) * (TILE_W / 2) + CENTER_X,
    y: (gx + gy) * (TILE_H / 2) + CENTER_Y,
  }
}


export const DISTRICT_THEMES = [
  { fill: '#CEEFE2', stroke: '#B4E5D1', textColor: '#0D9488' }, // Cyan-Green Attention Valley
  { fill: '#E8EDF9', stroke: '#CCD8F4', textColor: '#3B82F6' }, // Blue Memory Woods / Tech
  { fill: '#F4E9F7', stroke: '#E3CCE9', textColor: '#8B5CF6' }, // Purple Scholar Grove
  { fill: '#FDF1DF', stroke: '#F8DFBC', textColor: '#D97706' }, // Amber Benchmark Arena
]

export function isMainTower(b: { type?: string; level?: number; mentionCount?: number }): boolean {
  return (b.level ?? 1) >= 4 || b.type === 'CHAPTER' || b.type === 'ORG' || (b.mentionCount ?? 0) >= 20
}

// Generous regional hub anchors across 2048x1400 canvas for spacious distribution
const MAIN_TOWER_HUBS = [
  { x: 1020, y: 440 }, // Central Grand Citadel
  { x: 560, y: 380 },  // Northwest Scholar Bastion
  { x: 1520, y: 420 }, // Northeast Research Outpost
  { x: 620, y: 760 },  // Southwest Engineering Yard
  { x: 1460, y: 780 }, // Southeast Innovation Arena
  { x: 1040, y: 840 }, // South Nexus
]

export function useTownLayout() {
  function relaxCollision(placed: Array<BuildingLayoutInput & { x: number; y: number }>) {
    const MIN_DIST = 260
    const MIN_X = 210
    const MIN_Y = 160
    const ITERATIONS = 12

    for (let iter = 0; iter < ITERATIONS; iter++) {
      let moved = false
      for (let i = 0; i < placed.length; i++) {
        for (let j = i + 1; j < placed.length; j++) {
          const b1 = placed[i]
          const b2 = placed[j]
          const dx = b2.x - b1.x
          const dy = b2.y - b1.y
          const dist = Math.sqrt(dx * dx + dy * dy) || 1

          if (dist < MIN_DIST || (Math.abs(dx) < MIN_X && Math.abs(dy) < MIN_Y)) {
            moved = true
            const overlap = (MIN_DIST - dist) / 2
            const nx = dx / dist
            const ny = dy / dist

            b1.x = Math.max(160, Math.min(1920, Math.round(b1.x - nx * overlap * 0.6)))
            b1.y = Math.max(160, Math.min(1240, Math.round(b1.y - ny * overlap * 0.6)))
            b2.x = Math.max(160, Math.min(1920, Math.round(b2.x + nx * overlap * 0.6)))
            b2.y = Math.max(160, Math.min(1240, Math.round(b2.y + ny * overlap * 0.6)))
          }
        }
      }
      if (!moved) break
    }
    return placed
  }

  function layoutBuildings(buildings: BuildingLayoutInput[]) {
    let mainHubIdx = 0
    let subOrbitIdx = 0

    const placed = buildings.map((b) => {
      // If position already explicitly designated and non-zero
      if (b.x !== undefined && b.y !== undefined && (b.x > 0 || b.y > 0)) {
        return { ...b, x: b.x, y: b.y }
      }

      if (isMainTower(b)) {
        const hub = MAIN_TOWER_HUBS[mainHubIdx % MAIN_TOWER_HUBS.length]
        mainHubIdx++
        return { ...b, x: hub.x, y: hub.y }
      } else {
        // Sub towers orbit around recent main hub or canvas sectors
        const parentHub = MAIN_TOWER_HUBS[Math.max(0, mainHubIdx - 1) % MAIN_TOWER_HUBS.length]
        const angle = (subOrbitIdx * 65 * Math.PI) / 180
        const radius = 290 + (subOrbitIdx % 3) * 60
        subOrbitIdx++
        const x = Math.round(parentHub.x + Math.cos(angle) * radius)
        const y = Math.round(parentHub.y + Math.sin(angle) * (radius * 0.65))
        return {
          ...b,
          x: Math.max(160, Math.min(1920, x)),
          y: Math.max(160, Math.min(1240, y)),
        }
      }
    })

    // Perform physics repulsion pass to guarantee towers never crowd or overlap
    return relaxCollision(placed)
  }

  function layoutRoads(
    roads: RoadLayoutInput[],
    placedBuildings: Array<BuildingLayoutInput & { x: number; y: number }>
  ) {
    const posMap = new Map(placedBuildings.map((b) => [b.id, { x: b.x, y: b.y }]))

    return roads.map((r) => {
      const src = posMap.get(r.sourceId) ?? { x: CENTER_X, y: CENTER_Y }
      const tgt = posMap.get(r.targetId) ?? { x: CENTER_X, y: CENTER_Y }

      // Smooth curve between nodes
      const midX = (src.x + tgt.x) / 2
      const midY = (src.y + tgt.y) / 2 - 20

      return {
        ...r,
        svgPath: `M ${src.x},${src.y} Q ${midX},${midY} ${tgt.x},${tgt.y}`,
        sourcePos: src,
        targetPos: tgt,
      }
    })
  }

  function layoutDistricts(
    communities: CommunityLayoutInput[],
    placedBuildings: Array<BuildingLayoutInput & { x: number; y: number }>
  ) {
    const posMap = new Map(placedBuildings.map((b) => [b.id, { x: b.x, y: b.y }]))

    return communities.map((c, index) => {
      const theme = DISTRICT_THEMES[index % DISTRICT_THEMES.length]
      const memberPositions = c.entity_ids
        .map((id) => posMap.get(id))
        .filter((pos): pos is { x: number; y: number } => pos !== undefined)

      if (memberPositions.length === 0) {
        return {
          id: c.id,
          label: c.title,
          polygon: '',
          fill: theme.fill,
          stroke: theme.stroke,
          textColor: theme.textColor,
          centerX: 0,
          centerY: 0,
        }
      }

      // Compute generous bounding diamond around member buildings
      const xs = memberPositions.map((p) => p.x)
      const ys = memberPositions.map((p) => p.y)
      const minX = Math.min(...xs) - 140
      const maxX = Math.max(...xs) + 140
      const minY = Math.min(...ys) - 110
      const maxY = Math.max(...ys) + 110
      const midX = (minX + maxX) / 2
      const midY = (minY + maxY) / 2

      // Diamond polygon
      const points = `${midX},${minY} ${maxX},${midY} ${midX},${maxY} ${minX},${midY}`

      return {
        id: c.id,
        label: c.title,
        polygon: points,
        fill: theme.fill,
        stroke: theme.stroke,
        textColor: theme.textColor,
        centerX: midX,
        centerY: minY + 30,
      }
    })
  }

  return {
    layoutBuildings,
    layoutRoads,
    layoutDistricts,
    isoProject,
  }
}
