/* SC Carto — service worker
   Rôle : rendre l'application utilisable hors ligne (usine, sous-sol, pas de réseau).

   Stratégie pour la page elle-même : « cache d'abord, rafraîchi derrière ».
   Le cache répond immédiatement — jamais d'écran blanc, même en réseau dégradé —
   et pendant ce temps la dernière version est cherchée sur le réseau pour le
   lancement SUIVANT. Publier une mise à jour ne demande donc toujours que de
   remplacer index.html ; elle arrive au deuxième lancement.

   Aucune donnée métier ne transite ici : les relevés vivent dans IndexedDB. */

var VERSION = "sc-carto-v1.3.0";
var TUILES = "sc-tuiles-v1";      /* cache des tuiles IGN récentes */
var TUILES_MAX = 600;             /* ~40 Mo de photo aérienne au maximum */
var ESSENTIELS = ["./", "./index.html"];
var OPTIONNELS = ["./manifest.webmanifest", "./favicon.png",
                  "./icon-192.png", "./icon-512.png", "./apple-touch-icon.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(VERSION).then(function (c) {
      /* La coquille : si elle ne se met pas en cache, l'installation ÉCHOUE
         (le navigateur retentera) — un hors-ligne à coquille vide est pire
         qu'un service worker en retard. Les icônes, elles, sont tolérées. */
      return c.addAll(ESSENTIELS.map(function (u) { return new Request(u, { cache: "reload" }); }))
        .then(function () {
          return Promise.all(OPTIONNELS.map(function (u) {
            return c.add(new Request(u, { cache: "reload" }))["catch"](function () {});
          }));
        });
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (l) {
      return Promise.all(l.map(function (k) {
        return (k === VERSION || k === TUILES) ? null : caches["delete"](k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

/* Va chercher la page sur le réseau et met le cache à jour pour la prochaine fois. */
function rafraichir(cle) {
  return fetch(new Request(cle, { cache: "no-store" })).then(function (net) {
    if (net && net.status === 200) {
      var copie = net.clone();
      caches.open(VERSION).then(function (c) { c.put(cle, copie); });
    }
    return net;
  });
}

/* Tuiles IGN : cache d'abord (une zone déjà vue s'affiche même dans un trou
   de couverture), réseau sinon, avec un plafond d'entrées élagué au fil de l'eau. */
function servirTuile(r) {
  return caches.open(TUILES).then(function (c) {
    return c.match(r).then(function (rep) {
      if (rep) return rep;
      return fetch(r).then(function (net) {
        if (net && (net.status === 200 || net.type === "opaque")) {
          c.put(r, net.clone());
          if (Math.random() < 0.02) {
            c.keys().then(function (ks) {
              for (var i = 0; i < ks.length - TUILES_MAX; i++) c["delete"](ks[i]);
            });
          }
        }
        return net;
      });
    });
  });
}

self.addEventListener("fetch", function (e) {
  var r = e.request;
  if (r.method !== "GET") return;
  var u = new URL(r.url);
  if (u.hostname === "data.geopf.fr") { e.respondWith(servirTuile(r)); return; }
  if (u.origin !== self.location.origin) return;

  /* La page : cache immédiat + rafraîchissement silencieux derrière. */
  if (r.mode === "navigate") {
    e.respondWith(
      caches.match("./index.html").then(function (rep) {
        var reseau = rafraichir("./index.html");
        if (rep) { reseau["catch"](function () {}); return rep; }
        return reseau["catch"](function () { return caches.match("./"); });
      })
    );
    return;
  }

  /* Le reste (icônes, manifeste) : cache d'abord, réseau en secours. */
  e.respondWith(
    caches.match(r).then(function (rep) {
      if (rep) return rep;
      return fetch(r).then(function (net) {
        if (net && net.status === 200 && net.type === "basic") {
          var copie = net.clone();
          caches.open(VERSION).then(function (c) { c.put(r, copie); });
        }
        return net;
      });
    })
  );
});

self.addEventListener("message", function (e) {
  if (e.data === "activer-maintenant") self.skipWaiting();
});
