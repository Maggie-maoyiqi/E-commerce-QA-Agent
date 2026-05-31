import { useState, useRef, useEffect, KeyboardEvent } from 'react'
import { useChat } from './hooks/useChat'
import { ChatBubble } from './components/ChatBubble'

const QUICK_PROMPTS = [
  '订单1001的状态是什么？',
  '门铃支持夜视功能吗？',
  '如何申请退货退款？',
  '产品的保修期是多久？',
]

export default function App() {
  const { messages, sessionId, loading, error, send, newSession } = useChat()
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    if (input.trim()) {
      send(input.trim())
      setInput('')
    }
  }

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={{
      width: '100%',
      maxWidth: 760,
      height: '100vh',
      maxHeight: 700,
      display: 'flex',
      flexDirection: 'column',
      background: '#fff',
      borderRadius: 16,
      boxShadow: '0 4px 24px rgba(0,0,0,0.12)',
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
        color: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0,
      }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 16 }}>智能客服助手</div>
          <div style={{ fontSize: 12, opacity: 0.8, marginTop: 2 }}>
            {sessionId ? `会话: ${sessionId.slice(0, 8)}…` : '新会话'}
          </div>
        </div>
        <button
          onClick={newSession}
          style={{
            background: 'rgba(255,255,255,0.2)',
            border: '1px solid rgba(255,255,255,0.4)',
            color: '#fff',
            borderRadius: 8,
            padding: '6px 12px',
            fontSize: 13,
            cursor: 'pointer',
          }}
        >
          新会话
        </button>
      </div>

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px 20px',
        background: '#f8fafc',
      }}>
        {messages.map(msg => (
          <ChatBubble key={msg.id} message={msg} />
        ))}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, marginBottom: 12 }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              background: '#10b981', display: 'flex',
              alignItems: 'center', justifyContent: 'center',
              color: '#fff', fontSize: 14, flexShrink: 0,
            }}>客</div>
            <div style={{
              background: '#fff', borderRadius: '4px 18px 18px 18px',
              padding: '10px 14px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
            }}>
              <TypingDots />
            </div>
          </div>
        )}

        {error && (
          <div style={{
            background: '#fef2f2', border: '1px solid #fecaca',
            color: '#dc2626', borderRadius: 8, padding: '10px 14px',
            fontSize: 13, marginBottom: 12,
          }}>
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Quick prompts */}
      <div style={{
        padding: '8px 16px',
        borderTop: '1px solid #f1f5f9',
        display: 'flex',
        gap: 6,
        flexWrap: 'wrap',
        background: '#fff',
        flexShrink: 0,
      }}>
        {QUICK_PROMPTS.map(p => (
          <button
            key={p}
            onClick={() => { send(p) }}
            disabled={loading}
            style={{
              background: '#f1f5f9',
              border: '1px solid #e2e8f0',
              borderRadius: 16,
              padding: '4px 10px',
              fontSize: 12,
              color: '#475569',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.5 : 1,
              whiteSpace: 'nowrap',
            }}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input */}
      <div style={{
        padding: '12px 16px',
        borderTop: '1px solid #e2e8f0',
        display: 'flex',
        gap: 8,
        alignItems: 'flex-end',
        background: '#fff',
        flexShrink: 0,
      }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="输入您的问题… (Enter 发送，Shift+Enter 换行)"
          disabled={loading}
          rows={1}
          style={{
            flex: 1,
            resize: 'none',
            border: '1px solid #e2e8f0',
            borderRadius: 10,
            padding: '10px 14px',
            fontSize: 14,
            fontFamily: 'inherit',
            outline: 'none',
            lineHeight: 1.5,
            maxHeight: 120,
            overflowY: 'auto',
          }}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          style={{
            background: loading || !input.trim() ? '#cbd5e1' : '#2563eb',
            color: '#fff',
            border: 'none',
            borderRadius: 10,
            padding: '10px 18px',
            fontSize: 14,
            fontWeight: 600,
            cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
            flexShrink: 0,
            height: 42,
            transition: 'background 0.2s',
          }}
        >
          发送
        </button>
      </div>
    </div>
  )
}

function TypingDots() {
  return (
    <div style={{ display: 'flex', gap: 4, alignItems: 'center', height: 20 }}>
      {[0, 1, 2].map(i => (
        <span key={i} style={{
          width: 6, height: 6,
          borderRadius: '50%',
          background: '#94a3b8',
          display: 'inline-block',
          animation: `bounce 1.2s ${i * 0.2}s infinite`,
        }} />
      ))}
      <style>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  )
}
