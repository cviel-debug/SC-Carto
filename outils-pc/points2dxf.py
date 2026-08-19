#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
points2dxf.py — reinjecte les boites relevees avec SC Carto dans le DXF du client.

Entrees  : l'export JSON de l'application + le DXF d'origine + le fichier .calage.json
           produit par dxf2fond.py lors de la fabrication du fond de plan.
Sortie   : une copie du DXF enrichie d'un calque SC_BOITES_DERIVATION contenant,
           pour chaque boite, un symbole (cercle + croix) et son numero en texte.

Le client rouvre son propre plan, avec les boites dessinees a la bonne place.

Exemples
--------
    python points2dxf.py --json releve.json --dxf usine.dxf --calage fond.calage.json

    # taille du symbole imposee (en unites du dessin), couleurs par statut
    python points2dxf.py --json releve.json --dxf usine.dxf --calage fond.calage.json \
        --taille 0.35 --couleurs-statut -o usine_boites.dxf

    # sans fichier de calage : on donne la transformation a la main
    python points2dxf.py --json releve.json --dxf usine.dxf \
        --echelle 0.0521 --xmin 12500 --ymin 8400 --hauteur-px 2800

Dependance :  pip install ezdxf
"""

import argparse
import json
import math
import os
import sys
import zipfile
from datetime import datetime

try:
    import ezdxf
    from ezdxf import recover
except ImportError:
    sys.exit("Bibliotheque manquante. Installez-la avec :  pip install ezdxf")

# La console Windows n'encode pas tous les caracteres : un nom de site accentue
# ne doit pas faire planter l'affichage.
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


CALQUE = "SC_BOITES_DERIVATION"

# Couleurs AutoCAD (index ACI) par statut, utilisees avec --couleurs-statut
COULEUR_STATUT = {
    "a_identifier": 1,    # rouge
    "identifiee": 30,     # orange
    "traitee": 3,         # vert
}
LIBELLE_STATUT = {
    "a_identifier": "a identifier",
    "identifiee": "identifiee",
    "traitee": "traitee",
}


def charger_releve(chemin):
    """Accepte le ZIP exporte par l'application, ou un fichier JSON seul."""
    if zipfile.is_zipfile(chemin):
        with zipfile.ZipFile(chemin) as z:
            noms = [n for n in z.namelist() if n.lower().endswith("releve.json")]
            if not noms:
                sys.exit("%s ne contient pas de releve SC Carto (releve.json absent)." % chemin)
            with z.open(noms[0]) as f:
                return json.loads(f.read().decode("utf-8"))
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def ouvrir(chemin):
    try:
        return ezdxf.readfile(chemin)
    except ezdxf.DXFStructureError:
        print("  DXF abime : tentative de reparation...")
        doc, auditeur = recover.readfile(chemin)
        if auditeur.has_errors:
            print("  %d erreur(s) corrigee(s) a la volee." % len(auditeur.errors))
        return doc
    except IOError as e:
        sys.exit("Lecture impossible : %s" % e)


def charger_calage(a):
    """Renvoie (echelle_px_par_unite, xmin, ymin, hauteur_px)."""
    if a.calage:
        if not os.path.isfile(a.calage):
            sys.exit("Fichier de calage introuvable : %s" % a.calage)
        with open(a.calage, encoding="utf-8") as f:
            c = json.load(f)
        if c.get("format") != "sc-carto-fond":
            sys.exit("%s n'est pas un fichier de calage produit par dxf2fond.py" % a.calage)
        t = c["transformation"]
        return (float(t["echelle_px_par_unite"]), float(t["xmin"]),
                float(t["ymin"]), float(t["hauteur_px"]))
    if a.echelle is None:
        sys.exit("Il faut soit --calage fond.calage.json, soit --echelle/--xmin/--ymin/--hauteur-px.\n"
                 "Le fichier .calage.json est cree en meme temps que le SVG par dxf2fond.py.")
    for nom, val in (("--xmin", a.xmin), ("--ymin", a.ymin), ("--hauteur-px", a.hauteur_px)):
        if val is None:
            sys.exit("Option %s manquante (obligatoire avec --echelle)." % nom)
    return float(a.echelle), float(a.xmin), float(a.ymin), float(a.hauteur_px)


def px_vers_dxf(x, y, echelle, xmin, ymin, hauteur_px):
    return (x / echelle + xmin, (hauteur_px - y) / echelle + ymin)


