import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { SKILLS, DISCIPLINES, CROSS_LINKS } from '../data/skills.js'

const byId = Object.fromEntries(SKILLS.map((s) => [s.id, s]))
const R = 42 // node radius

const STATE_FILL_OPACITY = { locked: 0.16, learning: 0.5, practiced: 0.82, mastered: 1 }

// Split a label into at most two lines near the middle for tidy wrapping.
function wrapLabel(name) {
  if (name.length <= 15) return [name]
  const mid = Math.floor(name.length / 2)
  let split = name.lastIndexOf(' ', mid)
  if (split < 4) split = name.indexOf(' ', mid)
  if (split < 0) return [name]
  return [name.slice(0, split), name.slice(split + 1)]
}

export default function SkillGrid({
  stateOf,
  isAvailable,
  selectedId,
  onSelect,
  activeDiscipline,
}) {
  const containerRef = useRef(null)
  const [view, setView] = useState({ x: 0, y: 0, k: 1 })
  const [panning, setPanning] = useState(false)
  const pointer = useRef({ down: false, moved: false, startX: 0, startY: 0, ox: 0, oy: 0 })

  // Fit the whole grid into the viewport on first mount.
  useLayoutEffect(() => {
    const el = containerRef.current
    if (!el) return
    const { width, height } = el.getBoundingClientRect()
    const xs = SKILLS.map((s) => s.x)
    const ys = SKILLS.map((s) => s.y)
    const pad = 90
    const minX = Math.min(...xs) - pad
    const minY = Math.min(...ys) - pad
    const maxX = Math.max(...xs) + pad
    const maxY = Math.max(...ys) + pad
    const cw = maxX - minX
    const ch = maxY - minY
    const k = Math.min(width / cw, height / ch)
    const x = (width - cw * k) / 2 - minX * k
    const y = (height - ch * k) / 2 - minY * k
    setView({ x, y, k })
  }, [])

  const zoomAt = useCallback((factor, cx, cy) => {
    setView((v) => {
      const k = Math.max(0.3, Math.min(2.5, v.k * factor))
      const ratio = k / v.k
      return { k, x: cx - (cx - v.x) * ratio, y: cy - (cy - v.y) * ratio }
    })
  }, [])

  const onWheel = useCallback(
    (e) => {
      e.preventDefault()
      const rect = containerRef.current.getBoundingClientRect()
      zoomAt(e.deltaY < 0 ? 1.12 : 1 / 1.12, e.clientX - rect.left, e.clientY - rect.top)
    },
    [zoomAt],
  )

  // Wheel listener must be non-passive to allow preventDefault.
  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    el.addEventListener('wheel', onWheel, { passive: false })
    return () => el.removeEventListener('wheel', onWheel)
  }, [onWheel])

  const onPointerDown = (e) => {
    pointer.current = {
      down: true,
      moved: false,
      startX: e.clientX,
      startY: e.clientY,
      ox: view.x,
      oy: view.y,
    }
  }

  const onPointerMove = (e) => {
    const p = pointer.current
    if (!p.down) return
    const dx = e.clientX - p.startX
    const dy = e.clientY - p.startY
    if (!p.moved && Math.hypot(dx, dy) > 4) {
      p.moved = true
      setPanning(true)
    }
    if (p.moved) setView((v) => ({ ...v, x: p.ox + dx, y: p.oy + dy }))
  }

  const endPointer = () => {
    pointer.current.down = false
    setPanning(false)
  }

  const handleNodeClick = (id) => {
    // Ignore the click that ends a drag.
    if (pointer.current.moved) return
    onSelect(id)
  }

  const dimmed = (skill) => activeDiscipline && skill.discipline !== activeDiscipline

  return (
    <div
      ref={containerRef}
      className={`stage ${panning ? 'panning' : ''}`}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={endPointer}
      onPointerLeave={endPointer}
    >
      <svg className="grid-svg">
        <defs>
          <filter id="nodeGlow" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="6" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <g transform={`translate(${view.x} ${view.y}) scale(${view.k})`}>
          {/* Cross-links (faint, dashed) */}
          {CROSS_LINKS.map(([a, b], i) => {
            const sa = byId[a]
            const sb = byId[b]
            if (!sa || !sb) return null
            const faded = dimmed(sa) && dimmed(sb)
            return (
              <line
                key={`x-${i}`}
                x1={sa.x} y1={sa.y} x2={sb.x} y2={sb.y}
                stroke="#9a8fb5"
                strokeWidth={2}
                strokeDasharray="3 9"
                strokeLinecap="round"
                opacity={faded ? 0.12 : 0.4}
              />
            )
          })}

          {/* Prerequisite edges (the "came" lines) */}
          {SKILLS.flatMap((skill) =>
            skill.prereqs.map((pid) => {
              const from = byId[pid]
              if (!from) return null
              const lit = stateOf(pid) === 'mastered'
              const faded = dimmed(skill) && dimmed(from)
              const disc = DISCIPLINES[skill.discipline]
              return (
                <g key={`${pid}->${skill.id}`} opacity={faded ? 0.15 : 1}>
                  <line
                    x1={from.x} y1={from.y} x2={skill.x} y2={skill.y}
                    stroke="#14101f" strokeWidth={lit ? 8 : 6} strokeLinecap="round"
                  />
                  <line
                    x1={from.x} y1={from.y} x2={skill.x} y2={skill.y}
                    stroke={lit ? disc.glow : '#b8ac93'}
                    strokeWidth={lit ? 4 : 2.5}
                    strokeLinecap="round"
                    opacity={lit ? 0.95 : 0.55}
                  />
                </g>
              )
            }),
          )}

          {/* Nodes */}
          {SKILLS.map((skill) => {
            const disc = DISCIPLINES[skill.discipline]
            const state = stateOf(skill.id)
            const available = isAvailable(skill)
            const faded = dimmed(skill)
            const selected = selectedId === skill.id
            const lines = wrapLabel(skill.name)
            const mastered = state === 'mastered'
            const readyGlow = state === 'locked' && available
            return (
              <g
                key={skill.id}
                className="node-group"
                transform={`translate(${skill.x} ${skill.y})`}
                opacity={faded ? 0.28 : 1}
                onClick={() => handleNodeClick(skill.id)}
              >
                {mastered && (
                  <circle r={R + 6} fill="none" stroke={disc.glow} strokeWidth={5} opacity={0.55} filter="url(#nodeGlow)" />
                )}
                {readyGlow && (
                  <circle r={R + 5} fill="none" stroke={disc.glow} strokeWidth={2.5} strokeDasharray="4 6" opacity={0.7} />
                )}
                {selected && (
                  <circle r={R + 11} fill="none" stroke="#E0A526" strokeWidth={3.5} />
                )}
                <circle
                  className="node-circle"
                  r={R}
                  fill={disc.color}
                  fillOpacity={STATE_FILL_OPACITY[state]}
                  stroke="#14101f"
                  strokeWidth={4}
                  strokeDasharray={state === 'locked' && !available ? '5 5' : '0'}
                  filter={mastered ? 'url(#nodeGlow)' : undefined}
                />
                {skill.hub && (
                  <circle r={R - 12} fill="none" stroke="#14101f" strokeWidth={2} opacity={0.4} />
                )}
                <text
                  className={`node-label ${state === 'locked' && !available ? 'dim' : ''}`}
                  textAnchor="middle"
                  y={R + 22}
                >
                  {lines.map((ln, i) => (
                    <tspan key={i} x={0} dy={i === 0 ? 0 : 17}>{ln}</tspan>
                  ))}
                </text>
              </g>
            )
          })}
        </g>
      </svg>

      <div className="stage-hint">Drag to pan · scroll to zoom · click a node to open it</div>
      <div className="zoom-controls">
        <button className="btn" onClick={() => zoomAt(1.2, containerRef.current.clientWidth / 2, containerRef.current.clientHeight / 2)} aria-label="Zoom in">+</button>
        <button className="btn" onClick={() => zoomAt(1 / 1.2, containerRef.current.clientWidth / 2, containerRef.current.clientHeight / 2)} aria-label="Zoom out">−</button>
      </div>
    </div>
  )
}
