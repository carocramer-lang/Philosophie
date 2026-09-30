#!/usr/bin/env python3
# Innenraum Akademie der Wissenschaften: 40 x 24 Kacheln a 16 px, Topdown, gleiche Bausteine wie die anderen Raeume.
# Festsaal fuer den Abschluss: Podium mit dem Praesidenten, Baenke mit Gelehrten, vier Siegel an der Wand.
# Aufruf: python3 innen/akademie.py
# Ausgabe: akademie.png, akademie_2x.png, akademie_kollision.png, akademie.json und akademie_daten.js

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

# Interaktionen: praesident (Aufnahme, markiert), archiv (Mappe mit allen Texten), sanduhr (neues Spiel, erst am Ende)
INTERAKTIONEN = [
    {"id": "praesident", "objekt": (15, 3, 24, 6), "flaeche": (18, 7, 21, 7), "markiert": True},
    {"id": "archiv", "objekt": (8, 4, 9, 5), "flaeche": (8, 6, 9, 6), "markiert": False},
    {"id": "sanduhr", "objekt": (28, 19, 29, 19), "flaeche": (28, 20, 29, 20), "markiert": False},
]
# Figuren (Fusspunkte in Kacheln): Praesident vor dem Tisch, Onkel John daneben
PRAESIDENT = {"x": 19.5, "y": 6}
LOCKE = {"x": 23.5, "y": 6}
# Vier Siegel an der Rueckwand (Mittelpunkte in Pixeln): Observatorium, Lesesaal, Salon, Druckerei
SIEGEL = [{"x": 13 * T + 8, "y": 22}, {"x": 16 * T + 8, "y": 22}, {"x": 23 * T + 8, "y": 22}, {"x": 26 * T + 8, "y": 22}]

objs = []

def block(x0, y0, w, h, fn):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            assert grid[y][x] == "#", ("belegt", x, y)
            grid[y][x] = "X"
    objs.append(((y0 + h) * T, fn))

def mk(f, *a):
    return lambda: f(*a)

# ---------------------------------------------------------------- Boden: Marmor im Schachbrett
def checker(x, y):
    sq = 16
    cx, cy = (x + 8) // sq, (y + 8) // sq
    hell = (cx + cy) % 2 == 0
    base = (230, 224, 210) if hell else (118, 114, 122)
    v = G.vnoise(x, y, 6, 23)
    if abs(v - 0.5) < 0.018:
        base = mul(base, 0.86 if hell else 1.3)
    c = jit(base, (h2(cx, cy, 24) - 0.5) * 8)
    if (x + 8) % sq == 0 or (y + 8) % sq == 0:
        c = mul(c, 0.9 if hell else 1.15)
    return c

def floor_pass():
    b = cv.b
    for y in range(PH):
        for x in range(PW):
            c = checker(x, y)
            i = (y * PW + x) * 3
            b[i] = c[0]; b[i + 1] = c[1]; b[i + 2] = c[2]

def pool(cx, cy, rx, ry, f):
    for py in range(int(cy - ry), int(cy + ry) + 1):
        for px in range(int(cx - rx), int(cx + rx) + 1):
            d = ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2
            if d < 1:
                cv.shade(px, py, 1 + (f - 1) * (1 - d) ** 1.5)

# ---------------------------------------------------------------- Waende: Ocker wie die Fassade, weisse Pilaster, Eichenvertaefelung
OCKER = (226, 196, 132)
EICHE = (112, 72, 42)

def gilt_frame(x, y, w, h, inner=None):
    cv.rect(x - 1, y - 1, w + 2, h + 2, (70, 48, 20))
    cv.rect(x, y, w, h, (214, 170, 72))
    cv.rect(x, y, w, 1, (250, 222, 130))
    cv.rect(x + 2, y + 2, w - 4, h - 4, (120, 86, 30))
    if inner:
        cv.rect(x + 3, y + 3, w - 6, h - 6, inner)

