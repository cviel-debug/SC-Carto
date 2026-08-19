#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dxf2fond.py — convertit un DXF AutoCAD en fond de plan SVG allege pour SC Carto.

Principe : on aplatit la geometrie utile (lignes, polylignes, arcs, cercles, splines,
blocs eclates) en simples traits, on jette le superflu (hachures, cotations, calques
non retenus), et on ecrit un seul SVG en coordonnees pixels.

Deux fichiers sont produits :
  plan.svg           le fond de plan a importer dans l'application
  plan.calage.json   la correspondance pixels <-> coordonnees DXF,
                     indispensable a points2dxf.py pour le chemin retour.

Exemples
--------
    # 1. voir ce que contient le DXF
    python dxf2fond.py usine.dxf --lister

    # 2. convertir en ne gardant que les calques utiles
    python dxf2fond.py usine.dxf -o fond.svg --couches MURS,CLOISONS,POTEAUX

    # 3. convertir tout sauf le mobilier et les cotations
    python dxf2fond.py usine.dxf -o fond.svg --exclure MOBILIER,COTES,AXES

Dependance :  pip install ezdxf
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime

try:
    import ezdxf
    from ezdxf import path as ezpath
    from ezdxf import recover
except ImportError:
    sys.exit("Bibliotheque manquante. Installez-la avec :  pip install ezdxf")

# La console Windows n'encode pas tous les caracteres : un nom de calque exotique
# ne doit pas faire planter l'affichage.
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


# Types d'entites systematiquement ignores : ils alourdissent sans servir de fond de plan.
IGNORES = {"HATCH", "DIMENSION", "LEADER", "MULTILEADER", "MTEXT", "TEXT",
           "ATTDEF", "ATTRIB", "IMAGE", "WIPEOUT", "VIEWPORT", "POINT",
           "SHAPE", "TOLERANCE", "MESH", "BODY", "REGION", "3DSOLID"}

# Ces types-la donnent des traits exploitables.
GEOMETRIQUES = {"LINE", "LWPOLYLINE", "POLYLINE", "ARC", "CIRCLE", "ELLIPSE",
                "SPLINE", "SOLID", "TRACE", "3DFACE", "HELIX"}


# --------------------------------------------------------------------------- #
#  Lecture du DXF
# --------------------------------------------------------------------------- #
def ouvrir(chemin):
    """Ouvre le DXF, en reparant le fichier si besoin."""
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


def entites_a_plat(espace, profondeur=0):
    """Parcourt l'espace objet en eclatant les blocs (INSERT) rencontres.

    Convention AutoCAD : la geometrie dessinee sur le calque 0 a l'interieur d'un bloc
    prend le calque de l'insertion. On la reporte, sinon les poteaux et autres symboles
    inseres se retrouveraient tous sur le calque 0 et echapperaient au filtrage."""
    for e in espace:
        t = e.dxftype()
        if t == "INSERT":
            if profondeur >= 6:          # garde-fou contre les blocs recursifs
                continue
            parent = nom_couche(e)
            try:
                sous_entites = list(e.virtual_entities())
            except Exception:
                continue
            for sous in entites_a_plat(sous_entites, profondeur + 1):
                if parent != "0" and nom_couche(sous) == "0":
                    try:
                        sous.dxf.layer = parent
                    except Exception:
                        pass
                yield sous
        else:
            yield e


def nom_couche(e):
    try:
        return str(e.dxf.layer)
    except Exception:
        return "0"


def inventaire(doc):
    """Compte les entites par calque : sert au mode --lister."""
    compte = {}
    for e in entites_a_plat(doc.modelspace()):
        t = e.dxftype()
        if t in IGNORES:
            continue
        c = compte.setdefault(nom_couche(e), {"total": 0, "types": {}})
        c["total"] += 1
        c["types"][t] = c["types"].get(t, 0) + 1
    return compte


# --------------------------------------------------------------------------- #
#  Geometrie
# --------------------------------------------------------------------------- #
def polylignes(e, tolerance):
    """Transforme une entite en une ou plusieurs suites de points (x, y)."""
    t = e.dxftype()
    if t in ("SOLID", "TRACE", "3DFACE"):
        try:
            pts = [(p[0], p[1]) for p in
                   (e.dxf.vtx0, e.dxf.vtx1, e.dxf.vtx2, e.dxf.vtx3)]
            # vtx2 et vtx3 sont souvent confondus : on ferme proprement
            uniq = [pts[0]]
            for p in pts[1:]:
                if abs(p[0] - uniq[-1][0]) > 1e-9 or abs(p[1] - uniq[-1][1]) > 1e-9:
                    uniq.append(p)
            if len(uniq) > 2:
                uniq.append(uniq[0])
                return [uniq]
        except Exception:
            pass
        return []
    try:
        chemin = ezpath.make_path(e)
    except Exception:
        return []
    try:
        pts = [(v.x, v.y) for v in chemin.flattening(distance=tolerance, segments=4)]
    except Exception:
        return []
    return [pts] if len(pts) > 1 else []


