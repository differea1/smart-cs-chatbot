import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import 'vant/lib/index.css'
import './assets/main.css'
import { initNetworkListeners, initInstallPrompt, registerSW } from '@/utils/pwa'

// Initialize PWA
initNetworkListeners()
initInstallPrompt()
registerSW()

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
