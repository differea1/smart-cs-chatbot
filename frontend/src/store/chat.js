import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const sessionId = ref('')
  const messages = ref([])
  const isStreaming = ref(false)

  function setSessionId(id) {
    sessionId.value = id
    localStorage.setItem('cs_session_id', id)
  }

  function loadSessionId() {
    const saved = localStorage.getItem('cs_session_id')
    if (saved) sessionId.value = saved
  }

  function addUserMessage(content) {
    messages.value.push({ role: 'user', content, id: Date.now() })
  }

  function addAIMessage() {
    const msg = { role: 'assistant', content: '', id: Date.now(), isStreaming: true }
    messages.value.push(msg)
    return msg
  }

  function clearMessages() {
    messages.value = []
    sessionId.value = ''
    localStorage.removeItem('cs_session_id')
  }

  return { sessionId, messages, isStreaming, setSessionId, loadSessionId, addUserMessage, addAIMessage, clearMessages }
})
