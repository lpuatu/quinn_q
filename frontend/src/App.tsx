import React, { useEffect, useRef, useState } from 'react'

export default function App() {
  const [message, setMessage] = useState('Explain the Kami phase in Rising Sun.')
  type ChatMessage = { role: 'user' | 'assistant'; text: string }
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const endRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Rulebooks state
  const [showBooks, setShowBooks] = useState(false)
  const [rulebooks, setRulebooks] = useState<string[]>([])
  const [selectedRulebook, setSelectedRulebook] = useState<string>('')

  const send = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    const userText = message.trim()
    if (!userText) {
      setLoading(false)
      return
    }
    setMessages((m) => [...m, { role: 'user', text: userText }])
    setMessage('')
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText, rulebook: selectedRulebook || undefined })
      })
      if (!res.ok) {
        const txt = await res.text()
        throw new Error(`${res.status} ${res.statusText}: ${txt}`)
      }
      const data = await res.json()
      setMessages((m) => [...m, { role: 'assistant', text: data.reply ?? '' }])
    } catch (err: any) {
      setError(err.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Load available rulebooks on mount
  const refreshRulebooks = async () => {
    try {
      const res = await fetch('/api/rulebooks')
      if (!res.ok) throw new Error(await res.text())
      const list: string[] = await res.json()
      setRulebooks(list)
      if (!selectedRulebook) {
        const preferred = list.find(n => n.toLowerCase().includes('rising_sun')) || list[0]
        if (preferred) setSelectedRulebook(preferred)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load rulebooks')
    }
  }

  useEffect(() => {
    refreshRulebooks()
  }, [])

  const onFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    try {
      const fd = new FormData()
      fd.append('file', f)
      const res = await fetch('/api/rulebooks', { method: 'POST', body: fd })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      await refreshRulebooks()
      if (data?.filename) setSelectedRulebook(data.filename)
    } catch (err: any) {
      setError(err.message || 'Upload failed')
    } finally {
      e.target.value = ''
    }
  }

  return (
    <div style={{ fontFamily: 'Inter, system-ui, Avenir, Helvetica, Arial, sans-serif', padding: 24, maxWidth: 900 }}>
      <h1>Quinn Q</h1>
      <p>Ask questions about Rising Sun, powered by the rulebook.</p>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 8 }}>
        <button type="button" onClick={() => setShowBooks(s => !s)}
          style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #475569', background: '#0f172a', color: '#e2e8f0', cursor: 'pointer' }}>
          Rulebooks {showBooks ? '▴' : '▾'}
        </button>
        {selectedRulebook && (
          <span style={{ color: '#94a3b8' }}>Selected: {selectedRulebook}</span>
        )}
      </div>

      {showBooks && (
        <div style={{ marginTop: 8, padding: 12, border: '1px solid #334155', borderRadius: 8, background: '#0b1220' }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
            <select value={selectedRulebook} onChange={(e) => setSelectedRulebook(e.target.value)}
              style={{ padding: 8, background: '#0f172a', color: '#e2e8f0', border: '1px solid #475569', borderRadius: 6 }}>
              <option value="" disabled>{rulebooks.length ? 'Choose a rulebook…' : 'No rulebooks found'}</option>
              {rulebooks.map(name => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>

            <input ref={fileInputRef} type="file" accept="application/pdf,.pdf" onChange={onFileChange}
              style={{ color: '#e2e8f0' }} />

            <button type="button" onClick={refreshRulebooks}
              style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #475569', background: '#0f172a', color: '#e2e8f0', cursor: 'pointer' }}>
              Refresh
            </button>
          </div>
        </div>
      )}

      {/* Chat transcript */}
      <div style={{
        height: 360,
        overflowY: 'auto',
        padding: 12,
        border: '1px solid #334155',
        borderRadius: 8,
        background: '#0b1220'
      }}>
        {messages.map((m, i) => (
          <div key={i} style={{
            display: 'flex',
            justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
            margin: '6px 0'
          }}>
            <div style={{
              maxWidth: '75%',
              padding: '8px 12px',
              borderRadius: 12,
              border: '1px solid #475569',
              background: m.role === 'user' ? '#1e293b' : '#0f172a',
              color: '#e2e8f0',
              whiteSpace: 'pre-wrap'
            }}>
              {m.text}
            </div>
          </div>
        ))}
        <div ref={endRef} />
      </div>

      <form onSubmit={send} style={{ display: 'flex', gap: 8, margin: '16px 0' }}>
        <input
          value={message}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMessage(e.target.value)}
          placeholder="Type your question..."
          style={{ flex: 1, padding: 10, borderRadius: 8, border: '1px solid #475569', background: '#0b1220', color: '#e2e8f0' }}
        />
        <button disabled={loading} style={{ padding: '10px 16px', borderRadius: 8, border: '1px solid #475569', background: '#1e293b', color: '#e2e8f0', cursor: 'pointer' }}>
          {loading ? 'Sending…' : 'Send'}
        </button>
      </form>

      {error && (
        <div style={{ color: '#ef4444' }}>Error: {error}</div>
      )}


    </div>
  )
}
