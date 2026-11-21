"""Génère src/sprites/sprites.json, la planche de sprites du jeu.

Format (à respecter pour brancher les vrais sprites) :
{
  "palette": {"o": "#3b2414", ...},            # un caractère -> une couleur ; "." = transparent
  "kikou": {                                   # par stade 0..4
     "0": {"base": {"fps": 1, "frames": [[ "rang", ... ]]},
           "dort": {...}, "calme": {...}, ...  # optionnel : états et réactions
     }, ...
  },
  "props": {"main": {...}, "bol": {...}, ...}  # accessoires, même format
}
Toute animation absente d'un stade est remplacée en jeu par une animation
procédurale construite à partir de "base" (rebond, clignement, secousse...).
Noms reconnus pour Washi : base, dort, calme, faim, grognon, colere, content, teuf,
mange, refuse, sendort, fete, pascontent, reveille, dortsourit, propre, rien, surexcite, caca.
Les sprites de Washi regardent vers la gauche ; leur bas repose sur le sol.
"""
import json, os

PALETTE = {
  # Washi, berger australien noir tricolore (tools/vendor/washi.py)
  "o": "#151116", "f": "#34303a", "l": "#f7f2ea", "s": "#c97a3c", "g": "#6a6470",
  "e": "#4d9fdc", "w": "#ffffff", "n": "#0d0b0e", "k": "#1b1b1b", "p": "#f2a3a3",
  # accessoires
  "h": "#f1c7a0", "H": "#9a6a4a", "r": "#e0443e", "R": "#8e1f1f", "c": "#cf9a5c",
  "C": "#8c6239", "d": "#5b3a1e", "b": "#5a8fd0", "B": "#2f5a94", "y": "#f5d742",
  "x": "#ffffff", "z": "#6f7fb5", "m": "#7a7a8a", "M": "#4a4a58", "q": "#9be08a",
}

def a(*frames, fps=4):
    return {"fps": fps, "frames": [list(f) for f in frames]}

PROPS = {
  # main qui saupoudre (vient d'en haut à droite)
  "main": a([
    "..HHHH...",
    ".Hhhhhh..",
    "Hhhhhhhh.",
    "Hhhhhhhhh",
    ".Hhhhhhh.",
    "..HhhH.H.",
    "...HH....",
  ]),
  # doigt qui touche le nez (vient de la gauche)
  "doigt": a([
    "HHHH......",
    "hhhhHHHHH.",
    "hhhhhhhhhH",
    "hhhhHHHHH.",
    "HHHH......",
  ]),
  "bol": a([
    "y.y.y.y",
    "BbbbbbB",
    ".BbbbB.",
  ], [
    ".......",
    "BbbbbbB",
    ".BbbbB.",
  ]),
  "miette": a(["y"]),
  "bouche": a([
    ".rr.rr.",
    "rRrrrRr",
    ".rRRRr.",
    "..rrr..",
  ], [
    "..r.r..",
    ".rRrRr.",
    "..rRr..",
    "...r...",
  ]),
  "coeur": a([".r.r.", "rrrrr", "rrrrr", ".rrr.", "..r.."]),
  "z": a(["zzz", "..z", ".z.", "z..", "zzz"]),
  "nuage": a([".MMM..", "MmmmMM", "MmmmmM", ".MMMM."], [".MMM..", "MmmmMM", "MmmmmM", ".MMMM.", "..z..z"]),
  "colere": a(["r.r", ".r.", "r.r"], ["rr.", "..r", "rr."]),
  "exclam": a(["r", "r", "r", ".", "r"]),
  "croix": a(["R...R", ".R.R.", "..R..", ".R.R.", "R...R"]),
  "bulle": a([".oooooooo.", "oxxxxxxxxo", "oxxxxxxxxo", "oxxxxxxxxo", "oxxxxxxxxo",
              "oxxxxxxxxo", ".oooooooo.", "...oxo....", "....o....."]),
  # carton couché sur le côté (ouverture à droite)
  "carton": a([
    "CCCCCCCCCCCCCC..",
    "CccccccccccccC..",
    "CcdddddddddddCC.",
    "CcdddddddddddcCC",
    "CcdddddddddddccC",
    "CcdddddddddddccC",
    "CcdddddddddddccC",
    "CcdddddddddddccC",
    "CcdddddddddddcCC",
    "CccccccccccccCC.",
    "CCCCCCCCCCCCCC..",
  ]),
  # coussin donné à Washi (remplace le pip du Kikougochi)
  "coussin": {"fps": 1, "frames": [[
    "Y.........Y",
    ".PPPPPPPPP.",
    ".PpppppppP.",
    "PpqpppppppP",
    "PpppppppppP",
    ".PpppppppP.",
    ".PPPPPPPPP.",
    "Y.........Y",
  ]], "pal": {"P": "#8e3b6e", "p": "#e87aa0", "q": "#f6b8cf", "Y": "#f5d742"}},
  # caca (posé par terre) et balai pour nettoyer
  "caca": {"fps": 1, "frames": [[
    "..d...",
    ".dCd..",
    ".dddd.",
    "dCCCCd",
    "dddddd",
  ]], "pal": {"d": "#5b3a1e", "C": "#8c6239"}},
  "balai": {"fps": 1, "frames": [[
    "......H",
    ".....H.",
    "....H..",
    "...H...",
    "..H....",
    ".rr....",
    "yyyy...",
    "yYyYy..",
    "y.y.y..",
  ]], "pal": {"H": "#9a6a4a", "r": "#e0443e", "y": "#f5d742", "Y": "#c9a227"}},
}

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
from washi import STAGES as _ST   # sprites de base de Washi
STAGES = [g for _, g in _ST]

data = {"palette": PALETTE,
        "kikou": {str(i): {"base": a(g, fps=1)} for i, g in enumerate(STAGES)},
        "props": PROPS}
# Accessoires du fil visuels (prioritaires), avec leur propre palette
try:
    import etats as _E
    VP, VPAL = _E.PROPS, _E.PAL
    def va(*names, fps=6):
        fr = [list(VP[n]) for n in names]
        used = {c for f in fr for r in f for c in r if c != "."}
        return {"fps": fps, "frames": fr, "pal": {c: VPAL[c] for c in used if c in VPAL}}
    PROPS.update({"main": va("main_ouverte", "main_pince"), "miette": va("grain"),
                  "doigt": va("doigt"), "bouche": va("bouche_1", "bouche_2", fps=4),
                  "coeur_grand": va("coeur_3")})
    # Main qui pointe (index tendu, poing, manche)
    PROPS["doigt"] = {"fps": 1, "frames": [[
        ".......qqqq...",
        "......qhhhhqBB",
        "..qqqqqhqhhqbB",
        ".qnhhhhhqhhqbB",
        "..qqqqqqhhhqbB",
        "......qhhhhqbB",
        "......qqqhhqbB",
        "......qhhhhqbB",
        ".......qqqq.BB",
    ]], "pal": {"q": VPAL["q"], "h": VPAL["h"], "n": "#f7e3d0", "b": "#5a8fd0", "B": "#2f5a94"}}
except (ImportError, KeyError) as e:
    print("accessoires du fil visuels non trouvés :", e)
for i, g in enumerate(STAGES):
    assert len({len(r) for r in g}) == 1, i
out = os.path.join(os.path.dirname(__file__), "..", "src", "sprites", "sprites.json")
json.dump(data, open(out, "w"), ensure_ascii=False, indent=1)
print("ok", out)
