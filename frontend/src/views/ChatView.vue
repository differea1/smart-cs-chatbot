<template>
  <div class="chat-container">
    <!-- Header -->
    <header class="chat-header">
      <div class="header-left">
        <div class="brand-logo">极米</div>
        <div>
          <h2>小极 · 智能售后助手</h2>
          <span class="online-badge">{{ isOnline ? '● 在线' : '● 离线' }}</span>
        </div>
      </div>
      <button class="btn-clear" @click="handleClear">新对话</button>
    </header>

    <!-- Offline banner -->
    <div class="offline-banner" v-if="!isOnline">
      当前无网络连接，部分功能不可用
    </div>

    <!-- Messages -->
    <div class="msg-list" ref="listRef">
      <!-- Quick entry -->
      <div class="quick-cards" v-if="messages.length === 0">
        <h3>您好！请问需要什么帮助？ 😊</h3>
        <p class="subtitle">选择以下快捷入口或直接输入您的问题</p>
        <div class="card-grid">
          <div class="qcard" v-for="q in quickActions" :key="q.label" @click="send(q.text)">
            <span class="qicon">{{ q.icon }}</span>
            <span class="qlabel">{{ q.label }}</span>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div v-for="(msg, i) in messages" :key="msg.id" :class="['msg-row', msg.role]">
        <div class="msg-bubble" :class="msg.role">
          <div v-if="msg.role === 'assistant' && msg.content" v-html="renderMd(msg.content)"></div>
          <div v-if="msg.role === 'user'">{{ msg.content }}</div>
          <div class="typing" v-if="msg.isStreaming && !msg.content">
            <span></span><span></span><span></span>
          </div>
          <!-- Rate bar -->
          <div class="rate-bar" v-if="msg.role === 'assistant' && !msg.isStreaming && msg.content && msg.showRate">
            <span>这个回答有帮助吗？</span>
            <span class="stars">
              <template v-for="s in 5" :key="s">
                <span class="star" :class="{ active: msg.rating >= s }" @click="rateMsg(msg, s)">{{ msg.rating >= s ? '★' : '☆' }}</span>
              </template>
            </span>
            <span v-if="msg.rated" class="thanks">感谢反馈！</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="input-bar">
      <input
        ref="inputRef"
        v-model="inputText"
        @keyup.enter="send()"
        placeholder="输入您的问题..."
        :disabled="isStreaming"
        autofocus
      />
      <button @click="send()" :disabled="!inputText.trim() || isStreaming" class="btn-send">
        {{ isStreaming ? '回复中' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { marked } from 'marked'
import { useChatStore } from '@/store/chat'
import { isOnline } from '@/utils/pwa'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const chatStore = useChatStore()
const messages = ref([])
const inputText = ref('')
const isStreaming = ref(false)
const listRef = ref(null)
const inputRef = ref(null)

const quickActions = [
  { icon: '📦', label: '查询订单', text: '我想查询我的订单物流状态' },
  { icon: '↩️', label: '申请退货', text: '我想申请退货' },
  { icon: '🔧', label: '故障排查', text: '我的设备出现故障了' },
  { icon: 'ℹ️', label: '产品咨询', text: 'X1 Pro 的亮度和参数是什么？' },
]

onMounted(() => {
  chatStore.loadSessionId()
})

function renderMd(text) {
  try {
    return marked.parse(text, { breaks: true })
  } catch {
    return text
  }
}

async function send(text) {
  const msg = (text || inputText.value).trim()
  if (!msg) return

  // Add user message
  messages.value.push({ role: 'user', content: msg, id: Date.now() })
  inputText.value = ''
  isStreaming.value = true

  // Add AI placeholder
  const aiMsg = { role: 'assistant', content: '', id: Date.now() + 1, isStreaming: true, showRate: false, rating: 0, rated: false }
  messages.value.push(aiMsg)
  scrollBottom()

  try {
    const response = await fetch(`${API_BASE}/chat/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: 0,
        session_id: chatStore.sessionId || null,
        message: msg,
        message_type: 'text',
      }),
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)

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
            if (data.delta) {
              aiMsg.content += data.delta
              scrollBottom()
            }
          } catch {}
        }
        if (line.startsWith('event: done')) {
          const nextLine = buffer || ''
          try {
            const doneLine = nextLine.startsWith('data: ') ? JSON.parse(nextLine.slice(6)) : null
            if (doneLine?.session_id) {
              chatStore.setSessionId(doneLine.session_id)
              aiMsg.sessionData = doneLine
            }
          } catch {}
        }
      }
    }
  } catch (e) {
    aiMsg.content = `抱歉，服务暂时不可用。错误：${e.message}`
  }

  aiMsg.isStreaming = false
  aiMsg.showRate = true
  isStreaming.value = false
  scrollBottom()
}

function rateMsg(msg, rating) {
  msg.rating = rating
  msg.rated = true
  if (msg.sessionData?.message_id) {
    fetch(`${API_BASE}/chat/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message_id: msg.sessionData.message_id, rating }),
    }).catch(() => {})
  }
}

