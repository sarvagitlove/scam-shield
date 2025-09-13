import React, { useState } from 'react'

export default function Recovery(){
  const [text,setText] = useState('')
  const [result,setResult] = useState(null)

  async function onRecover(){
    const res = await fetch('http://localhost:8000/recovery', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({conversation_text: text})})
    const j = await res.json()
    setResult(j)
  }

  function downloadReport(){
    const blob = new Blob([JSON.stringify(result, null, 2)], {type:'text/plain'})
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'recovery_report.txt'; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="container">
      <h2>Recovery</h2>
      <textarea value={text} onChange={e=>setText(e.target.value)} placeholder="Paste scam conversation here" />
      <div className="actions">
        <button onClick={onRecover}>Analyze Recovery</button>
        <button onClick={downloadReport} disabled={!result}>Download Report</button>
      </div>
      {result && (
        <div className="result">
          <h4>Detected PII</h4>
          <ul>{result.detected_pii.map((p,i)=><li key={i}>{p}</li>)}</ul>
          <p>Risk Level: {result.risk_level}</p>
          <h4>What to do</h4>
          <ul>{result.what_to_do.map((w,i)=><li key={i}>{w}</li>)}</ul>
        </div>
      )}
    </div>
  )
}
