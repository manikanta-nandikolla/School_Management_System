self.addEventListener('install', function(e) {
  console.log('Service Worker installed');
  e.waitUntil(
    caches.open('vidyalaya-cache').then(function(cache) {
      return cache.addAll([
        '/',
        '/static/css/main.css',
        '/static/images/logo.jpeg'
      ]);
    })
  );
});

self.addEventListener('fetch', function(e) {
  e.respondWith(
    caches.match(e.request).then(function(response) {
      return response || fetch(e.request);
    })
  );
});
