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

1. Ouvrir `sw.js` sur GitHub, bouton crayon ✏️, changer la ligne
   `var VERSION = "sc-carto-v1.0.0";` en `...v1.0.1` (n'importe quel nouveau texte).
   **C'est ce changement qui déclenche la mise à jour sur les téléphones.**
2. Remplacer `index.html` (Add file → Upload files, même nom : il écrase).
3. Sur le téléphone, fermer puis rouvrir l'application **deux fois** :
   la première récupère la nouveauté, la seconde l'affiche.

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

**Calage GPS** (facultatif) : deux points suffisent. Se placer **dehors** à un
coin repérable du bâtiment, le pointer sur le plan, capturer 5 secondes de GPS ;
recommencer à l'angle **le plus éloigné possible**. L'application calcule alors
l'échelle, la rotation et la position du plan, affiche votre position en direct
et donne à chaque boîte ses coordonnées latitude/longitude.
Sans calage, tout le reste fonctionne normalement.

**Plein soleil** : le bouton **☀** en haut à droite du plan passe le fond
en blanc. Le reste de l'interface ne bouge pas.

**Plusieurs projets** : Réglages → *Changer / créer un projet*. Un projet = un site.

**Diagnostic** : Réglages → *Diagnostic*. Vérifie la base locale, le
fonctionnement hors ligne, le GPS, la caméra, l'espace disponible, et affiche
la version.

### Ce que produisent les exports

| Export | Contenu |
|---|---|
| **CSV** | numéro ; statut ; note ; X/Y plan ; latitude ; longitude ; date ; noms des photos — séparateur `;`, s'ouvre directement dans Excel |
| **ZIP** | le CSV + toutes les photos renommées `BD-001_1.jpg`, `BD-001_2.jpg`… |
| **JSON complet** | sauvegarde intégrale : projet, calage, fond de plan, points, photos. Restaurable sur un autre téléphone |
| **JSON léger** | idem sans les photos ni le fond — c'est le fichier qu'attend `points2dxf.py` |

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
