/* 7azar Fazar service worker.

   Strategy:
   - the shell (page, manifest, icons, question bank) is precached, so the game
     opens and plays with no network at all;
   - photos and reaction clips are cached as they are used rather than up front.
     Precaching them would mean a ~12 MB download before the first question,
     which is a poor trade on a phone. After one game night on wi-fi they are
     all local anyway.

   Bump CACHE_VERSION to retire old caches on the next deploy. */
const CACHE_VERSION = "v3";   // v3: expanded topics, local audio and refreshed home logo
const SHELL = `7azar-shell-${CACHE_VERSION}`;
const MEDIA = `7azar-media-${CACHE_VERSION}`;

/* Relative URLs throughout: the app must work from any base path, not just a
   domain root. Netlify serves it at /, but a preview or sub-path deploy would
   break absolute "/index.html" links. */
const SHELL_ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./trivia-questions.json",
  "./sounds/music/game-loop.mp3",
  "./sounds/effects/clock-ticking.mp3",
  "./icons/icon-192.png",
  "./icons/logo-home.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-192.png",
  "./icons/icon-maskable-512.png",
  "./icons/apple-touch-icon.png",
  "./icons/favicon-32.png",
];

const MEDIA_PATH = /\/(landmark-photos|country-flags|country-shapes|kangaroo-figures|logo-assets|reactions)\//;

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(SHELL);
    // addAll is atomic — one 404 would fail the whole install, so add
    // individually and let a missing optional file slide
    await Promise.all(SHELL_ASSETS.map(u => c.add(new Request(u, {cache:"reload"})).catch(()=>{})));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    const keep = new Set([SHELL, MEDIA]);
    for(const k of await caches.keys()) if(!keep.has(k)) await caches.delete(k);
    await self.clients.claim();
  })());
});

/* Media served from cache must honour Range requests. Safari asks for byte
   ranges when playing a <video>, and handing it a whole 200 response makes
   playback fail outright — so slice the cached body into a real 206. */
async function rangeAwareResponse(request, cached){
  const range = request.headers.get("range");
  if(!range) return cached;
  const buf = await cached.clone().arrayBuffer();
  const size = buf.byteLength;
  const m = /^bytes=(\d*)-(\d*)$/.exec(range.trim());
  if(!m) return cached;
  let start = m[1] === "" ? null : parseInt(m[1], 10);
  let end   = m[2] === "" ? null : parseInt(m[2], 10);
  if(start === null){                       // "bytes=-500" → final 500 bytes
    const n = end || 0;
    start = Math.max(0, size - n); end = size - 1;
  } else if(end === null || end >= size){
    end = size - 1;
  }
  if(start > end || start >= size){
    return new Response(null, {status:416, headers:{"Content-Range":`bytes */${size}`}});
  }
  const slice = buf.slice(start, end + 1);
  return new Response(slice, {
    status: 206, statusText: "Partial Content",
    headers: {
      "Content-Type": cached.headers.get("Content-Type") || "application/octet-stream",
      "Content-Length": String(slice.byteLength),
      "Content-Range": `bytes ${start}-${end}/${size}`,
      "Accept-Ranges": "bytes",
    },
  });
}

async function cacheFirstMedia(request){
  const cache = await caches.open(MEDIA);
  const url = new URL(request.url);
  const hit = await cache.match(url.pathname);       // key without the Range
  if(hit) return rangeAwareResponse(request, hit);
  try{
    // fetch the whole file, not the requested slice, so the cache holds
    // something we can serve future ranges from
    const full = await fetch(new Request(url.toString(), {cache:"reload"}));
    if(full.ok && full.status === 200) await cache.put(url.pathname, full.clone());
    return request.headers.get("range") ? rangeAwareResponse(request, full) : full;
  }catch(err){
    return hit || Response.error();
  }
}

async function staleWhileRevalidate(request, cacheName, fallback){
  const cache = await caches.open(cacheName);
  const hit = await cache.match(request, {ignoreSearch:true});
  const net = fetch(request).then(res => {
    if(res && res.ok && res.status === 200) cache.put(request, res.clone());
    return res;
  }).catch(()=>null);
  return hit || (await net) || (fallback ? cache.match(fallback) : undefined) || Response.error();
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if(req.method !== "GET") return;
  const url = new URL(req.url);
  if(url.origin !== self.location.origin) return;   // let the CDN script fail on its own

  if(req.mode === "navigate"){
    e.respondWith(staleWhileRevalidate(req, SHELL, "./index.html"));
    return;
  }
  if(MEDIA_PATH.test(url.pathname)){
    e.respondWith(cacheFirstMedia(req));
    return;
  }
  e.respondWith(staleWhileRevalidate(req, SHELL));
});
