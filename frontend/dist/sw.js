// Service Worker for 极米智能售后助手 PWA
const CACHE_NAME = 'xgimi-cs-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
];

// Install: pre-cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[SW] Cache addAll failed (some assets may be missing):', err);
      });
    }).then(() => self.skipWaiting())
  );
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...');
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: cache strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests and chrome-extension URLs
  if (request.method !== 'GET') return;
  if (url.protocol === 'chrome-extension:') return;

  // API requests: Network-First (try network, fall back to offline message)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Static assets: Cache-First (JS, CSS, fonts, images, icons)
  if (
    url.pathname.match(/\.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$/) ||
    url.pathname.startsWith('/assets/') ||
    url.pathname.startsWith('/icons/')
  ) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Navigation / HTML: Network-First
  event.respondWith(networkFirst(request));
});

// Cache-First strategy
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    // For static assets, return nothing on failure
    return new Response('', { status: 408 });
  }
}

// Network-First strategy (with timeout)
async function networkFirst(request) {
  try {
    const response = await fetchWithTimeout(request, 10000);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    // Fall back to cache
    const cached = await caches.match(request);
    if (cached) return cached;

    // For API requests, return a JSON offline message
    if (request.url.includes('/api/')) {
      return new Response(
        JSON.stringify({ error: 'offline', message: '当前无网络连接，请稍后重试' }),
        { status: 503, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // For HTML navigation, return the cached index.html (app shell)
    const cachedShell = await caches.match('/');
    if (cachedShell) return cachedShell;

    return new Response('当前无网络连接，请稍后重试', { status: 503 });
  }
}

// Fetch with timeout
function fetchWithTimeout(request, timeout) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('timeout')), timeout);
    fetch(request)
      .then((response) => { clearTimeout(timer); resolve(response); })
      .catch((err) => { clearTimeout(timer); reject(err); });
  });
}

// Listen for messages from the main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
