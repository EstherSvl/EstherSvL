import { useCallback, useEffect, useState } from 'react'
import { SKILLS, STATES } from '../data/skills.js'

const STORAGE_KEY = 'glass-grid-progress-v1'

function loadInitial() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {
    // ignore corrupt / unavailable storage
  }
  return {}
}

// Tracks each skill's state ('locked' by default) and persists to localStorage.
export function useProgress() {
  const [progress, setProgress] = useState(loadInitial)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(progress))
    } catch {
      // ignore storage write failures (e.g. private mode)
    }
  }, [progress])

  const stateOf = useCallback((id) => progress[id] || 'locked', [progress])

  const setState = useCallback((id, state) => {
    setProgress((prev) => ({ ...prev, [id]: state }))
  }, [])

  const cycle = useCallback((id) => {
    setProgress((prev) => {
      const current = prev[id] || 'locked'
      const next = STATES[(STATES.indexOf(current) + 1) % STATES.length]
      return { ...prev, [id]: next }
    })
  }, [])

  const reset = useCallback(() => setProgress({}), [])

  // A skill is "available" once every prerequisite is mastered.
  const isAvailable = useCallback(
    (skill) => skill.prereqs.every((p) => (progress[p] || 'locked') === 'mastered'),
    [progress],
  )

  const counts = STATES.reduce((acc, s) => ({ ...acc, [s]: 0 }), {})
  for (const skill of SKILLS) counts[progress[skill.id] || 'locked']++

  return { progress, stateOf, setState, cycle, reset, isAvailable, counts }
}
