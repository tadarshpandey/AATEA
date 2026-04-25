import { useState, useRef, useEffect } from 'react'

function App() {
  const [task, setTask] = useState('')
  const [loading, setLoading] = useState(false)
  const [plan, setPlan] = useState(null)
  const [liveLogs, setLiveLogs] = useState([])
  const [finalResult, setFinalResult] = useState(null)
  const [error, setError] = useState(null)
  
  const ws = useRef(null)

  useEffect(() => {
    return () => {
      if (ws.current) ws.current.close()
    }
  }, [])

  // Use deployed URL or local dev URL
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://aatea.onrender.com';
  
  // Convert http:// or https:// to ws:// or wss://
  const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');

  const handlePlan = async (e) => {
    e.preventDefault()
    if (!task.trim()) return
    
    setLoading(true)
    setError(null)
    setPlan(null)
    setLiveLogs([])
    setFinalResult(null)
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/task/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent: task }),
      });
      
      const data = await response.json();
      
      if (data.status === 'error' || data.status === 'failed') {
        setError(data.message || data.error);
      } else {
        setPlan(data.plan);
      }
    } catch (err) {
      setError("Failed to connect to the backend server. Is it running?");
    } finally {
      setLoading(false);
    }
  }

  const handleExecute = async () => {
    setLoading(true)
    setError(null)
    setLiveLogs([])
    
    // Connect to WebSocket for live logs
    ws.current = new WebSocket(`${WS_BASE_URL}/ws/logs`)
    ws.current.onmessage = (event) => {
      try {
        const logData = JSON.parse(event.data)
        setLiveLogs(prev => [...prev, logData])
      } catch(e) {}
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/task/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent: task, plan: plan }),
      });
      
      const data = await response.json();
      
      if (data.status === 'error' || data.status === 'failed') {
        setError(data.error);
      } else {
        setFinalResult(data.results);
      }
    } catch (err) {
      setError("Execution failed.");
    } finally {
      setLoading(false);
      if (ws.current) ws.current.close();
    }
  }

  return (
    <div className="app-container">
      <h1>AATEA</h1>
      <p className="subtitle">Autonomous AI Task Execution Agent</p>
      
      <form onSubmit={handlePlan}>
        <textarea 
          placeholder="Describe the task you want to execute... (e.g. Fetch latest github issues from facebook/react and send a summary to slack)"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          disabled={loading || plan}
        />
        
        {!plan && (
          <button type="submit" disabled={loading || !task.trim()}>
            {loading ? <><div className="spinner"></div> Generating Plan...</> : 'Generate Execution Plan'}
          </button>
        )}
      </form>
      
      {error && (
        <div className="result-box" style={{ borderColor: 'var(--error)' }}>
          <h3 style={{ color: 'var(--error)' }}>Error</h3>
          <p>{error}</p>
        </div>
      )}
      
      {plan && (
        <div className="result-box">
          <h3>Execution Plan Review</h3>
          <p style={{color: 'var(--text-muted)', marginBottom: '1rem'}}>
            The AI has generated the following execution plan. Please review and approve before execution begins.
          </p>
          
          {plan.steps.map((step, idx) => (
            <div key={idx} className="log-entry">
              <strong>Step {idx+1}:</strong> [{step.step_id}] Use <code>{step.tool_name}</code>
            </div>
          ))}
          
          {!finalResult && !loading && (
            <div style={{display: 'flex', gap: '1rem', marginTop: '1.5rem'}}>
              <button onClick={() => setPlan(null)} style={{background: 'rgba(255,255,255,0.1)'}}>
                Cancel / Edit
              </button>
              <button onClick={handleExecute} style={{background: 'var(--success)'}}>
                Approve & Execute
              </button>
            </div>
          )}
        </div>
      )}
      
      {(liveLogs.length > 0 || finalResult) && (
        <div className="result-box">
          <h3>Live Execution Logs</h3>
          <div className="terminal-logs" style={{background: 'rgba(0,0,0,0.5)', padding: '1rem', borderRadius: '0.5rem', fontFamily: 'monospace', fontSize: '0.875rem', marginBottom: '1.5rem', maxHeight: '300px', overflowY: 'auto'}}>
            {liveLogs.map((log, i) => (
              <div key={i} style={{
                color: log.status === 'error' ? '#ef4444' : log.status === 'success' ? '#10b981' : '#60a5fa',
                marginBottom: '0.25rem'
              }}>
                &gt; {log.message}
              </div>
            ))}
            {loading && <div style={{color: '#94a3b8', animation: 'pulse 1.5s infinite'}}>...</div>}
          </div>
          
          {finalResult && (
            <>
              <h3 style={{color: 'var(--success)'}}>Final Output</h3>
              <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
                {Object.entries(finalResult).map(([stepId, output]) => (
                  <div key={stepId} style={{background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '0.5rem', borderLeft: '4px solid var(--accent)'}}>
                    <strong style={{color: '#60a5fa', display: 'block', marginBottom: '0.5rem'}}>{stepId.toUpperCase()}</strong>
                    <div style={{whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: '0.95rem', color: 'var(--text-main)'}}>
                      {typeof output === 'string' ? output : JSON.stringify(output, null, 2)}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default App
