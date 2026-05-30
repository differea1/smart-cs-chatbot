// Environment detection and API URL configuration

// Detect if running inside Capacitor (native app)
export function isCapacitor() {
  try {
    // Capacitor injects this global
    return !!(window.Capacitor?.isNativePlatform?.())
  } catch {
    return false
  }
}

// Detect if running as PWA (standalone mode)
export function isPWA() {
  return window.matchMedia('(display-mode: standalone)').matches
}

// API base URL - configurable for production deployment
// When running in Capacitor (native app), must use absolute URL to your server
// Change this to your production server URL
const PRODUCTION_API_URL = 'https://your-server.com'

function getApiBaseUrl() {
  // Check for build-time env variable first
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }

  // Capacitor native app: need absolute URL
  if (isCapacitor()) {
    // Read from Capacitor's persisted config, or use default
    return localStorage.getItem('api_base_url') || PRODUCTION_API_URL
  }

  // Web/PWA: use relative URL (same origin, behind nginx proxy)
  return ''
}

export const API_BASE = getApiBaseUrl()

export function setApiBaseUrl(url) {
  localStorage.setItem('api_base_url', url)
  // Force reload to apply
  window.location.reload()
}
