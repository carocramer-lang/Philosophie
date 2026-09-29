#!/usr/bin/env python3
# Innenraum Observatorium: 40 x 24 Kacheln a 16 px, Topdown, gleiche Bausteine wie die Oberwelt.
# Aufruf: python3 innen/observatorium.py
# Ausgabe: observatorium.png, observatorium_2x.png, observatorium_kollision.png,
#          observatorium.json und observatorium_daten.js

import json, math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "welt"))
import generator as G  # noqa: E402  (Zeichenfunktionen der Oberwelt)

T = 16
W, H = 40, 24
PW, PH = W * T, H * T
cv = G.cv = G.Canvas(PW, PH)
h2, mul, jit, lerp = G.h2, G.mul, G.jit, G.lerp
BOOKS = G.BOOKS
DARK = G.DARK

# ---------------------------------------------------------------- Raster
# '#' Boden, 'X' Wand/Moebel, 'A' Ausgang, 'S' Eintrittsstelle, 'I' Interaktionsflaeche
grid = [["#"] * W for _ in range(H)]

def fill(x0, y0, x1, y1, t):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            grid[y][x] = t

fill(0, 0, W - 1, 2, "X")           # Rueckwand
fill(0, 0, 0, H - 1, "X")           # Seitenwaende
fill(W - 1, 0, W - 1, H - 1, "X")
fill(0, 22, W - 1, H - 1, "X")      # Frontwand
fill(18, 22, 21, 22, "A")           # Tuer, Rueckweg nach draussen
for wx in (13, 26):                 # Trennwaende mit breitem Durchgang (Zeilen 10 bis 15)
    fill(wx, 3, wx, 9, "X")
    fill(wx, 16, wx, 21, "X")
fill(16, 3, 23, 7, "X")             # Podest mit Teleskop
# Interaktionspunkte: Objekt (blockiert) und freie Flaeche davor (begehbar, 'I').
# "markiert": Kerze und Lichtschein zeigen, dass hier Material liegt.
INTERAKTIONEN = [
    {"id": "teleskop", "objekt": (16, 3, 23, 7), "flaeche": (17, 8, 22, 9), "markiert": False},
    {"id": "regal_links", "objekt": (2, 17, 5, 18), "flaeche": (2, 19, 5, 19), "markiert": True},
    {"id": "regal_rechts", "objekt": (8, 17, 11, 18), "flaeche": (8, 19, 11, 19), "markiert": True},
    {"id": "kartentisch", "objekt": (35, 5, 37, 7), "flaeche": (35, 8, 37, 9), "markiert": True},
]
fill(18, 20, 21, 20, "S")           # Eintrittsstelle hinter der Tuer

objs = []

def block(x0, y0, w, h, fn):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            assert grid[y][x] == "#", ("belegt", x, y)
            grid[y][x] = "X"
    objs.append(((y0 + h) * T, fn))

def mk(f, *a):
    return lambda: f(*a)

