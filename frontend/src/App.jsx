import { useState } from 'react'
import './App.css'

function App() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Hello! I am your CloudOps AI Assistant. I can help you monitor AWS resources, investigate infrastructure issues, and answer your cloud operations questions.'
    }
  ])
  const [loading, setLoading] = useState(false)

  const sendMessage = async (event) => {
    event.preventDefault()

    const prompt = question.trim()
    if (!prompt || loading) return

    setMessages(previous => [
      ...previous,
      { role: 'user', text: prompt }
    ])
    setQuestion('')
    setLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: prompt })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Unable to process your request')
      }

      setMessages(previous => [
        ...previous,
        { role: 'assistant', text: data.answer }
      ])
    } catch (error) {
      setMessages(previous => [
        ...previous,
        { role: 'assistant', text: `Error: ${error.message}` }
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">C</div>
          <div>
            <h2>CloudOps AI</h2>
            <span>INTELLIGENCE PLATFORM</span>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav>
          <a className="nav-item active" href="#chat">
            <span>◈</span> AI Assistant
          </a>
          <a className="nav-item" href="#overview">
            <span>▦</span> Overview
          </a>
          <a className="nav-item" href="#resources">
            <span>▣</span> AWS Resources
          </a>
          <a className="nav-item" href="#monitoring">
            <span>◷</span> Monitoring
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="connection">
            <span className="status-dot"></span>
            AI Agent Connected
          </div>
          <div className="user-profile">
            <div className="avatar">CA</div>
            <div>
              <strong>Cloud Administrator</strong>
              <span>Administrator</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="breadcrumb">Workspace / <strong>AI Assistant</strong></div>
            <h1>CloudOps AI Assistant</h1>
          </div>
          <div className="topbar-right">
            <span className="region">AWS · ap-south-2</span>
            <span className="online"><span className="status-dot"></span> Online</span>
          </div>
        </header>

        <section className="stats" id="overview">
          <div className="stat-card">
            <span className="stat-label">AI MODEL</span>
            <strong>Nova Lite</strong>
            <span className="stat-description">Amazon Bedrock</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">AWS REGION</span>
            <strong>Hyderabad</strong>
            <span className="stat-description">ap-south-2</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">AI AGENT</span>
            <strong className="healthy">Operational</strong>
            <span className="stat-description">Backend connected</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">CAPABILITIES</span>
            <strong>EC2 · S3</strong>
            <span className="stat-description">Live inventory APIs</span>
          </div>
        </section>

        <section className="chat-panel" id="chat">
          <div className="chat-header">
            <div className="assistant-avatar">✦</div>
            <div>
              <h2>CloudOps Assistant</h2>
              <span>Ask questions about your AWS infrastructure</span>
            </div>
            <div className="chat-live"><span className="status-dot"></span> Ready</div>
          </div>

          <div className="chat-messages">
            {messages.map((message, index) => (
              <div className={`message ${message.role}`} key={index}>
                <div className="message-avatar">
                  {message.role === 'assistant' ? '✦' : 'CA'}
                </div>
                <div className="message-content">
                  <div className="message-author">
                    {message.role === 'assistant' ? 'CloudOps AI' : 'You'}
                  </div>
                  <div className="message-text">{message.text}</div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="message assistant">
                <div className="message-avatar">✦</div>
                <div className="message-content">
                  <div className="message-author">CloudOps AI</div>
                  <div className="message-text loading-text">Analyzing your request...</div>
                </div>
              </div>
            )}
          </div>

          <div className="suggestions">
            <span>Try asking:</span>
            {[
              'Show my EC2 instances',
              'List my S3 buckets',
              'How many EC2 instances are running?'
            ].map(item => (
              <button key={item} onClick={() => setQuestion(item)}>
                {item}
              </button>
            ))}
          </div>

          <form className="chat-input" onSubmit={sendMessage}>
            <input
              value={question}
              onChange={event => setQuestion(event.target.value)}
              placeholder="Ask anything about your AWS infrastructure..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !question.trim()}>
              {loading ? '...' : 'Send ↑'}
            </button>
          </form>
          <div className="input-note">
            AI responses should be verified before making infrastructure changes.
          </div>
        </section>

        <footer>CloudOps AI Platform · Powered by Amazon Bedrock Nova Lite</footer>
      </main>
    </div>
  )
}

export default App
