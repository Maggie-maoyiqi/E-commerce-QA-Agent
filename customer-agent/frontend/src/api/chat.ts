const BASE = '/api/v1'

export interface ChatResponse {
  session_id: string
  answer: string
  intent: string
  sources: string[]
}

export interface SessionInfo {
  session_id: string
  created_at: string
  updated_at: string
  message_count: number
  history?: Array<{ role: string; content: string }>
}

export async function sendMessage(message: string, sessionId: string | null): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function createSession(): Promise<SessionInfo> {
  const res = await fetch(`${BASE}/sessions`, { method: 'POST' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function listSessions(): Promise<SessionInfo[]> {
  const res = await fetch(`${BASE}/sessions`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json()
  return data.sessions
}

export async function getSession(sessionId: string): Promise<SessionInfo> {
  const res = await fetch(`${BASE}/sessions/${sessionId}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function deleteSession(sessionId: string): Promise<void> {
  await fetch(`${BASE}/sessions/${sessionId}`, { method: 'DELETE' })
}
