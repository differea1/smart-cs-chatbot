<template>
  <div class="login-page">
    <div class="offline-banner" v-if="!isOnline">当前无网络连接，登录不可用</div>
    <div class="login-card">
      <h2>管理后台登录</h2>
      <input v-model="username" placeholder="用户名" @keyup.enter="focusPwd" />
      <input ref="pwdRef" v-model="password" type="password" placeholder="密码" @keyup.enter="login" />
      <button @click="login" :disabled="loading">{{ loading ? '登录中...' : '登 录' }}</button>
      <p class="error" v-if="error">{{ error }}</p>
      <p class="hint">默认账号: admin / admin123</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { isOnline } from '@/utils/pwa'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const router = useRouter()
const userStore = useUserStore()
const username = ref('admin')
const password = ref('admin123')
const loading = ref(false)
const error = ref('')
const pwdRef = ref(null)

function focusPwd() { pwdRef.value?.focus() }

async function login() {
  if (!username.value || !password.value) return
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value }),
    })
    if (!res.ok) { error.value = '用户名或密码错误'; return }
    const data = await res.json()
    userStore.setAuth(data.access_token, data.username, data.role)
    router.push('/admin')
  } catch {
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.offline-banner { position: fixed; top: 0; left: 0; right: 0; background: #fff3cd; color: #856404; text-align: center; padding: 8px; font-size: 13px; z-index: 10; }
.login-page { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: linear-gradient(135deg, #1890ff, #096dd9); }
.login-card { background: #fff; padding: 40px 32px; border-radius: 12px; width: 340px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,.15); }
.login-card h2 { margin-bottom: 24px; color: #333; }
.login-card input { width: 100%; padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 15px; margin-bottom: 12px; outline: none; }
.login-card input:focus { border-color: #1890ff; }
.login-card button { width: 100%; padding: 10px; background: #1890ff; color: #fff; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
.login-card button:disabled { opacity: .6; }
.error { color: #ff4d4f; margin-top: 8px; font-size: 14px; }
.hint { color: #999; margin-top: 12px; font-size: 12px; }
</style>
