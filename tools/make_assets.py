"""Génère les icônes de l'app. Les rêves sont des photos libres de coussins (tools/fetch_reves.py)."""
import os, sys
from PIL import Image, ImageDraw
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
