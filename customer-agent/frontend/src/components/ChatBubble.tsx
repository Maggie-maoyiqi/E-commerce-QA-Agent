import type { Message } from '../hooks/useChat'

const INTENT_LABELS: Record<string, string> = {
  general: '通用',
  knowledge: '知识检索',
  additional: '需补充信息',
}

const INTENT_COLORS: Record<string, string> = {
  general: '#6b7280',
  knowledge: '#2563eb',
  additional: '#d97706',
}

interface Props {
  message: Message
}

export function ChatBubble({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <div style={{
      display: 'flex',
      flexDirection: isUser ? 'row-reverse' : 'row',
      alignItems: 'flex-end',
      gap: '8px',
      marginBottom: '12px',
    }}>
      {/* Avatar */}
      <div style={{
        width: 32,
        height: 32,
        borderRadius: '50%',
        background: isUser ? '#2563eb' : '#10b981',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 14,
        color: '#fff',
        flexShrink: 0,
      }}>
        {isUser ? '我' : '客'}
      </div>

      <div style={{ maxWidth: '70%' }}>
        {/* Bubble */}
        <div style={{
          background: isUser ? '#2563eb' : '#fff',
          color: isUser ? '#fff' : '#111',
          padding: '10px 14px',
          borderRadius: isUser ? '18px 4px 18px 18px' : '4px 18px 18px 18px',
          fontSize: 14,
          lineHeight: 1.6,
          boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}>
          {message.content}
        </div>

        {/* Meta: intent + sources */}
        {!isUser && (message.intent || (message.sources && message.sources.length > 0)) && (
          <div style={{ marginTop: 4, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {message.intent && message.intent !== 'general' && (
              <span style={{
                fontSize: 11,
                background: INTENT_COLORS[message.intent] + '18',
                color: INTENT_COLORS[message.intent],
                border: `1px solid ${INTENT_COLORS[message.intent]}40`,
                borderRadius: 10,
                padding: '2px 8px',
              }}>
                {INTENT_LABELS[message.intent] ?? message.intent}
              </span>
            )}
            {message.sources && message.sources.slice(0, 3).map(s => (
              <span key={s} style={{
                fontSize: 11,
                background: '#f3f4f6',
                color: '#6b7280',
                border: '1px solid #e5e7eb',
                borderRadius: 10,
                padding: '2px 8px',
              }}>
                来源: {s}
              </span>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div style={{
          fontSize: 11,
          color: '#9ca3af',
          marginTop: 3,
          textAlign: isUser ? 'right' : 'left',
        }}>
          {message.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  )
}
