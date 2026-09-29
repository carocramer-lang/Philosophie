#!/usr/bin/env python3
# Innenraum Lesesaal: 40 x 24 Kacheln a 16 px, Topdown, gleiche Bausteine wie Oberwelt und Observatorium.
# Aufruf: python3 innen/lesesaal.py
# Ausgabe: lesesaal.png, lesesaal_2x.png, lesesaal_kollision.png, lesesaal.json und lesesaal_daten.js

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
fill(16, 3, 23, 5, "X")            # Podest mit Schreibpult

# Interaktionspunkte: Objekt (blockiert) und freie Flaeche davor (begehbar, 'I').
INTERAKTIONEN = [
    {"id": "lesepult", "objekt": (28, 17, 30, 18), "flaeche": (28, 19, 30, 19), "markiert": True},
    {"id": "schreibpult", "objekt": (17, 3, 22, 5), "flaeche": (17, 6, 22, 7), "markiert": False},
]
# Hier erscheint der Bibliothekar, sobald Jonny seine Zusammenfassung abgibt
BIBLIOTHEKAR = {"x": 23, "y": 5}

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
NAVE0, NAVE1 = 14 * T, 26 * T   # Mittelschiff aus Stein

def basket(x, y):
    """Korbgeflecht-Parkett: 12er-Felder, abwechselnd waagrecht und senkrecht verlegt."""
    cx, cy = x // 12, y // 12
    lx, ly = x % 12, y % 12
    quer = (cx + cy) % 2 == 0
    k = (ly if quer else lx) // 4
    base = [(168, 114, 66), (156, 104, 60), (178, 124, 74)][(k + cx * 3 + cy) % 3]
    c = jit(base, (h2(x // 4 if quer else x, y if quer else y // 4, 21) - 0.5) * 10)
    along = lx if quer else ly
    across = ly % 4 if quer else lx % 4
    if across == 3:
        return mul(base, 0.72)
    if across == 0:
        c = mul(c, 1.08)
    if along == 0:
        return mul(base, 0.8)
    return c

def floor_pass():
    b = cv.b
    for y in range(PH):
        for x in range(PW):
            c = G.flag_px(x + 3, y + 5) if NAVE0 <= x < NAVE1 else basket(x, y)
            if x in (NAVE0, NAVE1 - 1):
                c = (132, 118, 100)
            i = (y * PW + x) * 3
            b[i] = c[0]; b[i + 1] = c[1]; b[i + 2] = c[2]

def light_shaft(x0, x1, y_top, length, spread=14):
    for py in range(y_top, y_top + length):
        t = (py - y_top) / length
        g = int(t * spread)
        for px in range(x0 - g, x1 + g):
            cv.shade(px, py, 1.0 + 0.2 * (1 - t))

# ---------------------------------------------------------------- Waende
STONE = (226, 214, 186)

def back_wall():
    hh = 3 * T
    cv.rect(0, 0, PW, 6, O.CAP)
    cv.rect(0, 5, PW, 1, O.CAP_L)
    G.wall(0, 6, PW, hh - 6, STONE, "stone")
    # Rhythmus: Pilaster, dazwischen abwechselnd hohes Fenster und Wandregal
    fenster = []
    for i, sx in enumerate(range(T, 13 * T, 48)):
        if i % 2 == 0:
            G.window(sx + 17, 12, 12, 28, "lit", arch=True)
            fenster.append(sx + 17)
        else:
            O.shelf_wall(sx + 6, 10, 36, 36, 200 + i)
    for i, sx in enumerate(range(27 * T, 38 * T, 48)):
        if i % 2 == 1:
            G.window(sx + 17, 12, 12, 28, "lit", arch=True)
            fenster.append(sx + 17)
        else:
            O.shelf_wall(sx + 6, 10, 36, 36, 300 + i)
    for px in list(range(T, 13 * T + 1, 48)) + list(range(27 * T, 38 * T + 1, 48)):
        cv.rect(px - 3, 7, 7, hh - 8, (242, 234, 214))
        cv.rect(px + 3, 7, 1, hh - 8, (190, 178, 152))
        cv.rect(px - 4, 7, 9, 3, (250, 244, 228))
    # Mitte: Nische mit Rundfenster wie das Okulus im Giebel der Fassade
    cx = 20 * T
    cv.rect(cx - 72, 6, 144, hh - 6, mul(STONE, 0.9))
    cv.rect(cx - 72, 6, 2, hh - 6, (170, 158, 132))
    cv.rect(cx + 70, 6, 2, hh - 6, (170, 158, 132))
    cv.ellipse(cx, 25, 18, 18, (120, 110, 96))
    cv.ellipse(cx, 25, 16, 16, (236, 228, 208))
    cv.ellipse(cx, 25, 13, 13, (140, 190, 228))
    for k in range(8):
        a = k * math.pi / 4
        cv.line(cx, 25, cx + math.cos(a) * 13, 25 + math.sin(a) * 13, (236, 228, 208))
    cv.ellipse(cx, 25, 4, 4, (236, 228, 208))
    cv.ellipse(cx - 4, 20, 3, 2, (210, 236, 250))
    for bx in (cx - 52, cx + 52):
        # Buesten auf Konsolen links und rechts der Nische
        cv.rect(bx - 9, 36, 18, 4, (200, 190, 170))
        cv.rect(bx - 9, 39, 18, 1, (130, 120, 104))
        cv.ellipse(bx, 31, 7, 4, (236, 234, 230))
        cv.ellipse(bx, 23, 5, 6, (240, 238, 234))
        cv.rect(bx - 5, 17, 10, 4, (228, 226, 222))
        cv.set(bx + 2, 23, (170, 168, 164))
    cv.rect(0, hh - 3, PW, 3, (74, 46, 30))
    cv.rect(0, hh - 3, PW, 1, (110, 72, 44))
    cv.shade_rect(0, hh, PW, 4, 0.78)
    for fx in fenster:
        light_shaft(fx, fx + 12, hh, 70)
    light_shaft(cx - 12, cx + 12, hh, 40, 10)

# ---------------------------------------------------------------- Moebel und Architektur
def column(tx, ty):
    cx, b = tx * T + 8, ty * T + 14
    cv.shade_ellipse(cx + 5, b, 11, 4, 0.6)
    cv.rect(cx - 8, b - 6, 16, 6, (200, 190, 170))
    cv.rect(cx - 8, b - 6, 16, 1, (236, 228, 212))
    cv.rect(cx - 8, b - 1, 16, 1, (130, 120, 104))
    top = b - 38
    for px in range(cx - 5, cx + 6):
        t = (px - (cx - 5)) / 10
        c = mul((244, 238, 224), 0.78 + 0.3 * math.sin(math.pi * t) - 0.12 * t)
        cv.rect(px, top, 1, b - 6 - top, c)
    for fx in (cx - 3, cx, cx + 3):
        cv.rect(fx, top + 3, 1, b - 9 - top, (214, 206, 188))
    cv.rect(cx - 7, top - 4, 14, 4, (236, 230, 214))
    cv.rect(cx - 8, top - 6, 16, 3, (248, 244, 232))
    cv.rect(cx - 8, top - 1, 16, 1, (150, 140, 124))

def dais_and_desk():
    x0, y0 = 16 * T, 3 * T
    w, h = 8 * T, 3 * T
    O.shadow_box(x0, y0, w, h)
    cv.rect(x0, y0, w, h, (96, 60, 36))
    for py in range(y0 + 1, y0 + h - 6):
        cv.rect(x0 + 1, py, w - 2, 1, (150, 98, 58) if (py - y0) % 5 else (120, 78, 46))
    cv.rect(x0, y0 + h - 6, w, 6, (126, 82, 50))
    cv.rect(x0, y0 + h - 6, w, 1, (176, 122, 76))
    cv.rect(x0, y0 + h - 1, w, 1, (70, 44, 28))
    # Stehpult mit ausgerollter Papierrolle
    dx, dy, dw, dh = 17 * T + 6, 3 * T + 2, 6 * T - 12, 26
    cv.shade_rect(dx + 4, dy + dh, dw, 5, 0.6)
    cv.rect(dx + 8, dy + dh - 2, 4, 10, (70, 44, 28))
    cv.rect(dx + dw - 12, dy + dh - 2, 4, 10, (70, 44, 28))
    cv.rect(dx, dy, dw, dh, (74, 46, 28))
    cv.rect(dx + 2, dy + 2, dw - 4, dh - 6, (116, 74, 44))
    cv.rect(dx + 2, dy + dh - 4, dw - 4, 2, (150, 100, 60))
    px0, px1 = dx + 14, dx + dw - 14
    cv.rect(px0, dy + 3, px1 - px0, dh - 9, (246, 236, 208))
    for ly in range(dy + 6, dy + dh - 8, 3):
        cv.rect(px0 + 4, ly, int((px1 - px0 - 8) * (0.55 + 0.4 * h2(ly, 1, 5))), 1, (190, 176, 150))
    for rx in (px0 - 3, px1):
        cv.rect(rx, dy + 2, 4, dh - 7, (226, 212, 180))
        cv.rect(rx, dy + 2, 4, 1, (250, 244, 226))
        cv.rect(rx + 1, dy, 2, 2, (120, 80, 50))
        cv.rect(rx + 1, dy + dh - 5, 2, 2, (120, 80, 50))
    cv.ellipse(dx + 7, dy + 10, 3, 3, (30, 30, 40))
    cv.line(dx + 7, dy + 9, dx + 1, dy - 2, (246, 246, 240), 2)
    O.candle(dx + dw - 6, dy + 10)

def reading_room_table(tx, ty, tw):
    O.reading_table(tx, ty, tw)

def librarian_desk(tx, ty):
    x, y, w, h = tx * T, ty * T - 4, 5 * T, 2 * T + 4
    O.shadow_box(x, y, w, h)
    cv.rect(x, y, w, h, (70, 44, 28))
    cv.rect(x + 2, y + 2, w - 4, 12, (120, 80, 50))
    cv.rect(x + 2, y + 14, w - 4, h - 16, (100, 64, 38))
    for px in range(x + 8, x + w - 6, 18):
        cv.rect(px, y + 18, 12, h - 22, (88, 56, 34))
        cv.rect(px + 5, y + 22, 2, 2, (230, 190, 90))
    cv.rect(x + 8, y + 4, 14, 8, (236, 226, 196))
    cv.rect(x + 26, y + 4, 10, 7, (60, 90, 150))
    cv.rect(x + 26, y + 4, 10, 2, (90, 120, 180))
    cv.ellipse(x + w - 16, y + 9, 5, 3, (200, 160, 60))
    cv.ellipse(x + w - 16, y + 7, 3, 3, (236, 200, 90))
    cv.rect(x + w - 17, y + 3, 2, 2, (250, 230, 150))
    cv.rect(x + w - 30, y + 5, 6, 6, (140, 40, 40))

def big_lectern(tx, ty):
    """Kettenpult mit aufgeschlagenem Folianten: hier liegt der Text zum Herunterladen."""
    x, y, w = tx * T + 2, ty * T - 2, 3 * T - 4
    O.shadow_box(x + 6, y + 8, w - 12, 26)
    cv.rect(x + w // 2 - 3, y + 16, 6, 18, (70, 44, 28))
    cv.rect(x + 8, y + 30, w - 16, 4, (70, 44, 28))
    cv.rect(x, y + 2, w, 18, (86, 54, 32))
    cv.rect(x + 1, y + 3, w - 2, 15, (126, 82, 48))
    cv.rect(x + 4, y + 4, w - 8, 12, (246, 238, 214))
    cv.rect(x + w // 2 - 1, y + 4, 2, 12, (180, 160, 128))
    for ly in range(y + 6, y + 15, 2):
        cv.rect(x + 7, ly, w // 2 - 10, 1, (150, 140, 120))
        cv.rect(x + w // 2 + 3, ly, w // 2 - 10, 1, (150, 140, 120))
    cv.rect(x + 4, y + 4, 2, 12, (150, 40, 50))
    for k in range(6):
        cv.rect(x + w - 6 + (k % 2), y + 18 + k * 3, 2, 2, (150, 150, 160))

def catalogue(tx, ty, th):
    O.cabinet_v(tx, ty, th)

def small_table_with_globe(tx, ty):
    O.globe(tx, ty)

# ---------------------------------------------------------------- Einrichtung
# Linke Seite: drei lange Lesetische, darunter blaue Teppiche
TABLES = [(2, 5, 10), (2, 10, 10), (2, 15, 10)]
for tx_, ty_, tw_ in TABLES:
    block(tx_, ty_, tw_, 2, mk(reading_room_table, tx_, ty_, tw_))
block(1, 20, 2, 2, mk(small_table_with_globe, 1, 20))
block(12, 20, 1, 1, mk(O.plant, 12, 20))
block(12, 3, 1, 1, mk(O.plant, 12, 3))
# Mittelschiff: Saeulenreihen an beiden Kanten, Kandelaber am Podest, Buesten am Eingang
for cy in (7, 11, 15):
    block(14, cy, 1, 1, mk(column, 14, cy))
    block(25, cy, 1, 1, mk(column, 25, cy))
block(15, 3, 1, 1, mk(O.candelabra, 15, 3))
block(24, 3, 1, 1, mk(O.candelabra, 24, 3))
block(14, 20, 1, 1, mk(O.bust, 14, 20))
block(25, 20, 1, 1, mk(O.bust, 25, 20))
# Rechte Seite: Buecherstapel, Tisch des Bibliothekars, Katalogschrank, Lesepult
block(28, 5, 4, 2, mk(O.shelf_island, 28, 5, 4, 401))
block(33, 5, 4, 2, mk(O.shelf_island, 33, 5, 4, 402))
block(28, 10, 4, 2, mk(O.shelf_island, 28, 10, 4, 403))
block(33, 10, 5, 2, mk(librarian_desk, 33, 10))
block(38, 13, 1, 5, mk(catalogue, 38, 13, 5))
block(28, 17, 3, 2, mk(big_lectern, 28, 17))
block(35, 20, 1, 1, mk(O.plant, 35, 20))
block(27, 20, 1, 1, mk(O.plant, 27, 20))

for ia in INTERAKTIONEN:
    x0, y0, x1, y1 = ia["flaeche"]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            assert grid[y][x] == "#", ("Interaktionsflaeche belegt", ia["id"], x, y)
    fill(x0, y0, x1, y1, "I")


def render():
    floor_pass()
    for tx_, ty_, tw_ in TABLES:
        O.rug(tx_ * T - 6, ty_ * T - 6, tw_ * T + 12, 2 * T + 12, (44, 62, 120))
    O.runner(18 * T, 8 * T, 4 * T, 14 * T, (150, 40, 50))
    O.runner(15 * T + 8, 6 * T, 9 * T, 2 * T, (150, 40, 50))
    back_wall()
    O.side_walls()
    O.front_wall()
    for ia in INTERAKTIONEN:
        if ia["markiert"]:
            O.floor_glow(ia["flaeche"])
    objs.append((6 * T, dais_and_desk))
    for _, f in sorted(objs, key=lambda o: o[0]):
        f()
    for ia in INTERAKTIONEN:
        if ia["markiert"]:
            x0, y0, x1, y1 = ia["objekt"]
            O.marker_candle((x1 + 1) * T - 6, y0 * T - 2)


COLL = {"#": (40, 200, 80), "X": (220, 40, 40), "A": (230, 40, 220), "S": (40, 210, 230), "I": (250, 150, 30)}

def export():
    cv.save(os.path.join(HERE, "lesesaal.png"))
    cv.save(os.path.join(HERE, "lesesaal_2x.png"), 2)
    ov = G.Canvas(PW, PH)
    ov.b[:] = cv.b
    for ty in range(H):
        for tx in range(W):
            c = COLL[grid[ty][tx]]
            for py in range(ty * T, ty * T + T):
                for px in range(tx * T, tx * T + T):
                    edge = px % T == 0 or py % T == 0
                    ov.set(px, py, lerp(ov.get(px, py), c, 0.8 if edge else 0.5))
    ov.save(os.path.join(HERE, "lesesaal_kollision.png"), 2)
    data = {
        "name": "lesesaal",
        "kachelgroesse": T, "breite": W, "hoehe": H,
        "legende": {"#": "Boden, begehbar", "X": "Wand oder Moebel", "A": "Ausgang (Tuer nach draussen)",
                    "S": "Eintrittsstelle, begehbar", "I": "Interaktionsflaeche vor einem Objekt, begehbar"},
        "eintritt": {"x": 19, "y": 20, "blick": "up"},
        "ausgang": [{"x": x, "y": 22} for x in range(18, 22)],
        "interaktionen": [{"id": ia["id"], "markiert": ia["markiert"],
                           "flaeche": dict(zip(("x0", "y0", "x1", "y1"), ia["flaeche"])),
                           "objekt": dict(zip(("x0", "y0", "x1", "y1"), ia["objekt"]))}
                          for ia in INTERAKTIONEN],
        "bibliothekar": BIBLIOTHEKAR,
        "raster": ["".join(r) for r in grid],
    }
    with open(os.path.join(HERE, "lesesaal.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "lesesaal_daten.js"), "w", encoding="utf-8") as f:
        f.write("window.INNEN = window.INNEN || {};\nwindow.INNEN.lesesaal = " + json.dumps(data, ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    render()
    export()
    print("Fertig:", PW, "x", PH)
