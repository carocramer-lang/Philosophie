#!/usr/bin/env python3
# Oberwelt fuer das Lernspiel "Lockes Neffe": Pixel-Art, Topdown, 96 x 54 Kacheln a 16 px.
# Reines Python ohne Zusatzpakete. Aufruf: python3 generator.py
# Ausgabe: welt.png (1x), welt_2x.png, welt_kollision.png (Vorschlag), welt.json (Kachelraster)

import json, math, os, random, struct, zlib

T = 16
W, H = 96, 54
PW, PH = W * T, H * T
OUT = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- Farbe und Rauschen
def cl(v):
    return 0 if v < 0 else 255 if v > 255 else int(v)

def mul(c, f):
    return (cl(c[0] * f), cl(c[1] * f), cl(c[2] * f))

def jit(c, d):
    return (cl(c[0] + d), cl(c[1] + d), cl(c[2] + d))

def lerp(a, b, t):
    return (cl(a[0] + (b[0] - a[0]) * t), cl(a[1] + (b[1] - a[1]) * t), cl(a[2] + (b[2] - a[2]) * t))

def h2(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2246822519) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0

def vnoise(x, y, sc, s=0):
    fx, fy = x / sc, y / sc
    ix, iy = math.floor(fx), math.floor(fy)
    tx, ty = fx - ix, fy - iy
    tx = tx * tx * (3 - 2 * tx)
    ty = ty * ty * (3 - 2 * ty)
    a, b = h2(ix, iy, s), h2(ix + 1, iy, s)
    c, d = h2(ix, iy + 1, s), h2(ix + 1, iy + 1, s)
    return a + (b - a) * tx + (c - a) * ty + (a - b - c + d) * tx * ty