def main():
    ap = argparse.ArgumentParser(
        description="Reinjecte les boites de derivation de SC Carto dans un DXF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    ap.add_argument("--json", required=True,
                    help="fichier exporte par SC Carto (le ZIP, ou un ancien .json)")
    ap.add_argument("--dxf", required=True, help="DXF d'origine du client")
    ap.add_argument("--calage", help="fichier .calage.json produit par dxf2fond.py")
    ap.add_argument("-o", "--sortie", help="DXF produit (defaut : <dxf>_boites.dxf)")
    ap.add_argument("--taille", type=float,
                    help="rayon du symbole en unites du dessin (defaut : auto)")
    ap.add_argument("--couleurs-statut", action="store_true",
                    help="colorer chaque boite selon son statut au lieu de la couleur du calque")
    ap.add_argument("--couleur-calque", type=int, default=1,
                    help="couleur AutoCAD du calque (defaut 1 = rouge)")
    ap.add_argument("--sans-texte", action="store_true", help="ne pas ecrire les numeros")
    ap.add_argument("--remplacer", action="store_true",
                    help="vider le calque %s s'il existe deja" % CALQUE)
    # calage manuel
    ap.add_argument("--echelle", type=float, help="pixels par unite DXF")
    ap.add_argument("--xmin", type=float, help="X du coin bas-gauche du fond, en unites DXF")
    ap.add_argument("--ymin", type=float, help="Y du coin bas-gauche du fond, en unites DXF")
    ap.add_argument("--hauteur-px", type=float, dest="hauteur_px",
                    help="hauteur du fond de plan en pixels")
    a = ap.parse_args()

    for f in (a.json, a.dxf):
        if not os.path.isfile(f):
            sys.exit("Fichier introuvable : %s" % f)

    # ---- releve ----------------------------------------------------------- #
    rel = charger_releve(a.json)
    if rel.get("format") != "sc-carto":
        sys.exit("%s n'est pas un export SC Carto." % a.json)
    points = [p for p in rel.get("points", [])
              if p.get("couche", "boites_derivation") == "boites_derivation"]
    autres = len(rel.get("points", [])) - len(points)
    if not points:
        sys.exit("Aucune boite de derivation dans cet export.")
    print("Releve : %s — %d boite(s)%s"
          % (rel.get("projet", {}).get("nom", "?"), len(points),
             (" (%d point(s) d'une autre couche ignore(s))" % autres) if autres else ""))

    echelle, xmin, ymin, hpx = charger_calage(a)
    print("Calage : 1 px = %.5f unite DXF, origine (%.3f ; %.3f), hauteur %d px"
          % (1.0 / echelle, xmin, ymin, hpx))

    # ---- DXF -------------------------------------------------------------- #
    print("Lecture de %s ..." % a.dxf)
    doc = ouvrir(a.dxf)
    msp = doc.modelspace()

    if CALQUE not in doc.layers:
        doc.layers.add(CALQUE, color=a.couleur_calque)
    elif a.remplacer:
        vieux = [e for e in msp if e.dxf.layer == CALQUE]
        for e in vieux:
            msp.delete_entity(e)
        print("Calque %s vide de ses %d entite(s) precedente(s)." % (CALQUE, len(vieux)))

    # taille du symbole : par defaut ~0,4 % de la diagonale du releve, borne raisonnablement
    if a.taille:
        rayon = a.taille
    else:
        xs = [p["x"] for p in points]
        ys = [p["y"] for p in points]
        diag_px = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or hpx
        rayon = max(diag_px * 0.004 / echelle, 0.05)
    hauteur_txt = rayon * 1.6
    print("Symbole : rayon %.3f unite(s) DXF, texte %.3f" % (rayon, hauteur_txt))

    # ---- dessin ----------------------------------------------------------- #
    dehors = 0
    for p in points:
        x, y = px_vers_dxf(float(p["x"]), float(p["y"]), echelle, xmin, ymin, hpx)
        attr = {"layer": CALQUE}
        if a.couleurs_statut:
            attr["color"] = COULEUR_STATUT.get(p.get("statut"), 7)

        msp.add_circle((x, y), rayon, dxfattribs=dict(attr))
        msp.add_line((x - rayon, y), (x + rayon, y), dxfattribs=dict(attr))
        msp.add_line((x, y - rayon), (x, y + rayon), dxfattribs=dict(attr))

        if not a.sans_texte:
            t = msp.add_text(str(p.get("numero", "?")),
                             dxfattribs=dict(attr, height=hauteur_txt))
            t.set_placement((x + rayon * 1.4, y + rayon * 0.6))

        if float(p["x"]) < 0 or float(p["y"]) < 0 or float(p["y"]) > hpx:
            dehors += 1

    if dehors:
        print("  Attention : %d boite(s) hors des limites du fond de plan." % dehors)

    sortie = a.sortie or (os.path.splitext(a.dxf)[0] + "_boites.dxf")
    doc.saveas(sortie)

    print("")
    print("  DXF produit : %s" % sortie)
    print("  Calque      : %s (%d boites : %d cercles, %d traits, %d textes)"
          % (CALQUE, len(points), len(points), len(points) * 2,
             0 if a.sans_texte else len(points)))
    repart = {}
    for p in points:
        repart[p.get("statut", "?")] = repart.get(p.get("statut", "?"), 0) + 1
    print("  Statuts     : " + ", ".join(
        "%s = %d" % (LIBELLE_STATUT.get(k, k), v) for k, v in sorted(repart.items())))
    print("  Genere le   : %s" % datetime.now().strftime("%d/%m/%Y a %H:%M"))


if __name__ == "__main__":
    main()
