// Keeps the whole helmet on the headset: network first (so updates land when the PC is reachable), cache when it isn't.
const CACHE = 'jarvis-v2';
const VOICES = ['boot_morning', 'boot_afternoon', 'boot_evening', 'scan', 'scan_done', 'repulsors_on', 'repulsors_off', 'rim_on', 'rim_off',
  'quip_0', 'quip_1', 'quip_2', 'quip_3', 'quip_4', 'quip_5', 'wreck', 'lowpower', 'nohands'];
const FILES = ['./', './index.html', './vendor/three.module.js', './manifest.json', './icon-192.png', './icon-512.png',
  ...VOICES.map(v => './audio/' + v + '.mp3')];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 2500);
      const r = await fetch(e.request, { signal: ctl.signal }); clearTimeout(t);
      if (r.ok) cache.put(e.request, r.clone());
      return r;
    } catch (err) {
      return (await cache.match(e.request, { ignoreSearch: true })) || (await cache.match('./index.html')) || Response.error();
    }
  })());
});
