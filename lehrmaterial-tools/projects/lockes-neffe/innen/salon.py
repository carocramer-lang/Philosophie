#!/usr/bin/env python3
# Innenraum Historischer Salon: 40 x 24 Kacheln a 16 px, Topdown, gleiche Bausteine wie die anderen Raeume.
# Aufruf: python3 innen/salon.py
# Ausgabe: salon.png, salon_2x.png, salon_kollision.png, salon.json und salon_daten.js

import json, math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "welt"))
import generator as G  # noqa: E402
import observatorium as O  # noqa: E402  (Moebel und Wandbausteine)

T = 16
W, H = 40, 24
PW, PH = W * T, H * T
cv = G.Canvas(PW, PH)
G.cv = O.cv = cv
h2, mul, jit, lerp = G.h2, G.mul, G.jit, G.lerp
DARK = G.DARK

# ---------------------------------------------------------------- Raster
# '#' Boden, 'X' Wand/Moebel, 'A' Ausgang, 'S' Eintrittsstelle, 'I' Interaktionsflaeche
grid = [["#"] * W for _ in range(H)]

def fill(x0, y0, x1, y1, t):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            grid[y][x] = t

fill(0, 0, W - 1, 2, "X")
fill(0, 0, 0, H - 1, "X")
fill(W - 1, 0, W - 1, H - 1, "X")
fill(0, 22, W - 1, H - 1, "X")
fill(18, 22, 21, 22, "A")
fill(18, 20, 21, 20, "S")

# Interaktionspunkte: Objekt (blockiert) und freie Flaeche davor (begehbar, 'I').
# sekretaer: Brief der Akademie mit dem Analyseauftrag, hier wird auch geschrieben (markiert, leuchtet zuerst)
# kamin: hier erscheint der Geist des Philosophen und gibt Rueckmeldung
INTERAKTIONEN = [
    {"id": "sekretaer", "objekt": (3, 3, 6, 4), "flaeche": (3, 5, 6, 6), "markiert": True},
    {"id": "kamin", "objekt": (17, 3, 22, 5), "flaeche": (18, 6, 21, 6), "markiert": False},
]
# Fusspunkt des Geistes vor dem Kamin (Kachelkoordinaten, x zwischen zwei Kacheln)
GEIST = {"x": 19.5, "y": 5}
# Grosses Portraet ueber dem Kamin (Rahmen x, y, Breite, Hoehe in Pixeln). Waehrend der Geist im Raum steht, ist es leer.
PORTRAET = (18 * T + 6, 7, 4 * T - 12, 30)

objs = []

def block(x0, y0, w, h, fn):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            assert grid[y][x] == "#", ("belegt", x, y)
            grid[y][x] = "X"
    objs.append(((y0 + h) * T, fn))

def mk(f, *a):
    return lambda: f(*a)