def portrait(x, y, coat, wig):
    gilt_frame(x, y, 16, 22, (40, 32, 30))
    cx = x + 8
    cv.rect(cx - 4, y + 14, 9, 5, coat)
    cv.rect(cx - 1, y + 13, 3, 2, (236, 232, 222))
    cv.ellipse(cx, y + 10, 2.5, 3, (226, 190, 160))
    cv.ellipse(cx, y + 8, 3.5, 2.5, wig)
    cv.rect(cx - 4, y + 9, 2, 6, wig)
    cv.rect(cx + 3, y + 9, 2, 6, wig)

def seal_medallion(cx, cy):
    """Leerer Siegelplatz aus Messing. Das Spiel laesst ihn aufleuchten, sobald das Siegel erworben ist."""
    for r, col in ((10, (70, 48, 20)), (9, (190, 150, 60)), (7, (120, 86, 30)), (6, (150, 40, 36))):
        cv.ellipse(cx, cy, r, r, col)
    cv.ellipse(cx - 2, cy - 2, 2, 2, (190, 70, 60))

def emblem(cx, cy):
    """Wappen der Akademie ohne Schrift: Schild mit drei Sternen und einem Buch, darueber Lorbeer."""
    for k in range(9):
        a = math.pi * (0.15 + 0.7 * k / 8)
        for sgn in (-1, 1):
            px, py = cx + sgn * math.cos(a) * 20, cy + 4 - math.sin(a) * 18
            cv.ellipse(px, py, 3, 2, (70, 120, 70))
    cv.rect(cx - 12, cy - 12, 24, 18, (40, 60, 110))
    for py in range(cy + 6, cy + 14):
        wdt = int(12 * (1 - (py - cy - 6) / 8))
        cv.rect(cx - wdt, py, 2 * wdt, 1, (40, 60, 110))
    cv.rect(cx - 13, cy - 13, 26, 2, (214, 170, 72))
    for sx in (cx - 6, cx, cx + 6):
        cv.set(sx, cy - 6, (250, 230, 140)); cv.set(sx - 1, cy - 6, (220, 190, 90)); cv.set(sx + 1, cy - 6, (220, 190, 90))
        cv.set(sx, cy - 7, (220, 190, 90)); cv.set(sx, cy - 5, (220, 190, 90))
    cv.rect(cx - 6, cy, 12, 7, (246, 238, 214))
    cv.rect(cx, cy, 1, 7, (170, 150, 120))

def back_wall():
    hh = 3 * T
    cv.rect(0, 0, PW, 6, O.CAP)
    cv.rect(0, 5, PW, 1, O.CAP_L)
    G.wall(0, 6, PW, hh - 6, OCKER, "plaster")
    for py in range(hh - 16, hh - 3):                   # Eichenvertaefelung
        cv.rect(0, py, PW, 1, mul(EICHE, 0.92 + 0.12 * ((py % 4) == 0)))
    cv.rect(0, hh - 17, PW, 2, (150, 104, 62))
    for px in range(0, PW, 32):                          # weisse Pilaster
        cv.rect(px + 2, 6, 6, hh - 23, (248, 240, 222))
        cv.rect(px + 7, 6, 1, hh - 23, (200, 184, 150))
        cv.rect(px + 1, 6, 8, 2, (252, 248, 236))
    fenster = [2 * T + 8, 6 * T + 8, 33 * T + 8, 37 * T + 4]
    for fx in fenster:
        G.window(fx, 10, 12, 22, "glass", arch=True)
    portrait(10 * T, 9, (60, 40, 70), (70, 50, 40))
    portrait(29 * T - 2, 9, (40, 50, 90), (236, 232, 222))
    # Mitte: Wappen zwischen den vier Siegeln, Baldachin in Gruen
    cx = 20 * T
    cv.rect(cx - 56, 6, 112, hh - 23, (60, 110, 90))
    for px in range(cx - 56, cx + 56, 8):
        cv.rect(px, 6, 1, hh - 23, (50, 94, 76))
    cv.rect(cx - 58, 6, 116, 3, (214, 170, 72))
    emblem(cx, 20)
    for s in SIEGEL:
        seal_medallion(s["x"], s["y"])
    cv.rect(0, hh - 3, PW, 3, (74, 46, 30))
    cv.rect(0, hh - 3, PW, 1, (110, 72, 44))
    cv.shade_rect(0, hh, PW, 4, 0.78)
    for fx in fenster:
        O.light_pool(fx, fx + 12, hh + 50, 50)

