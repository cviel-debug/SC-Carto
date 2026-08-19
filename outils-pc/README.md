# Boîte à outils PC — SC Carto

Deux scripts Python, à lancer depuis le PC du bureau d'études. Ils ne servent
qu'aux deux extrémités de la chaîne : fabriquer le fond de plan, puis renvoyer
le relevé dans le DXF du client.

```
   usine.dxf ──dxf2fond.py──► fond.svg ──► [téléphone : SC Carto] ──► releve.json
       │                    + fond.calage.json                            │
       └──────────────────── points2dxf.py ◄─────────────────────────────┘
                                   │
                            usine_boites.dxf   (calque SC_BOITES_DERIVATION)
```

## Installation

Python 3.9 ou plus, puis :

```bash
pip install -r requirements.txt
```

Une seule dépendance : **ezdxf**.

---

## La méthode simple : les deux icônes

Sans ligne de commande. Deux fichiers `.bat` sont posés dans ce dossier ;
**on glisse un fichier dessus** et ils font le reste.

### `1 - Fabriquer le fond de plan (glisser un DXF ici).bat`

Glissez le **DXF du client** sur l'icône. Une fenêtre s'ouvre, affiche les
calques du plan et demande lesquels jeter (cotations, mobilier, axes…).
Tapez leurs noms séparés par des virgules, Entrée.

Deux fichiers apparaissent à côté du DXF :

* le `.svg` → à copier sur le téléphone ;
* le `.calage.json` → **à laisser là**, il sert au retour.

Le résultat ne convient pas ? On relance en jetant d'autres calques, ça ne coûte rien.

### `2 - Rendre le plan au client (glisser le relevé ici).bat`

Glissez le **ZIP exporté** par l'application sur l'icône. La fenêtre réclame
ensuite deux fichiers, l'un après l'autre : **glissez-les dans la fenêtre**
(le chemin s'écrit tout seul), puis Entrée.

1. le DXF d'origine ;
2. le `.calage.json` fabriqué à l'étape précédente.

Sortie : `<nom>_boites.dxf`. Le plan du client n'est pas modifié — c'est une
copie, avec un calque en plus.

> Ces deux fichiers n'ont pas d'accents dans leurs messages, et pas de
> `chcp 65001` : sous Windows, la page de code UTF-8 empêche `set /p` de lire
> ce qu'on tape. Ne le remettez pas.

La suite de ce document décrit les mêmes outils **en ligne de commande**, pour
les cas particuliers (choix fin des calques, taille des symboles, calage manuel).

---

---

## `dxf2fond.py` — DXF ➜ fond de plan SVG

Aplatit la géométrie utile (lignes, polylignes, arcs, cercles, splines, blocs
éclatés) en simples traits, jette le superflu (hachures, cotations, textes,
calques non retenus) et écrit un SVG léger, sous les 2 Mo.

**1. Regarder ce que contient le DXF**

```bash
python dxf2fond.py usine.dxf --lister
```

```
CALQUE                              ENTITES   TYPES
------------------------------------------------------------------------------
COTES                                   200   LINE x200
MOBILIER                                 60   LWPOLYLINE x60
POTEAUX                                  16   LWPOLYLINE x8, CIRCLE x8
CLOISONS                                  5   LINE x5
MURS                                      4   LWPOLYLINE x1, ARC x1, CIRCLE x1
```

**2. Convertir en choisissant les calques**

```bash
# ne garder que l'essentiel
python dxf2fond.py usine.dxf -o fond.svg --couches MURS,CLOISONS,POTEAUX

# ou : tout garder sauf le bruit
python dxf2fond.py usine.dxf -o fond.svg --exclure COTES,MOBILIER,AXES
```

Deux fichiers sortent :

* `fond.svg` — à copier sur le téléphone, puis *Réglages ▸ Importer un fond de plan* ;
* `fond.calage.json` — **à conserver à côté du DXF**, `points2dxf.py` en a besoin
  pour retrouver les coordonnées AutoCAD.

### Options

| Option | Effet |
|---|---|
| `--lister` | affiche les calques et s'arrête |
| `--couches A,B,C` | ne garder que ces calques |
| `--exclure X,Y` | ignorer ces calques |
| `--largeur 4000` | taille en pixels du plus grand côté (défaut 4000) |
| `--max-mo 2` | plafond de taille ; au-delà le script simplifie tout seul |
| `--epaisseur 1.2` | épaisseur du trait |
| `--fond #ffffff` / `--trait #141414` | couleurs |

### Bon à savoir

* La géométrie dessinée sur le **calque 0 à l'intérieur d'un bloc** est reportée
  sur le calque de l'insertion, comme le fait AutoCAD. Les poteaux insérés en
  bloc restent donc filtrables par leur calque.
* Les **hachures, cotations et textes** sont systématiquement écartés : sur un
  fond de plan de repérage, ils n'apportent rien et pèsent beaucoup.
* Un DXF abîmé est réparé automatiquement (`ezdxf.recover`).
* Si le SVG dépasse le plafond, le script simplifie progressivement (arrondi des
  coordonnées, suppression des micro-traits) et le dit à l'écran.

---

## `points2dxf.py` — relevé ➜ DXF enrichi

Reprend le DXF d'origine **sans y toucher** et ajoute un calque
`SC_BOITES_DERIVATION` contenant, pour chaque boîte : un cercle, une croix, et
le numéro en texte à côté, aux coordonnées exactes du dessin.

```bash
python points2dxf.py --json SC-Carto_PALM_Mortagne_20260819.zip --dxf usine.dxf --calage fond.calage.json
```

Sortie : `usine_boites.dxf`.

L'option `--json` accepte **le ZIP exporté par l'application** (il en extrait
`releve.json` tout seul) aussi bien qu'un fichier `.json` produit par les
versions précédentes.

### Options

| Option | Effet |
|---|---|
| `-o fichier.dxf` | nom du DXF produit (défaut `<dxf>_boites.dxf`) |
| `--taille 0.35` | rayon du symbole en unités du dessin (défaut : calculé) |
| `--couleurs-statut` | rouge / orange / vert selon le statut de chaque boîte |
| `--couleur-calque 1` | couleur AutoCAD du calque (défaut 1 = rouge) |
| `--sans-texte` | symboles seuls, sans les numéros |
| `--remplacer` | vide le calque `SC_BOITES_DERIVATION` s'il existe déjà |

### Sans fichier de calage

Si le fond de plan n'a pas été fabriqué par `dxf2fond.py` (une photo du plan
papier, par exemple), la transformation se donne à la main :

```bash
python points2dxf.py --json releve.json --dxf usine.dxf \
    --echelle 33.3333 --xmin 512340 --ymin 6789120 --hauteur-px 2667
```

* `--echelle` : nombre de pixels du fond par unité du dessin ;
* `--xmin`, `--ymin` : coordonnées AutoCAD du **coin bas-gauche** du fond ;
* `--hauteur-px` : hauteur du fond en pixels.

---

## Vérification de la chaîne

La chaîne complète a été contrôlée sur un plan d'essai
(bâtiment 120 × 80 m placé en coordonnées Lambert) :
un point posé dans l'application ressort dans le DXF **à moins de 0,01 mm**
de sa position théorique. La précision réelle est donc celle du doigt sur
l'écran, pas celle des outils.
