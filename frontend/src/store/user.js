import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const username = ref('')
  const role = ref('')

  function setAuth(t, u, r) {
    token.value = t
    username.value = u
    role.value = r
    localStorage.setItem('cs_token', t)
  }

  function loadAuth() {
    token.value = localStorage.getItem('cs_token') || ''
  }

  function logout() {
    token.value = ''
    username.value = ''
    role.value = ''
    localStorage.removeItem('cs_token')
  }

  return { token, username, role, setAuth, loadAuth, logout }
})
