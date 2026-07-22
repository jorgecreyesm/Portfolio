// Minimal service worker — enables PWA install prompt on Android/Chrome
self.addEventListener('install', (e) => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
