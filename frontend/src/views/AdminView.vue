<template>
  <div class="admin-page" v-if="userStore.token">
    <div class="offline-banner" v-if="!isOnline">当前无网络连接，数据可能不是最新</div>
    <!-- Sidebar -->
    <aside class="sidebar">
      <h3>极米管理后台</h3>
      <nav>
        <a :class="{ active: tab === 'dashboard' }" @click="tab = 'dashboard'">📊 仪表盘</a>
        <a :class="{ active: tab === 'conversations' }" @click="tab = 'conversations'">💬 对话记录</a>
        <a :class="{ active: tab === 'knowledge' }" @click="tab = 'knowledge'">📚 知识库</a>
      </nav>
      <div class="user-info">
        <span>{{ userStore.username }} ({{ userStore.role }})</span>
        <button @click="logout">退出</button>
      </div>
    </aside>

    <!-- Main -->
    <main class="main">
      <!-- Dashboard -->
      <div v-if="tab === 'dashboard'">
        <h2>仪表盘</h2>
        <div class="stats">
          <div class="stat-card"><span class="num">{{ dash.total_conversations }}</span><span class="lbl">总对话数</span></div>
          <div class="stat-card"><span class="num">{{ dash.today_conversations }}</span><span class="lbl">今日对话</span></div>
          <div class="stat-card"><span class="num">{{ dash.avg_satisfaction }}</span><span class="lbl">平均满意度</span></div>
          <div class="stat-card"><span class="num">{{ dash.escalation_rate }}%</span><span class="lbl">升级率</span></div>
        </div>
      </div>

      <!-- Conversations -->
      <div v-if="tab === 'conversations'">
        <h2>对话记录</h2>
        <div class="conv-list">
          <div v-for="c in conversations" :key="c.id" class="conv-item" @click="viewMessages(c.id)">
            <div>
              <strong>#{{ c.id }}</strong> {{ c.title }}
              <span class="tag" :class="c.sentiment_trend">{{ c.sentiment_trend }}</span>
              <span class="tag">{{ c.intent_type }}</span>
            </div>
            <div class="conv-meta">{{ c.message_count }} 条消息 · {{ c.created_at?.slice(0, 10) }}</div>
          </div>
        </div>
        <!-- Message detail -->
        <div v-if="selectedConv" class="msg-detail">
          <h3>对话 #{{ selectedConv }} <button @click="selectedConv = null; msgDetail = []">关闭</button></h3>
          <div v-for="m in msgDetail" :key="m.id" :class="['msg-item', m.role]">
            <span class="role-tag">{{ m.role === 'user' ? '用户' : 'AI' }}</span>
            {{ m.content?.slice(0, 200) }}{{ m.content?.length > 200 ? '...' : '' }}
          </div>
        </div>
      </div>

      <!-- Knowledge -->
      <div v-if="tab === 'knowledge'">
        <h2>知识库管理</h2>
        <div class="kb-grid">
          <div v-for="item in kbItems" :key="item.id" class="kb-card">
            <h4>{{ item.title }}</h4>
            <p>{{ item.content?.slice(0, 100) }}...</p>
            <div class="kb-meta">
              <span class="tag">{{ item.type }}</span>
              <span>ID: {{ item.id }}</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { isOnline } from '@/utils/pwa'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const router = useRouter()
const userStore = useUserStore()
const tab = ref('dashboard')
const dash = ref({ total_conversations: 0, today_conversations: 0, avg_satisfaction: 0, escalation_rate: 0 })
const conversations = ref([])
const kbItems = ref([])
const selectedConv = ref(null)
const msgDetail = ref([])

onMounted(() => {
  userStore.loadAuth()
  if (!userStore.token) { router.push('/login'); return }
  loadDashboard()
})

async function api(url) {
  const res = await fetch(url, { headers: { Authorization: `Bearer ${userStore.token}` } })
  return res.json()
}

async function loadDashboard() {
  dash.value = await api(`${API_BASE}/admin/dashboard`)
}

async function viewMessages(convId) {
  if (tab.value !== 'conversations') {
    tab.value = 'conversations'
    conversations.value = (await api(`${API_BASE}/admin/conversations?page_size=50`)).items || []
  }
  selectedConv.value = convId
  msgDetail.value = await api(`${API_BASE}/admin/messages/${convId}`)
}

async function loadKB() {
  const data = await api(`${API_BASE}/knowledge/items?page_size=50`)
  kbItems.value = data.items || []
}

watch(tab, (v) => {
  if (v === 'conversations') api(`${API_BASE}/admin/conversations?page_size=50`).then(d => conversations.value = d.items || [])
  if (v === 'knowledge') loadKB()
})

import { watch } from 'vue'

function logout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.offline-banner { background: #fff3cd; color: #856404; text-align: center; padding: 8px; font-size: 13px; }
.admin-page { display: flex; height: 100vh; }
.sidebar { width: 220px; background: #001529; color: #fff; display: flex; flex-direction: column; padding: 20px 0; }
.sidebar h3 { padding: 0 20px 20px; border-bottom: 1px solid rgba(255,255,255,.1); font-size: 16px; }
.sidebar nav { flex: 1; padding: 12px 0; }
.sidebar nav a { display: block; padding: 10px 20px; color: rgba(255,255,255,.65); cursor: pointer; font-size: 14px; transition: .2s; }
.sidebar nav a:hover, .sidebar nav a.active { color: #fff; background: rgba(255,255,255,.08); }
.user-info { padding: 12px 20px; border-top: 1px solid rgba(255,255,255,.1); font-size: 13px; display: flex; justify-content: space-between; align-items: center; }
.user-info button { background: #ff4d4f; color: #fff; border: none; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; }

.main { flex: 1; overflow-y: auto; padding: 24px; background: #f0f2f5; }
.main h2 { margin-bottom: 20px; }

.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }
.stat-card { background: #fff; padding: 24px; border-radius: 8px; text-align: center; }
.stat-card .num { display: block; font-size: 32px; font-weight: bold; color: #1890ff; }
.stat-card .lbl { font-size: 14px; color: #999; margin-top: 4px; }

.conv-item { background: #fff; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; cursor: pointer; }
.conv-item:hover { background: #fafafa; }
.conv-meta { font-size: 12px; color: #999; margin-top: 4px; }
.tag { display: inline-block; padding: 1px 8px; background: #f0f0f0; border-radius: 10px; font-size: 12px; margin: 0 4px; }
.tag.negative { background: #fff1f0; color: #ff4d4f; }
.tag.positive { background: #f6ffed; color: #52c41a; }

.msg-detail { background: #fff; border-radius: 8px; padding: 16px; margin-top: 16px; }
.msg-detail h3 { display: flex; justify-content: space-between; margin-bottom: 12px; }
.msg-item { padding: 8px 0; border-bottom: 1px solid #f5f5f5; font-size: 14px; }
.msg-item.user { color: #1890ff; }
.role-tag { display: inline-block; width: 32px; font-size: 11px; color: #999; }

.kb-grid { display: grid; gap: 12px; }
.kb-card { background: #fff; padding: 16px; border-radius: 8px; }
.kb-card h4 { margin-bottom: 8px; font-size: 15px; }
.kb-card p { color: #666; font-size: 13px; margin-bottom: 8px; }
.kb-meta { font-size: 12px; color: #999; display: flex; gap: 8px; }
</style>