# ---------------------------------------------------------------- Boeden
def parquet(x, y):
    r = y // 5
    off = int(h2(r, 0, 5) * 40)
    seg = (x + off) // 38
    base = [(150, 96, 58), (164, 108, 66), (140, 88, 54)][int(h2(seg, r, 6) * 3)]
    c = jit(base, (h2(x // 3, y, 7) - 0.5) * 8)
    if y % 5 == 4:
        return mul(base, 0.72)
    if (x + off) % 38 == 0:
        return mul(base, 0.78)
    if y % 5 == 0:
        return mul(c, 1.07)
    return c

RCX, RCY = 20 * T, 13 * T + 8   # Mitte der Rotunde, Kompassrose

def marble(x, y):
    dx, dy = x - RCX, (y - RCY) * 1.25
    d = math.hypot(dx, dy)
    if d < 76:
        a = math.atan2(dy, dx)
        star = 0.5 + 0.5 * abs(math.cos(4 * a))
        if d < 6:
            return (232, 190, 80)
        if d < 64 * (0.35 + 0.65 * star ** 6) and d > 4:
            half = math.sin(8 * a) > 0
            return (236, 206, 120) if half else (196, 150, 64)
        if 64 <= d < 68 or 72 <= d < 76:
            return (150, 60, 50)
        if 68 <= d < 72:
            return (230, 214, 180)
        return (42, 58, 104) if int((a + math.pi) / (math.pi / 16)) % 2 else (54, 72, 126)
    sq = 16
    cx, cy = (x + 8) // sq, (y + 8) // sq
    light = (cx + cy) % 2 == 0
    base = (230, 222, 204) if light else (186, 172, 150)
    v = G.vnoise(x, y, 5, 11)
    if abs(v - 0.5) < 0.02:
        base = mul(base, 0.9)
    c = jit(base, (h2(cx, cy, 12) - 0.5) * 8)
    if (x + 8) % sq == 0 or (y + 8) % sq == 0:
        c = mul(c, 0.88)
    return c

def floor_pass():
    b = cv.b
    for y in range(PH):
        for x in range(PW):
            c = marble(x, y) if 14 * T <= x < 26 * T else parquet(x, y)
            i = (y * PW + x) * 3
            b[i] = c[0]; b[i + 1] = c[1]; b[i + 2] = c[2]

def runner(x, y, w, h, col, border=(214, 170, 70), vertical=True):
    cv.shade_rect(x + 2, y + 2, w, h, 0.75)
    cv.rect(x, y, w, h, mul(col, 0.6))
    cv.rect(x + 2, y + 2, w - 4, h - 4, border)
    cv.rect(x + 4, y + 4, w - 8, h - 8, col)
    for py in range(y + 6, y + h - 6):
        for px in range(x + 6, x + w - 6):
            u, v = (px - x) % 12, (py - y) % 12
            if (u in (5, 6) and v in (2, 3, 8, 9)) or (v in (5, 6) and u in (2, 3, 8, 9)):
                cv.set(px, py, mul(border, 0.9))
            elif (u, v) in ((5, 5), (6, 6), (5, 6), (6, 5)):
                cv.set(px, py, mul(col, 1.35))

def light_pool(x0, x1, y_bottom, hgt):
    for py in range(y_bottom - hgt, y_bottom):
        t = (py - (y_bottom - hgt)) / hgt
        grow = int((1 - t) * 10)
        for px in range(x0 - grow, x1 + grow):
            cv.shade(px, py, 1.0 + 0.22 * t)

def glow(cx, cy, r, f=1.25):
    for py in range(int(cy - r), int(cy + r) + 1):
        for px in range(int(cx - r), int(cx + r) + 1):
            d = math.hypot(px - cx, (py - cy) * 1.3) / r
            if d < 1:
                cv.shade(px, py, 1 + (f - 1) * (1 - d) ** 2)

# ---------------------------------------------------------------- Waende
CAP = (70, 58, 54)
CAP_L = (116, 100, 92)

def wall_top(x, y, w, h):
    cv.rect(x, y, w, h, CAP)
    cv.rect(x + 1, y + 1, w - 2, h - 2, (92, 78, 72))
    for py in range(y + 2, y + h - 2, 6):
        cv.rect(x + 2, py, w - 4, 1, (80, 68, 62))
    cv.rect(x + 1, y + 1, w - 2, 1, CAP_L)

def brick_face(x, y, w, h):
    G.wall(x, y, w, h, (156, 88, 64), "brick")

def shelf_wall(x, y, w, h, seed):
    cv.rect(x, y, w, h, (86, 54, 34))
    rows = (h - 4) // 10
    for r in range(rows):
        sy = y + 3 + r * 10
        cv.rect(x + 2, sy, w - 4, 8, (60, 38, 26))
        px = x + 3
        while px < x + w - 4:
            bw = 2 + int(h2(px, sy, seed) * 2)
            bh = 5 + int(h2(px, sy, seed + 1) * 3)
            col = BOOKS[int(h2(px, sy, seed + 2) * len(BOOKS))]
            if h2(px, sy, seed + 3) < 0.08:
                px += 3
                continue
            cv.rect(px, sy + 8 - bh, bw, bh, col)
            cv.rect(px, sy + 8 - bh, 1, bh, mul(col, 1.25))
            cv.rect(px, sy + 8 - bh + 1, bw, 1, mul(col, 0.7))
            px += bw
        cv.rect(x + 2, sy + 8, w - 4, 2, (130, 86, 52))
        cv.rect(x + 2, sy + 9, w - 4, 1, (70, 44, 28))
    cv.rect(x, y, w, 2, (120, 80, 50))
    cv.rect(x, y, 1, h, (50, 32, 22))
    cv.rect(x + w - 1, y, 1, h, (50, 32, 22))

def star_chart(x, y, w, h, seed):
    cv.rect(x - 2, y - 2, w + 4, h + 4, (170, 130, 60))
    cv.rect(x - 1, y - 1, w + 2, h + 2, (110, 80, 40))
    cv.rect(x, y, w, h, (26, 36, 76))
    rng = random.Random(seed)
    pts = [(x + 3 + rng.randint(0, w - 6), y + 3 + rng.randint(0, h - 6)) for _ in range(7)]
    for a, b in zip(pts, pts[1:4]):
        cv.line(a[0], a[1], b[0], b[1], (90, 110, 170))
    for _ in range(18):
        cv.set(x + rng.randint(1, w - 2), y + rng.randint(1, h - 2), (200, 210, 240))
    for p in pts:
        cv.rect(p[0], p[1], 2, 2, (255, 240, 180))
    for k in range(60):
        a = k / 60 * 6.283
        cv.set(x + w / 2 + math.cos(a) * (w / 2 - 3), y + h / 2 + math.sin(a) * (h / 2 - 3), (150, 130, 80))

def back_wall():
    y0, hh = 0, 3 * T
    # Kappe oben (Mauerstaerke) und Wandflaeche
    for x0, x1 in ((0, 14 * T), (26 * T, PW)):
        cv.rect(x0, 0, x1 - x0, 6, CAP)
        cv.rect(x0, 5, x1 - x0, 1, CAP_L)
        brick_face(x0, 6, x1 - x0, hh - 6)
    # Bibliothek links: Wandregale mit Pilastern
    for sx in range(T, 13 * T, 64):
        shelf_wall(sx + 4, 10, 56, 36, sx)
    for px in range(T, 13 * T + 1, 64):
        cv.rect(px - 2, 8, 6, 40, (226, 218, 198))
        cv.rect(px + 3, 8, 1, 40, (160, 150, 130))
    # Werkstatt rechts: Sternkarten, Instrumentenschrank
    star_chart(27 * T + 10, 12, 40, 26, 3)
    star_chart(31 * T + 10, 10, 30, 30, 4)
    cab_x = 35 * T - 4
    cv.rect(cab_x, 8, 52, 40, (86, 54, 34))
    cv.rect(cab_x + 2, 10, 48, 34, (140, 190, 210))
    for gx in (cab_x + 18, cab_x + 34):
        cv.rect(gx, 10, 1, 34, (86, 54, 34))
    cv.rect(cab_x + 2, 26, 48, 1, (86, 54, 34))
    cv.line(cab_x + 5, 22, cab_x + 14, 14, (212, 170, 76), 2)      # Fernrohr im Schrank
    cv.ellipse(cab_x + 26, 18, 5, 5, (212, 170, 76))                 # Astrolabium
    cv.ellipse(cab_x + 26, 18, 3, 3, (140, 190, 210))
    cv.rect(cab_x + 38, 32, 8, 8, (200, 60, 50))                     # Buch
    cv.rect(cab_x + 22, 34, 10, 6, (230, 220, 190))
    # Rotunde: helle Steinwand mit Rippen, Kuppelspalt mit Nachthimmel
    for py in range(0, hh):
        for px in range(14 * T, 26 * T):
            dxn = (px - RCX) / (6 * T)
            c = mul((228, 220, 198), 0.78 + 0.22 * math.cos(dxn * 1.4))
            if py < 6:
                c = CAP if py < 5 else CAP_L
            elif (px - 14 * T) % 24 == 0:
                c = mul(c, 0.82)
            elif (py - 6) % 9 == 8:
                c = mul(c, 0.9)
            cv.set(px, py, c)
    sx0, sx1 = 18 * T + 6, 22 * T - 6
    for py in range(0, hh):
        for px in range(sx0, sx1):
            t = py / hh
            c = lerp((10, 14, 40), (30, 40, 92), t)
            cv.set(px, py, c)
    cv.rect(sx0 - 3, 0, 3, hh, (150, 150, 162))
    cv.rect(sx1, 0, 3, hh, (120, 120, 132))
    rng = random.Random(9)
    for _ in range(22):
        cv.set(rng.randint(sx0 + 1, sx1 - 2), rng.randint(1, hh - 4), (255, 250, 210) if rng.random() < 0.3 else (190, 200, 240))
    cv.rect(sx0 + 10, 8, 2, 2, (255, 246, 200))
    cv.rect(sx1 - 14, 30, 2, 2, (255, 246, 200))
    # Sockelleiste
    cv.rect(0, hh - 3, PW, 3, (74, 46, 30))
    cv.rect(0, hh - 3, PW, 1, (110, 72, 44))
    cv.shade_rect(0, hh, PW, 4, 0.78)

def side_walls():
    for x in (0, PW - T):
        cv.rect(x, 0, T, PH, CAP)
        cv.rect(x + 2, 0, T - 4, PH, (92, 78, 72))
        for py in range(4, PH, 8):
            cv.rect(x + 3, py, T - 6, 1, (80, 68, 62))
        edge = x + T - 1 if x == 0 else x
        cv.rect(edge, 0, 1, PH, CAP_L)
    cv.shade_rect(T, 3 * T, 4, 19 * T, 0.8)

def dividers():
    for wx in (13 * T, 26 * T):
        for y0, y1 in ((3 * T, 10 * T), (16 * T, 22 * T)):
            wall_top(wx, y0, T, y1 - y0 - (12 if y1 == 10 * T else 0))
            cv.shade_rect(wx + T, y0, 4, y1 - y0, 0.78)
        # Stirnseite zum Durchgang und Saeulen am Durchgang
        brick_face(wx, 10 * T - 12, T, 12)
        for cy in (10 * T - 26, 16 * T - 2):
            cv.ellipse(wx + 8, cy + 6, 9, 5, (120, 110, 100))
            cv.ellipse(wx + 8, cy + 5, 8, 4, (236, 230, 214))
        cv.shade_rect(wx - 2, 10 * T, T + 6, 4, 0.8)

def front_wall():
    y0 = 22 * T
    cv.rect(0, y0, PW, 2 * T, CAP)
    cv.rect(0, y0 + 1, PW, 2 * T - 2, (96, 82, 76))
    for py in range(y0 + 5, PH, 6):
        cv.rect(0, py, PW, 1, (84, 72, 66))
    cv.rect(0, y0, PW, 1, CAP_L)
    cv.shade_rect(0, y0 - 3, PW, 3, 0.82)
    # Fenster wie an der Fassade: drei je Fluegel, Licht faellt auf den Boden
    for wx in (40, 96, 152, 456, 512, 568):
        cv.rect(wx - 2, y0 + 6, 28, 12, (226, 218, 198))
        cv.rect(wx, y0 + 8, 24, 8, (150, 200, 232))
        cv.rect(wx, y0 + 8, 24, 2, (206, 232, 248))
        cv.rect(wx + 11, y0 + 8, 2, 8, (226, 218, 198))
        light_pool(wx, wx + 24, y0, 40)
    # Tuer: Schwelle, geoeffnete Fluegel, Blick nach draussen
    dx0, dx1 = 18 * T, 22 * T
    cv.rect(dx0 - 8, y0, 8, 2 * T, (226, 218, 198))
    cv.rect(dx1, y0, 8, 2 * T, (226, 218, 198))
    cv.rect(dx0 - 8, y0, 1, 2 * T, (140, 130, 116))
    cv.rect(dx1 + 7, y0, 1, 2 * T, (140, 130, 116))
    for py in range(y0, PH):
        for px in range(dx0, dx1):
            c = G.flag_px(px + 700, py)
            if py < y0 + 6:
                c = (214, 206, 190) if py > y0 + 1 else (160, 150, 136)
            cv.set(px, py, c)
    cv.rect(dx0, y0 + 6, 6, 2 * T - 6, (110, 62, 40))
    cv.rect(dx1 - 6, y0 + 6, 6, 2 * T - 6, (110, 62, 40))
    cv.rect(dx0 + 5, y0 + 6, 1, 2 * T - 6, (70, 40, 26))
    cv.rect(dx1 - 6, y0 + 6, 1, 2 * T - 6, (70, 40, 26))
    light_pool(dx0 + 6, dx1 - 6, y0, 56)
    # Fussmatte an der Eintrittsstelle
    cv.rect(dx0 + 6, 20 * T + 2, 4 * T - 12, 12, (90, 70, 40))
    cv.rect(dx0 + 8, 20 * T + 4, 4 * T - 16, 8, (150, 120, 70))
    for px in range(dx0 + 9, dx1 - 9, 3):
        cv.rect(px, 20 * T + 5, 1, 6, (120, 94, 56))

# ---------------------------------------------------------------- Teleskop-Podest
def dais():
    cx, top = 20 * T, 3 * T
    rx, ry = 66, 78
    for yy, a, b in cv.spans(cx + 6, top + 4, rx + 2, ry + 2):
        if yy >= top:
            for xx in range(a, b):
                cv.shade(xx, yy, 0.7)
    for py in range(top, 8 * T):
        for px in range(cx - rx, cx + rx):
            nx, ny = (px - cx) / rx, (py - top) / ry
            d = nx * nx + ny * ny
            if d > 1:
                continue
            if d > 0.86:
                c = (86, 52, 32) if d > 0.95 else (112, 70, 42)
            else:
                c = (150, 96, 58) if (py - top) % 6 else (118, 74, 44)
                c = jit(c, (h2(px // 20, (py - top) // 6, 13) - 0.5) * 16)
            cv.set(px, py, c)
    for k in range(120):
        a = k / 120 * math.pi
        x = cx + math.cos(a) * (rx - 5)
        y = top + math.sin(a) * (ry - 5)
        if abs(x - cx) < 22 and y > top + 50:
            continue
        cv.rect(x, y - 8, 2, 2, (230, 190, 90))
        if k % 8 == 0:
            cv.rect(x, y - 7, 2, 8, (170, 130, 56))
    for i in range(3):
        cv.rect(cx - 22 - i * 2, 8 * T - 14 + i * 5, 44 + i * 4, 5, (176, 118, 72))
        cv.rect(cx - 22 - i * 2, 8 * T - 10 + i * 5, 44 + i * 4, 1, (96, 60, 36))
    # Montierung und Rohr, das durch den Kuppelspalt ragt
    cv.shade_ellipse(cx + 8, 6 * T - 4, 20, 7, 0.6)
    for ang in (-2.4, -0.7, 1.57):
        cv.line(cx, 5 * T - 6, cx + math.cos(ang) * 18, 6 * T - 6 + math.sin(ang) * 4, (60, 44, 34), 3)
    cv.ellipse(cx, 5 * T - 4, 9, 6, (56, 50, 50))
    cv.ellipse(cx, 5 * T - 5, 7, 4, (96, 90, 90))
    x0, y0, x1, y1 = cx - 6, 5 * T + 4, cx + 8, -2
    for i in range(0, 101):
        t = i / 100
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        r = 7 - 2 * t
        for k in range(-int(r), int(r) + 1):
            f = k / r
            c = (214, 170, 76) if f < 0.3 else (170, 128, 50)
            if f < -0.5:
                c = (250, 220, 130)
            cv.set(x + k, y, c)
        cv.set(x - r - 1, y, (70, 50, 26))
        cv.set(x + r + 1, y, (70, 50, 26))
    for t in (0.25, 0.55, 0.8):
        y = y0 + (y1 - y0) * t
        x = x0 + (x1 - x0) * t
        cv.rect(x - 7, y, 15, 2, (120, 90, 40))
    cv.line(cx + 8, 5 * T, cx + 16, 2 * T, (150, 150, 160), 2)          # Sucherfernrohr
    cv.rect(x0 - 3, y0, 6, 5, (40, 36, 36))                                # Okular
    cv.rect(x0 - 2, y0 + 1, 4, 2, (150, 200, 236))
    # Beobachterstuhl und Atlaspult auf dem Podest
    cv.rect(cx - 40, 5 * T + 2, 12, 10, (60, 40, 30))
    cv.rect(cx - 39, 5 * T + 3, 10, 7, (150, 40, 50))
    cv.rect(cx + 28, 5 * T, 16, 12, (90, 56, 34))
    cv.rect(cx + 30, 5 * T + 1, 12, 8, (240, 230, 200))
    cv.rect(cx + 35, 5 * T + 1, 1, 8, (150, 120, 90))
    cv.rect(cx + 31, 5 * T + 3, 3, 1, (60, 80, 150))
    # Messingstern vor dem Podest: Platz fuer die Interaktion
    cv.shade_ellipse(cx, 9 * T, 22, 9, 1.18)
    for k in range(8):
        a = k * math.pi / 4
        r = 14 if k % 2 == 0 else 8
        cv.line(cx, 9 * T, cx + math.cos(a) * r, 9 * T + math.sin(a) * r * 0.55, (230, 190, 80), 2)
    cv.ellipse(cx, 9 * T, 3, 2, (250, 220, 120))

# ---------------------------------------------------------------- Moebel
def shadow_box(x, y, w, h):
    cv.shade_rect(x + 3, y + h, w, 4, 0.66)
    cv.shade_rect(x + w, y + 6, 4, h - 2, 0.72)

def shelf_island(tx, ty, tw, seed):
    x, y, w = tx * T, ty * T - 10, tw * T
    h = 2 * T + 10
    shadow_box(x, y, w, h)
    cv.rect(x, y, w, 8, (70, 44, 28))
    cv.rect(x + 1, y + 1, w - 2, 5, (120, 80, 50))
    cv.rect(x + 1, y + 1, w - 2, 1, (156, 110, 70))
    shelf_wall(x, y + 8, w, h - 8, seed)

def reading_table(tx, ty, tw):
    x, y, w, h = tx * T, ty * T, tw * T, 2 * T
    for cx in (x + 8, x + w - 8):                               # Stuehle an den Stirnseiten
        cv.shade_rect(cx - 5, y + 20, 12, 4, 0.66)
        cv.rect(cx - 6, y + 6, 12, 16, (70, 44, 30))
        cv.rect(cx - 5, y + 8, 10, 10, (150, 40, 50))
    tx0, tw0 = x + 16, w - 32
    shadow_box(tx0, y + 2, tw0, h - 4)
    cv.rect(tx0, y + 2, tw0, h - 6, (96, 60, 36))
    cv.rect(tx0 + 2, y + 4, tw0 - 4, h - 12, (58, 104, 70))
    cv.rect(tx0, y + h - 4, tw0, 3, (74, 46, 28))
    cv.rect(tx0 + 10, y + 8, 18, 12, (244, 236, 214))            # aufgeschlagenes Buch
    cv.rect(tx0 + 18, y + 8, 2, 12, (180, 160, 130))
    for ly in range(y + 10, y + 19, 2):
        cv.rect(tx0 + 12, ly, 5, 1, (150, 140, 120))
        cv.rect(tx0 + 21, ly, 5, 1, (150, 140, 120))
    cv.rect(tx0 + tw0 - 30, y + 7, 10, 14, (60, 90, 160))        # Buecherstapel
    cv.rect(tx0 + tw0 - 30, y + 11, 10, 4, (170, 50, 50))
    cv.ellipse(tx0 + tw0 // 2 + 6, y + 12, 3, 3, (30, 30, 40))   # Tintenfass statt Kerze

def candle(cx, cy):
    glow(cx, cy - 4, 26, 1.28)
    cv.rect(cx - 3, cy + 2, 7, 3, (200, 170, 70))
    cv.rect(cx - 1, cy - 4, 3, 7, (246, 240, 224))
    cv.rect(cx, cy - 7, 1, 3, (255, 214, 90))
    cv.set(cx, cy - 8, (255, 250, 200))

def marker_candle(cx, cy):
    """Brennende Kerze im Messinghalter mit weitem Lichtschein: hier liegt Material."""
    glow(cx, cy - 6, 44, 1.45)
    cv.ellipse(cx, cy + 3, 6, 2.5, (150, 110, 40))
    cv.ellipse(cx, cy + 2, 5, 2, (230, 190, 80))
    cv.rect(cx - 2, cy - 9, 5, 11, (248, 242, 226))
    cv.rect(cx + 2, cy - 9, 1, 11, (214, 204, 184))
    cv.rect(cx - 2, cy - 9, 5, 1, (255, 255, 250))
    cv.rect(cx, cy - 11, 1, 2, (60, 40, 30))
    cv.rect(cx - 1, cy - 16, 3, 5, (255, 186, 60))
    cv.rect(cx, cy - 18, 1, 3, (255, 236, 150))
    cv.set(cx, cy - 13, (255, 255, 230))

def floor_glow(fl):
    x0, y0, x1, y1 = fl
    cx = (x0 + x1 + 1) * T / 2
    cy = (y0 + y1 + 1) * T / 2
    rx = (x1 - x0 + 1) * T / 2 + 4
    ry = (y1 - y0 + 1) * T / 2 + 5
    for py in range(int(cy - ry), int(cy + ry) + 1):
        for px in range(int(cx - rx), int(cx + rx) + 1):
            d = ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2
            if d < 1:
                cv.shade(px, py, 1 + 0.28 * (1 - d))

def globe(tx, ty):
    cx, b = tx * T + 16, ty * T + 30
    cv.shade_ellipse(cx + 4, b, 14, 4, 0.62)
    for a in (-2.5, -0.64, 1.57):
        cv.line(cx, b - 10, cx + math.cos(a) * 11, b + math.sin(a) * 2, (96, 60, 36), 2)
    cv.ellipse(cx, b - 22, 13, 13, (90, 70, 40))
    cv.ellipse(cx, b - 22, 11.5, 11.5, (70, 120, 190))
    rng = random.Random(4)
    for _ in range(6):
        cv.ellipse(cx - 7 + rng.randint(0, 12), b - 30 + rng.randint(0, 14), 3 + rng.random() * 2, 2 + rng.random() * 2, (110, 160, 80))
    cv.ellipse(cx - 4, b - 27, 3, 2, (170, 206, 240))
    for k in range(80):
        a = k / 80 * 6.283
        cv.set(cx + math.cos(a) * 14, b - 22 + math.sin(a) * 14, (220, 180, 80))

def lectern(tx, ty):
    x, y = tx * T + 2, ty * T + 2
    cv.shade_rect(x + 3, y + 28, 12, 3, 0.64)
    cv.rect(x + 5, y + 12, 3, 18, (80, 50, 30))
    cv.rect(x, y + 26, 13, 3, (80, 50, 30))
    cv.rect(x - 2, y, 16, 13, (104, 66, 40))
    cv.rect(x - 1, y + 1, 14, 9, (242, 234, 212))
    cv.rect(x + 6, y + 1, 1, 9, (170, 150, 120))
    cv.rect(x + 8, y + 3, 4, 1, (140, 130, 110))

def cabinet_v(tx, ty, th):
    x, y, w, h = tx * T + 1, ty * T - 8, T - 2, th * T + 6
    shadow_box(x, y, w, h)
    cv.rect(x, y, w, h, (70, 44, 28))
    cv.rect(x + 1, y + 1, w - 2, 5, (120, 80, 50))
    for py in range(y + 8, y + h - 2, 7):
        cv.rect(x + 2, py, w - 4, 6, (140, 92, 56))
        cv.rect(x + 2, py + 5, w - 4, 1, (90, 58, 36))
        cv.rect(x + w // 2 - 1, py + 2, 2, 2, (230, 190, 90))

def orrery(tx, ty):
    cx, cy = tx * T + 32, ty * T + 34
    cv.shade_ellipse(cx + 6, cy + 10, 30, 16, 0.62)
    cv.ellipse(cx, cy + 6, 30, 16, (58, 36, 24))
    cv.ellipse(cx, cy + 4, 30, 16, (110, 70, 42))
    cv.ellipse(cx, cy + 3, 27, 13, (134, 88, 52))
    glow(cx, cy - 6, 28, 1.25)
    for r, ry in ((24, 10), (17, 7), (10, 4)):
        for k in range(160):
            a = k / 160 * 6.283
            cv.set(cx + math.cos(a) * r, cy - 2 + math.sin(a) * ry, (220, 180, 80))
    cv.rect(cx - 1, cy - 8, 2, 8, (180, 140, 60))
    cv.ellipse(cx, cy - 10, 5, 5, (250, 200, 60))
    cv.ellipse(cx - 1, cy - 11, 2, 2, (255, 246, 190))
    for r, ry, a, col, s in ((10, 4, 0.6, (200, 110, 70), 2), (17, 7, 2.4, (90, 140, 220), 3),
                             (24, 10, 4.2, (220, 190, 140), 4), (24, 10, 5.5, (200, 90, 60), 2)):
        px, py = cx + math.cos(a) * r, cy - 2 + math.sin(a) * ry
        cv.line(cx, cy - 4, px, py - 3, (170, 130, 60))
        cv.ellipse(px, py - 4, s, s, col)
        cv.set(px - 1, py - 5, mul(col, 1.4))

def chart_table(tx, ty):
    x, y, w, h = tx * T + 2, ty * T + 2, 3 * T - 4, 3 * T - 6
    shadow_box(x, y, w, h)
    cv.rect(x, y, w, h, (96, 60, 36))
    cv.rect(x, y + h - 4, w, 4, (70, 44, 28))
    cv.rect(x + 3, y + 3, w - 6, h - 10, (30, 42, 86))
    rng = random.Random(8)
    for _ in range(20):
        cv.set(x + 4 + rng.randint(0, w - 9), y + 4 + rng.randint(0, h - 13), (220, 226, 250))
    for k in range(50):
        a = k / 50 * 6.283
        cv.set(x + w / 2 + math.cos(a) * 12, y + (h - 6) / 2 + math.sin(a) * 9, (180, 160, 100))
    for i, col in enumerate(((236, 226, 196), (220, 206, 170))):
        cv.rect(x + 2 + i * 14, y + h - 12, 12, 5, col)
        cv.ellipse(x + 2 + i * 14, y + h - 10, 1.5, 2.5, mul(col, 0.7))

def writing_desk(tx, ty, tw):
    x, y, w = tx * T, ty * T, tw * T
    cv.shade_rect(x + w // 2 - 4, y + 26, 12, 4, 0.66)
    cv.rect(x + w // 2 - 6, y + 20, 12, 10, (70, 44, 30))
    cv.rect(x + w // 2 - 5, y + 21, 10, 7, (60, 90, 70))
    shadow_box(x + 2, y + 2, w - 4, 20)
    cv.rect(x + 2, y + 2, w - 4, 18, (110, 70, 42))
    cv.rect(x + 2, y + 17, w - 4, 3, (74, 46, 28))
    cv.rect(x + 8, y + 5, 16, 11, (244, 236, 214))
    for ly in range(y + 7, y + 15, 2):
        cv.rect(x + 10, ly, 11, 1, (120, 110, 100))
    cv.ellipse(x + 32, y + 10, 3, 3, (30, 30, 40))
    cv.line(x + 32, y + 9, x + 40, y + 2, (246, 246, 240), 2)
    cv.rect(x + w - 16, y + 6, 8, 10, (60, 90, 160))           # Buch statt Kerze
    cv.rect(x + w - 16, y + 6, 8, 2, (90, 120, 190))

def quadrant(tx, ty):
    cx, b = tx * T + 16, ty * T + 28
    cv.shade_ellipse(cx + 4, b, 10, 3, 0.64)
    cv.rect(cx - 1, b - 14, 3, 14, (70, 50, 36))
    cv.rect(cx - 6, b - 2, 13, 3, (70, 50, 36))
    for k in range(40):
        a = math.pi + k / 40 * (math.pi / 2)
        cv.set(cx + 10 + math.cos(a) * 18, b - 14 + math.sin(a) * 18, (230, 190, 80))
        cv.set(cx + 10 + math.cos(a) * 17, b - 14 + math.sin(a) * 17, (180, 140, 60))
    cv.line(cx + 10, b - 14, cx - 8, b - 14, (200, 160, 70), 2)
    cv.line(cx + 10, b - 14, cx + 10, b - 32, (200, 160, 70), 2)
    cv.line(cx + 10, b - 14, cx - 3, b - 27, (120, 90, 50))

def small_telescope(tx, ty):
    cx, cy = tx * T + 16, ty * T + 16
    cv.shade_ellipse(cx + 4, cy + 12, 12, 4, 0.62)
    for ex, ey in ((cx - 9, cy + 12), (cx + 9, cy + 12), (cx, cy + 14)):
        cv.line(cx, cy, ex, ey, (96, 64, 40), 2)
    cv.line(cx - 12, cy + 4, cx + 12, cy - 12, (70, 50, 26), 6)
    cv.line(cx - 12, cy + 4, cx + 12, cy - 12, (214, 170, 76), 4)
    cv.line(cx - 11, cy + 2, cx + 11, cy - 13, (250, 222, 130))

def map_chest(tx, ty, th):
    x, y, w, h = tx * T - 6, ty * T - 8, T + 5, th * T + 6
    shadow_box(x, y, w, h)
    cv.rect(x, y, w, h, (70, 44, 28))
    cv.rect(x + 1, y + 1, w - 2, 5, (120, 80, 50))
    for py in range(y + 8, y + h - 3, 5):
        cv.rect(x + 2, py, w - 4, 4, (130, 86, 52))
        cv.rect(x + w // 2 - 2, py + 1, 4, 1, (230, 190, 90))

def bust(tx, ty):
    cx, b = tx * T + 8, ty * T + 14
    cv.shade_ellipse(cx + 4, b, 8, 3, 0.62)
    cv.rect(cx - 6, b - 14, 12, 14, (200, 194, 182))
    cv.rect(cx - 7, b - 16, 14, 3, (226, 220, 210))
    cv.rect(cx + 4, b - 13, 2, 13, (160, 154, 144))
    cv.ellipse(cx, b - 21, 7, 4, (234, 232, 228))
    cv.ellipse(cx, b - 28, 4.5, 5, (238, 236, 232))
    cv.rect(cx - 5, b - 33, 10, 4, (226, 224, 220))
    cv.set(cx + 2, b - 28, (170, 168, 164))

def candelabra(tx, ty):
    cx, b = tx * T + 8, ty * T + 14
    glow(cx, b - 30, 30, 1.3)
    cv.shade_ellipse(cx + 3, b, 6, 2, 0.62)
    cv.rect(cx - 4, b - 3, 9, 3, (50, 44, 44))
    cv.rect(cx, b - 24, 2, 22, (60, 54, 54))
    cv.rect(cx - 7, b - 24, 16, 2, (60, 54, 54))
    for dx in (-7, 0, 7):
        cv.rect(cx + dx, b - 31, 2, 7, (246, 240, 224))
        cv.set(cx + dx, b - 33, (255, 214, 90))
        cv.set(cx + dx + 1, b - 32, (255, 240, 170))

def plant(tx, ty):
    cx, b = tx * T + 8, ty * T + 14
    cv.shade_ellipse(cx + 3, b, 7, 2, 0.62)
    cv.rect(cx - 5, b - 9, 11, 9, (170, 90, 60))
    cv.rect(cx - 6, b - 10, 13, 2, (196, 110, 76))
    G.canopy(cx, b - 17, 9, G.PAL_LIME, 21)

def rug(x, y, w, h, col):
    cv.rect(x, y, w, h, mul(col, 0.6))
    cv.rect(x + 2, y + 2, w - 4, h - 4, col)
    cv.rect(x + 5, y + 5, w - 10, h - 10, mul(col, 1.2))
    cv.rect(x + 8, y + 8, w - 16, h - 16, col)

# ---------------------------------------------------------------- Einrichtung
# Bibliothek links
block(2, 5, 4, 2, mk(shelf_island, 2, 5, 4, 101))
block(8, 5, 4, 2, mk(shelf_island, 8, 5, 4, 102))
block(3, 8, 8, 2, mk(reading_table, 3, 8, 8))
block(2, 17, 4, 2, mk(shelf_island, 2, 17, 4, 103))
block(8, 17, 4, 2, mk(shelf_island, 8, 17, 4, 104))
block(1, 20, 2, 2, mk(globe, 1, 20))
block(11, 20, 1, 2, mk(lectern, 11, 20))
block(12, 3, 1, 1, mk(plant, 12, 3))
# Rotunde
block(15, 3, 1, 1, mk(candelabra, 15, 3))
block(24, 3, 1, 1, mk(candelabra, 24, 3))
block(14, 20, 1, 1, mk(bust, 14, 20))
block(25, 20, 1, 1, mk(bust, 25, 20))
block(14, 3, 1, 1, mk(plant, 14, 3))
block(25, 3, 1, 1, mk(plant, 25, 3))
# Werkstatt rechts
block(29, 5, 4, 4, mk(orrery, 29, 5))
block(35, 5, 3, 3, mk(chart_table, 35, 5))
block(28, 17, 4, 2, mk(writing_desk, 28, 17, 4))
block(34, 17, 2, 2, mk(quadrant, 34, 17))
block(38, 16, 1, 4, mk(map_chest, 38, 16, 4))
block(35, 20, 2, 2, mk(small_telescope, 35, 20))
block(27, 20, 1, 1, mk(plant, 27, 20))

for ia in INTERAKTIONEN:
    x0, y0, x1, y1 = ia["flaeche"]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            assert grid[y][x] == "#", ("Interaktionsflaeche belegt", ia["id"], x, y)
    fill(x0, y0, x1, y1, "I")


def render():
    floor_pass()
    runner(3 * T, 12 * T, 10 * T, 3 * T, (44, 62, 120))
    runner(27 * T, 12 * T, 11 * T, 3 * T, (44, 62, 120))
    runner(18 * T, 17 * T + 4, 4 * T, 5 * T - 4, (150, 40, 50))
    runner(18 * T, 8 * T, 4 * T, 2 * T + 4, (150, 40, 50))
    rug(29 * T - 6, 5 * T - 4, 4 * T + 12, 4 * T + 6, (120, 50, 60))
    back_wall()
    side_walls()
    front_wall()
    dividers()
    dais()
    for ia in INTERAKTIONEN:
        if ia["markiert"]:
            floor_glow(ia["flaeche"])
    for _, f in sorted(objs, key=lambda o: o[0]):
        f()
    # Kerzen zuletzt, damit sie ueber Regalkante und Tisch stehen
    for ia in INTERAKTIONEN:
        if ia["markiert"]:
            x0, y0, x1, y1 = ia["objekt"]
            cx = (x0 + x1 + 1) * T // 2
            cy = y0 * T - 6 if ia["id"].startswith("regal") else y0 * T + 12
            if ia["id"] == "kartentisch":
                cx = (x1 + 1) * T - 8
            marker_candle(cx, cy)


COLL = {"#": (40, 200, 80), "X": (220, 40, 40), "A": (230, 40, 220), "S": (40, 210, 230), "I": (250, 150, 30)}

def export():
    cv.save(os.path.join(HERE, "observatorium.png"))
    cv.save(os.path.join(HERE, "observatorium_2x.png"), 2)
    ov = G.Canvas(PW, PH)
    ov.b[:] = cv.b
    for ty in range(H):
        for tx in range(W):
            c = COLL[grid[ty][tx]]
            for py in range(ty * T, ty * T + T):
                for px in range(tx * T, tx * T + T):
                    edge = px % T == 0 or py % T == 0
                    ov.set(px, py, lerp(ov.get(px, py), c, 0.8 if edge else 0.5))
    ov.save(os.path.join(HERE, "observatorium_kollision.png"), 2)
    data = {
        "name": "observatorium",
        "kachelgroesse": T, "breite": W, "hoehe": H,
        "legende": {"#": "Boden, begehbar", "X": "Wand oder Moebel", "A": "Ausgang (Tuer nach draussen)",
                    "S": "Eintrittsstelle, begehbar", "I": "Interaktionsflaeche vor einem Objekt, begehbar"},
        "eintritt": {"x": 19, "y": 20, "blick": "up"},
        "ausgang": [{"x": x, "y": 22} for x in range(18, 22)],
        "interaktionen": [{"id": ia["id"], "markiert": ia["markiert"],
                           "flaeche": dict(zip(("x0", "y0", "x1", "y1"), ia["flaeche"])),
                           "objekt": dict(zip(("x0", "y0", "x1", "y1"), ia["objekt"]))}
                          for ia in INTERAKTIONEN],
        "raster": ["".join(r) for r in grid],
    }
    with open(os.path.join(HERE, "observatorium.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "observatorium_daten.js"), "w", encoding="utf-8") as f:
        f.write("window.INNEN = window.INNEN || {};\nwindow.INNEN.observatorium = " + json.dumps(data, ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    render()
    export()
    print("Fertig:", PW, "x", PH)
