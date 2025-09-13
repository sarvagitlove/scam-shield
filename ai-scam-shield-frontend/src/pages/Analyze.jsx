import React, { useState } from 'react'

export default function Analyze(){
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)

  async function onAnalyze(){
    const res = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text})
    })
    const j = await res.json()
    setResult(j)
  }

  async function onReport(){
    await fetch('http://localhost:8000/report', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text})
    })
    alert('Saved report locally')
  }

  return (
    <div className="container">
      <h2>Analyze</h2>
      <textarea value={text} onChange={e=>setText(e.target.value)} placeholder="Paste suspicious message here" />
      <div className="actions">
        <button onClick={onAnalyze}>Analyze</button>
        <button onClick={onReport}>Report Scam</button>
      </div>
      {result && (
        <div className="result">
          <h3>Trust Score: {result.trust_score}</h3>
          <p>Heuristic Score: {result.heuristic_score}</p>
          <p>Model Score: {String(result.model_score)}</p>
          <h4>Reasons</h4>
          <ul>{result.reasons.map((r,i)=><li key={i}>{r}</li>)}</ul>
          <h4>Recommended Action</h4>
          <p>{result.recommended_action}</p>
        </div>
      )}
    </div>
  )
}