# ---------------------------------------------------------------- Podium, Tisch, Zepter
def dais():
    x0, y0, x1, y1 = 14 * T, 3 * T, 26 * T, 7 * T
    O.shadow_box(x0, y0, x1 - x0, y1 - y0)
    cv.rect(x0, y0, x1 - x0, y1 - y0, (96, 60, 36))
    for py in range(y0 + 1, y1 - 6):
        cv.rect(x0 + 1, py, x1 - x0 - 2, 1, (150, 98, 58) if (py - y0) % 5 else (120, 78, 46))
    cv.rect(x0, y1 - 6, x1 - x0, 6, (126, 82, 50))
    cv.rect(x0, y1 - 6, x1 - x0, 1, (176, 122, 76))
    cv.rect(x0, y1 - 1, x1 - x0, 1, (70, 44, 28))
    # Stufen vorn in der Mitte
    for k in range(2):
        cv.rect(18 * T - k * 4, y1 + k * 3, 4 * T + k * 8, 3, (140, 92, 56) if k == 0 else (120, 78, 46))
    # langer Tisch mit gruenem Tuch
    tx0, tx1, ty = 15 * T + 4, 25 * T - 4, 3 * T + 2
    O.shadow_box(tx0, ty, tx1 - tx0, 22)
    cv.rect(tx0, ty, tx1 - tx0, 22, (40, 84, 64))
    cv.rect(tx0, ty, tx1 - tx0, 2, (70, 120, 94))
    cv.rect(tx0, ty + 16, tx1 - tx0, 6, (30, 64, 48))
    for px in range(tx0 + 4, tx1 - 4, 6):
        cv.rect(px, ty + 21, 3, 2, (214, 170, 72))
    # Zeremonienzepter der Akademie
    cv.line(tx0 + 60, ty + 9, tx0 + 110, ty + 7, (214, 170, 72), 3)
    cv.ellipse(tx0 + 112, ty + 7, 5, 4, (230, 190, 80))
    cv.ellipse(tx0 + 112, ty + 6, 3, 2, (250, 226, 140))
    # Urkunde mit Siegel, Buecher, Tintenfass
    cv.rect(tx0 + 16, ty + 5, 18, 10, (246, 238, 214))
    cv.ellipse(tx0 + 25, ty + 12, 2.5, 2.5, (170, 30, 36))
    cv.rect(tx1 - 40, ty + 4, 12, 10, (122, 72, 42)); cv.rect(tx1 - 40, ty + 4, 12, 2, (150, 90, 52))
    cv.ellipse(tx1 - 18, ty + 9, 3, 3, (30, 30, 40))
    cv.line(tx1 - 18, ty + 8, tx1 - 12, ty + 1, (246, 246, 240), 2)
    # Stuhl des Praesidenten hinter dem Tisch
    cx = 20 * T
    cv.rect(cx - 8, ty - 10, 16, 12, (120, 30, 40))
    cv.rect(cx - 9, ty - 12, 18, 3, (214, 170, 72))

