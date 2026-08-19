# SC Carto v1.0

Application de cartographie terrain de **Sari-Concept** (agence de l'Orne).

Recenser les **boîtes de dérivation** sur le plan d'une usine, depuis un smartphone,
en marchant dans le bâtiment. Hors ligne, sans compte, sans serveur :
**toutes les données restent dans le téléphone**.

Le dépôt contient deux choses indépendantes :

| Dossier | Quoi | Pour qui |
|---|---|---|
| racine (`index.html`, `sw.js`, `manifest.webmanifest`, icônes) | l'application terrain (PWA) | le téléphone |
| `outils-pc/` | deux scripts Python | le PC bureau d'études |

---

## 1. Mettre l'application en ligne (GitHub Pages)

L'application a besoin de **HTTPS** pour accéder au GPS et à l'appareil photo.
GitHub Pages fournit ce HTTPS gratuitement. Compter 15 minutes la première fois.

### Étape 1 — créer un compte GitHub

Aller sur <https://github.com>, bouton **Sign up**. Adresse mail professionnelle,
un mot de passe, et c'est fait. Notez votre **nom d'utilisateur** : il apparaîtra
dans l'adresse de l'application.

### Étape 2 — créer le dépôt

1. En haut à droite, le **+** puis **New repository**.
2. **Repository name** : `sc-carto`
3. Cocher **Public**.
   *GitHub Pages n'est gratuit que pour les dépôts publics. Le code de
   l'application sera donc visible ; ce n'est pas gênant, il ne contient aucune
   donnée client — les relevés ne quittent jamais le téléphone.*
4. Ne rien cocher d'autre. Bouton **Create repository**.

### Étape 3 — envoyer les fichiers

Le plus simple, sans installer Git :

1. Sur la page du dépôt vide : lien **uploading an existing file**
   (ou onglet **Add file** → **Upload files**).
2. Faire glisser dans la page **le contenu** du dossier `sc-carto` :
   `index.html`, `sw.js`, `manifest.webmanifest`, `.nojekyll`,
   `icon-192.png`, `icon-512.png`, `apple-touch-icon.png`, `favicon.png`,
   `README.md`, et le dossier `outils-pc`.
   ⚠ Il faut envoyer **le contenu du dossier**, pas le dossier `sc-carto` lui-même :
   `index.html` doit se trouver à la racine du dépôt.
3. En bas, dans **Commit changes**, écrire `Version 1.0` puis **Commit changes**.

<details>
<summary>Variante en ligne de commande (si vous préférez apprendre Git)</summary>

Installer Git depuis <https://git-scm.com>, puis, dans le dossier `sc-carto` :

```bash
git init
git add .
git commit -m "SC Carto v1.0"
git branch -M main
git remote add origin https://github.com/VOTRE-NOM/sc-carto.git
git push -u origin main
```

GitHub demandera votre identifiant et un **jeton d'accès** (pas le mot de passe) :
menu photo de profil → *Settings* → *Developer settings* → *Personal access tokens*
→ *Tokens (classic)* → *Generate new token*, en cochant `repo`.
</details>

### Étape 4 — activer Pages

1. Dans le dépôt, onglet **Settings** (en haut à droite).
2. Colonne de gauche, **Pages**.
3. **Source** : *Deploy from a branch*.
   **Branch** : `main`, dossier `/ (root)`. Bouton **Save**.
4. Recharger la page au bout d'une minute : GitHub affiche l'adresse

   ```
   https://VOTRE-NOM.github.io/sc-carto/
   ```

Le premier déploiement prend 1 à 3 minutes. Un point vert dans l'onglet
**Actions** indique que c'est publié.

### Étape 5 — installer sur le téléphone

Ouvrir l'adresse ci-dessus **dans le navigateur du téléphone**, puis :

* **Android (Chrome)** : menu ⋮ → *Ajouter à l'écran d'accueil* → *Installer*.
* **iPhone (Safari — obligatoirement Safari, pas Chrome)** : bouton Partager ⬆️
  → *Sur l'écran d'accueil*.

L'icône SC apparaît comme une vraie application. Elle fonctionne ensuite
**sans réseau** : le premier lancement met tout en cache.

Au premier usage, le téléphone demandera l'autorisation d'accéder à la
**position** et à l'**appareil photo** : répondre oui aux deux
(la position peut être refusée, l'application marche quand même).

### Mettre à jour l'application plus tard

Les étapes 1 à 4 ci-dessus ne se font **qu'une seule fois**. Ensuite, publier une
nouvelle version tient en une manipulation : **remplacer `index.html`**
(*Add file ▸ Upload files*, même nom : il écrase l'ancien).

Il n'y a **rien d'autre à modifier** : au lancement suivant, chaque téléphone va
chercher la dernière version sur le réseau. S'il n'a pas de réseau, il démarre
sur la version qu'il a déjà en mémoire — l'application reste utilisable en usine
comme avant.

> **Avant toute mise à jour**, demandez aux utilisateurs d'exporter une
> sauvegarde JSON. Les données ne sont pas perdues par une mise à jour,
> mais la prudence ne coûte rien.

---

## 2. Utiliser l'application

| Onglet | À quoi ça sert |
|---|---|
| **Plan** | le fond de plan, les repères, le bouton **+** pour poser une boîte |
| **Boîtes** | la liste, la recherche par numéro, le tri, « centrer sur le plan » |
| **Exporter** | CSV, ZIP avec photos, sauvegarde JSON, restauration |
| **Réglages** | nom du site, préfixe des numéros, fond de plan, calage GPS, projets, diagnostic |

**Poser une boîte** : bouton **+** → le repère apparaît sur votre position GPS
si le calage est fait, sinon au centre de l'écran → on le fait glisser au doigt
→ **Valider** → la fiche s'ouvre (numéro, statut, photos, note).

**Statuts** : 🔴 à identifier · 🟠 identifiée · 🟢 traitée.

**Numérotation** : automatique, `BD-001`, `BD-002`… Le préfixe se change dans
les Réglages, par projet.

**Calage** (facultatif) : deux points suffisent. L'application en déduit
l'échelle, la rotation et la position du plan, affiche votre position en direct
et donne à chaque boîte ses coordonnées latitude/longitude.
Sans calage, tout le reste fonctionne normalement.

Deux méthodes, au choix au début de l'assistant :

* **① Saisir les coordonnées — la plus juste.** Sur l'ordinateur, clic droit dans
  Google Earth (ou sur cartes.gouv.fr) sur deux points reconnaissables du site :
  leurs coordonnées s'affichent, on les recopie. Rien à mesurer sur place, donc
  aucune dérive. C'est la méthode à privilégier quand le fond de plan vient
  d'une image aérienne.
* **② Mesurer au GPS sur place.** Se placer **dehors** sur chaque point, le
  pointer sur le plan, laisser mesurer 5 secondes. Il faut **réellement marcher**
  entre les deux mesures : sinon le téléphone renvoie deux fois la même position.
  L'application écarte désormais les positions périmées ou imprécises et attend
  de vraies mesures satellite.

Dans les deux cas, l'application annonce **la taille qu'aurait le plan**
(« 120 m × 80 m ») et demande confirmation. Elle refuse d'enregistrer un calage
dont les deux relevés sont distants de moins de 15 m, ou qui donne des
dimensions absurdes — c'est le garde-fou contre le calage silencieusement faux.

*Réglages ▸ Détail du calage* rouvre à tout moment les deux points, leur
écartement et l'échelle obtenue.

**Plein soleil** : le bouton **☀** en haut à droite du plan passe le fond
en blanc. Le reste de l'interface ne bouge pas.

**Plusieurs projets** : Réglages → *Changer / créer un projet*. Un projet = un site.

**Diagnostic** : Réglages → *Diagnostic*. Vérifie la base locale, le
fonctionnement hors ligne, le GPS, la caméra, l'espace disponible, et affiche
la version.

### Enregistrement et export : deux choses différentes

**Il n'y a rien à enregistrer.** Chaque boîte, chaque photo, chaque changement de
statut est écrit dans le téléphone au moment de la saisie. On peut fermer
l'application, la tuer, éteindre le téléphone : tout est là au redémarrage.

L'onglet **Exporter** ne sert qu'à *sortir* le relevé du téléphone, avec un
bouton unique qui produit **un seul fichier ZIP** :

| Dans le ZIP | Pour qui |
|---|---|
| `releve.csv` | le tableur — numéro ; statut ; note ; X/Y plan ; latitude ; longitude ; date ; photos |
| `photos/BD-001_1.jpg`… | le client, renommées par numéro |
| `plan.svg` (ou `.png`) | le fond de plan tel qu'importé |
| `releve.json` | `points2dxf.py`, et la reprise du relevé sur un autre téléphone |

Le même fichier sert donc au client, au bureau d'études et à la reprise. Les
photos y restent des photos : il est environ quatre fois plus léger qu'un export
qui les encoderait en texte.

*Reprendre un relevé* rouvre ce ZIP (les anciens fichiers `.json` restent acceptés).

### Faire descendre le fichier sur le PC

Deux boutons sur la fiche « Fichier prêt » :

* **Envoyer vers…** ouvre le menu de partage du téléphone. Sur iPhone, *Enregistrer
  dans Dropbox* est dans la **liste du bas**, qu'il faut faire défiler — pas dans la
  rangée d'icônes du haut. Si Dropbox n'y figure pas alors que l'application est
  installée, son extension a été désactivée : tout en bas de cette liste,
  **Modifier les actions**, puis on la réactive.
* **Enregistrer** dépose le fichier dans l'application *Fichiers*.

> À ne pas faire : changer `Réglages ▸ Safari ▸ Téléchargements` pour pointer sur
> Dropbox. Ce réglage est **global** — tout ce que Safari téléchargerait ensuite,
> pièces jointes comprises, se déverserait dans le Dropbox de l'agence.

Dans l'autre sens (le plan qui descend sur le téléphone) : déposer le `.svg` dans
Dropbox, puis *Réglages ▸ Importer un fond de plan ▸ Parcourir ▸ Dropbox*.
Si Dropbox n'apparaît pas dans le sélecteur : application *Fichiers* → les trois
points en haut → *Modifier* → activer Dropbox.

---

## 3. Les outils PC

Voir [`outils-pc/README.md`](outils-pc/README.md).

En deux lignes :

```bash
python outils-pc/dxf2fond.py usine.dxf -o fond.svg --exclure COTES,MOBILIER
python outils-pc/points2dxf.py --json releve.json --dxf usine.dxf --calage fond.calage.json
```

Le premier fabrique le fond de plan à importer dans l'application.
Le second renvoie les boîtes relevées dans le DXF du client.

---

## 4. Points techniques

* **Aucune dépendance réseau** après le premier chargement : tout le CSS, tout le
  JavaScript et le logo sont dans `index.html`. Pas de CDN, pas de police
  distante, pas de bibliothèque externe.
* **Mise à jour automatique** : le service worker va chercher `index.html` sur le
  réseau au lancement, avec un délai d'attente de 2,5 s au-delà duquel il sert la
  version en cache. Une nouvelle version mise en ligne est donc prise au
  lancement suivant, sans numéro de version à changer nulle part, et sans jamais
  empêcher un démarrage hors ligne.
* **Stockage** : IndexedDB (projets, points, photos, fond de plan). Les photos
  sont réduites à 1600 px et recompressées en JPEG à l'enregistrement.
* **ZIP** : écrit directement par l'application, en mode « stocké » sans
  compression — les JPEG ne se compressent pas, et cela évite d'embarquer une
  bibliothèque de 100 Ko pour rien.
* **Calage GPS** : similitude à 2 points (échelle + rotation + translation),
  calculée sur une projection locale plan tangent. Précision typique en extérieur
  ± 5 m sur les points de calage.
* **Modèle de données** : chaque point porte un champ `couche`, figé à
  `"boites_derivation"` en v1. Les couches futures (éclairage, coffrets,
  chemins de câbles…) s'ajouteront sans casser les exports ni les sauvegardes.
* **Hors périmètre v1**, volontairement : autres couches dans l'interface,
  rapports Apave, fonds cadastre/IGN, synchronisation multi-appareils.

## 5. Sauvegarde et sécurité des données

Les relevés vivent **uniquement** dans le téléphone. Conséquences :

* téléphone perdu ou réinitialisé = relevé perdu ;
* désinstaller l'application efface les données ;
* le navigateur peut purger le stockage si l'appareil est saturé
  (l'application demande le mode « stockage permanent », le diagnostic indique
  s'il a été accordé).

**Donc : exporter une sauvegarde JSON à la fin de chaque journée de relevé**,
et la déposer dans le Dropbox de l'agence.

---

*SC Carto v1.0 — Sari-Concept, agence de l'Orne.*
