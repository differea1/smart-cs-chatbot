// Use absolute URL for Capacitor builds, relative for web
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export function sendMessageStream(message, sessionId, userId = 0, { onDelta, onDone, onError }) {
  const params = new URLSearchParams()
  params.append('message', message)
  params.append('user_id', userId)
  if (sessionId) params.append('session_id', sessionId)

  fetch(`${API_BASE}/chat/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      session_id: sessionId || null,
      message,
      message_type: 'text',
    }),
  }).then(async (response) => {
    if (!response.ok) {
      onError?.(new Error(`HTTP ${response.status}`))
      return
    }
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.delta) onDelta?.(data.delta)
            if (line.includes('"event":"done"') || data.session_id) {
              // It's in the done event format
            }
          } catch { /* skip parse errors */ }
        }
        if (line.startsWith('event: done')) {
          continue
        }
        if (line.startsWith('data: ') && line.includes('"session_id"')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.session_id) onDone?.(data)
          } catch { /* skip */ }
        }
      }
    }
    onDone?.({})
  }).catch(err => onError?.(err))
}

export function submitFeedback(messageId, rating) {
  return fetch(`${API_BASE}/chat/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message_id: messageId, rating }),
  })
}