# ---------------------------------------------------------------- Boden: Fischgraetparkett
def herringbone(x, y):
    """Fischgraet: Staebe 16 x 4 px, abwechselnd nach rechts und links geneigt."""
    col = x // 16
    ly = (y + (x % 16) * (1 if col % 2 == 0 else -1)) % 64
    k = ly // 4
    base = [(150, 92, 52), (136, 82, 46), (162, 102, 58), (144, 88, 50)][(k + col * 3) % 4]
    c = jit(base, (h2(x // 3, k + col * 17, 31) - 0.5) * 10)
    if ly % 4 == 3:
        return mul(base, 0.7)
    if x % 16 == 0:
        return mul(base, 0.76)
    if ly % 4 == 0:
        c = mul(c, 1.08)
    return c

def floor_pass():
    b = cv.b
    for y in range(PH):
        for x in range(PW):
            c = herringbone(x, y)
            i = (y * PW + x) * 3
            b[i] = c[0]; b[i + 1] = c[1]; b[i + 2] = c[2]

def pool(cx, cy, rx, ry, f):
    for py in range(int(cy - ry), int(cy + ry) + 1):
        for px in range(int(cx - rx), int(cx + rx) + 1):
            d = ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2
            if d < 1:
                cv.shade(px, py, 1 + (f - 1) * (1 - d) ** 1.5)

# ---------------------------------------------------------------- Teppiche
def persian(x, y, w, h, feld=(150, 36, 44), rand=(34, 48, 96), gold=(214, 170, 80)):
    """Orientteppich mit Bordueren, Mittelmedaillon und Fransen an den Schmalseiten."""
    cv.shade_rect(x + 3, y + 3, w, h, 0.8)
    for fx in range(x + 2, x + w - 2, 3):
        cv.rect(fx, y - 3, 1, 3, (236, 226, 200))
        cv.rect(fx, y + h, 1, 3, (236, 226, 200))
    cv.rect(x, y, w, h, mul(rand, 0.7))
    cv.rect(x + 2, y + 2, w - 4, h - 4, rand)
    for px in range(x + 3, x + w - 3):
        for py in (y + 4, y + h - 5):
            if (px // 3) % 2 == 0:
                cv.set(px, py, gold)
    for py in range(y + 3, y + h - 3):
        for px in (x + 4, x + w - 5):
            if (py // 3) % 2 == 0:
                cv.set(px, py, gold)
    cv.rect(x + 8, y + 8, w - 16, h - 16, mul(gold, 0.8))
    cv.rect(x + 9, y + 9, w - 18, h - 18, feld)
    cx, cy = x + w / 2, y + h / 2
    for py in range(y + 10, y + h - 10):
        for px in range(x + 10, x + w - 10):
            if (px + py) % 12 == 0 or (px - py) % 12 == 0:
                cv.set(px, py, mul(feld, 1.18))
    rx, ry = min(w, h * 1.6) * 0.26, min(h, w / 1.6) * 0.26
    for py in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for px in range(int(cx - rx) - 1, int(cx + rx) + 2):
            d = abs(px - cx) / rx + abs(py - cy) / ry
            if d < 1:
                c = rand if d > 0.82 else (gold if d > 0.72 else (mul(feld, 0.78) if d > 0.35 else gold))
                if d < 0.2:
                    c = (236, 226, 200)
                cv.set(px, py, c)
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        ex, ey = cx + sx * (w / 2 - 16), cy + sy * (h / 2 - 16)
        cv.ellipse(ex, ey, 4, 3, gold)
        cv.ellipse(ex, ey, 2, 1.5, rand)

# ---------------------------------------------------------------- Waende
DAMAST = (118, 34, 46)
PANEEL = (236, 226, 204)

def damask_wall(x, y, w, h):
    """Rote Seidentapete mit Rautenmuster, darunter weisse Wandvertaefelung."""
    for py in range(y, y + h):
        for px in range(x, x + w):
            u, v = px % 12, (py - y) % 14
            d = abs(u - 6) / 6 + abs(v - 7) / 7
            c = mul(DAMAST, 0.95 + G.vnoise(px, py, 6, 40) * 0.08)
            if 0.78 < d < 0.92 or (d < 0.25 and (u + v) % 2 == 0):
                c = mul(DAMAST, 1.28)
            cv.set(px, py, c)
    for i, f in enumerate((0.5, 0.66, 0.8, 0.9)):
        cv.shade_rect(x, y + i, w, 1, f)

def gilt_frame(x, y, w, h, inner=None):
    cv.rect(x - 1, y - 1, w + 2, h + 2, (70, 48, 20))
    cv.rect(x, y, w, h, (214, 170, 72))
    cv.rect(x, y, w, 1, (250, 222, 130))
    cv.rect(x, y + h - 1, w, 1, (150, 110, 40))
    cv.rect(x + 2, y + 2, w - 4, h - 4, (120, 86, 30))
    if inner:
        cv.rect(x + 3, y + 3, w - 6, h - 6, inner)

def landscape(x, y, w, h, seed):
    """Kleines Oelbild: Himmel, Huegel, ein Baum."""
    gilt_frame(x, y, w, h)
    ix, iy, iw, ih = x + 3, y + 3, w - 6, h - 6
    for py in range(iy, iy + ih):
        t = (py - iy) / ih
        cv.rect(ix, py, iw, 1, lerp((150, 180, 196), (228, 206, 150), t))
    rng = random.Random(seed)
    base = iy + ih * 0.55
    for px in range(ix, ix + iw):
        top = int(base + math.sin(px * 0.25 + seed) * 2 + rng.random())
        cv.rect(px, top, 1, iy + ih - top, (86, 110, 64) if px % 3 else (74, 96, 56))
    tx = ix + 3 + rng.randint(0, max(1, iw - 8))
    cv.rect(tx + 1, int(base) - 3, 1, 4, (70, 50, 34))
    cv.ellipse(tx + 1, int(base) - 5, 2.5, 2.5, (60, 84, 50))

def small_portrait(x, y, w, h, coat, hair):
    gilt_frame(x, y, w, h, (40, 32, 30))
    cx = x + w // 2
    cv.rect(cx - 4, y + h - 8, 9, 5, coat)
    cv.rect(cx - 1, y + h - 9, 3, 2, (236, 232, 222))
    cv.ellipse(cx, y + h - 12, 2.5, 3, (226, 190, 160))
    cv.ellipse(cx, y + h - 14, 3.5, 2.5, hair)
    cv.rect(cx - 4, y + h - 13, 2, 5, hair)
    cv.rect(cx + 3, y + h - 13, 2, 5, hair)

def sconce(cx, cy):
    O.glow(cx, cy, 20, 1.25)
    cv.rect(cx - 2, cy + 2, 5, 2, (200, 160, 60))
    cv.rect(cx - 1, cy - 3, 3, 5, (246, 240, 224))
    cv.set(cx, cy - 5, (255, 214, 90))
    cv.set(cx, cy - 4, (255, 240, 170))

def back_wall():
    hh = 3 * T
    cv.rect(0, 0, PW, 6, O.CAP)
    cv.rect(0, 5, PW, 1, O.CAP_L)
    damask_wall(0, 6, PW, hh - 6)
    # Vertaefelung unten mit Feldern
    py0 = hh - 13
    cv.rect(0, py0, PW, 10, PANEEL)
    cv.rect(0, py0, PW, 1, (252, 246, 232))
    cv.rect(0, py0 + 1, PW, 1, (200, 188, 164))
    for px in range(4, PW - 8, 24):
        cv.rect(px, py0 + 3, 20, 5, (226, 214, 188))
        cv.rect(px, py0 + 3, 20, 1, (196, 182, 156))
        cv.rect(px, py0 + 7, 20, 1, (250, 244, 228))
    # Fenster mit roten Vorhaengen wie an der Fassade, dazwischen Bilder und Wandleuchter
    fenster = [2 * T + 8, 10 * T + 8, 28 * T + 8, 35 * T + 8]
    for fx in fenster:
        G.window(fx, 10, 14, 24, "lit", arch=True, curtain=(170, 40, 50))
        cv.rect(fx - 4, 8, 3, 28, (150, 30, 42))
        cv.rect(fx + 15, 8, 3, 28, (150, 30, 42))
        cv.rect(fx - 5, 7, 24, 2, (214, 170, 72))
    landscape(6 * T + 2, 12, 26, 18, 3)
    small_portrait(13 * T + 4, 10, 16, 22, (60, 40, 70), (240, 236, 228))
    small_portrait(25 * T - 4, 10, 16, 22, (40, 70, 60), (70, 50, 40))
    landscape(31 * T + 6, 12, 26, 18, 7)
    for sx in (9 * T + 4, 16 * T - 2, 24 * T + 2, 33 * T + 8):
        sconce(sx, 22)
    cv.rect(0, hh - 3, PW, 3, (74, 46, 30))
    cv.rect(0, hh - 3, PW, 1, (110, 72, 44))
    cv.shade_rect(0, hh, PW, 4, 0.78)
    for fx in fenster:
        O.light_pool(fx, fx + 14, hh + 44, 44)

# ---------------------------------------------------------------- Kamin mit grossem Portraet
def fireplace():
    """Kaminvorsprung in der Rueckwand, grosses Portraet darueber, Feuerstelle auf dem Boden."""
    x0, x1 = 17 * T, 23 * T
    # Kaminvorsprung (etwas heller, wirft Schatten)
    cv.rect(x0 + 6, 6, x1 - x0 - 12, 3 * T - 6, mul(DAMAST, 1.1))
    cv.shade_rect(x1 - 6, 8, 4, 3 * T - 8, 0.7)
    # grosses Portraet: Platon mit Stirnband und weissem Bart, im Himation. Aus diesem Bild tritt der Geist.
    px, py, pw, ph = PORTRAET
    gilt_frame(px, py, pw, ph, (34, 28, 30))
    for yy in range(py + 3, py + ph - 3):
        t = (yy - py) / ph
        cv.rect(px + 3, yy, pw - 6, 1, lerp((60, 50, 44), (28, 24, 26), t))
    cx = px + pw // 2
    cv.rect(cx - 12, py + ph - 11, 24, 8, (226, 214, 188))          # Himation
    cv.line(cx - 12, py + ph - 11, cx + 6, py + ph - 3, (176, 150, 110))
    cv.rect(cx + 6, py + ph - 11, 6, 8, (170, 120, 70))               # ockerfarbener Saum ueber der Schulter
    cv.ellipse(cx, py + 13, 4, 5, (222, 186, 150))                   # Gesicht
    cv.set(cx - 2, py + 12, (60, 40, 30)); cv.set(cx + 1, py + 12, (60, 40, 30))
    cv.ellipse(cx, py + 8, 6, 3, (236, 234, 228))                    # weisses Haar
    cv.rect(cx - 6, py + 8, 12, 1, (214, 170, 72))                   # Stirnband
    cv.ellipse(cx, py + 19, 5, 5, (240, 238, 232))                   # Bart
    cv.ellipse(cx, py + 17, 3, 1.5, (240, 238, 232))
    cv.rect(cx - 1, py + 16, 2, 1, (170, 110, 90))
    for dx, dy in ((-2, 20), (1, 22), (2, 18)):
        cv.set(cx + dx, py + dy, (200, 196, 190))
    # Kaminsims aus Marmor
    mx0, mx1, my = x0 + 4, x1 - 4, 2 * T + 6
    cv.rect(mx0 - 3, my - 3, mx1 - mx0 + 6, 5, (246, 240, 228))
    cv.rect(mx0 - 3, my + 1, mx1 - mx0 + 6, 1, (170, 160, 146))
    cv.rect(mx0, my + 2, mx1 - mx0, 5 * T - my - 2, (232, 226, 214))
    for yy in range(my + 2, 5 * T):
        for xx in range(mx0, mx1):
            if G.vnoise(xx, yy, 5, 17) > 0.62 and h2(xx, yy, 3) < 0.4:
                cv.set(xx, yy, (200, 196, 190))
    cv.rect(mx1 - 3, my + 2, 3, 5 * T - my - 2, (196, 188, 174))
    # Feueroeffnung mit Glut und Flammen
    ox0, ox1, oy0, oy1 = mx0 + 12, mx1 - 12, my + 8, 5 * T
    cv.rect(ox0, oy0, ox1 - ox0, oy1 - oy0, (30, 22, 20))
    for yy in range(oy0, oy0 + 6):
        cv.rect(ox0, yy, ox1 - ox0, 1, lerp((16, 12, 12), (30, 22, 20), (yy - oy0) / 6))
    for k in range(ox1 - ox0):
        hgt = int(8 + 7 * abs(math.sin(k * 0.55)) + h2(k, 1, 44) * 4)
        for j in range(hgt):
            t = j / hgt
            c = lerp((255, 236, 150), (220, 70, 30), t)
            if t > 0.8:
                c = (150, 40, 24)
            cv.set(ox0 + k, oy1 - 3 - j, c)
    cv.rect(ox0 + 2, oy1 - 4, ox1 - ox0 - 4, 3, (90, 50, 36))       # Holzscheite
    cv.rect(ox0 + 6, oy1 - 6, ox1 - ox0 - 14, 2, (120, 70, 44))
    for k in range(10):
        cv.set(ox0 + 3 + int(h2(k, 2, 45) * (ox1 - ox0 - 6)), oy1 - 2, (255, 150, 60))
    # Herdplatte, Messinggitter und Feuerschein
    cv.rect(x0 + 2, 5 * T, x1 - x0 - 4, T - 2, (206, 198, 186))
    cv.rect(x0 + 2, 5 * T, x1 - x0 - 4, 1, (240, 236, 226))
    cv.rect(x0 + 2, 6 * T - 3, x1 - x0 - 4, 1, (150, 142, 130))
    cv.rect(ox0 - 4, 5 * T + 3, ox1 - ox0 + 8, 2, (214, 170, 72))
    for xx in range(ox0 - 4, ox1 + 5, 4):
        cv.rect(xx, 5 * T, 1, 4, (190, 150, 60))
    cv.rect(ox1 + 8, 5 * T - 12, 2, 14, (60, 54, 54))                 # Schuerhaken
    cv.rect(ox1 + 7, 5 * T - 13, 4, 2, (214, 170, 72))
    pool((ox0 + ox1) / 2, 6 * T + 6, 58, 28, 1.3)

# ---------------------------------------------------------------- Moebel
def wing_chair(tx, ty, facing):
    """Ohrensessel, schraeg zum Kamin gedreht (facing -1: nach links oben, 1: nach rechts oben)."""
    x, y = tx * T + 2, ty * T + 2
    O.shadow_box(x + 2, y + 4, 24, 22)
    cv.rect(x + 2, y + 4, 24, 24, (70, 44, 28))
    cv.rect(x + 4, y + 6, 20, 18, (40, 84, 70))
    cv.rect(x + 3, y + 22, 22, 6, (32, 68, 56))
    cv.rect(x + 3, y + 22, 22, 1, (60, 110, 92))
    side = x + 2 if facing > 0 else x + 20
    cv.rect(side, y + 6, 6, 18, (32, 68, 56))
    cv.rect(x + 8, y + 9, 12, 9, (54, 104, 86))
    cv.rect(x + 9, y + 10, 4, 2, (80, 132, 112))
    for lx in (x + 3, x + 23):
        cv.rect(lx, y + 27, 2, 2, (214, 170, 72))

def settee_group(tx, ty):
    """Kanapee mit Teetisch und zwei Stuehlen: Tee kam um 1660 in Londoner Salons in Mode."""
    x, y = tx * T, ty * T
    # Kanapee
    O.shadow_box(x + 2, y + 2, 5 * T - 4, 26)
    cv.rect(x + 2, y + 2, 5 * T - 4, 26, (150, 110, 40))
    cv.rect(x + 4, y + 4, 5 * T - 8, 10, (160, 40, 52))
    cv.rect(x + 4, y + 4, 5 * T - 8, 1, (200, 70, 80))
    for px in range(x + 14, x + 5 * T - 8, 14):
        cv.set(px, y + 8, (214, 170, 72))
    cv.rect(x + 4, y + 14, 5 * T - 8, 10, (140, 32, 44))
    for k in range(3):
        cv.rect(x + 6 + k * 24, y + 15, 22, 8, (176, 48, 60))
        cv.rect(x + 6 + k * 24, y + 22, 22, 1, (110, 24, 34))
    cv.rect(x + 2, y + 2, 4, 26, (176, 132, 56))
    cv.rect(x + 5 * T - 6, y + 2, 4, 26, (176, 132, 56))
    # Teetisch mit Service
    t0 = y + 3 * T - 4
    O.shadow_box(x + 20, t0, 40, 16)
    cv.rect(x + 20, t0, 40, 14, (96, 60, 36))
    cv.rect(x + 21, t0 + 1, 38, 10, (128, 82, 48))
    cv.rect(x + 20, t0 + 11, 40, 3, (74, 46, 28))
    cv.ellipse(x + 32, t0 + 6, 5, 4, (240, 242, 248))                # Teekanne blau-weiss
    cv.ellipse(x + 32, t0 + 6, 3, 2, (60, 90, 170))
    cv.rect(x + 37, t0 + 4, 3, 1, (240, 242, 248))
    cv.rect(x + 31, t0 + 1, 2, 2, (60, 90, 170))
    for dx in (44, 51):
        cv.ellipse(x + dx, t0 + 6, 2.5, 2, (240, 242, 248))
        cv.set(x + dx, t0 + 6, (140, 90, 50))
    # Stuehle links und rechts
    for sx in (x + 4, x + 5 * T - 16):
        cv.shade_rect(sx + 2, t0 + 14, 12, 3, 0.66)
        cv.rect(sx, t0 - 2, 12, 16, (150, 110, 40))
        cv.rect(sx + 1, t0, 10, 10, (160, 40, 52))

def harpsichord(tx, ty):
    """Cembalo von oben: Fluegelform, geoeffneter Deckel mit bemaltem Resonanzboden, Hocker davor."""
    x, y = tx * T + 2, ty * T
    w, h = 5 * T - 4, 2 * T + 2
    O.shadow_box(x, y, w, h)
    for py in range(y, y + h):
        # Fluegelform: rechts laenger, links verjuengt
        t = (py - y) / h
        left = x + int((1 - t) * 18)
        cv.rect(left, py, x + w - left, 1, (26, 56, 44))
        cv.set(left, py, (214, 170, 72))
    cv.rect(x, y + h - 1, w, 1, (214, 170, 72))
    cv.rect(x + w - 1, y, 1, h, (214, 170, 72))
    for py in range(y + 3, y + h - 8):
        t = (py - y) / h
        left = x + int((1 - t) * 18) + 4
        cv.rect(left, py, x + w - 4 - left, 1, (232, 208, 150))
    rng = random.Random(21)
    for _ in range(14):
        fx, fy = x + 24 + rng.randint(0, w - 32), y + 6 + rng.randint(0, h - 18)
        cv.set(fx, fy, (190, 60, 70)); cv.set(fx + 1, fy, (90, 140, 80))
    cv.ellipse(x + w - 22, y + 12, 5, 5, (120, 90, 50))               # Rosette
    cv.ellipse(x + w - 22, y + 12, 3, 3, (232, 208, 150))
    # Tastatur
    ky = y + h - 8
    cv.rect(x + 16, ky, w - 20, 6, (246, 240, 226))
    for k in range(x + 17, x + w - 5, 3):
        cv.rect(k, ky, 1, 6, (170, 160, 140))
        if (k // 3) % 7 not in (2, 6):
            cv.rect(k + 1, ky, 1, 3, (30, 26, 26))
    # Hocker
    cv.shade_rect(x + w // 2 - 4, y + h + 10, 16, 3, 0.66)
    cv.rect(x + w // 2 - 6, y + h + 2, 14, 10, (150, 110, 40))
    cv.rect(x + w // 2 - 5, y + h + 3, 12, 7, (160, 40, 52))

def chess_table(tx, ty):
    """Spieltisch mit Schachbrett und zwei Stuehlen: das Spiel der Vernunft."""
    x, y = tx * T, ty * T
    for sx in (x + 2, x + 5 * T - 14):
        cv.shade_rect(sx + 2, y + 24, 12, 3, 0.66)
        cv.rect(sx, y + 6, 12, 18, (70, 44, 28))
        cv.rect(sx + 1, y + 8, 10, 10, (40, 84, 70))
    bx, by, bw = x + 18, y + 2, 2 * T + 12   # Platte zwischen den Stuehlen
    O.shadow_box(bx, by, bw, 26)
    cv.rect(bx, by, bw, 26, (96, 60, 36))
    cv.rect(bx, by + 22, bw, 4, (74, 46, 28))
    cv.rect(bx + 5, by + 3, 32, 16, (60, 40, 26))
    for r in range(4):
        for c in range(8):
            cv.rect(bx + 6 + c * 4, by + 4 + r * 4 - (1 if r == 3 else 0), 4, 4 if r < 3 else 3,
                    (236, 222, 190) if (r + c) % 2 == 0 else (110, 70, 40))
    for fx, fy, col in ((bx + 8, by + 5, (246, 244, 236)), (bx + 16, by + 9, (246, 244, 236)),
                        (bx + 26, by + 6, (30, 26, 26)), (bx + 30, by + 13, (30, 26, 26)), (bx + 20, by + 14, (246, 244, 236))):
        cv.rect(fx, fy, 2, 3, col)
        cv.set(fx, fy - 1, col)

def curiosity_cabinet(tx, ty):
    """Vitrine mit Kuriositaeten: Nautilus, Koralle, Muscheln, Kompass, Schaedel."""
    x, y, w, h = tx * T + 2, ty * T - 6, 4 * T - 4, 2 * T + 4
    O.shadow_box(x, y, w, h)
    cv.rect(x, y, w, h, (70, 44, 28))
    cv.rect(x + 2, y + 2, w - 4, h - 10, (150, 190, 200))
    for py in range(y + 2, y + h - 8):
        cv.rect(x + 2, py, w - 4, 1, lerp((190, 222, 230), (120, 160, 176), (py - y) / h))
    cv.rect(x + 2, y + 15, w - 4, 1, (110, 72, 44))
    cv.ellipse(x + 10, y + 9, 5, 4, (236, 200, 170))                  # Nautilus
    cv.ellipse(x + 11, y + 9, 3, 2.5, (210, 150, 110))
    cv.ellipse(x + 12, y + 9, 1.3, 1.2, (236, 200, 170))
    for k in range(5):                                                # Koralle
        cv.line(x + 24, y + 14, x + 20 + k * 2, y + 5 + (k % 2) * 2, (220, 70, 60))
    cv.ellipse(x + 38, y + 10, 4, 3.5, (236, 230, 214))                # Schaedel
    cv.set(x + 37, y + 10, (60, 50, 50)); cv.set(x + 39, y + 10, (60, 50, 50))
    cv.rect(x + 37, y + 12, 3, 1, (170, 160, 146))
    cv.ellipse(x + 50, y + 10, 4, 4, (200, 160, 60))                  # Kompass
    cv.ellipse(x + 50, y + 10, 2.5, 2.5, (240, 236, 220))
    cv.set(x + 50, y + 9, (180, 40, 40))
    for k, col in enumerate(((236, 210, 180), (250, 236, 220), (220, 180, 150))):
        cv.ellipse(x + 10 + k * 8, y + 21, 3, 2, col)                 # Muscheln
    cv.ellipse(x + 40, y + 21, 5, 2, (120, 110, 100))                  # Fossil
    cv.ellipse(x + 40, y + 21, 3, 1.2, (170, 160, 146))
    cv.rect(x, y + h - 8, w, 8, (110, 70, 42))
    cv.rect(x + 2, y + h - 6, w - 4, 1, (150, 100, 60))
    cv.rect(x + w // 2 - 2, y + h - 4, 4, 1, (214, 170, 72))

def longcase_clock(tx, ty):
    """Standuhr mit Pendel: Huygens' Pendeluhr, die Zeit der neuen Wissenschaft."""
    x, y, w = tx * T + 1, ty * T - 20, T - 2
    h = 3 * T + 18
    O.shadow_box(x, y, w, h)
    cv.rect(x, y, w, h, (70, 40, 26))
    cv.rect(x + 1, y + 1, w - 2, h - 2, (108, 64, 38))
    cv.rect(x - 1, y, w + 2, 3, (214, 170, 72))
    cv.ellipse(x + w / 2 - 0.5, y + 11, 5, 5, (214, 170, 72))
    cv.ellipse(x + w / 2 - 0.5, y + 11, 4, 4, (244, 238, 220))
    cv.line(x + w / 2 - 0.5, y + 11, x + w / 2 - 0.5, y + 8, (30, 26, 26))
    cv.line(x + w / 2 - 0.5, y + 11, x + w / 2 + 2, y + 12, (30, 26, 26))
    cv.rect(x + 3, y + 20, w - 6, 26, (40, 24, 18))
    cv.rect(x + w // 2 - 1, y + 20, 1, 18, (214, 170, 72))
    cv.ellipse(x + w / 2 - 1, y + 39, 3, 3, (230, 190, 80))
    cv.rect(x + 2, y + h - 12, w - 4, 10, (90, 54, 32))

def secretary(tx, ty):
    """Sekretaer mit Aufsatzschrank und aufgeklappter Schreibplatte. Darauf der gesiegelte Brief der Akademie."""
    x, y, w = tx * T + 2, ty * T, 4 * T - 4
    # Aufsatz mit Buechern ragt vor die Wand
    top = y - 30
    cv.rect(x + 4, top, w - 8, 32, (74, 44, 26))
    cv.rect(x + 3, top - 3, w - 6, 4, (110, 66, 38))
    cv.rect(x + 3, top - 4, w - 6, 1, (214, 170, 72))
    for side in (x + 6, x + w // 2 + 1):
        cv.rect(side, top + 3, w // 2 - 7, 24, (40, 26, 18))
        for bx in range(side + 1, side + w // 2 - 8, 2):
            col = G.BOOKS[int(h2(bx, top, 71) * len(G.BOOKS))]
            hh = 9 + int(h2(bx, 2, 71) * 2)
            cv.rect(bx, top + 13 - hh, 2, hh, col)
            cv.rect(bx, top + 24 - hh, 2, hh, mul(col, 0.9))
        cv.rect(side, top + 13, w // 2 - 7, 1, (110, 66, 38))
        for k in range(0, 24, 3):
            cv.set(side + (k % 5), top + 3 + k, (200, 230, 240))     # Glanz auf den Glastueren
    # Unterbau mit Schubladen
    O.shadow_box(x, y + 2, w, 2 * T - 2)
    cv.rect(x, y + 2, w, 2 * T - 2, (96, 58, 34))
    for k in range(3):
        dy = y + 12 + k * 6
        cv.rect(x + 3, dy, w - 6, 5, (124, 76, 44))
        cv.rect(x + 3, dy + 4, w - 6, 1, (80, 48, 28))
        cv.rect(x + w // 2 - 2, dy + 2, 4, 1, (214, 170, 72))
    # aufgeklappte Schreibplatte mit gruenem Leder
    cv.rect(x - 2, y + 2, w + 4, 9, (86, 52, 30))
    cv.rect(x, y + 3, w, 7, (48, 98, 72))
    cv.rect(x + 6, y + 3, 14, 7, (246, 238, 214))                    # Papier
    for ly in range(y + 5, y + 9, 2):
        cv.rect(x + 8, ly, 9, 1, (170, 156, 130))
    cv.rect(x + 26, y + 3, 12, 6, (238, 226, 196))                    # Brief der Akademie
    cv.line(x + 26, y + 3, x + 32, y + 6, (200, 186, 156))
    cv.line(x + 37, y + 3, x + 32, y + 6, (200, 186, 156))
    cv.ellipse(x + 32, y + 6, 2, 2, (170, 30, 36))                    # rotes Wachssiegel
    cv.ellipse(x + 44, y + 6, 2.5, 2.5, (30, 30, 40))                 # Tintenfass
    cv.line(x + 44, y + 5, x + 49, y - 3, (246, 246, 240), 2)         # Feder

def pedestal_bust(tx, ty, bart):
    """Buste auf Saeulenstumpf. bart=True: antiker Philosoph."""
    O.bust(tx, ty)
    if bart:
        cx, b = tx * T + 8, ty * T + 14
        cv.ellipse(cx, b - 24, 3.5, 3, (226, 224, 220))
        cv.set(cx + 1, b - 23, (190, 188, 184))

def chandelier_light():
    """Kronleuchter in der Mitte: nur sein Lichtschein auf dem Teppich."""
    pool(20 * T, 13 * T, 110, 60, 1.18)

# ---------------------------------------------------------------- Einrichtung
# Links oben: Sekretaer mit dem Auftrag (Interaktion), links die Kuriositaeten
block(3, 3, 4, 2, mk(secretary, 3, 3))
block(1, 3, 1, 1, mk(O.plant, 1, 3))
block(8, 3, 1, 1, mk(O.candelabra, 8, 3))
block(2, 9, 4, 2, mk(curiosity_cabinet, 2, 9))
# Mitte oben: Kamin (Interaktion) mit zwei Ohrensesseln
block(17, 3, 6, 3, lambda: None)
block(14, 5, 2, 2, mk(wing_chair, 14, 5, 1))
block(24, 5, 2, 2, mk(wing_chair, 24, 5, -1))
block(15, 3, 1, 1, mk(O.candelabra, 15, 3))
block(24, 3, 1, 1, mk(O.candelabra, 24, 3))
# Rechts oben: Cembalo, Standuhr
block(29, 3, 5, 3, mk(harpsichord, 29, 3))
block(38, 4, 1, 2, mk(longcase_clock, 38, 4))
block(36, 3, 1, 1, mk(O.plant, 36, 3))
# Unten links: Kanapee mit Teetisch
block(3, 15, 5, 3, mk(settee_group, 3, 15))
block(1, 20, 1, 1, mk(O.plant, 1, 20))
# Unten rechts: Schachtisch, Vitrine mit Globus
block(30, 10, 5, 2, mk(chess_table, 30, 10))
block(32, 16, 2, 2, mk(O.globe, 32, 16))
block(37, 15, 1, 1, mk(O.plant, 37, 15))
# Eingang: Bueste eines antiken Philosophen und eines Neuzeitlichen, Pflanzen
block(14, 20, 1, 1, mk(pedestal_bust, 14, 20, True))
block(25, 20, 1, 1, mk(pedestal_bust, 25, 20, False))
block(12, 20, 1, 1, mk(O.plant, 12, 20))
block(27, 20, 1, 1, mk(O.plant, 27, 20))

for ia in INTERAKTIONEN:
    x0, y0, x1, y1 = ia["flaeche"]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            assert grid[y][x] == "#", ("Interaktionsflaeche belegt", ia["id"], x, y)
    fill(x0, y0, x1, y1, "I")


def render():
    floor_pass()
    persian(12 * T, 8 * T, 16 * T, 11 * T)
    persian(2 * T - 4, 14 * T + 4, 7 * T + 8, 5 * T, feld=(40, 60, 110), rand=(130, 36, 44))
    persian(28 * T + 4, 9 * T, 8 * T, 4 * T, feld=(60, 90, 70), rand=(130, 36, 44))
    O.runner(18 * T, 19 * T, 4 * T, 3 * T, (150, 40, 50))
    chandelier_light()
    back_wall()
    O.side_walls()
    O.front_wall()
    fireplace()
    for ia in INTERAKTIONEN:
        if ia["markiert"]:
            O.floor_glow(ia["flaeche"])
    for _, f in sorted(objs, key=lambda o: o[0]):
        f()
    for ia in INTERAKTIONEN:
        if ia["markiert"]:
            x0, y0, x1, y1 = ia["objekt"]
            O.marker_candle((x1 + 1) * T - 6, y0 * T - 2)


COLL = {"#": (40, 200, 80), "X": (220, 40, 40), "A": (230, 40, 220), "S": (40, 210, 230), "I": (250, 150, 30)}

def export():
    cv.save(os.path.join(HERE, "salon.png"))
    cv.save(os.path.join(HERE, "salon_2x.png"), 2)
    ov = G.Canvas(PW, PH)
    ov.b[:] = cv.b
    for ty in range(H):
        for tx in range(W):
            c = COLL[grid[ty][tx]]
            for py in range(ty * T, ty * T + T):
                for px in range(tx * T, tx * T + T):
                    edge = px % T == 0 or py % T == 0
                    ov.set(px, py, lerp(ov.get(px, py), c, 0.8 if edge else 0.5))
    ov.save(os.path.join(HERE, "salon_kollision.png"), 2)
    data = {
        "name": "salon",
        "kachelgroesse": T, "breite": W, "hoehe": H,
        "legende": {"#": "Boden, begehbar", "X": "Wand oder Moebel", "A": "Ausgang (Tuer nach draussen)",
                    "S": "Eintrittsstelle, begehbar", "I": "Interaktionsflaeche vor einem Objekt, begehbar"},
        "eintritt": {"x": 19, "y": 20, "blick": "up"},
        "ausgang": [{"x": x, "y": 22} for x in range(18, 22)],
        "interaktionen": [{"id": ia["id"], "markiert": ia["markiert"],
                           "flaeche": dict(zip(("x0", "y0", "x1", "y1"), ia["flaeche"])),
                           "objekt": dict(zip(("x0", "y0", "x1", "y1"), ia["objekt"]))}
                          for ia in INTERAKTIONEN],
        "geist": GEIST,
        "portraet": {"x": PORTRAET[0] + 3, "y": PORTRAET[1] + 3, "w": PORTRAET[2] - 6, "h": PORTRAET[3] - 6},
        "raster": ["".join(r) for r in grid],
    }
    with open(os.path.join(HERE, "salon.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "salon_daten.js"), "w", encoding="utf-8") as f:
        f.write("window.INNEN = window.INNEN || {};\nwindow.INNEN.salon = " + json.dumps(data, ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    render()
    export()
    print("Fertig:", PW, "x", PH)