function handleClear() {
  messages.value = []
  chatStore.clearMessages()
}

function scrollBottom() {
  nextTick(() => {
    if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight
  })
}
</script>

<style scoped>
.chat-container { display: flex; flex-direction: column; height: 100vh; max-width: 800px; margin: 0 auto; background: #f5f5f5; }
.chat-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: linear-gradient(135deg, #1890ff, #096dd9); color: #fff; }
.header-left { display: flex; align-items: center; gap: 12px; }
.brand-logo { width: 36px; height: 36px; background: rgba(255,255,255,.2); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
.header-left h2 { font-size: 17px; font-weight: 600; }
.online-badge { font-size: 12px; opacity: .85; }
.btn-clear { background: rgba(255,255,255,.2); border: none; color: #fff; padding: 6px 14px; border-radius: 16px; font-size: 13px; cursor: pointer; }

.msg-list { flex: 1; overflow-y: auto; padding: 16px; }
.quick-cards { text-align: center; padding: 30px 0; }
.quick-cards h3 { font-size: 20px; margin-bottom: 8px; }
.subtitle { color: #999; font-size: 14px; margin-bottom: 24px; }
.card-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 360px; margin: 0 auto; }
.qcard { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 20px 12px; background: #fff; border-radius: 12px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,.06); transition: transform .15s; }
.qcard:active { transform: scale(.97); }
.qicon { font-size: 32px; }
.qlabel { font-size: 14px; font-weight: 500; color: #333; }

.msg-row { display: flex; margin-bottom: 16px; }
.msg-row.user { justify-content: flex-end; }
.msg-row.assistant { justify-content: flex-start; }
.msg-bubble { max-width: 82%; padding: 12px 16px; border-radius: 12px; line-height: 1.65; font-size: 15px; }
.msg-bubble.user { background: #1890ff; color: #fff; border-bottom-right-radius: 4px; }
.msg-bubble.assistant { background: #fff; border-bottom-left-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.msg-bubble.assistant :deep(p) { margin-bottom: 8px; }
.msg-bubble.assistant :deep(p:last-child) { margin-bottom: 0; }
.msg-bubble.assistant :deep(ul), .msg-bubble.assistant :deep(ol) { padding-left: 20px; margin: 6px 0; }
.msg-bubble.assistant :deep(strong) { color: #333; }

.typing { display: flex; gap: 4px; padding: 8px 0; }
.typing span { width: 8px; height: 8px; border-radius: 50%; background: #ccc; animation: bounce 1.4s infinite ease-in-out; }
.typing span:nth-child(2) { animation-delay: .16s; }
.typing span:nth-child(3) { animation-delay: .32s; }
@keyframes bounce { 0%,80%,100%{transform:scale(0)}40%{transform:scale(1)} }

.rate-bar { margin-top: 10px; padding-top: 10px; border-top: 1px solid #f0f0f0; font-size: 13px; color: #999; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.stars { color: #faad14; cursor: pointer; }
.star { font-size: 20px; margin: 0 1px; }
.thanks { color: #52c41a; }

.input-bar { display: flex; padding: 10px 16px; background: #fff; gap: 8px; border-top: 1px solid #eee; }
.offline-banner { background: #fff3cd; color: #856404; text-align: center; padding: 8px; font-size: 13px; }
.input-bar input { flex: 1; padding: 10px 16px; border: 1px solid #e0e0e0; border-radius: 24px; font-size: 15px; outline: none; transition: border-color .2s; }
.input-bar input:focus { border-color: #1890ff; }
.input-bar input:disabled { background: #f5f5f5; }
.btn-send { padding: 10px 22px; background: #1890ff; color: #fff; border: none; border-radius: 24px; font-size: 15px; cursor: pointer; white-space: nowrap; }
.btn-send:disabled { background: #ccc; cursor: not-allowed; }
</style>
