"""Génère les icônes de l'app et les rêves de Washi : des coussins en pixel art (64×64, agrandis ×4)."""
import os, sys, json, random, math
from PIL import Image, ImageDraw, ImageColor
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))
from washi import STAGES
import etats
PAL = etats.PAL
PUB = os.path.join(HERE, "..", "public")


def sprite(g, s):
    w = max(len(r) for r in g); im = Image.new("RGBA", (w * s, len(g) * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for y, r in enumerate(g):
        for x, c in enumerate(r):
            if c != "." and c in PAL: d.rectangle([x*s, y*s, (x+1)*s-1, (y+1)*s-1], fill=PAL[c])
    return im


def icon(size, pad=0.18, bg="#9fcbe6"):
    im = Image.new("RGBA", (size, size), bg)
    g = STAGES[2][1]; inner = int(size * (1 - 2 * pad)); s = inner // max(len(g), len(g[0]))
    sp = sprite(g, s); im.paste(sp, ((size - sp.width) // 2, (size - sp.height) // 2 + s // 2), sp)
    return im


os.makedirs(f"{PUB}/icons", exist_ok=True)
icon(192).save(f"{PUB}/icons/icon-192.png"); icon(512).save(f"{PUB}/icons/icon-512.png")
icon(512, pad=0.26).save(f"{PUB}/icons/icon-512-maskable.png")
icon(180, pad=0.14).convert("RGB").save(f"{PUB}/icons/apple-touch-icon.png")


# ---------- Rêves : coussins ----------
def shade(hexc, k):
    r, g, b = (int(hexc[i:i+2], 16) for i in (1, 3, 5))
    f = lambda v: max(0, min(255, int(v * k if k < 1 else v + (255 - v) * (k - 1))))
    return "#%02x%02x%02x" % (f(r), f(g), f(b))


def cushion_mask(kind, w, h):
    """Forme du coussin : ensemble des pixels (x, y) dans une boîte w×h."""
    pts = set()
    cx, cy = (w - 1) / 2, (h - 1) / 2
    for y in range(h):
        for x in range(w):
            u, v = (x - cx) / (w / 2), (y - cy) / (h / 2)
            if kind == "carre":    # coussin carré gonflé : bords creusés, coins pointus
                ok = abs(v) <= 1 - 0.12 * (1 - u * u) and abs(u) <= 1 - 0.12 * (1 - v * v)
            elif kind == "rond":
                ok = u * u + v * v <= 1
            elif kind == "coeur":
                X, Y = u * 1.25, -v * 1.3 + 0.2
                ok = (X * X + Y * Y - 1) ** 3 - X * X * Y ** 3 <= 0
            elif kind == "os":     # coussin en forme d'os
                ok = (abs(v) <= 0.45 and abs(u) <= 0.8) or any(
                    ((u - sx * 0.8) ** 2) / 0.04 + ((v - sy * 0.45) ** 2) / 0.3 <= 1 for sx in (-1, 1) for sy in (-1, 1))
            elif kind == "lune":
                ok = u * u + v * v <= 1 and (u - 0.5) ** 2 + (v + 0.25) ** 2 > 0.55
            elif kind == "boudin":  # traversin
                ok = abs(v) <= 0.9 and (abs(u) <= 0.85 or ((abs(u) - 0.85) / 0.15) ** 2 + v * v / 0.81 <= 1)
            else:
                ok = True
            if ok: pts.add((x, y))
    return pts


def pattern(kind, x, y, base, alt):
    if kind == "rayures": return alt if (x // 3) % 2 else base
    if kind == "pois": return alt if (x % 6 in (2, 3) and y % 6 in (2, 3)) or ((x + 3) % 6 in (2, 3) and (y + 3) % 6 in (2, 3)) else base
    if kind == "vichy": return alt if ((x // 3) + (y // 3)) % 2 else base
    if kind == "zigzag": return alt if (y + abs((x % 8) - 4)) % 6 < 2 else base
    if kind == "losanges": return alt if (abs((x % 8) - 4) + abs((y % 8) - 4)) == 3 else base
    return base


def draw_cushion(im, ox, oy, w, h, kind, pat, base, alt, tassels=None, motif=None):
    m = cushion_mask(kind, w, h)
    edge, light, dark = shade(base, 0.55), shade(base, 1.35), shade(base, 0.8)
    px = im.load()
    for (x, y) in m:
        border = any((x + dx, y + dy) not in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        c = edge if border else pattern(pat, x, y, base, alt)
        if not border and c == base:
            # volume : clair en haut à gauche, sombre en bas à droite
            if (x - 2, y - 2) not in m: c = light
            elif (x + 2, y + 2) not in m: c = dark
        X, Y = ox + x, oy + y
        if 0 <= X < im.width and 0 <= Y < im.height: px[X, Y] = ImageColor.getrgb(c)
    d = ImageDraw.Draw(im)
    cx, cy = ox + w // 2, oy + h // 2
    if kind in ("carre", "rond") and pat == "uni" and not motif:  # capiton central
        d.point([(cx, cy), (cx - 1, cy), (cx, cy - 1), (cx - 1, cy - 1)], fill=shade(base, 0.6))
    if motif == "coeur":
        for (x, y) in cushion_mask("coeur", 9, 8): d.point((cx - 4 + x, cy - 4 + y), fill=alt)
    if motif == "etoile":
        for i in range(5):
            a = -math.pi / 2 + i * 2 * math.pi / 5
            for r in range(6): d.point((round(cx + r * math.cos(a)), round(cy + r * math.sin(a))), fill=alt)
        d.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=alt)
    if motif == "patte":   # empreinte de patte
        cy2 = cy + 2
        d.ellipse([cx - 3, cy2 - 2, cx + 3, cy2 + 3], fill=alt)
        for dx, dy in ((-5, -4), (-2, -7), (2, -7), (5, -4)):
            d.ellipse([cx + dx - 1, cy2 + dy - 1, cx + dx + 1, cy2 + dy + 1], fill=alt)
    if tassels and kind == "carre":  # pompons aux coins
        for (x, y) in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            sx, sy = (-1 if x == 0 else 1), (-1 if y == 0 else 1)
            X, Y = ox + x, oy + y
            d.point([(X + sx, Y + sy), (X + 2 * sx, Y + 2 * sy), (X + 2 * sx, Y + sy), (X + sx, Y + 2 * sy)], fill=tassels)


def backdrop(im, sky, ground, rnd, deco):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 63, 63], fill=sky)
    d.rectangle([0, 46, 63, 63], fill=ground)
    for _ in range(16):
        x, y = rnd.randrange(60), rnd.randrange(2, 42)
        if deco == "etoiles": d.point((x, y), fill="#fff6c8")
        elif deco == "nuages" and rnd.random() < 0.3:
            d.rectangle([x, y, x + 6, y + 2], fill="#ffffff"); d.rectangle([x + 2, y - 1, x + 4, y], fill="#ffffff")
        elif deco == "coeurs": d.point([(x, y), (x + 2, y), (x, y + 1), (x + 1, y + 1), (x + 2, y + 1), (x + 1, y + 2)], fill="#f7a1c0")
        elif deco == "plumes" and rnd.random() < 0.5: d.line([(x, y), (x + 2, y + 3)], fill="#ffffff"); d.point((x + 1, y + 1), fill="#e0e0ea")


# (titre, ciel, sol, décor, forme, tissu, couleur, couleur 2, pompons, dessin)
DREAMS = [
    ("Le coussin rose à pompons", "#ffe3ec", "#f2b8c9", "coeurs", "carre", "uni", "#e87aa0", "#ffffff", "#f5d742", None),
    ("Le coussin à rayures", "#cfe9ff", "#9fc79a", "nuages", "carre", "rayures", "#5a8fd0", "#f4f1e6", None, None),
    ("Le coussin cœur", "#2b2f5c", "#3c3b6e", "etoiles", "coeur", "uni", "#e0443e", "#ffffff", None, None),
    ("Le coussin à pois", "#fff3cf", "#e6c98a", None, "carre", "pois", "#f2a03c", "#fff7e0", "#8c6239", None),
    ("Le gros coussin rond", "#d9f2e3", "#9ccfa8", "plumes", "rond", "uni", "#7c5cc4", "#ffffff", None, None),
    ("Le coussin vichy", "#fdeede", "#d6b08a", None, "carre", "vichy", "#d0453f", "#f7efe4", None, None),
    ("Le coussin en os", "#bfe6ff", "#86c27a", "nuages", "os", "uni", "#f0d9a8", "#ffffff", None, None),
    ("Le coussin lune", "#1d2452", "#2e3a6e", "etoiles", "lune", "uni", "#f5d742", "#ffffff", None, None),
    ("Le coussin étoile", "#e9e4ff", "#b9b0e6", "etoiles", "carre", "uni", "#3a3f8f", "#f5d742", "#f5d742", "etoile"),
    ("Le traversin zigzag", "#ffe9d6", "#e4b48c", "plumes", "boudin", "zigzag", "#2a9d8f", "#f4f1e6", None, None),
    ("Le coussin patte de chien", "#d8f0ff", "#a6d29e", "nuages", "carre", "uni", "#9bc4e8", "#34303a", "#ffffff", "patte"),
    ("Le coussin du canapé", "#f7e8ff", "#c9a5d9", "coeurs", "carre", "losanges", "#8e3b6e", "#f2a3c8", "#f5d742", None),
]
SIZES = {"carre": (36, 28), "rond": (32, 30), "coeur": (34, 30), "os": (40, 22), "lune": (32, 30), "boudin": (44, 18)}

os.makedirs(f"{PUB}/reves", exist_ok=True)
names, titles = [], {}
for i, (nom, sky, ground, deco, kind, pat, base, alt, tas, motif) in enumerate(DREAMS):
    rnd = random.Random(i + 10)
    im = Image.new("RGB", (64, 64), sky)
    backdrop(im, sky, ground, rnd, deco)
    w, h = SIZES[kind]
    ox, oy = 32 - w // 2, 49 - h
    ImageDraw.Draw(im).ellipse([ox + 3, 46, ox + w - 3, 51], fill=shade(ground, 0.8))  # ombre
    draw_cushion(im, ox, oy, w, h, kind, pat, base, alt, tas, motif)
    n = f"coussin-{i+1:02d}.png"
    im.resize((256, 256), Image.NEAREST).save(f"{PUB}/reves/{n}")
    names.append(n); titles[n] = nom
json.dump({"photos": names, "titres": titles}, open(f"{PUB}/reves/reves.json", "w"), ensure_ascii=False, indent=1)
print("ok", names)
