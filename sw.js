/* SC Carto — service worker
   Rôle : rendre l'application utilisable hors ligne (usine, sous-sol, pas de réseau).
   Stratégie : « cache d'abord » pour la coquille, avec rafraîchissement en arrière-plan.
   Aucune donnée métier ne transite ici : les relevés vivent dans IndexedDB, côté page. */

var VERSION = "sc-carto-v1.0.0";
var COQUILLE = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./favicon.png",
  "./icon-192.png",
  "./icon-512.png",
  "./apple-touch-icon.png"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(VERSION).then(function (c) {
      return Promise.all(COQUILLE.map(function (u) {
        return c.add(new Request(u, { cache: "reload" }))["catch"](function () { /* fichier optionnel */ });
      }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (l) {
      return Promise.all(l.map(function (k) { return k === VERSION ? null : caches["delete"](k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  var r = e.request;
  if (r.method !== "GET") return;
  var u = new URL(r.url);
  if (u.origin !== self.location.origin) return;

  // Navigation : on sert index.html depuis le cache, même hors ligne.
  if (r.mode === "navigate") {
    e.respondWith(
      caches.match("./index.html").then(function (rep) {
        return rep || fetch(r)["catch"](function () { return caches.match("./"); });
      })
    );
    return;
  }

  e.respondWith(
    caches.match(r).then(function (rep) {
      var reseau = fetch(r).then(function (net) {
        if (net && net.status === 200 && net.type === "basic") {
          var copie = net.clone();
          caches.open(VERSION).then(function (c) { c.put(r, copie); });
        }
        return net;
      })["catch"](function () { return rep; });
      return rep || reseau;
    })
  );
});

self.addEventListener("message", function (e) {
  if (e.data === "activer-maintenant") self.skipWaiting();
});
