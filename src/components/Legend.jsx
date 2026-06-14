import { DISCIPLINES } from '../data/skills.js'

const STATE_DOTS = [
  { key: 'locked', label: 'Not started', color: 'rgba(120,110,140,0.25)' },
  { key: 'learning', label: 'Learning', color: '#B23A4C' },
  { key: 'practiced', label: 'Practiced', color: '#2E9B6B' },
  { key: 'mastered', label: 'Mastered', color: '#E0A526' },
]

export default function Legend({ activeDiscipline, onToggleDiscipline }) {
  return (
    <div className="legend">
      <h3>Disciplines</h3>
      {Object.values(DISCIPLINES).map((d) => (
        <div
          key={d.id}
          className={`legend-row ${activeDiscipline && activeDiscipline !== d.id ? 'muted' : ''}`}
          onClick={() => onToggleDiscipline(d.id)}
          title="Click to highlight this discipline"
        >
          <span className="legend-swatch" style={{ background: d.color }} />
          {d.label}
        </div>
      ))}
      <div className="legend-divider" />
      <h3>Progress</h3>
      {STATE_DOTS.map((s) => (
        <div key={s.key} className="legend-state">
          <span className="legend-dot" style={{ background: s.color }} />
          {s.label}
        </div>
      ))}
    </div>
  )
}
