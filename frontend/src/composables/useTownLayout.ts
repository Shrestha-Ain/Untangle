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

function spiralCoords(index: number) {
  if (index === 0) return { gx: 0, gy: 0 }
  const ring = Math.floor(Math.sqrt(index))
  const pos = index - ring * ring
  const side = Math.floor(pos / Math.max(ring, 1))
  const offset = pos % Math.max(ring, 1)

  const directions = [
    { gx: 1, gy: 0 },
    { gx: 0, gy: 1 },
    { gx: -1, gy: 0 },
    { gx: 0, gy: -1 },
  ]
  const dir = directions[side % 4]
  const nextDir = directions[(side + 1) % 4]

  return {
    gx: ring * dir.gx + offset * nextDir.gx,
    gy: ring * dir.gy + offset * nextDir.gy,
  }
}

export const DISTRICT_THEMES = [
  { fill: '#CEEFE2', stroke: '#B4E5D1', textColor: '#0D9488' }, // Cyan-Green Attention Valley
  { fill: '#E8EDF9', stroke: '#CCD8F4', textColor: '#3B82F6' }, // Blue Memory Woods / Tech
  { fill: '#F4E9F7', stroke: '#E3CCE9', textColor: '#8B5CF6' }, // Purple Scholar Grove
  { fill: '#FDF1DF', stroke: '#F8DFBC', textColor: '#D97706' }, // Amber Benchmark Arena
]

export function useTownLayout() {
  function layoutBuildings(buildings: BuildingLayoutInput[]) {
    // If buildings already have distinct x/y, preserve them
    const sorted = [...buildings].sort((a, b) => (b.mentionCount || 1) - (a.mentionCount || 1))

    return sorted.map((b, i) => {
      if (b.x !== undefined && b.y !== undefined) {
        return { ...b, x: b.x, y: b.y }
      }
      const { gx, gy } = spiralCoords(i)
      const { x, y } = isoProject(gx, gy)
      return { ...b, x, y }
    })
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
