// src/App.jsx
import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [domain, setDomain] = useState('')
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://91.107.140.150:8000/lookup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ domain }),
      })
      
      if (!response.ok) {
        throw new Error('Domain not found')
      }
      
      const data = await response.json()
      setResult(data)
      fetchHistory()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchHistory = async () => {
    try {
      const response = await fetch('http://91.107.140.150:8000/history?limit=10')
      const data = await response.json()
      setHistory(data)
    } catch (err) {
      console.error('Failed to fetch history:', err)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  return (
    <div className="container">
      <h1>Domain to IP Lookup</h1>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          placeholder="Enter domain (e.g., google.com)"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Looking up...' : 'Lookup'}
        </button>
      </form>
      
      {error && <div className="error">{error}</div>}
      
      {result && (
        <div className="result">
          <h2>Result</h2>
          <p><strong>Domain:</strong> {result.domain}</p>
          <p><strong>IP Address:</strong> {result.ip_address}</p>
          <p><strong>Source:</strong> {result.source}</p>
          <p><strong>Time:</strong> {new Date(result.timestamp).toLocaleString()}</p>
        </div>
      )}
      
      <div className="history">
        <h2>Recent Lookups</h2>
        <table>
          <thead>
            <tr>
              <th>Domain</th>
              <th>IP Address</th>
              <th>Time</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item, index) => (
              <tr key={index}>
                <td>{item.domain}</td>
                <td>{item.ip_address}</td>
                <td>{new Date(item.timestamp).toLocaleString()}</td>
                <td>{item.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default App