def simplifier(pts, seuil):
    """Retire les points inutiles : trop proches, ou alignes avec leurs voisins."""
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for p in pts[1:-1]:
        a = out[-1]
        if math.hypot(p[0] - a[0], p[1] - a[1]) < seuil:
            continue
        out.append(p)
    out.append(pts[-1])
    if len(out) < 3:
        return out
    # suppression des points alignes (aire du triangle sous le seuil)
    net = [out[0]]
    for i in range(1, len(out) - 1):
        a, b, c = net[-1], out[i], out[i + 1]
        aire = abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2.0
        if aire > seuil * seuil * 0.5:
            net.append(b)
    net.append(out[-1])
    return net


def etendue(traces):
    xmin = ymin = float("inf")
    xmax = ymax = float("-inf")
    for pts in traces:
        for x, y in pts:
            if x < xmin: xmin = x
            if x > xmax: xmax = x
            if y < ymin: ymin = y
            if y > ymax: ymax = y
    return xmin, ymin, xmax, ymax


# --------------------------------------------------------------------------- #
#  Ecriture du SVG
# --------------------------------------------------------------------------- #
def ecrire_svg(traces, xmin, ymin, echelle, larg, haut, decimales, epaisseur, fond, trait):
    """Assemble le SVG. Les coordonnees sont deja en pixels, sans transform SVG :
    l'application lit donc directement des pixels, et points2dxf.py fait l'inverse."""
    fmt = "%%.%df" % decimales
    morceaux = []
    for pts in traces:
        d = []
        prem = True
        for x, y in pts:
            px = (x - xmin) * echelle
            py = haut - (y - ymin) * echelle
            d.append(("M" if prem else "L") + (fmt % px) + " " + (fmt % py))
            prem = False
        morceaux.append("".join(d))
    corps = "".join('<path d="%s"/>' % m for m in morceaux)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d">\n'
        '<rect x="0" y="0" width="%d" height="%d" fill="%s"/>\n'
        '<g fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" '
        'stroke-linejoin="round">%s</g>\n</svg>\n'
        % (larg, haut, larg, haut, larg, haut, fond, trait, epaisseur, corps)
    )