# ---------------------------------------------------------------- Leinwand
class Canvas:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.b = bytearray(w * h * 3)

    def set(s, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < s.w and 0 <= y < s.h:
            i = (y * s.w + x) * 3
            s.b[i] = c[0]; s.b[i + 1] = c[1]; s.b[i + 2] = c[2]

    def get(s, x, y):
        i = (y * s.w + x) * 3
        return (s.b[i], s.b[i + 1], s.b[i + 2])

    def rect(s, x, y, w, h, c):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(s.w, int(x + w)), min(s.h, int(y + h))
        if x1 <= x0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * s.w + x0) * 3
            s.b[i:i + len(row)] = row

    def shade(s, x, y, f):
        x, y = int(x), int(y)
        if 0 <= x < s.w and 0 <= y < s.h:
            i = (y * s.w + x) * 3
            b = s.b
            b[i] = cl(b[i] * f); b[i + 1] = cl(b[i + 1] * f); b[i + 2] = cl(b[i + 2] * f)

    def shade_rect(s, x, y, w, h, f):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                s.shade(xx, yy, f)

    def spans(s, cx, cy, rx, ry):
        for yy in range(int(math.floor(cy - ry)), int(math.ceil(cy + ry)) + 1):
            dy = (yy + 0.5 - cy) / ry
            if abs(dy) >= 1:
                continue
            dx = rx * math.sqrt(1 - dy * dy)
            yield yy, int(round(cx - dx)), int(round(cx + dx))

    def ellipse(s, cx, cy, rx, ry, c):
        for yy, a, b in s.spans(cx, cy, rx, ry):
            s.rect(a, yy, b - a, 1, c)

    def shade_ellipse(s, cx, cy, rx, ry, f):
        for yy, a, b in s.spans(cx, cy, rx, ry):
            for xx in range(a, b):
                s.shade(xx, yy, f)

    def line(s, x0, y0, x1, y1, c, t=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            y = y0 + (y1 - y0) * i / n
            s.rect(round(x - (t - 1) / 2), round(y - (t - 1) / 2), t, t, c)

    def save(s, path, scale=1):
        raw = bytearray()
        for y in range(s.h):
            row = s.b[y * s.w * 3:(y + 1) * s.w * 3]
            if scale > 1:
                big = bytearray(len(row) * scale)
                for k in range(scale):
                    for ch in range(3):
                        big[k * 3 + ch::3 * scale] = row[ch::3]
                row = big
            line = b"\x00" + bytes(row)
            for _ in range(scale):
                raw += line

        def chunk(t, d):
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", s.w * scale, s.h * scale, 8, 2, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        png += chunk(b"IEND", b"")
        with open(path, "wb") as f:
            f.write(png)


cv = Canvas(PW, PH)

# ---------------------------------------------------------------- Kachelkarte
# G Wiese, F Wald (Rand), P Pflasterweg, Q Platz/Vorplatz, W Fluss, V Teich,
# R Brueckenweg, X Brueckengelaender, B Gebaeude, E Eingang (Tuer)
gd = [["G"] * W for _ in range(H)]
blocked = set()

def fill(x0, y0, x1, y1, t):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if 0 <= x < W and 0 <= y < H:
                gd[y][x] = t

def g(x, y):
    return gd[y][x] if 0 <= x < W and 0 <= y < H else "F"

for y in range(H):
    for x in range(W):
        if x < 3 or x > 92 or y < 3 or y > 50:
            gd[y][x] = "F"

# Strassennetz: drei Ost-West-Achsen, drei Nord-Sued-Achsen, Zentralplatz
fill(3, 19, 92, 21, "P")     # Nordstrasse
fill(3, 44, 92, 46, "P")     # Suedstrasse
fill(26, 31, 88, 33, "P")    # Mittelstrasse
fill(26, 19, 28, 46, "P")    # Weststrasse
fill(86, 19, 88, 46, "P")    # Oststrasse
fill(46, 22, 49, 24, "P")    # Platz -> Observatorium
fill(46, 40, 49, 43, "P")    # Platz -> Suedstrasse
fill(38, 25, 57, 39, "Q")    # Zentralplatz

# Fluss mit Muehlgraben und drei Bruecken
fill(60, 0, 63, H - 1, "W")
fill(64, 37, 66, 39, "W")
for yr in (19, 31, 44):
    fill(59, yr, 64, yr + 2, "R")
    fill(59, yr - 1, 64, yr - 1, "X")
    fill(59, yr + 3, 64, yr + 3, "X")

fill(9, 25, 14, 27, "V")     # Parkteich
fill(33, 48, 41, 50, "V")    # Dorfteich

BUILDINGS = {
    "observatorium": (38, 4, 20, 12),
    "lesesaal": (7, 5, 16, 11),
    "salon": (7, 34, 14, 8),
    "druckerei": (67, 35, 16, 7),
    "akademie": (66, 4, 18, 12),
}
DOORS = {
    "observatorium": [(47, 15), (48, 15)],
    "lesesaal": [(14, 15), (15, 15)],
    "salon": [(13, 41), (14, 41)],
    "druckerei": [(74, 41), (75, 41)],
    "akademie": [(74, 15), (75, 15)],
}
COURTS = {
    "observatorium": (44, 16, 51, 18),
    "lesesaal": (12, 16, 17, 18),
    "salon": (10, 42, 17, 43),
    "druckerei": (71, 42, 78, 43),
    "akademie": (71, 16, 78, 18),
}
HOUSES = [
    (30, 23, 6, 7, (184, 84, 58), (238, 226, 200), "timber", 1),
    (30, 35, 6, 8, (84, 100, 138), (230, 214, 184), "timber", 2),
    (66, 23, 6, 7, (196, 110, 60), (236, 222, 196), "timber", 3),
    (74, 23, 6, 7, (170, 70, 62), (214, 196, 170), "stone", 4),
]
for bx, by, bw, bh in BUILDINGS.values():
    fill(bx, by, bx + bw - 1, by + bh - 1, "B")
for hx, hy, hw, hh, *_ in HOUSES:
    fill(hx, hy, hx + hw - 1, hy + hh - 1, "B")
for ds in DOORS.values():
    for x, y in ds:
        gd[y][x] = "E"
for a, b, c, d in COURTS.values():
    fill(a, b, c, d, "Q")


# ---------------------------------------------------------------- Boden
RH = 6
cob_s, cob_e = [], []
for r in range(PH // RH + 2):
    s_, e_ = [0] * PW, [0] * PW
    x, k = -int(h2(r, 0, 7) * 8), 0
    while x < PW:
        wd = 6 + int(h2(r, k, 8) * 5)
        for xx in range(max(0, x), min(PW, x + wd)):
            s_[xx], e_[xx] = x, x + wd
        x += wd
        k += 1
    cob_s.append(s_)
    cob_e.append(e_)

def cobble_px(x, y):
    r, yy = y // RH, y % RH
    x0, w = cob_s[r][x], cob_e[r][x] - cob_s[r][x]
    xx = x - x0
    if xx == 0 or yy == RH - 1:
        return (92, 116, 70) if h2(x, y, 60) < 0.05 else (112, 102, 94)
    if (yy == 0 or yy == RH - 2) and (xx == 1 or xx == w - 1):
        return (142, 132, 122)
    v = h2(x0, r, 10)
    base = (158, 156, 154) if v < 0.22 else (188, 166, 138) if v > 0.85 else (176, 166, 150)
    c = jit(base, (h2(x0, r, 9) - 0.5) * 26)
    if yy == 0:
        c = jit(c, 18)
    elif yy == RH - 2:
        c = jit(c, -18)
    elif xx == w - 1:
        c = jit(c, -10)
    elif xx == 1:
        c = jit(c, 8)
    if h2(x, y, 61) < 0.08:
        c = jit(c, -8)
    return c

FCX, FCY = 48 * T, 32 * T

def flag_px(x, y):
    d = math.hypot(x - FCX, y - FCY)
    if 40 <= d < 56 and 38 * T <= x < 58 * T and 25 * T <= y < 40 * T:
        if d < 41.5 or d >= 54.5:
            return (140, 120, 104)
        a = int((math.atan2(y - FCY, x - FCX) + math.pi) / (math.pi / 10))
        base = (186, 128, 100) if a % 2 == 0 else (222, 204, 172)
        return jit(base, (h2(x // 3, y // 3, 12) - 0.5) * 10)
    FS = 12
    r = y // FS
    off = (r % 2) * 6
    cx, xx, yy = (x + off) // FS, (x + off) % FS, y % FS
    c = jit((208, 194, 166), (h2(cx, r, 11) - 0.5) * 22)
    if xx == 0 or yy == 0:
        return (160, 146, 126)
    if xx == 1 or yy == 1:
        return jit(c, 12)
    if xx == FS - 1 or yy == FS - 1:
        return jit(c, -12)
    if h2(x, y, 62) < 0.06:
        c = jit(c, -7)
    return c

def grass_px(x, y, forest):
    n = vnoise(x, y, 40, 1) * 0.55 + vnoise(x, y, 9, 2) * 0.45
    n = min(4, int(n * 5)) / 4
    c = lerp((38, 92, 44), (58, 120, 52), n) if forest else lerp((76, 154, 58), (116, 194, 76), n)
    r = h2(x, y, 3)
    if r < 0.07:
        c = mul(c, 0.86)
    elif r > 0.95:
        c = mul(c, 1.12)
    return c

def water_px(x, y):
    n = vnoise(x, y, 22, 4) * 0.6 + vnoise(x, y, 7, 5) * 0.4
    c = lerp((40, 100, 186), (68, 142, 222), min(3, int(n * 4)) / 3)
    cx, cy = x // 9, y // 6
    if h2(cx, cy, 12) < 0.4:
        wx = cx * 9 + int(h2(cx, cy, 13) * 4)
        wy = cy * 6 + int(h2(cx, cy, 14) * 4)
        if y == wy and wx <= x < wx + 4:
            return (158, 210, 246)
        if y == wy + 1 and wx + 1 <= x < wx + 5:
            return mul(c, 0.86)
    return c

def parapet_px(lx, ly, x, y):
    if ly < 9:
        if ly == 0:
            return (96, 88, 80)
        if ly == 1:
            return (226, 218, 202)
        return (150, 140, 128) if x % 12 == 0 else jit((202, 192, 174), (h2(x // 12, y, 70) - 0.5) * 12)
    if ly == 9:
        return (170, 158, 142)
    if ly == 15:
        return (72, 66, 60)
    if ly == 12 or (x + (6 if ly > 12 else 0)) % 12 == 0:
        return (110, 100, 90)
    return (146, 134, 118)

def ground_pass():
    b = cv.b
    for ty in range(H):
        for tx in range(W):
            t = gd[ty][tx]
            for ly in range(T):
                y = ty * T + ly
                i = (y * PW + tx * T) * 3
                for lx in range(T):
                    x = tx * T + lx
                    if t in "GB":
                        c = grass_px(x, y, False)
                    elif t == "F":
                        c = grass_px(x, y, True)
                    elif t == "P":
                        c = cobble_px(x, y)
                    elif t in "QE":
                        c = flag_px(x, y)
                    elif t == "R":
                        c = jit(cobble_px(x, y), 14)
                    elif t == "X":
                        c = parapet_px(lx, ly, x, y)
                    else:
                        c = water_px(x, y)
                    b[i] = c[0]; b[i + 1] = c[1]; b[i + 2] = c[2]
                    i += 3

FLOWER_C = [(250, 250, 240), (250, 214, 70), (236, 120, 170), (150, 150, 240), (240, 110, 80)]

def detail_pass():
    for ty in range(H):
        for tx in range(W):
            t = gd[ty][tx]
            if t not in "GF":
                continue
            for sy in range(2):
                for sx in range(2):
                    cx, cy = tx * 2 + sx, ty * 2 + sy
                    if h2(cx, cy, 50) < 0.5:
                        x = cx * 8 + 1 + int(h2(cx, cy, 51) * 6)
                        y = cy * 8 + 2 + int(h2(cx, cy, 52) * 5)
                        for dx, dy in ((-1, -1), (0, 0), (1, -1)):
                            cv.shade(x + dx, y + dy, 0.8)
                        cv.shade(x + 1, y - 2, 1.15)
            if t == "G" and h2(tx, ty, 53) < 0.22:
                n = 1 + int(h2(tx, ty, 54) * 3)
                col = FLOWER_C[int(h2(tx, ty, 55) * len(FLOWER_C))]
                for k in range(n):
                    x = tx * T + 3 + int(h2(tx, ty, 56 + k) * 10)
                    y = ty * T + 3 + int(h2(tx, ty, 60 + k) * 10)
                    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                        cv.set(x + dx, y + dy, col)
                    cv.set(x, y, (250, 200, 60) if col != (250, 214, 70) else (200, 110, 40))

BANK = [(118, 110, 96), (172, 162, 142), (188, 178, 156), (150, 142, 122)]
SAND = [(168, 150, 96), (198, 180, 120), (212, 196, 138)]

def edge_pass():
    sides = {"n": (0, -1), "s": (0, 1), "w": (-1, 0), "e": (1, 0)}

    def pix(side, d, k):
        if side == "n":
            return k, d
        if side == "s":
            return k, T - 1 - d
        if side == "w":
            return d, k
        return T - 1 - d, k

    for ty in range(H):
        for tx in range(W):
            t = gd[ty][tx]
            x0, y0 = tx * T, ty * T
            for side, (dx, dy) in sides.items():
                nt = g(tx + dx, ty + dy)
                if t in "PQ" and nt in "GF":
                    for k in range(T):
                        lx, ly = pix(side, 0, k)
                        cv.set(x0 + lx, y0 + ly, (96, 88, 80))
                        lx, ly = pix(side, 1, k)
                        cv.set(x0 + lx, y0 + ly, (172, 162, 148) if k % 8 == 7 else (214, 206, 192))
                elif t in "GFB" and nt == "W":
                    for d in range(4):
                        for k in range(T):
                            lx, ly = pix(side, d, k)
                            c = BANK[d]
                            if d in (1, 2) and ((x0 + k) if side in "ns" else (y0 + k)) % 10 == 0:
                                c = (132, 122, 106)
                            cv.set(x0 + lx, y0 + ly, c)
                elif t in "GF" and nt == "V":
                    for d in range(3):
                        for k in range(T):
                            lx, ly = pix(side, d, k)
                            cv.set(x0 + lx, y0 + ly, jit(SAND[d], (h2(x0 + lx, y0 + ly, 71) - 0.5) * 14))
                elif t in "WV" and nt not in "WVRX":
                    for d, f in enumerate((0.6, 0.76)):
                        for k in range(T):
                            lx, ly = pix(side, d, k)
                            cv.shade(x0 + lx, y0 + ly, f)
                    for k in range(T):
                        lx, ly = pix(side, 2, k)
                        if h2(x0 + lx, y0 + ly, 72) < 0.6:
                            cv.set(x0 + lx, y0 + ly, (164, 212, 244))
                elif t in "WV" and side == "n" and nt == "X":
                    for d in range(5):
                        for k in range(T):
                            cv.shade(x0 + k, y0 + d, 0.55 + d * 0.07)


# ---------------------------------------------------------------- Pflanzen
PAL_OAK = [(26, 64, 34), (40, 98, 44), (62, 134, 52), (92, 168, 62), (138, 204, 86)]
PAL_DEEP = [(18, 46, 30), (28, 78, 42), (44, 108, 50), (68, 138, 58), (102, 170, 72)]
PAL_LIME = [(40, 78, 30), (78, 128, 44), (112, 164, 54), (152, 198, 70), (198, 228, 112)]
PAL_BLOSSOM = [(120, 58, 90), (194, 108, 150), (226, 150, 186), (244, 190, 214), (255, 228, 240)]
PAL_AUTUMN = [(90, 46, 24), (170, 86, 34), (212, 126, 46), (236, 170, 64), (250, 212, 110)]
PAL_PINE = [(16, 50, 40), (26, 84, 58), (40, 116, 72), (66, 146, 88), (100, 176, 110)]

def canopy(cx, cy, r, pal, seed, fruit=None):
    ri = int(r) + 3
    for py in range(int(cy - ri), int(cy + ri) + 1):
        for px in range(int(cx - ri), int(cx + ri) + 1):
            dx, dy = px - cx, (py - cy) * 1.08
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            re = r * (1 + 0.1 * math.sin(ang * 6 + seed) + 0.06 * math.sin(ang * 11 + seed * 2))
            if d > re:
                continue
            if d > re - 1.3:
                c = pal[0]
            else:
                light = (-dx * 0.55 - dy * 0.85) / r
                v = 0.5 + light * 0.42 + (vnoise(px, py, 3.6, seed) - 0.5) * 0.75 - (d / re) * 0.12
                c = pal[1] if v < 0.3 else pal[2] if v < 0.55 else pal[3] if v < 0.8 else pal[4]
            cv.set(px, py, c)
    if fruit:
        rng = random.Random(seed)
        for _ in range(int(r * 0.7)):
            a, rr = rng.random() * 6.28, rng.random() * r * 0.75
            x, y = int(cx + math.cos(a) * rr), int(cy + math.sin(a) * rr)
            cv.rect(x, y, 2, 2, fruit)
            cv.set(x, y, mul(fruit, 1.3))

def tree(cx, base, r, pal, seed, fruit=None):
    cv.shade_ellipse(cx + 4, base - 1, r * 0.95, r * 0.38, 0.6)
    cv.rect(cx - 2, base - r - 2, 5, r + 2, (104, 68, 42))
    cv.rect(cx + 2, base - r - 2, 1, r + 2, (74, 46, 30))
    cv.rect(cx - 2, base - r - 2, 1, r + 2, (134, 90, 58))
    cv.rect(cx - 3, base - 2, 7, 2, (88, 58, 36))
    canopy(cx, base - r - 7, r, pal, seed, fruit)

def conifer(cx, base, hgt, pal, seed):
    cv.shade_ellipse(cx + 4, base - 1, hgt * 0.32, hgt * 0.14, 0.6)
    cv.rect(cx - 2, base - 7, 4, 7, (96, 62, 40))
    top = base - hgt
    for py in range(top, base - 4):
        t = (py - top) / (hgt - 4)
        tier = (t * 3) % 1
        hw = (2 + hgt * 0.36 * t) * (0.6 + 0.4 * tier)
        for px in range(int(cx - hw), int(cx + hw) + 1):
            e = abs(px - cx) >= hw - 1.2 or tier < 0.08
            if e:
                c = pal[0]
            else:
                v = 0.55 - (px - cx) / (hw + 1) * 0.4 + (h2(px, py, seed) - 0.5) * 0.4 - tier * 0.15
                c = pal[1] if v < 0.3 else pal[2] if v < 0.55 else pal[3] if v < 0.8 else pal[4]
            cv.set(px, py, c)

def bush(cx, base, r, pal, seed, flowers=None):
    cv.shade_ellipse(cx + 3, base - 1, r * 1.0, r * 0.4, 0.62)
    canopy(cx, base - r + 1, r, pal, seed)
    if flowers:
        rng = random.Random(seed)
        for _ in range(int(r * 1.2)):
            a, rr = rng.random() * 6.28, rng.random() * r * 0.8
            x, y = int(cx + math.cos(a) * rr), int(base - r + 1 + math.sin(a) * rr * 0.9)
            cv.set(x, y, flowers)
            cv.set(x + 1, y, mul(flowers, 0.85))
            cv.set(x, y - 1, mul(flowers, 1.15))


# ---------------------------------------------------------------- Gebaeudeteile
DARK = (52, 42, 40)

def roof(x, y, w, h, col, hipr=0.5, ridge=0.3, sh=5):
    out = mul(col, 0.42)
    lit, drk, back = mul(col, 1.22), mul(col, 0.66), mul(col, 0.86)
    ry = y + int(h * ridge)
    hw = int(min(w * 0.32, h * hipr))
    for py in range(y, y + h):
        f = (py - y) / max(1, ry - y) if py <= ry else 1 - (py - ry) / max(1, y + h - 1 - ry)
        side = int(hw * f)
        for px in range(x, x + w):
            lx = px - x
            if side and (lx == side - 1 or lx == w - side):
                c = mul(col, 0.52)
            elif lx < side:
                c = lit if (py - y) % sh != sh - 1 else mul(lit, 0.86)
            elif lx >= w - side:
                c = drk if (py - y) % sh != sh - 1 else mul(drk, 0.86)
            elif py < ry:
                c = back if (py - y) % 3 != 2 else mul(back, 0.84)
            else:
                k, yy = (py - ry) // sh, (py - ry) % sh
                c = mul(col, 1.06 - 0.16 * (py - ry) / max(1, y + h - ry))
                if yy == sh - 1:
                    c = mul(c, 0.76)
                elif (lx + (k % 2) * 4) % 8 == 0:
                    c = mul(c, 0.86)
                elif yy == 0:
                    c = mul(c, 1.08)
            if h2(px, py, 31) < 0.06:
                c = mul(c, 0.92)
            cv.set(px, py, c)
    cv.rect(x + hw, ry, w - 2 * hw, 1, mul(col, 1.35))
    cv.rect(x + hw, ry + 1, w - 2 * hw, 1, mul(col, 1.12))
    cv.rect(x, y, w, 1, out)
    cv.rect(x, y + h - 1, w, 1, out)
    cv.rect(x, y + h - 2, w, 1, mul(col, 0.55))
    cv.rect(x, y, 1, h, out)
    cv.rect(x + w - 1, y, 1, h, out)

def wall(x, y, w, h, col, style="plaster"):
    for py in range(y, y + h):
        for px in range(x, x + w):
            lx, ly = px - x, py - y
            c = mul(col, 0.95 + vnoise(px, py, 6, 40) * 0.08)
            if style == "stone":
                r = ly // 7
                if ly % 7 == 6 or (lx + (r % 2) * 7) % 14 == 0:
                    c = mul(col, 0.8)
                elif ly % 7 == 0:
                    c = mul(c, 1.06)
            elif style == "brick":
                r = ly // 4
                off = (r % 2) * 4
                c = mul(col, 0.9 + h2((lx + off) // 8, r, 41) * 0.18)
                if ly % 4 == 3 or (lx + off) % 8 == 0:
                    c = (176, 156, 136)
            cv.set(px, py, c)
    for i, f in enumerate((0.5, 0.66, 0.8, 0.9)):
        cv.shade_rect(x, y + i, w, 1, f)
    cv.rect(x, y + h - 3, w, 3, mul(col, 0.7))
    cv.rect(x, y + h - 1, w, 1, mul(col, 0.5))
    cv.shade_rect(x + w - 2, y, 2, h, 0.8)
    cv.rect(x, y, 1, h, mul(col, 0.55))
    cv.rect(x + w - 1, y, 1, h, mul(col, 0.5))

def timber(x, y, w, h, beam=(94, 58, 38), step=18):
    xs = [x + 1] + list(range(x + step, x + w - 6, step)) + [x + w - 4]
    for vx in xs:
        cv.rect(vx, y + 3, 3, h - 6, beam)
    cv.rect(x, y + 3, w, 3, beam)
    cv.rect(x, y + h // 2, w, 3, beam)
    for i in range(len(xs) - 1):
        if i % 2 == 0:
            a, b = xs[i] + 3, xs[i + 1]
            cv.line(a, y + h // 2 + 3, b - 1, y + h - 4, beam, 2)

def arch_ok(lx, ly, w):
    r = w / 2
    if ly >= r:
        return True
    return (lx - (w - 1) / 2) ** 2 + (ly - r + 0.5) ** 2 <= r * r

BOOKS = [(170, 50, 50), (60, 90, 160), (70, 130, 70), (206, 162, 60), (122, 72, 42), (150, 80, 150), (220, 210, 190)]

def window(x, y, w, h, kind="glass", frame=(238, 232, 216), arch=False, box=None, curtain=None):
    for pad, col in ((2, DARK), (1, frame)):
        for py in range(y - pad, y + h + pad):
            for px in range(x - pad, x + w + pad):
                if not arch or arch_ok(px - x + pad, py - y + pad, w + 2 * pad):
                    cv.set(px, py, col)
    for py in range(y, y + h):
        for px in range(x, x + w):
            lx, ly = px - x, py - y
            if arch and not arch_ok(lx, ly, w):
                continue
            if kind == "glass":
                c = lerp((126, 182, 224), (62, 100, 160), ly / max(1, h - 1))
                if 0 <= lx + ly - w // 2 < 2:
                    c = (200, 230, 248)
            elif kind == "lit":
                c = lerp((255, 232, 150), (224, 146, 70), ly / max(1, h - 1))
            elif kind == "ghost":
                c = lerp((214, 252, 255), (110, 200, 224), ly / max(1, h - 1))
                if h2(px, py, 80) < 0.08:
                    c = (255, 255, 255)
            else:
                sy = ly % 7
                spine = lx // 2
                if sy == 6:
                    c = (104, 66, 40)
                elif sy < int(h2(spine, ly // 7, 81) * 2.4):
                    c = (70, 46, 34)
                else:
                    c = BOOKS[int(h2(spine, ly // 7 + x, 82) * len(BOOKS))]
                    if lx % 2 == 1:
                        c = mul(c, 0.8)
                    c = lerp(c, (255, 210, 120), 0.18)
            cv.set(px, py, c)
    if curtain:
        cv.rect(x, y, 2, h, curtain)
        cv.rect(x + w - 2, y, 2, h, curtain)
    if kind != "books":
        if w >= 8:
            cv.rect(x + w // 2, y, 1, h, frame)
        if h >= 10:
            cv.rect(x, y + h // 2, w, 1, frame)
    cv.rect(x - 3, y + h + 2, w + 6, 2, mul(frame, 1.03))
    cv.rect(x - 3, y + h + 4, w + 6, 1, mul(frame, 0.55))
    if box:
        cv.rect(x - 2, y + h + 4, w + 4, 3, (120, 76, 48))
        for k in range(w + 3):
            if h2(x + k, y, 83) < 0.7:
                cv.set(x - 2 + k, y + h + 3, (70, 150, 60))
                if h2(x + k, y, 84) < 0.45:
                    cv.set(x - 2 + k, y + h + 2, box)

def door(x, y, w, h, col=(126, 78, 46), frame=(214, 204, 184), arch=True, double=True, bands=False):
    for pad, c in ((3, DARK), (2, frame), (1, mul(frame, 0.8))):
        for py in range(y - pad, y + h):
            for px in range(x - pad, x + w + pad):
                if not arch or arch_ok(px - x + pad, py - y + pad, w + 2 * pad):
                    cv.set(px, py, c)
    for py in range(y, y + h):
        for px in range(x, x + w):
            lx, ly = px - x, py - y
            if arch and not arch_ok(lx, ly, w):
                continue
            c = mul(col, 1.0 - 0.18 * ly / h)
            if lx % 4 == 3:
                c = mul(c, 0.76)
            elif lx % 4 == 0:
                c = mul(c, 1.1)
            cv.set(px, py, c)
    if double:
        cv.rect(x + w // 2 - 1, y + 2, 2, h - 2, mul(col, 0.45))
    if bands:
        for by in (y + h // 4, y + h * 3 // 4):
            cv.rect(x, by, w, 2, (62, 56, 54))
    hy = y + h // 2 + 2
    cv.rect(x + w // 2 - 4, hy, 2, 2, (246, 206, 92))
    cv.rect(x + w // 2 + 2, hy, 2, 2, (246, 206, 92))

def steps(cx, y, w, n=3, col=(222, 214, 196)):
    for i in range(n):
        ww = w + i * 6
        cv.rect(cx - ww // 2, y + i * 3, ww, 3, jit(col, -i * 6))
        cv.rect(cx - ww // 2, y + i * 3 + 2, ww, 1, mul(col, 0.62))

def column(x, y, w, h):
    cv.rect(x, y, w, h, (238, 232, 216))
    for fx in range(x + 2, x + w - 2, 2):
        cv.rect(fx, y + 4, 1, h - 8, (218, 210, 192))
    cv.rect(x + w - 2, y, 2, h, (192, 182, 162))
    cv.rect(x, y, 1, h, (252, 248, 240))
    cv.rect(x - 1, y, w + 2, 3, (228, 220, 200))
    cv.rect(x - 1, y + 3, w + 2, 1, (160, 150, 132))
    cv.rect(x - 1, y + h - 3, w + 2, 3, (228, 220, 200))
    cv.rect(x - 1, y + h - 1, w + 2, 1, (140, 130, 116))

def pediment(cx, base, pw, ph, col=(236, 228, 208), tymp=(206, 194, 170)):
    for i in range(ph):
        hw = int(pw / 2 * (i + 1) / ph)
        yy = base - ph + i
        cv.rect(cx - hw, yy, 2 * hw, 1, col)
        cv.set(cx - hw, yy, (96, 86, 76))
        cv.set(cx + hw - 1, yy, (96, 86, 76))
    inner = ph - 9
    for i in range(inner):
        hw = int((pw / 2 - 12) * (i + 1) / inner)
        cv.rect(cx - hw, base - ph + 6 + i, 2 * hw, 1, tymp)
    cv.rect(cx - pw // 2, base - 3, pw, 3, col)
    cv.rect(cx - pw // 2, base - 1, pw, 1, (120, 110, 96))

def chimney(x, y, w=8, h=14, smoke=False):
    cv.shade_rect(x + w, y + 3, 3, h - 3, 0.7)
    cv.rect(x, y, w, h, (150, 82, 64))
    for yy in range(y + 3, y + h, 3):
        cv.rect(x, yy, w, 1, (116, 62, 50))
    cv.rect(x - 1, y, w + 2, 3, (128, 120, 114))
    cv.rect(x + 1, y, w - 2, 1, (40, 34, 32))
    if smoke:
        for i, (dx, dy, r) in enumerate(((3, -6, 3), (7, -13, 4), (13, -21, 5), (20, -29, 5))):
            cv.ellipse(x + w // 2 + dx, y + dy, r + 1, r + 1, (196, 198, 206))
            cv.ellipse(x + w // 2 + dx - 1, y + dy - 1, r, r, (234, 234, 240))

def dormer(x, y, col, roofcol):
    cv.shade_rect(x + 14, y + 6, 3, 11, 0.7)
    cv.rect(x + 1, y + 6, 14, 11, DARK)
    cv.rect(x + 2, y + 7, 12, 10, col)
    window(x + 5, y + 9, 6, 6, "lit")
    for i in range(8):
        cv.rect(x + 7 - i, y + i, 2 * (i + 1) + 1, 1, roofcol if i < 7 else mul(roofcol, 0.5))
        cv.set(x + 7 - i, y + i, mul(roofcol, 0.45))
        cv.set(x + 8 + i, y + i, mul(roofcol, 0.45))

def bshadow(x, y, w, h):
    cv.shade_rect(x + w, y + 12, 7, h - 10, 0.66)
    cv.shade_rect(x + 6, y + h, w, 3, 0.8)


# ---------------------------------------------------------------- Lernorte
def draw_lesesaal():
    x, y, w, h = 7 * T, 5 * T, 16 * T, 11 * T
    bshadow(x, y, w, h)
    rh = 92
    roof(x + 4, y + 2, w - 8, rh - 2, (96, 116, 158), hipr=0.7, ridge=0.28)
    fy, fh = y + rh, h - rh
    wall(x, fy, w, fh, (224, 212, 184), "stone")
    cv.shade_rect(x + 8, fy + 8, w - 16, fh - 18, 0.78)
    ncol, span = 8, w - 26
    cols = [x + 13 + round(i * span / (ncol - 1)) for i in range(ncol)]
    for i in range(ncol - 1):
        if i == 3:
            continue
        mx = (cols[i] + cols[i + 1]) // 2
        window(mx - 6, fy + 20, 12, 36, "lit", arch=True)
    for cx in cols:
        column(cx - 4, fy + 7, 8, fh - 17)
    door(x + w // 2 - 14, fy + fh - 10 - 44, 28, 44, col=(64, 88, 128), frame=(236, 228, 208))
    cv.rect(x, fy, w, 7, (240, 232, 212))
    cv.rect(x, fy + 7, w, 1, (150, 140, 120))
    for gx in range(x + 4, x + w - 4, 8):
        cv.rect(gx, fy + 2, 4, 3, (212, 202, 180))
    for i in range(3):
        cv.rect(x + 2 - i * 2, fy + fh - 10 + i * 3, w - 4 + i * 4, 3, jit((226, 218, 200), -i * 8))
        cv.rect(x + 2 - i * 2, fy + fh - 8 + i * 3, w - 4 + i * 4, 1, (150, 140, 124))
    pediment(x + w // 2, fy + 1, 136, 36)
    cv.ellipse(x + w // 2, fy - 13, 7, 7, (120, 110, 96))
    cv.ellipse(x + w // 2, fy - 13, 5, 5, (130, 184, 226))
    cv.set(x + w // 2 - 2, fy - 15, (220, 240, 252))
    for sx in (x + w // 2 - 68, x + w // 2 + 66):
        cv.rect(sx - 1, fy - 5, 4, 5, (236, 228, 208))

def draw_observatorium():
    x, y, w, h = 38 * T, 4 * T, 20 * T, 12 * T
    bshadow(x, y, w, h)
    slate = (72, 96, 148)
    for wx in (x, x + w - 116):
        roof(wx + 2, y + 32, 112, 80, slate, hipr=0.75, ridge=0.3)
        wall(wx, y + 110, 116, 82, (156, 88, 64), "brick")
        cv.rect(wx, y + 110, 116, 5, (226, 218, 198))
        cv.rect(wx, y + 115, 116, 1, (130, 110, 96))
        for qy in range(y + 118, y + 186, 8):
            for qx in (wx, wx + 110):
                cv.rect(qx, qy, 6, 6, (220, 210, 188))
                cv.rect(qx, qy + 6, 6, 1, (150, 140, 124))
        for i in range(3):
            window(wx + 18 + i * 32, y + 128, 16, 42, "books", frame=(226, 218, 198), arch=True)
    chimney(x + 20, y + 40, smoke=False)
    chimney(x + w - 30, y + 40)
    cx = x + w // 2
    rx0, rw, top = cx - 50, 100, y + 86
    for py in range(top, y + h):
        for px in range(rx0, rx0 + rw):
            t = (px - rx0) / (rw - 1)
            f = 0.72 + 0.34 * math.sin(math.pi * t) + 0.1 * (0.5 - t)
            c = mul((228, 220, 198), f)
            if (py - top) % 9 == 8:
                c = mul(c, 0.84)
            cv.set(px, py, c)
    cv.rect(rx0, top, 1, y + h - top, (110, 100, 90))
    cv.rect(rx0 + rw - 1, top, 1, y + h - top, (90, 80, 72))
    for px_ in (rx0 + 18, rx0 + rw - 22):
        cv.rect(px_, top + 8, 4, y + h - top - 18, (244, 238, 226))
        cv.rect(px_ + 3, top + 8, 1, y + h - top - 18, (180, 170, 150))
    for ox in (rx0 + 8, rx0 + rw - 8):
        cv.ellipse(ox, top + 34, 5, 5, DARK)
        cv.ellipse(ox, top + 34, 4, 4, (130, 180, 224))
    dy0, drx, dry = top, 56, 74
    for py in range(dy0 - dry, dy0 + 1):
        for px in range(cx - drx, cx + drx + 1):
            nx, ny = (px - cx) / drx, (py - dy0) / dry
            d = nx * nx + ny * ny
            if d > 1:
                continue
            if d > 0.93:
                c = (96, 100, 112)
            else:
                v = 0.55 - nx * 0.45 - ny * 0.25 + (h2(px // 2, py // 2, 90) - 0.5) * 0.1
                c = (150, 156, 172) if v < 0.35 else (190, 196, 210) if v < 0.6 else (220, 224, 234) if v < 0.85 else (246, 248, 252)
                wdt = math.sqrt(max(0.0, 1 - ny * ny))
                for k in (-0.66, -0.33, 0.33, 0.66):
                    if abs(nx - k * wdt) < 0.022:
                        c = mul(c, 0.78)
            cv.set(px, py, c)
    for py in range(dy0 - dry + 6, dy0 - 4):
        for px in range(cx + 2, cx + 13):
            c = (24, 30, 64) if px not in (cx + 2, cx + 12) else (60, 64, 80)
            cv.set(px, py, c)
    for sx, sy in ((cx + 5, dy0 - 50), (cx + 9, dy0 - 32), (cx + 6, dy0 - 18)):
        cv.set(sx, sy, (255, 250, 200))
    cv.line(cx + 6, dy0 - 36, cx + 44, dy0 - 66, (82, 60, 30), 7)
    cv.line(cx + 6, dy0 - 36, cx + 44, dy0 - 66, (212, 170, 76), 5)
    cv.line(cx + 8, dy0 - 39, cx + 42, dy0 - 66, (250, 220, 130), 1)
    cv.ellipse(cx + 45, dy0 - 67, 3, 3, (150, 200, 236))
    cv.rect(cx - drx - 4, dy0 - 2, 2 * drx + 8, 6, (238, 232, 216))
    cv.rect(cx - drx - 4, dy0 + 4, 2 * drx + 8, 1, (130, 120, 108))
    cv.rect(cx - 5, dy0 - dry - 8, 10, 10, (214, 190, 110))
    cv.rect(cx - 5, dy0 - dry - 8, 10, 1, (120, 96, 50))
    cv.rect(cx - 1, dy0 - dry - 13, 2, 5, (230, 200, 100))
    door(cx - 14, y + h - 10 - 46, 28, 46, col=(110, 62, 40), frame=(238, 230, 210))
    steps(cx, y + h - 10, 44, 3)

def draw_akademie():
    x, y, w, h = 66 * T, 4 * T, 18 * T, 12 * T
    bshadow(x, y, w, h)
    cu = (80, 158, 138)
    roof(x + 4, y + 36, w - 8, 88, cu, hipr=0.6, ridge=0.3)
    fy = y + 122
    fh = y + h - fy
    wall(x, fy, w, fh, (238, 212, 148), "plaster")
    for px in range(x + 6, x + w - 4, 32):
        cv.rect(px, fy + 4, 6, fh - 7, (248, 240, 222))
        cv.rect(px + 5, fy + 4, 1, fh - 7, (200, 184, 150))
    cx = x + w // 2
    for px in list(range(x + 18, cx - 40, 32)) + list(range(cx + 50, x + w - 16, 32)):
        window(px, fy + 16, 12, 30, "glass", arch=True)
        window(px, fy + 54, 12, 10, "glass")
    for ch in (x + 30, x + w - 40):
        chimney(ch, y + 44)
    tx = cx - 16
    for py in range(y + 16, y + 100):
        for px in range(tx, tx + 32):
            t = (px - tx) / 31
            cv.set(px, py, mul((240, 230, 206), 0.8 + 0.28 * math.sin(math.pi * t)))
    cv.rect(tx, y + 16, 1, 84, (120, 110, 96))
    cv.rect(tx + 31, y + 16, 1, 84, (110, 100, 88))
    cv.ellipse(cx, y + 50, 11, 11, (80, 70, 60))
    cv.ellipse(cx, y + 50, 10, 10, (214, 176, 70))
    cv.ellipse(cx, y + 50, 8, 8, (250, 246, 232))
    cv.line(cx, y + 50, cx, y + 44, (40, 36, 34))
    cv.line(cx, y + 50, cx + 5, y + 52, (40, 36, 34))
    for py in range(y - 2, y + 18):
        t = (py - (y - 2)) / 20
        hw = int(4 + 16 * math.sin(t * math.pi / 2))
        cv.rect(cx - hw, py, 2 * hw, 1, mul(cu, 0.85 + 0.3 * (1 - t)))
        cv.set(cx - hw, py, mul(cu, 0.45))
        cv.set(cx + hw - 1, py, mul(cu, 0.45))
    cv.rect(cx - 1, y - 12, 2, 10, (230, 196, 80))
    cv.ellipse(cx, y - 13, 3, 3, (246, 214, 96))
    rx0, rw = cx - 40, 80
    wall(rx0, fy - 12, rw, fh + 12, (246, 234, 206), "stone")
    for i in range(4):
        column(rx0 + 6 + i * 22, fy - 4, 7, fh - 8)
    pediment(cx, fy - 11, 96, 30, col=(246, 238, 218), tymp=(216, 200, 170))
    for k in range(9):
        a = math.pi + k * math.pi / 8
        cv.line(cx, fy - 17, cx + math.cos(a) * 14, fy - 17 + math.sin(a) * 10, (230, 186, 70))
    cv.ellipse(cx, fy - 17, 4, 4, (250, 214, 96))
    door(cx - 14, y + h - 10 - 42, 28, 42, col=(90, 54, 36), frame=(246, 238, 218))
    steps(cx, y + h - 10, 56, 3)

def draw_salon():
    x, y, w, h = 7 * T, 34 * T, 14 * T, 8 * T
    bshadow(x, y, w, h)
    rc = (150, 60, 72)
    roof(x + 4, y, w - 8, 68, rc, hipr=0.6, ridge=0.3)
    chimney(x + 30, y - 2)
    chimney(x + w - 40, y - 2, smoke=True)
    for dx in (x + 40, x + w // 2 - 8, x + w - 56):
        dormer(dx, y + 28, (240, 228, 208), rc)
    fy, fh = y + 66, h - 66
    wall(x, fy, w, fh, (242, 230, 210), "plaster")
    for px in range(x + 4, x + w - 4, 28):
        cv.rect(px, fy + 4, 5, fh - 7, (252, 246, 232))
        cv.rect(px + 4, fy + 4, 1, fh - 7, (206, 190, 166))
    cx = x + w // 2
    wins = [x + 18, x + 50, cx + 36, x + w - 34]
    for i, wx in enumerate(wins):
        window(wx, fy + 12, 16, 30, "ghost" if i == 2 else "lit", arch=True, curtain=(170, 40, 50))
    cv.ellipse(cx, fy + 11, 12, 8, DARK)
    cv.ellipse(cx, fy + 11, 11, 7, (238, 228, 208))
    cv.ellipse(cx, fy + 12, 9, 6, (255, 226, 140))
    door(cx - 12, y + h - 8 - 36, 24, 36, col=(52, 108, 86), frame=(238, 228, 208), arch=False)
    cv.rect(cx - 20, fy + 4, 40, 4, mul(rc, 0.9))
    cv.rect(cx - 20, fy + 8, 40, 1, mul(rc, 0.5))
    steps(cx, y + h - 8, 34, 2)

def draw_druckerei():
    x, y, w, h = 67 * T, 35 * T, 16 * T, 7 * T
    bshadow(x, y, w, h)
    mw = 176
    wall(x + mw, y + 64, w - mw, h - 64, (164, 158, 150), "stone")
    roof(x + mw - 4, y + 18, w - mw + 4, 48, (104, 112, 136), hipr=0.5, ridge=0.3)
    chimney(x + w - 30, y + 10, smoke=True)
    window(x + mw + 14, y + 76, 14, 14, "lit")
    window(x + mw + 46, y + 76, 14, 14, "lit")
    roof(x, y, mw, 60, (78, 86, 114), hipr=0.45, ridge=0.3)
    dormer(x + 34, y + 22, (232, 220, 194), (78, 86, 114))
    dormer(x + mw - 52, y + 22, (232, 220, 194), (78, 86, 114))
    fy, fh = y + 58, h - 58
    wall(x, fy, mw, fh, (234, 222, 196), "plaster")
    timber(x, fy, mw, fh, step=22)
    for wx in (x + 12, x + 44, x + 130, x + 156):
        window(wx, fy + 12, 12, 16, "lit", frame=(110, 70, 44))
    cx = 74 * T + 16
    door(cx - 16, y + h - 42, 32, 40, col=(122, 80, 48), frame=(94, 58, 38), arch=False, bands=True)
    sx = cx + 22
    cv.rect(sx, fy + 6, 14, 2, (50, 44, 40))
    cv.rect(sx + 2, fy + 8, 1, 3, (50, 44, 40))
    cv.rect(sx + 11, fy + 8, 1, 3, (50, 44, 40))
    cv.rect(sx, fy + 11, 14, 11, DARK)
    cv.rect(sx + 1, fy + 12, 12, 9, (196, 150, 90))
    cv.rect(sx + 2, fy + 14, 4, 5, (250, 246, 230))
    cv.rect(sx + 8, fy + 14, 4, 5, (250, 246, 230))
    cv.rect(sx + 6, fy + 13, 2, 7, (130, 40, 40))
    cv.rect(x + 64, y + h - 1, 2, 1, DARK)

def draw_wheel():
    x, y = 65 * T + 3, 36 * T + 2
    ww, hh = 24, 74
    cv.shade_rect(x + ww, y + 4, 4, hh, 0.7)
    cv.rect(x, y, ww, hh, (70, 44, 28))
    for py in range(y + 2, y + hh - 2):
        k = (py - y) % 6
        c = (150, 102, 60) if k < 4 else (98, 64, 38)
        if k == 0:
            c = (176, 126, 76)
        cv.rect(x + 3, py, ww - 6, 1, c)
    cv.rect(x + 1, y, 2, hh, (110, 72, 44))
    cv.rect(x + ww - 3, y, 2, hh, (110, 72, 44))
    cv.rect(x + ww - 2, y + hh // 2 - 3, 10, 6, (90, 90, 96))
    cv.rect(x + ww // 2 - 4, y + hh // 2 - 4, 8, 8, (60, 56, 56))
    for i in range(14):
        sx, sy = x + int(h2(i, 1, 91) * ww), y + hh - 6 + int(h2(i, 2, 91) * 12)
        cv.rect(sx, sy, 2, 1, (230, 244, 252))

def draw_house(tx, ty, tw, th, rc, wc, style, seed):
    x, y, w, h = tx * T, ty * T, tw * T, th * T
    bshadow(x, y, w, h)
    rng = random.Random(seed)
    rh = int(h * 0.56)
    roof(x + 1, y, w - 2, rh + 2, rc, hipr=0.3 + rng.random() * 0.3, ridge=0.28)
    chimney(x + 12 + rng.randint(0, w - 36), y - 4, smoke=rng.random() < 0.5)
    fy, fh = y + rh, h - rh
    wall(x + 4, fy, w - 8, fh, wc, "stone" if style == "stone" else "plaster")
    if style == "timber":
        timber(x + 4, fy, w - 8, fh, step=20)
    cx = x + w // 2
    dcol = [(122, 78, 46), (60, 100, 140), (140, 50, 50), (60, 110, 80)][seed % 4]
    door(cx - 7, y + h - 26, 14, 24, col=dcol, frame=(200, 186, 160), arch=seed % 2 == 0, double=False)
    box = [(236, 90, 110), (250, 210, 70), (240, 240, 240), (200, 110, 220)][seed % 4]
    for wx in (x + 14, x + w - 26):
        window(wx, fy + 12, 12, 12, "glass", frame=(240, 232, 214), box=box)


# ---------------------------------------------------------------- Dekor
def lamp(tx, ty):
    x, b = tx * T + 8, ty * T + 14
    cv.shade_ellipse(x + 3, b, 6, 2, 0.6)
    cv.rect(x - 3, b - 3, 7, 3, (46, 44, 52))
    cv.rect(x - 1, b - 26, 3, 24, (46, 44, 52))
    cv.rect(x, b - 26, 1, 24, (90, 88, 100))
    cv.rect(x - 4, b - 35, 9, 9, (40, 38, 46))
    cv.rect(x - 3, b - 34, 7, 7, (255, 222, 120))
    cv.rect(x - 2, b - 33, 2, 3, (255, 250, 210))
    cv.rect(x - 5, b - 37, 11, 2, (40, 38, 46))
    cv.rect(x - 1, b - 39, 3, 2, (40, 38, 46))

def bench(tx, ty):
    x, y = tx * T + 2, ty * T + 3
    cv.shade_rect(x + 3, y + 10, 28, 3, 0.65)
    cv.rect(x, y, 28, 3, (110, 70, 42))
    cv.rect(x, y, 28, 1, (160, 108, 66))
    for i in range(2):
        cv.rect(x, y + 4 + i * 3, 28, 2, (150, 98, 58))
        cv.rect(x, y + 4 + i * 3, 28, 1, (186, 130, 80))
    cv.rect(x + 1, y + 10, 2, 3, (60, 44, 34))
    cv.rect(x + 25, y + 10, 2, 3, (60, 44, 34))

def fountain(tx, ty):
    cx, cy = tx * T + 32, ty * T + 34
    cv.shade_ellipse(cx + 4, cy + 5, 32, 25, 0.6)
    cv.ellipse(cx, cy, 31, 25, (92, 86, 84))
    cv.ellipse(cx, cy, 30, 24, (216, 210, 198))
    cv.ellipse(cx, cy - 1, 29, 23, (236, 232, 222))
    cv.ellipse(cx, cy + 1, 26, 20, (150, 144, 136))
    for yy, a, b in cv.spans(cx, cy + 3, 24, 17):
        for xx in range(a, b):
            cv.set(xx, yy, water_px(xx, yy))
    for rr in (9, 15):
        for k in range(40):
            ang = k / 40 * 6.283
            if k % 3:
                cv.set(cx + math.cos(ang) * rr * 1.25, cy + 3 + math.sin(ang) * rr * 0.9, (170, 216, 246))
    cv.ellipse(cx, cy + 3, 7, 5, (170, 164, 154))
    cv.rect(cx - 3, cy - 14, 7, 17, (206, 200, 188))
    cv.rect(cx + 2, cy - 14, 2, 17, (160, 154, 144))
    cv.ellipse(cx, cy - 15, 12, 5, (92, 86, 84))
    cv.ellipse(cx, cy - 15, 11, 4, (226, 220, 208))
    cv.ellipse(cx, cy - 15, 8, 2, (90, 160, 220))
    for k in range(34):
        a = h2(k, 1, 92) * 6.283
        r = 4 + h2(k, 2, 92) * 16
        yy = cy - 22 - int(h2(k, 3, 92) * 8) + int(r * 0.4)
        cv.set(cx + math.cos(a) * r, yy + math.sin(a) * r * 0.3, (214, 238, 252) if k % 2 else (255, 255, 255))
    cv.rect(cx - 1, cy - 28, 3, 12, (200, 232, 250))
    cv.rect(cx, cy - 30, 1, 3, (255, 255, 255))

def planter_tree(tx, ty, seed):
    x, y = tx * T + 2, ty * T + 14
    cv.shade_rect(x + 4, y + 16, 28, 3, 0.62)
    cv.rect(x, y, 28, 16, (98, 88, 80))
    cv.rect(x + 1, y + 1, 26, 11, (206, 198, 184))
    cv.rect(x + 1, y + 12, 26, 3, (160, 150, 136))
    cv.rect(x + 4, y + 3, 20, 6, (96, 64, 40))
    tree(x + 14, y + 8, 14, PAL_BLOSSOM, seed)

def stall(tx, ty, col, goods):
    x, y = tx * T, ty * T
    cv.shade_rect(x + 5, y + 44, 44, 4, 0.62)
    cv.rect(x + 4, y + 18, 3, 28, (86, 58, 38))
    cv.rect(x + 41, y + 18, 3, 28, (86, 58, 38))
    cv.rect(x + 2, y + 30, 44, 14, (96, 62, 38))
    cv.rect(x + 3, y + 31, 42, 5, (176, 120, 72))
    cv.rect(x + 3, y + 36, 42, 7, (136, 88, 52))
    rng = random.Random(tx * 7 + ty)
    for i in range(9):
        gx = x + 5 + i * 4 + rng.randint(0, 1)
        if goods == "books":
            c = BOOKS[rng.randint(0, len(BOOKS) - 1)]
            cv.rect(gx, y + 30, 3, 5, c)
            cv.rect(gx, y + 30, 3, 1, mul(c, 1.3))
        else:
            c = [(210, 40, 40), (240, 180, 50), (120, 180, 60)][rng.randint(0, 2)]
            cv.ellipse(gx + 1.5, y + 32, 2, 2, c)
            cv.set(gx + 1, y + 31, (255, 255, 255))
    for px in range(x + 1, x + 47):
        stripe = ((px - x - 1) // 6) % 2
        c0 = col if stripe else (244, 238, 226)
        seg = (px - x - 1) % 6
        bottom = y + 24 + (1 if seg in (0, 5) else 2 if seg in (1, 4) else 3)
        for py in range(y + 3, bottom):
            f = 1.08 - 0.25 * (py - y - 3) / 24
            cv.set(px, py, mul(c0, f))
        cv.set(px, bottom, mul(c0, 0.5))
        cv.set(px, y + 2, mul(c0, 0.5))
    cv.rect(x + 1, y + 2, 1, 24, DARK)
    cv.rect(x + 46, y + 2, 1, 24, DARK)
    cv.rect(x + 1, y + 10, 46, 1, (255, 255, 255))

def telescope(tx, ty):
    cx, cy = tx * T + 8, ty * T + 10
    cv.shade_ellipse(cx + 3, cy + 5, 8, 3, 0.62)
    for ex, ey in ((cx - 6, cy + 6), (cx + 6, cy + 6), (cx, cy + 7)):
        cv.line(cx, cy - 4, ex, ey, (96, 64, 40))
    cv.line(cx - 9, cy - 1, cx + 9, cy - 13, (70, 50, 26), 5)
    cv.line(cx - 9, cy - 1, cx + 9, cy - 13, (214, 170, 76), 3)
    cv.line(cx - 8, cy - 3, cx + 8, cy - 14, (250, 222, 130))
    cv.rect(cx + 8, cy - 15, 3, 3, (150, 200, 236))

def armillary(tx, ty):
    cx, cy = tx * T + 16, ty * T + 18
    cv.shade_ellipse(cx + 4, cy + 11, 11, 4, 0.6)
    cv.rect(cx - 7, cy + 6, 14, 6, (200, 194, 182))
    cv.rect(cx - 7, cy + 11, 14, 1, (130, 124, 116))
    cv.rect(cx - 2, cy - 2, 4, 8, (170, 164, 154))
    oy = cy - 12
    for k in range(120):
        a = k / 120 * 6.283
        cv.set(cx + math.cos(a) * 11, oy + math.sin(a) * 11, (206, 160, 60))
        cv.set(cx + math.cos(a) * 11, oy + math.sin(a) * 4, (236, 196, 90))
        cv.set(cx + math.cos(a) * 4, oy + math.sin(a) * 11, (236, 196, 90))
        u, v = math.cos(a) * 11, math.sin(a) * 4
        cv.set(cx + u * 0.8 - v * 0.6, oy + u * 0.6 + v * 0.8, (250, 214, 110))
    cv.ellipse(cx, oy, 3, 3, (90, 150, 210))
    cv.set(cx - 1, oy - 1, (200, 230, 250))

def flagpole(tx, ty, col):
    x, b = tx * T + 6, ty * T + 14
    cv.shade_ellipse(x + 4, b, 5, 2, 0.6)
    cv.rect(x - 2, b - 3, 5, 3, (120, 112, 104))
    cv.rect(x, b - 46, 2, 44, (80, 76, 72))
    cv.ellipse(x + 1, b - 47, 2, 2, (240, 204, 90))
    for i in range(22):
        wv = int(math.sin(i * 0.5) * 1.5)
        for j in range(12):
            c = col
            if 4 <= j <= 7 and 7 <= i <= 12:
                c = (246, 206, 90)
            cv.set(x + 2 + j, b - 44 + i + wv * (j > 6), c if j < 11 else mul(col, 0.6))
    cv.line(x + 2, b - 22, x + 8, b - 18, col, 2)
    cv.line(x + 13, b - 22, x + 8, b - 18, col, 2)

def crates(tx, ty):
    for dx, dy in ((2, 14), (16, 16), (6, 2)):
        x, y = tx * T + dx, ty * T + dy
        cv.shade_rect(x + 3, y + 12, 12, 3, 0.62)
        cv.rect(x, y, 13, 13, (86, 56, 34))
        cv.rect(x + 1, y + 1, 11, 11, (176, 126, 74))
        cv.line(x + 1, y + 1, x + 11, y + 11, (130, 88, 50))
        cv.line(x + 11, y + 1, x + 1, y + 11, (130, 88, 50))
        cv.rect(x + 1, y + 1, 11, 1, (206, 156, 100))

def barrels(tx, ty, n=2):
    for i in range(n):
        cx, b = tx * T + 8 + i * 16, ty * T + 14
        cv.shade_ellipse(cx + 3, b, 7, 2, 0.6)
        cv.rect(cx - 6, b - 14, 12, 13, (128, 80, 44))
        cv.rect(cx - 6, b - 14, 3, 13, (158, 104, 60))
        cv.rect(cx + 3, b - 14, 3, 13, (98, 62, 36))
        for by in (b - 12, b - 5):
            cv.rect(cx - 6, by, 12, 2, (70, 64, 62))
        cv.ellipse(cx, b - 15, 6, 2.5, (96, 60, 34))
        cv.ellipse(cx, b - 15, 4.5, 1.5, (150, 100, 56))

def paper_bales(tx, ty):
    for i, (dx, dy) in enumerate(((2, 18), (16, 18), (8, 6), (22, 4))):
        x, y = tx * T + dx, ty * T + dy
        cv.shade_rect(x + 3, y + 9, 12, 3, 0.65)
        cv.rect(x, y, 13, 10, (120, 110, 96))
        cv.rect(x + 1, y + 1, 11, 8, (246, 240, 224))
        for k in range(y + 3, y + 9, 2):
            cv.rect(x + 1, k, 11, 1, (220, 212, 192))
        cv.rect(x + 6, y, 1, 10, (160, 60, 50))

def cart(tx, ty):
    x, y = tx * T + 2, ty * T + 6
    cv.shade_rect(x + 4, y + 20, 28, 4, 0.62)
    cv.rect(x, y, 28, 18, (84, 54, 32))
    cv.rect(x + 1, y + 1, 26, 12, (160, 110, 64))
    for k in range(x + 1, x + 27, 5):
        cv.rect(k, y + 1, 1, 12, (120, 80, 46))
    cv.rect(x + 3, y + 2, 10, 8, (246, 240, 224))
    cv.rect(x + 14, y + 3, 10, 7, (230, 200, 150))
    for wx in (x + 2, x + 22):
        cv.rect(wx, y + 12, 5, 10, (54, 40, 30))
        cv.rect(wx + 1, y + 13, 3, 8, (120, 84, 50))
    cv.rect(x + 28, y + 8, 8, 2, (96, 62, 38))

def hedge(tx, ty, tw, th=1):
    x, y, w, h = tx * T, ty * T + 2, tw * T, th * T - 2
    cv.shade_rect(x + 3, y + h, w, 3, 0.62)
    for py in range(y, y + h):
        for px in range(x, x + w):
            front = py >= y + h - 6
            v = vnoise(px, py, 3, 93) + (-0.25 if front else 0.1) - (0.15 if py < y + 2 else 0) * -1
            p = PAL_DEEP if front else PAL_OAK
            c = p[1] if v < 0.35 else p[2] if v < 0.6 else p[3] if v < 0.85 else p[4]
            if px in (x, x + w - 1) or py in (y, y + h - 1):
                c = PAL_OAK[0]
            cv.set(px, py, c)

def flowerbed(tx, ty, tw, seed, th=1):
    x, y, w, h = tx * T + 1, ty * T + 3, tw * T - 2, th * T - 5
    cv.rect(x, y, w, h, (128, 118, 106))
    cv.rect(x + 1, y + 1, w - 2, h - 2, (200, 192, 178))
    cv.rect(x + 2, y + 2, w - 4, h - 4, (96, 64, 42))
    rng = random.Random(seed)
    cols = rng.sample(FLOWER_C + [(210, 50, 60)], 3)
    for fy in range(y + 4, y + h - 3, 4):
        for fx in range(x + 4 + (fy // 4) % 2 * 2, x + w - 3, 4):
            cv.rect(fx - 1, fy, 3, 2, (60, 130, 56))
            c = cols[(fx // 4 + fy // 4) % 3]
            cv.set(fx, fy - 1, c)
            cv.set(fx - 1, fy, c)
            cv.set(fx + 1, fy, mul(c, 0.8))

def iron_h(tx0, tx1, ty):
    b = ty * T + 12
    x0, x1 = tx0 * T, (tx1 + 1) * T
    cv.shade_rect(x0 + 2, b + 1, x1 - x0, 2, 0.7)
    cv.rect(x0, b - 11, x1 - x0, 2, (44, 40, 44))
    cv.rect(x0, b - 3, x1 - x0, 2, (44, 40, 44))
    for px in range(x0 + 2, x1, 5):
        cv.rect(px, b - 13, 2, 13, (40, 36, 40))
        cv.set(px, b - 14, (40, 36, 40))
        cv.set(px, b - 12, (110, 104, 110))
    for px in (x0, x1 - 8):
        cv.rect(px, b - 17, 8, 17, (98, 92, 88))
        cv.rect(px + 1, b - 16, 6, 12, (196, 188, 176))
        cv.rect(px - 1, b - 18, 10, 3, (220, 214, 204))

def iron_v(tx, ty0, ty1):
    x = tx * T + 7
    for py in range(ty0 * T, (ty1 + 1) * T, 4):
        cv.rect(x, py - 10, 2, 11, (40, 36, 40))
        cv.set(x, py - 11, (110, 104, 110))
    cv.rect(x + 2, ty0 * T - 8, 1, (ty1 - ty0 + 1) * T, (80, 76, 80))

def wood_h(tx0, tx1, ty):
    b = ty * T + 12
    x0, x1 = tx0 * T, (tx1 + 1) * T
    cv.rect(x0, b - 8, x1 - x0, 2, (130, 88, 52))
    cv.rect(x0, b - 3, x1 - x0, 2, (130, 88, 52))
    for px in range(x0, x1, 8):
        cv.rect(px, b - 11, 3, 11, (104, 68, 40))
        cv.rect(px, b - 11, 3, 1, (170, 124, 80))

def wood_v(tx, ty0, ty1):
    x = tx * T + 6
    for py in range(ty0 * T, (ty1 + 1) * T, 8):
        cv.rect(x, py - 9, 3, 10, (104, 68, 40))
        cv.rect(x, py - 9, 3, 1, (170, 124, 80))
    cv.rect(x + 1, ty0 * T - 6, 1, (ty1 - ty0 + 1) * T, (130, 88, 52))

def stonewall_h(tx0, tx1, ty):
    x0, x1, y = tx0 * T, (tx1 + 1) * T, ty * T + 3
    cv.shade_rect(x0 + 3, y + 12, x1 - x0, 3, 0.66)
    cv.rect(x0, y, x1 - x0, 6, (206, 198, 182))
    cv.rect(x0, y, x1 - x0, 1, (110, 100, 90))
    cv.rect(x0, y + 1, x1 - x0, 1, (230, 224, 210))
    for py in range(y + 6, y + 12):
        for px in range(x0, x1):
            r = (py - y - 6) // 3
            c = (150, 140, 126)
            if (py - y - 6) % 3 == 2 or (px + r * 5) % 10 == 0:
                c = (112, 102, 92)
            cv.set(px, py, c)
    cv.rect(x0, y + 12, x1 - x0, 1, (80, 72, 66))
    cv.rect(x0, y, 1, 13, (110, 100, 90))
    cv.rect(x1 - 1, y, 1, 13, (110, 100, 90))

def stonewall_v(tx, ty0, ty1):
    x, y0, y1 = tx * T + 4, ty0 * T, (ty1 + 1) * T
    cv.shade_rect(x + 8, y0 + 3, 3, y1 - y0, 0.66)
    for py in range(y0 - 3, y1 - 3):
        for px in range(x, x + 8):
            c = (206, 198, 182)
            if py % 10 == 0:
                c = (170, 160, 146)
            if px == x or px == x + 7:
                c = (110, 100, 90)
            elif px == x + 1:
                c = (230, 224, 210)
            cv.set(px, py, c)

def gazebo(tx, ty):
    cx, cy = tx * T + 32, ty * T + 26
    b = ty * T + 60
    cv.shade_ellipse(cx + 5, b - 4, 30, 10, 0.6)
    cv.ellipse(cx, b - 6, 28, 8, (120, 112, 104))
    cv.ellipse(cx, b - 7, 27, 7, (226, 220, 208))
    for k in (-22, -8, 8, 22):
        cv.rect(cx + k - 2, cy + 8, 4, b - 8 - cy - 8, (244, 240, 230))
        cv.rect(cx + k + 1, cy + 8, 1, b - 8 - cy - 8, (190, 184, 170))
    for py in range(cy - 24, cy + 14):
        for px in range(cx - 32, cx + 33):
            nx, ny = (px - cx) / 31, (py - cy - 2) / 16
            d = nx * nx + ny * ny
            if d > 1:
                continue
            a = math.atan2(ny, nx)
            seg = int((a + math.pi) / (math.pi / 4))
            c = (82, 160, 150) if seg % 2 else (110, 186, 172)
            if d > 0.9:
                c = (44, 96, 92)
            elif d < 0.05:
                c = (240, 206, 96)
            if ny < -0.2 and d < 0.9:
                c = mul(c, 1.08)
            cv.set(px, py, c)
    cv.rect(cx - 1, cy - 20, 3, 6, (240, 206, 96))

def pond_life(tx, ty, tw, th, seed):
    rng = random.Random(seed)
    for _ in range(tw):
        x = tx * T + 6 + rng.randint(0, tw * T - 16)
        y = ty * T + 6 + rng.randint(0, th * T - 14)
        cv.ellipse(x, y, 4, 3, (56, 130, 60))
        cv.ellipse(x - 1, y - 1, 3, 2, (86, 164, 72))
        cv.set(x + 2, y - 1, water_px(x + 2, y - 1))
        cv.set(x + 3, y - 1, water_px(x + 3, y - 1))
        if rng.random() < 0.3:
            cv.set(x - 1, y - 1, (250, 200, 220))
    for i in range(2):
        x = tx * T + 16 + rng.randint(0, tw * T - 32)
        y = ty * T + 12 + rng.randint(0, th * T - 24)
        cv.shade_ellipse(x + 1, y + 3, 5, 2, 0.75)
        cv.ellipse(x, y, 4, 3, (250, 250, 244))
        cv.rect(x - 4, y - 5, 3, 3, (250, 250, 244))
        cv.set(x - 5, y - 4, (240, 160, 40))
        cv.set(x - 3, y - 5, (30, 30, 30))

def reeds(tx, ty, seed):
    rng = random.Random(seed)
    for _ in range(6):
        x = tx * T + rng.randint(1, 14)
        b = ty * T + rng.randint(10, 15)
        hgt = rng.randint(6, 11)
        cv.rect(x, b - hgt, 1, hgt, (70, 120, 50))
        cv.rect(x, b - hgt, 1, 3, (120, 80, 40))

def vegetable_garden(tx, ty, tw, th):
    x, y, w, h = tx * T, ty * T, tw * T, th * T
    cv.rect(x + 4, y + 4, w - 8, h - 8, (110, 74, 46))
    for ry in range(y + 8, y + h - 8, 7):
        cv.rect(x + 6, ry, w - 12, 5, (132, 90, 56))
        cv.rect(x + 6, ry + 4, w - 12, 1, (90, 60, 38))
        kind = (ry // 7) % 3
        for px in range(x + 10, x + w - 10, 7):
            if kind == 0:
                cv.ellipse(px, ry + 2, 3, 2.5, (80, 150, 70))
                cv.set(px - 1, ry + 1, (150, 210, 110))
            elif kind == 1:
                cv.rect(px, ry, 1, 3, (70, 150, 60))
                cv.rect(px - 1, ry + 3, 3, 2, (236, 130, 40))
            else:
                cv.ellipse(px, ry + 2, 2.5, 2, (60, 130, 60))
                cv.set(px + 1, ry + 1, (220, 50, 50))
    wood_h(tx, tx + tw - 1, ty)
    wood_h(tx, tx + tw - 1, ty + th - 1)
    wood_v(tx, ty + 1, ty + th - 1)
    wood_v(tx + tw - 1, ty + 1, ty + th - 1)

def flower_garden(tx, ty, tw, th):
    for i in range(th - 2):
        flowerbed(tx + 1, ty + 1 + i, tw - 2, 300 + i)
    wood_h(tx, tx + tw - 1, ty)
    wood_v(tx, ty + 1, ty + th - 1)
    wood_v(tx + tw - 1, ty + 1, ty + th - 1)
    wood_h(tx, tx + tw - 1, ty + th - 1)

def hay(tx, ty):
    cx, b = tx * T + 8, ty * T + 14
    cv.shade_ellipse(cx + 3, b, 9, 3, 0.62)
    cv.ellipse(cx, b - 7, 8, 7, (170, 130, 50))
    cv.ellipse(cx - 1, b - 8, 7, 6, (226, 190, 90))
    for k in range(-5, 6, 2):
        cv.line(cx + k, b - 13, cx + k + 1, b - 2, (190, 150, 60))

def beehive(tx, ty):
    cx, b = tx * T + 8, ty * T + 14
    cv.shade_ellipse(cx + 3, b, 7, 2, 0.62)
    for i, r in enumerate((6, 6, 5, 4, 3)):
        yy = b - 3 - i * 3
        cv.ellipse(cx, yy, r + 0.5, 2, (150, 110, 40))
        cv.ellipse(cx, yy - 0.5, r, 1.5, (226, 184, 90))
    cv.rect(cx - 1, b - 4, 3, 2, (40, 30, 20))

def well(tx, ty):
    cx, cy = tx * T + 16, ty * T + 20
    cv.shade_ellipse(cx + 4, cy + 8, 14, 6, 0.6)
    cv.ellipse(cx, cy, 13, 9, (96, 90, 86))
    cv.ellipse(cx, cy - 1, 12, 8, (196, 188, 176))
    cv.ellipse(cx, cy, 8, 5, (30, 50, 80))
    cv.rect(cx - 12, cy - 22, 3, 20, (100, 66, 40))
    cv.rect(cx + 9, cy - 22, 3, 20, (100, 66, 40))
    for i in range(7):
        cv.rect(cx - 15 + i, cy - 28 + i, 32 - 2 * i, 1, (160, 70, 50) if i < 6 else (100, 40, 30))
    cv.rect(cx - 9, cy - 16, 18, 2, (90, 60, 40))
    cv.rect(cx - 1, cy - 14, 2, 8, (150, 140, 120))
    cv.rect(cx - 3, cy - 7, 6, 4, (120, 80, 50))

def boat(tx, ty):
    cx, cy = tx * T + 16, ty * T + 16
    cv.shade_ellipse(cx + 2, cy + 3, 8, 16, 0.7)
    cv.ellipse(cx, cy, 8, 16, (70, 44, 28))
    cv.ellipse(cx, cy, 6.5, 14.5, (156, 104, 60))
    cv.ellipse(cx, cy, 4.5, 12, (120, 78, 44))
    for yy in (cy - 5, cy + 4):
        cv.rect(cx - 5, yy, 10, 2, (186, 132, 80))
    cv.line(cx + 5, cy - 2, cx + 14, cy - 8, (180, 130, 80), 1)

# ---------------------------------------------------------------- Objekte platzieren
objs = []
warn = []

def free(x0, y0, w, h, allow):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if g(x, y) not in allow or (x, y) in blocked:
                return False
    return True

def place(x0, y0, w, h, fn, allow="G", block=True, key=None, name=""):
    if not free(x0, y0, w, h, allow):
        warn.append(name or fn.__name__ + str((x0, y0)))
        return False
    if block:
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                blocked.add((x, y))
    objs.append(((y0 + h) * T if key is None else key, fn))
    return True

def mk(f, *a):
    return lambda: f(*a)

# Lernorte und Haeuser
objs.append((16 * T, draw_observatorium))
objs.append((16 * T, draw_lesesaal))
objs.append((16 * T, draw_akademie))
objs.append((42 * T, draw_salon))
objs.append((42 * T, draw_druckerei))
for hx, hy, hw, hh, rc, wc, st, sd in HOUSES:
    objs.append(((hy + hh) * T, mk(draw_house, hx, hy, hw, hh, rc, wc, st, sd)))
place(65, 36, 2, 5, draw_wheel, allow="GW", name="wheel")

# Zaeune, Mauern, Parkanlage West
for x in range(5, 25):
    for y in (23, 29):
        blocked.add((x, y))
for y in range(24, 29):
    blocked.add((5, y)); blocked.add((24, y))
objs.append((23 * T + 12, mk(iron_h, 5, 24, 23)))
objs.append((29 * T + 12, mk(iron_h, 5, 24, 29)))
objs.append((29 * T, mk(iron_v, 5, 24, 28)))
objs.append((29 * T, mk(iron_v, 24, 24, 28)))
for x in range(6, 24):
    for y in range(24, 29):
        if gd[y][x] == "G":
            blocked.add((x, y))
objs.append((28 * T, mk(gazebo, 18, 24)))
objs.append((29 * T, mk(flowerbed, 7, 28, 6, 11)))
objs.append((29 * T, mk(flowerbed, 16, 28, 7, 12)))
objs.append((0, mk(pond_life, 9, 25, 6, 3, 5)))
for bx, by in ((7, 25), (16, 25), (22, 24), (7, 27), (16, 27)):
    objs.append(((by + 1) * T, mk(bush, bx * T + 8, (by + 1) * T - 2, 7, PAL_OAK, bx * 3 + by, (236, 120, 170) if bx % 2 else None)))

# Teleskopgarten neben dem Observatorium
for x in range(30, 37):
    blocked.add((x, 7))
    if x != 33:
        blocked.add((x, 16))
for y in range(8, 16):
    blocked.add((30, y)); blocked.add((36, y))
objs.append((7 * T + 15, mk(stonewall_h, 30, 36, 7)))
objs.append((16 * T + 15, mk(stonewall_h, 30, 32, 16)))
objs.append((16 * T + 15, mk(stonewall_h, 34, 36, 16)))
objs.append((16 * T, mk(stonewall_v, 30, 8, 15)))
objs.append((16 * T, mk(stonewall_v, 36, 8, 15)))
for tx_, ty_ in ((31, 9), (35, 9), (31, 14), (35, 14)):
    place(tx_, ty_, 1, 1, mk(telescope, tx_, ty_), name="telescope")
place(32, 11, 2, 2, mk(armillary, 32, 11), name="armillary")

# Eingangsbereiche
place(8, 17, 3, 1, mk(flowerbed, 8, 17, 3, 21), name="fb")
place(19, 17, 3, 1, mk(flowerbed, 19, 17, 3, 22), name="fb")
place(39, 17, 3, 1, mk(flowerbed, 39, 17, 3, 23), name="fb")
place(54, 17, 3, 1, mk(flowerbed, 54, 17, 3, 24), name="fb")
place(70, 17, 1, 1, mk(flagpole, 70, 17, (50, 80, 160)), name="flag")
place(79, 17, 1, 1, mk(flagpole, 79, 17, (160, 40, 50)), name="flag")
place(66, 17, 3, 1, mk(hedge, 66, 17, 3), name="hedge")
place(81, 17, 3, 1, mk(hedge, 81, 17, 3), name="hedge")
place(9, 42, 1, 1, mk(bush, 9 * T + 8, 43 * T - 2, 8, PAL_OAK, 41, (220, 50, 70)), name="rose")
place(18, 42, 1, 1, mk(bush, 18 * T + 8, 43 * T - 2, 8, PAL_OAK, 42, (220, 50, 70)), name="rose")
place(68, 42, 2, 2, mk(crates, 68, 42), name="crates")
place(80, 42, 2, 1, mk(barrels, 80, 42), name="barrels")
place(83, 40, 2, 2, mk(paper_bales, 83, 40), name="bales")
place(83, 36, 2, 2, mk(cart, 83, 36), name="cart")

# Zentralplatz
place(46, 30, 4, 4, mk(fountain, 46, 30), allow="Q", name="fountain")
place(39, 26, 2, 2, mk(planter_tree, 39, 26, 7), allow="Q", name="planter")
place(55, 26, 2, 2, mk(planter_tree, 55, 26, 8), allow="Q", name="planter")
place(39, 37, 3, 3, mk(stall, 39, 37, (200, 50, 60), "books"), allow="Q", name="stall")
place(54, 37, 3, 3, mk(stall, 54, 37, (50, 90, 170), "fruit"), allow="Q", name="stall")
place(41, 23, 2, 1, mk(bench, 41, 23), name="bench")
place(53, 23, 2, 1, mk(bench, 53, 23), name="bench")
place(40, 41, 5, 1, mk(flowerbed, 40, 41, 5, 25), name="fb")
place(51, 41, 5, 1, mk(flowerbed, 51, 41, 5, 26), name="fb")
place(10, 30, 2, 1, mk(bench, 10, 30), name="bench")
place(17, 30, 2, 1, mk(bench, 17, 30), name="bench")
place(72, 30, 2, 1, mk(bench, 72, 30), name="bench")

# Laternen entlang der Strassen
for lx_, ly_ in ((11, 18), (18, 18), (43, 18), (52, 18), (8, 22), (20, 22), (36, 22), (57, 22),
                 (67, 22), (82, 22), (6, 43), (21, 43), (37, 43), (58, 43), (70, 43), (79, 43),
                 (21, 47), (30, 47), (45, 47), (50, 47), (66, 47), (84, 47), (25, 26), (25, 38),
                 (29, 26), (29, 38), (85, 26), (85, 38), (89, 26), (89, 38), (37, 30), (37, 34),
                 (58, 30), (58, 34), (45, 23), (50, 23), (45, 41), (50, 41), (65, 30), (65, 34)):
    place(lx_, ly_, 1, 1, mk(lamp, lx_, ly_), name="lamp" + str((lx_, ly_)))

# Garten Ost, Suedrand
place(81, 23, 4, 7, mk(flower_garden, 81, 23, 4, 7), name="fgarden")
place(5, 48, 13, 3, mk(vegetable_garden, 5, 48, 13, 3), name="veg")
place(20, 48, 1, 1, mk(hay, 20, 48), name="hay")
place(22, 49, 1, 1, mk(hay, 22, 49), name="hay")
place(21, 49, 1, 1, mk(hay, 21, 49), name="hay")
place(46, 48, 2, 2, mk(well, 46, 48), name="well")
place(83, 49, 1, 1, mk(beehive, 83, 49), name="hive")
place(85, 49, 1, 1, mk(beehive, 85, 49), name="hive")
objs.append((0, mk(pond_life, 33, 48, 9, 3, 9)))
for rx_, ry_ in ((32, 48), (32, 49), (42, 49), (42, 50), (8, 26), (15, 25)):
    if g(rx_, ry_) == "G":
        objs.append(((ry_ + 1) * T - 1, mk(reeds, rx_, ry_, rx_ * 5 + ry_)))
place(61, 9, 2, 2, mk(boat, 61, 9), allow="W", block=False, name="boat")
place(61, 25, 2, 2, mk(boat, 61, 25), allow="W", block=False, name="boat")

# Buesche an schmalen Streifen
for bx, by in ((58, 6), (58, 10), (58, 14), (37, 5), (65, 6), (65, 10), (65, 14), (65, 24),
               (65, 28), (72, 25), (73, 27), (37, 24), (37, 27), (37, 37), (37, 40), (36, 45 - 3),
               (23, 36), (24, 40), (4, 36), (4, 40), (25, 11), (55, 47 + 2)):
    pal = [PAL_OAK, PAL_LIME, PAL_OAK][(bx + by) % 3]
    fl = [None, (250, 214, 70), (236, 120, 170), (250, 250, 240)][(bx * by) % 4]
    place(bx, by, 1, 1, mk(bush, bx * T + 8, (by + 1) * T - 2, 7, pal, bx * 11 + by, fl), name="bush" + str((bx, by)))

# Baeume streuen: 2x2 Kacheln, ein Feld Abstand zu Wegen
def scatter(x0, y0, x1, y1, n, seed, kinds):
    rng = random.Random(seed)
    tries = 0
    while n > 0 and tries < 800:
        tries += 1
        tx_, ty_ = rng.randint(x0, x1 - 1), rng.randint(y0, y1 - 1)
        ok = free(tx_, ty_, 2, 2, "G")
        if ok:
            for yy in range(ty_ - 1, ty_ + 3):
                for xx in range(tx_ - 1, tx_ + 3):
                    if g(xx, yy) not in "GF" or (xx, yy) in blocked:
                        ok = False
        if not ok:
            continue
        kind = kinds[rng.randint(0, len(kinds) - 1)]
        cx, b = (tx_ + 1) * T, (ty_ + 2) * T - 3
        sd = rng.randint(0, 999)
        if kind == "pine":
            f = mk(conifer, cx, b, 40 + rng.randint(0, 8), PAL_PINE, sd)
        elif kind == "fruit":
            f = mk(tree, cx, b, 13, PAL_OAK, sd, (214, 40, 40))
        else:
            pal = {"oak": PAL_OAK, "lime": PAL_LIME, "blossom": PAL_BLOSSOM, "autumn": PAL_AUTUMN}[kind]
            f = mk(tree, cx, b, 14 + rng.randint(0, 3), pal, sd)
        place(tx_, ty_, 2, 2, f, key=b)
        n -= 1

scatter(3, 3, 7, 18, 5, 1, ["oak", "pine", "oak"])
scatter(23, 3, 30, 18, 7, 2, ["oak", "lime", "blossom", "pine"])
scatter(84, 3, 93, 18, 8, 3, ["oak", "pine", "autumn"])
scatter(3, 30, 26, 34, 6, 4, ["oak", "lime", "blossom"])
scatter(3, 34, 7, 44, 3, 5, ["oak", "pine"])
scatter(21, 34, 26, 44, 2, 6, ["blossom", "oak"])
scatter(89, 19, 93, 51, 8, 7, ["oak", "pine", "autumn", "lime"])
scatter(19, 47, 33, 51, 3, 8, ["oak", "lime"])
scatter(42, 47, 60, 51, 5, 9, ["oak", "blossom", "pine"])
scatter(64, 47, 86, 51, 7, 10, ["fruit", "fruit", "blossom"])
scatter(64, 3, 67, 19, 1, 11, ["lime"])
scatter(36, 3, 38, 18, 1, 12, ["oak"])

# Waldrand: dicht, nur auf Waldkacheln
rng = random.Random(77)
for gy in range(-6, PH + 24, 17):
    for gx in range(-6, PW + 16, 17):
        cx = gx + rng.randint(-5, 5)
        b = gy + rng.randint(-5, 5)
        tx_, ty_ = cx // T, (b - 4) // T
        # Krone muss im Wald bleiben, damit der Rand die Spielflaeche nicht ueberdeckt
        if g(cx // T, (b - 4) // T) != "F" or any(g(px_ // T, py_ // T) not in "FW" for px_, py_ in
                                                  ((cx, b - 34), (cx - 14, b - 12), (cx + 14, b - 12))):
            continue
        sd = rng.randint(0, 999)
        r = rng.random()
        if r < 0.28:
            objs.append((b, mk(conifer, cx, b, 38 + rng.randint(0, 12), PAL_PINE, sd)))
        else:
            pal = PAL_DEEP if r < 0.8 else PAL_OAK if r < 0.93 else PAL_AUTUMN
            objs.append((b, mk(tree, cx, b, 15 + rng.randint(0, 4), pal, sd)))


# ---------------------------------------------------------------- Rendern
def render():
    ground_pass()
    detail_pass()
    edge_pass()
    for _, f in sorted(objs, key=lambda o: o[0]):
        f()

def walk_class(x, y):
    t = gd[y][x]
    if t == "E":
        return "E"
    if (x, y) in blocked:
        return "X"
    if t in "PQR":
        return "#"
    if t == "G":
        return "."
    if t in "WV":
        return "~"
    return "X"

COLL = {"#": (40, 200, 80), ".": (240, 220, 60), "X": (220, 40, 40), "~": (40, 110, 240), "E": (230, 40, 220)}

def export():
    cv.save(os.path.join(OUT, "welt.png"))
    cv.save(os.path.join(OUT, "welt_2x.png"), 2)
    ov = Canvas(PW, PH)
    ov.b[:] = cv.b
    rows = []
    for ty in range(H):
        row = ""
        for tx in range(W):
            k = walk_class(tx, ty)
            row += k
            c = COLL[k]
            for py in range(ty * T, ty * T + T):
                for px in range(tx * T, tx * T + T):
                    o = ov.get(px, py)
                    edge = px % T == 0 or py % T == 0
                    ov.set(px, py, lerp(o, c, 0.8 if edge else 0.5))
        rows.append(row)
    ov.save(os.path.join(OUT, "welt_kollision.png"), 2)
    data = {
        "kachelgroesse": T,
        "breite": W,
        "hoehe": H,
        "legende": {"#": "Weg/Platz, begehbar", ".": "Wiese, begehbar (optional sperren)",
                    "X": "Hindernis", "~": "Wasser", "E": "Eingang (Tuer)"},
        "start": {"x": 47, "y": 36, "hinweis": "Zentralplatz, suedlich des Brunnens"},
        "lernorte": {
            k: {"gebaeude": {"x": v[0], "y": v[1], "w": v[2], "h": v[3]},
                "tuer": [{"x": a, "y": b} for a, b in DOORS[k]],
                "vorplatz": {"x0": COURTS[k][0], "y0": COURTS[k][1], "x1": COURTS[k][2], "y1": COURTS[k][3]}}
            for k, v in BUILDINGS.items()},
        "raster": rows,
    }
    with open(os.path.join(OUT, "welt.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    render()
    export()
    if warn:
        print("Nicht platziert:", ", ".join(warn))
    print("Fertig:", PW, "x", PH)