def archive_desk(tx, ty):
    """Pult mit dem grossen Mitgliederbuch: hier liegt Jonnys Mappe mit allen Texten."""
    x, y = tx * T, ty * T
    O.shadow_box(x + 2, y + 6, 2 * T - 4, 2 * T - 8)
    cv.rect(x + 12, y + 14, 8, 16, (70, 44, 28))
    cv.rect(x + 4, y + 28, 24, 3, (70, 44, 28))
    cv.rect(x, y, 2 * T, 16, (86, 54, 32))
    cv.rect(x + 1, y + 1, 2 * T - 2, 13, (126, 82, 48))
    cv.rect(x + 3, y + 2, 2 * T - 6, 10, (246, 238, 214))
    cv.rect(x + T - 1, y + 2, 2, 10, (170, 150, 120))
    for ly in range(y + 4, y + 11, 2):
        cv.rect(x + 5, ly, 8, 1, (150, 140, 120)); cv.rect(x + T + 3, ly, 8, 1, (150, 140, 120))
    cv.rect(x + 20, y - 2, 8, 6, (150, 40, 50))                    # Lesezeichen und Mappe
    cv.rect(x + 20, y - 2, 8, 1, (190, 70, 70))

def hourglass_table(tx, ty):
    """Kleiner Tisch mit einer Sanduhr: Wer sie umdreht, beginnt von vorn."""
    x, y = tx * T, ty * T
    O.shadow_box(x + 4, y + 4, 2 * T - 8, 10)
    cv.rect(x + 3, y + 2, 2 * T - 6, 10, (86, 54, 32))
    cv.rect(x + 4, y + 3, 2 * T - 8, 7, (126, 82, 48))
    cx = x + T
    cv.rect(cx - 6, y - 14, 12, 2, (120, 80, 50)); cv.rect(cx - 6, y + 2, 12, 2, (120, 80, 50))
    cv.rect(cx - 6, y - 12, 1, 14, (120, 80, 50)); cv.rect(cx + 5, y - 12, 1, 14, (120, 80, 50))
    for k in range(7):
        wdt = 4 - abs(k - 3) + (1 if k in (0, 6) else 0)
        cv.rect(cx - wdt, y - 12 + k * 2, 2 * wdt, 2, (200, 226, 240))
    cv.rect(cx - 3, y - 12, 6, 3, (230, 200, 130))
    cv.rect(cx - 3, y - 2, 6, 3, (230, 200, 130))
    cv.rect(cx, y - 8, 1, 6, (230, 200, 130))

def pew(tx, ty, tw, seed):
    """Bank mit Gelehrten, von hinten gesehen: Peruecken, Roecke, Schultern."""
    x, y, w = tx * T, ty * T, tw * T
    O.shadow_box(x + 2, y + 10, w - 4, 18)
    cv.rect(x + 2, y + 18, w - 4, 10, (96, 60, 36))
    cv.rect(x + 2, y + 18, w - 4, 2, (136, 92, 56))
    cv.rect(x + 2, y + 26, w - 4, 2, (70, 44, 28))
    rng = random.Random(seed)
    peruecken = [(236, 232, 222), (200, 196, 190), (90, 66, 48), (50, 40, 36), (160, 120, 80)]
    roecke = [(40, 50, 90), (90, 30, 40), (40, 70, 60), (60, 50, 44), (30, 30, 36), (110, 90, 60)]
    px = x + 8
    while px < x + w - 14:
        if rng.random() < 0.82:
            coat, wig = rng.choice(roecke), rng.choice(peruecken)
            cv.rect(px - 6, y + 10, 13, 10, mul(coat, 0.85))
            cv.rect(px - 5, y + 9, 11, 9, coat)
            cv.ellipse(px, y + 5, 5, 5, wig)
            cv.rect(px - 5, y + 5, 11, 6, wig)
            cv.set(px - 2, y + 2, mul(wig, 1.1))
            if rng.random() < 0.3:
                cv.rect(px - 1, y + 11, 3, 5, mul(wig, 0.8))       # Zopf
        px += 17 + rng.randint(0, 5)

def bust_on_pedestal(tx, ty):
    O.bust(tx, ty)