# --------------------------------------------------------------------------- #
#  Programme
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(
        description="Convertit un DXF en fond de plan SVG allege pour SC Carto.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    ap.add_argument("dxf", help="fichier DXF a convertir")
    ap.add_argument("-o", "--sortie", help="fichier SVG produit (defaut : <dxf>.svg)")
    ap.add_argument("--lister", action="store_true",
                    help="affiche les calques et leur contenu, puis s'arrete")
    ap.add_argument("--couches", default="",
                    help="ne garder que ces calques (noms separes par des virgules)")
    ap.add_argument("--exclure", default="",
                    help="ignorer ces calques (noms separes par des virgules)")
    ap.add_argument("--largeur", type=int, default=4000,
                    help="taille en pixels du plus grand cote (defaut 4000)")
    ap.add_argument("--max-mo", type=float, default=2.0,
                    help="taille maximale du SVG en Mo (defaut 2)")
    ap.add_argument("--epaisseur", default="1.2", help="epaisseur du trait (defaut 1.2)")
    ap.add_argument("--fond", default="#ffffff", help="couleur de fond (defaut blanc)")
    ap.add_argument("--trait", default="#141414", help="couleur des traits (defaut noir)")
    a = ap.parse_args()

    if not os.path.isfile(a.dxf):
        sys.exit("Fichier introuvable : %s" % a.dxf)

    print("Lecture de %s ..." % a.dxf)
    doc = ouvrir(a.dxf)
    msp = doc.modelspace()

    # ---- mode inventaire -------------------------------------------------- #
    if a.lister:
        inv = inventaire(doc)
        if not inv:
            sys.exit("Aucune entite exploitable dans ce DXF.")
        print("\n%-34s %8s   %s" % ("CALQUE", "ENTITES", "TYPES"))
        print("-" * 78)
        for nom in sorted(inv, key=lambda n: -inv[n]["total"]):
            d = inv[nom]
            types = ", ".join("%s x%d" % (t, n) for t, n in
                              sorted(d["types"].items(), key=lambda kv: -kv[1])[:4])
            print("%-34s %8d   %s" % (nom[:34], d["total"], types))
        print("-" * 78)
        print("%d calque(s). Reprenez la commande avec --couches ou --exclure." % len(inv))
        return

    # ---- selection des calques -------------------------------------------- #
    garder = set(s.strip().upper() for s in a.couches.split(",") if s.strip())
    jeter = set(s.strip().upper() for s in a.exclure.split(",") if s.strip())

    # ---- premiere passe : etendue approximative pour calibrer la finesse --- #
    brut = []
    for e in entites_a_plat(msp):
        if e.dxftype() not in GEOMETRIQUES:
            continue
        c = nom_couche(e).upper()
        if garder and c not in garder:
            continue
        if c in jeter:
            continue
        brut.append(e)

    if not brut:
        sys.exit("Aucune geometrie retenue. Verifiez --couches / --exclure "
                 "(lancez --lister pour voir les calques disponibles).")

    print("%d entite(s) retenue(s) sur %d calque(s)."
          % (len(brut), len(set(nom_couche(e).upper() for e in brut))))

    grossier = []
    for e in brut:
        for pts in polylignes(e, 1.0):
            grossier.append(pts)
    if not grossier:
        sys.exit("Geometrie illisible : rien a tracer.")
    xmin, ymin, xmax, ymax = etendue(grossier)
    larg_u = max(xmax - xmin, 1e-9)
    haut_u = max(ymax - ymin, 1e-9)
    echelle = a.largeur / max(larg_u, haut_u)     # pixels par unite DXF

    # ---- seconde passe : aplatissement a la finesse du pixel -------------- #
    tol = 0.4 / echelle          # ~0.4 pixel de fleche maximale
    traces = []
    for e in brut:
        for pts in polylignes(e, tol):
            pts = simplifier(pts, 0.5 / echelle)
            if len(pts) > 1:
                traces.append(pts)

    xmin, ymin, xmax, ymax = etendue(traces)
    larg_u = max(xmax - xmin, 1e-9)
    haut_u = max(ymax - ymin, 1e-9)
    echelle = a.largeur / max(larg_u, haut_u)
    larg = max(1, int(round(larg_u * echelle)))
    haut = max(1, int(round(haut_u * echelle)))

    # ---- ecriture, avec degradation progressive si le fichier est trop gros - #
    plafond = a.max_mo * 1024 * 1024
    svg = None
    for decimales, filtre in ((1, 0.0), (1, 1.0), (0, 1.5), (0, 3.0)):
        jeu = traces
        if filtre:
            jeu = []
            for pts in traces:
                p = simplifier(pts, filtre / echelle)
                # on jette aussi les micro-traits invisibles a l'ecran
                lg = sum(math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1])
                         for i in range(len(p) - 1))
                if len(p) > 1 and lg * echelle > filtre:
                    jeu.append(p)
        svg = ecrire_svg(jeu, xmin, ymin, echelle, larg, haut,
                         decimales, a.epaisseur, a.fond, a.trait)
        taille = len(svg.encode("utf-8"))
        if taille <= plafond:
            traces = jeu
            break
        print("  %.2f Mo > plafond : on simplifie davantage..." % (taille / 1048576.0))
    taille = len(svg.encode("utf-8"))

    sortie = a.sortie or (os.path.splitext(a.dxf)[0] + ".svg")
    with open(sortie, "w", encoding="utf-8") as f:
        f.write(svg)

    calage = {
        "format": "sc-carto-fond",
        "version": 1,
        "source_dxf": os.path.basename(a.dxf),
        "genere": datetime.now().isoformat(timespec="seconds"),
        "unites_dxf": str(doc.header.get("$INSUNITS", 0)),
        "svg": {"fichier": os.path.basename(sortie),
                "largeur_px": larg, "hauteur_px": haut},
        "transformation": {
            "echelle_px_par_unite": echelle,
            "xmin": xmin, "ymin": ymin,
            "hauteur_px": haut
        },
        "formules": {
            "px_x": "(dxf_x - xmin) * echelle_px_par_unite",
            "px_y": "hauteur_px - (dxf_y - ymin) * echelle_px_par_unite",
            "dxf_x": "px_x / echelle_px_par_unite + xmin",
            "dxf_y": "(hauteur_px - px_y) / echelle_px_par_unite + ymin"
        }
    }
    fcal = os.path.splitext(sortie)[0] + ".calage.json"
    with open(fcal, "w", encoding="utf-8") as f:
        json.dump(calage, f, ensure_ascii=False, indent=1)

    print("")
    print("  SVG      : %s  (%d x %d px, %.2f Mo, %d traces)"
          % (sortie, larg, haut, taille / 1048576.0, len(traces)))
    print("  Calage   : %s" % fcal)
    print("  Echelle  : 1 unite DXF = %.4f px   /   1 px = %.4f unite DXF"
          % (echelle, 1.0 / echelle))
    print("  Emprise  : %.1f x %.1f unites DXF" % (larg_u, haut_u))
    print("")
    print("  A faire : copier le SVG sur le telephone, puis Reglages > Importer un fond de plan.")
    print("  Gardez le fichier .calage.json a cote du DXF : points2dxf.py en a besoin.")


if __name__ == "__main__":
    main()
