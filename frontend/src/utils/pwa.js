import { ref } from 'vue'
import { showDialog } from 'vant'

// Track online status
export const isOnline = ref(navigator.onLine)

// Track install prompt
let deferredPrompt = null
export const canInstall = ref(false)

// Initialize network listeners
export function initNetworkListeners() {
  window.addEventListener('online', () => {
    isOnline.value = true
  })
  window.addEventListener('offline', () => {
    isOnline.value = false
  })
}

// Register service worker
export async function registerSW() {
  if (!('serviceWorker' in navigator)) {
    console.log('[PWA] Service Worker not supported in this browser')
    return
  }

  try {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/',
    })
    console.log('[PWA] Service Worker registered:', registration.scope)

    // Check for updates
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing
      if (!newWorker) return
      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
          // New version available - could show update prompt
          console.log('[PWA] New version available')
        }
      })
    })
  } catch (err) {
    console.error('[PWA] Service Worker registration failed:', err)
  }
}

// Listen for install prompt
export function initInstallPrompt() {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferredPrompt = e
    canInstall.value = true
  })

  window.addEventListener('appinstalled', () => {
    deferredPrompt = null
    canInstall.value = false
    console.log('[PWA] App installed successfully')
  })
}

// Show install dialog
export async function showInstallPrompt() {
  if (!deferredPrompt) {
    // iOS fallback: show instructions
    const isIOS = /iphone|ipad|ipod/.test(navigator.userAgent.toLowerCase())
    if (isIOS) {
      showDialog({
        title: '添加到主屏幕',
        message: '点击浏览器底部的"分享"按钮，然后选择"添加到主屏幕"即可安装此应用。',
        confirmButtonText: '知道了',
      })
    } else {
      showDialog({
        title: '提示',
        message: '您的浏览器暂不支持快速安装。请使用 Chrome 浏览器打开以安装此应用。',
        confirmButtonText: '知道了',
      })
    }
    return
  }

  try {
    await deferredPrompt.prompt()
    const { outcome } = await deferredPrompt.userChoice
    console.log(`[PWA] Install prompt outcome: ${outcome}`)
    deferredPrompt = null
    canInstall.value = false
  } catch (err) {
    console.error('[PWA] Install prompt failed:', err)
  }
}
