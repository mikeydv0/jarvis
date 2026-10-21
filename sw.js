// Keeps the whole helmet on the headset: network first (so updates land when the PC is reachable), cache when it isn't.
const CACHE = 'jarvis-v10';
const VOICES = ['boot_morning', 'boot_afternoon', 'boot_evening', 'scan', 'scan_done', 'repulsors_on', 'repulsors_off', 'rim_on', 'rim_off',
  'quip_0', 'quip_1', 'quip_2', 'quip_3', 'quip_4', 'quip_5', 'wreck', 'lowpower', 'nohands'];
const FILES = ['./', './index.html', './vendor/three.module.js', './manifest.json', './icon-192.png', './icon-512.png',
  ...VOICES.map(v => './audio/' + v + '.mp3'),
  './manhattan/', './manhattan/index.html', './manhattan/manifest.json', './manhattan/icon-192.png', './manhattan/icon-512.png',
  ...['boot', 'explode_0', 'explode_1', 'crush_0', 'crush_1', 'release', 'idle', 'many'].map(v => './manhattan/audio/' + v + '.mp3'),
  './desert/', './desert/index.html',
  ...['boot', 'explode_0', 'explode_1', 'crush_0', 'crush_1', 'release', 'wave', 'shot'].map(v => './desert/audio/' + v + '.mp3'),
  './fan/', './fan/index.html', './fan/manifest.json', './fan/icon-192.png', './fan/icon-512.png',
  ...['boot', 'linked', 'on', 'max', 'off', 'swing_on', 'swing_off', 'offline'].map(v => './fan/audio/' + v + '.mp3')];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 2500);
      const r = await fetch(e.request, { signal: ctl.signal, cache: e.request.mode === 'navigate' ? 'reload' : 'no-cache' }); // always revalidate, Pages caches 10 min clearTimeout(t);
      if (r.ok) cache.put(e.request, r.clone());
      return r;
    } catch (err) {
      return (await cache.match(e.request, { ignoreSearch: true })) || (await cache.match('./index.html')) || Response.error();
    }
  })());
});
