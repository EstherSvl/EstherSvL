import { useState } from 'react'
import { SKILLS } from './data/skills.js'
import { useProgress } from './hooks/useProgress.js'
import SkillGrid from './components/SkillGrid.jsx'
import DetailPanel from './components/DetailPanel.jsx'
import Legend from './components/Legend.jsx'

const byId = Object.fromEntries(SKILLS.map((s) => [s.id, s]))
const TOTAL = SKILLS.length

export default function App() {
  const { stateOf, setState, isAvailable, counts } = useProgress()
  const [selectedId, setSelectedId] = useState(null)
  const [activeDiscipline, setActiveDiscipline] = useState(null)

  const pct = (n) => `${(n / TOTAL) * 100}%`

  const toggleDiscipline = (id) =>
    setActiveDiscipline((cur) => (cur === id ? null : id))

  const resetAll = () => {
    if (window.confirm('Reset all progress? This clears every skill back to "Not started".')) {
      for (const s of SKILLS) setState(s.id, 'locked')
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-title">
          <h1>The Glass Artist&rsquo;s Grid</h1>
          <span>A sphere grid for the path to mastery</span>
        </div>
        <div className="progress-wrap">
          <div className="progress-bar" title="Mastered / Practiced / Learning">
            <div className="progress-seg mastered" style={{ width: pct(counts.mastered) }} />
            <div className="progress-seg practiced" style={{ width: pct(counts.practiced) }} />
            <div className="progress-seg learning" style={{ width: pct(counts.learning) }} />
          </div>
          <div className="progress-meta">
            <span>{counts.mastered} mastered · {counts.practiced} practiced · {counts.learning} learning</span>
            <span>{counts.mastered}/{TOTAL}</span>
          </div>
        </div>
        <div className="header-actions">
          <button className="btn ghost" onClick={resetAll}>Reset</button>
        </div>
      </header>

      <SkillGrid
        stateOf={stateOf}
        isAvailable={isAvailable}
        selectedId={selectedId}
        onSelect={setSelectedId}
        activeDiscipline={activeDiscipline}
      />

      <Legend
        activeDiscipline={activeDiscipline}
        onToggleDiscipline={toggleDiscipline}
      />

      <DetailPanel
        skill={selectedId ? byId[selectedId] : null}
        stateOf={stateOf}
        isAvailable={isAvailable}
        onSetState={setState}
        onClose={() => setSelectedId(null)}
        onSelect={setSelectedId}
      />
    </div>
  )
}
