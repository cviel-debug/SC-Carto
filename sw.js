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

/* Récupère l'application sur le réseau, sinon dans le cache.
   Délai court : au-delà, on n'attend pas et on sert la version en cache. */
function reseauDabord(requete, secours, delai) {
  return new Promise(function (res) {
    var repondu = false;
    function servirCache() {
      if (repondu) return;
      repondu = true;
      caches.match(secours).then(function (rep) {
        res(rep || Response.error());
      });
    }
    var minuteur = setTimeout(servirCache, delai);
    fetch(requete, { cache: "no-store" }).then(function (net) {
      if (!net || net.status !== 200) throw new Error("reponse inutilisable");
      var copie = net.clone();
      caches.open(VERSION).then(function (c) { c.put(secours, copie); });
      clearTimeout(minuteur);
      if (!repondu) { repondu = true; res(net); }
    })["catch"](function () {
      clearTimeout(minuteur);
      servirCache();
    });
  });
}

self.addEventListener("fetch", function (e) {
  var r = e.request;
  if (r.method !== "GET") return;
  var u = new URL(r.url);
  if (u.origin !== self.location.origin) return;

  /* L'application elle-même : réseau d'abord, cache en secours.
     Une nouvelle version mise en ligne est donc prise au lancement suivant,
     sans rien avoir à modifier ici — et hors ligne, le cache prend le relais. */
  if (r.mode === "navigate" || /(^|\/)(index\.html)?$/.test(u.pathname)) {
    e.respondWith(reseauDabord(r, "./index.html", 2500));
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
