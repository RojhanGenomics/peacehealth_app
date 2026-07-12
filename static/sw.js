// Minimal service worker — required by browsers as one of the
// installability criteria for "Add to Home Screen" as a standalone app.
// It does not cache anything yet; it simply passes all requests through.

self.addEventListener("install", (event) => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  // Pass-through: no offline caching for now.
  event.respondWith(fetch(event.request));
});
