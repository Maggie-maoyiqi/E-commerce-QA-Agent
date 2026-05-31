import { useState, useCallback } from 'react'
import { sendMessage, createSession } from '../api/chat'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  intent?: string
  sources?: string[]
  timestamp: Date
}

export function useChat() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: '您好！我是智能客服助手，可以帮您查询订单、了解产品信息、处理售后问题。请问有什么可以帮您？',
      timestamp: new Date(),
    },
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const send = useCallback(async (text: string) => {
    if (!text.trim() || loading) return

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)
    setError(null)

    try {
      const res = await sendMessage(text, sessionId)
      if (!sessionId) setSessionId(res.session_id)

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.answer,
        intent: res.intent,
        sources: res.sources,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (e) {
      setError('无法连接到服务器，请确认后端是否启动。')
    } finally {
      setLoading(false)
    }
  }, [sessionId, loading])

  const newSession = useCallback(async () => {
    setSessionId(null)
    setMessages([
      {
        id: '0',
        role: 'assistant',
        content: '您好！我是智能客服助手，可以帮您查询订单、了解产品信息、处理售后问题。请问有什么可以帮您？',
        timestamp: new Date(),
      },
    ])
    setError(null)
  }, [])

  return { messages, sessionId, loading, error, send, newSession }
}