# ---------------------------------------------------------------- Einrichtung
block(14, 3, 12, 4, dais)
block(8, 4, 2, 2, mk(archive_desk, 8, 4))
for i, (ty_) in enumerate((9, 12, 15)):
    block(2, ty_, 12, 2, mk(pew, 2, ty_, 12, 10 + i))
    block(26, ty_, 12, 2, mk(pew, 26, ty_, 12, 20 + i))
block(28, 19, 2, 1, mk(hourglass_table, 28, 19))
block(12, 3, 1, 1, mk(O.candelabra, 12, 3))
block(27, 3, 1, 1, mk(O.candelabra, 27, 3))
block(14, 20, 1, 1, mk(bust_on_pedestal, 14, 20))
block(25, 20, 1, 1, mk(bust_on_pedestal, 25, 20))
block(1, 3, 1, 1, mk(O.plant, 1, 3))
block(38, 3, 1, 1, mk(O.plant, 38, 3))
block(1, 20, 1, 1, mk(O.plant, 1, 20))
block(38, 20, 1, 1, mk(O.plant, 38, 20))

for ia in INTERAKTIONEN:
    x0, y0, x1, y1 = ia["flaeche"]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            assert grid[y][x] == "#", ("Interaktionsflaeche belegt", ia["id"], x, y)
    fill(x0, y0, x1, y1, "I")


def render():
    floor_pass()
    O.runner(18 * T, 8 * T, 4 * T, 14 * T, (150, 40, 50))
    back_wall()
    O.side_walls()
    O.front_wall()
    pool(20 * T, 12 * T, 120, 70, 1.14)
    for ia in INTERAKTIONEN:
        if ia["markiert"]:
            O.floor_glow(ia["flaeche"])
    for _, f in sorted(objs, key=lambda o: o[0]):
        f()


COLL = {"#": (40, 200, 80), "X": (220, 40, 40), "A": (230, 40, 220), "S": (40, 210, 230), "I": (250, 150, 30)}

def export():
    cv.save(os.path.join(HERE, "akademie.png"))
    cv.save(os.path.join(HERE, "akademie_2x.png"), 2)
    ov = G.Canvas(PW, PH)
    ov.b[:] = cv.b
    for ty in range(H):
        for tx in range(W):
            c = COLL[grid[ty][tx]]
            for py in range(ty * T, ty * T + T):
                for px in range(tx * T, tx * T + T):
                    edge = px % T == 0 or py % T == 0
                    ov.set(px, py, lerp(ov.get(px, py), c, 0.8 if edge else 0.5))
    ov.save(os.path.join(HERE, "akademie_kollision.png"), 2)
    data = {
        "name": "akademie",
        "kachelgroesse": T, "breite": W, "hoehe": H,
        "legende": {"#": "Boden, begehbar", "X": "Wand oder Moebel", "A": "Ausgang (Tuer nach draussen)",
                    "S": "Eintrittsstelle, begehbar", "I": "Interaktionsflaeche vor einem Objekt, begehbar"},
        "eintritt": {"x": 19, "y": 20, "blick": "up"},
        "ausgang": [{"x": x, "y": 22} for x in range(18, 22)],
        "interaktionen": [{"id": ia["id"], "markiert": ia["markiert"],
                           "flaeche": dict(zip(("x0", "y0", "x1", "y1"), ia["flaeche"])),
                           "objekt": dict(zip(("x0", "y0", "x1", "y1"), ia["objekt"]))}
                          for ia in INTERAKTIONEN],
        "praesident": PRAESIDENT, "locke": LOCKE, "siegel": SIEGEL,
        "raster": ["".join(r) for r in grid],
    }
    with open(os.path.join(HERE, "akademie.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "akademie_daten.js"), "w", encoding="utf-8") as f:
        f.write("window.INNEN = window.INNEN || {};\nwindow.INNEN.akademie = " + json.dumps(data, ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    render()
    export()
    print("Fertig:", PW, "x", PH)
