const CACHE_NAME = 'news-pwa-v2';

const STATIC_ASSETS = [
  '/',
  '/search',
  '/about',
  '/contact',

  '/static/frontend/css/base.css',
  '/static/frontend/css/layout.css',
  '/static/frontend/css/responsive.css',

  '/static/news/offline.html'
];

self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  event.respondWith(fetch(event.request));
});

