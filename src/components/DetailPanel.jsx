import { DISCIPLINES, STATES, STATE_META, SKILLS } from '../data/skills.js'

const byId = Object.fromEntries(SKILLS.map((s) => [s.id, s]))

export default function DetailPanel({ skill, stateOf, isAvailable, onSetState, onClose, onSelect }) {
  if (!skill) return null
  const disc = DISCIPLINES[skill.discipline]
  const current = stateOf(skill.id)
  const available = isAvailable(skill)
  const prereqsMet = skill.prereqs.filter((p) => stateOf(p) === 'mastered')

  return (
    <div className="detail" role="dialog" aria-label={`${skill.name} details`}>
      <button className="detail-close" onClick={onClose} aria-label="Close">×</button>
      <div className="detail-top">
        <span className="detail-disc" style={{ color: disc.color }}>
          <span className="legend-swatch" style={{ background: disc.color }} />
          {disc.label}
        </span>
        <h2>{skill.name}</h2>
      </div>
      <div className="detail-body">
        <p className="detail-summary">{skill.summary}</p>
        <p className="detail-details">{skill.details}</p>

        <p className="detail-section-label">Builds on</p>
        {skill.prereqs.length === 0 ? (
          <p className="prereq-none">Nothing — this is a starting node.</p>
        ) : (
          <ul className="prereq-list">
            {skill.prereqs.map((p) => {
              const met = stateOf(p) === 'mastered'
              return (
                <li
                  key={p}
                  className={`prereq-item ${met ? 'met' : 'unmet'}`}
                  onClick={() => onSelect(p)}
                  style={{ cursor: 'pointer' }}
                  title="Go to this skill"
                >
                  <span className="tick">{met ? '✓' : '○'}</span>
                  {byId[p]?.name || p}
                </li>
              )
            })}
          </ul>
        )}

        <p className="detail-section-label">Your progress</p>
        <div className="state-buttons">
          {STATES.map((s) => (
            <button
              key={s}
              className={`state-btn ${s} ${current === s ? 'active' : ''}`}
              onClick={() => onSetState(skill.id, s)}
            >
              {STATE_META[s].label}
            </button>
          ))}
        </div>

        {skill.prereqs.length > 0 && (
          <p className={`avail-note ${available ? 'ready' : ''}`}>
            {available
              ? '✓ All prerequisites mastered — you’re ready to take this on.'
              : `In progress: ${prereqsMet.length}/${skill.prereqs.length} prerequisites mastered.`}
          </p>
        )}
      </div>
    </div>
  )
}
