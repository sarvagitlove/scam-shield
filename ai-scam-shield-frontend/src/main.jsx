import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Analyze from './pages/Analyze'
import Recovery from './pages/Recovery'
import './styles.css'

function App(){
  return (
    <BrowserRouter>
      <div className="nav">
        <Link to="/">Analyze</Link>
        <Link to="/recovery">Recovery</Link>
      </div>
      <Routes>
        <Route path="/" element={<Analyze/>} />
        <Route path="/recovery" element={<Recovery/>} />
      </Routes>
    </BrowserRouter>
  )
}

createRoot(document.getElementById('root')).render(<App />)
