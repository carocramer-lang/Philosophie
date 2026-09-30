#!/usr/bin/env python3
# Innenraum Buchdruckerei: 40 x 24 Kacheln a 16 px, Topdown, gleiche Bausteine wie die anderen Raeume.
# Aufruf: python3 innen/druckerei.py
# Ausgabe: druckerei.png, druckerei_2x.png, druckerei_kollision.png, druckerei.json, druckerei_daten.js
#          druckerei_presse.png: Sprite-Blatt der Druckerpresse (16 Bilder a 128 x 128, transparent),
#          das Spiel spielt es ab, damit sich Karren, Bengel, Tiegel und Deckel wirklich bewegen.

import json, math, os, random, struct, sys, zlib

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

# Interaktionen: setzkasten (Auftrag, markiert), setzpult (schreiben), presse (Druckermeister), tafel (Infotafel, freiwillig)
INTERAKTIONEN = [
    {"id": "setzkasten", "objekt": (3, 3, 6, 4), "flaeche": (3, 5, 6, 6), "markiert": True},
    {"id": "setzpult", "objekt": (3, 11, 6, 12), "flaeche": (3, 13, 6, 13), "markiert": False},
    {"id": "presse", "objekt": (17, 3, 22, 8), "flaeche": (18, 9, 21, 9), "markiert": False},
    {"id": "tafel", "objekt": (29, 15, 33, 16), "flaeche": (29, 17, 33, 17), "markiert": False},
]
# Druckerpresse als Sprite: linke obere Ecke in Pixeln, 128 x 128 je Bild
PRESSE = {"x": 16 * T, "y": 16, "w": 128, "h": 128, "bilder": 16}
# Fusspunkt des Druckermeisters am Bengel (Kachelkoordinaten)
MEISTER = {"x": 24.3, "y": 4}

objs = []

def block(x0, y0, w, h, fn):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            assert grid[y][x] == "#", ("belegt", x, y)
            grid[y][x] = "X"
    objs.append(((y0 + h) * T, fn))

def mk(f, *a):
    return lambda: f(*a)

# ---------------------------------------------------------------- Boden: grobe Dielen, Steinplatten am Ofen
def planks(x, y):
    row = x // 20                       # Dielen laufen von vorn nach hinten
    off = int(h2(row, 0, 51) * 60)
    seg = (y + off) // 70
    base = [(128, 92, 60), (118, 84, 54), (136, 98, 64), (122, 88, 58)][int(h2(row, seg, 52) * 4)]
    c = jit(base, (h2(x, y // 3, 53) - 0.5) * 9)
    lx = x % 20
    if lx == 19:
        return mul(base, 0.62)
    if lx == 0:
        c = mul(c, 1.07)
    if (y + off) % 70 == 0:
        return mul(base, 0.7)
    if lx in (5, 14) and (y + off) % 70 in (6, 64):
        return (70, 54, 40)             # Naegel
    return c

def slabs(x, y):
    sx, sy = x // 22, y // 18
    base = [(150, 142, 132), (140, 132, 124), (158, 150, 140)][int(h2(sx, sy, 54) * 3)]
    c = jit(base, (h2(x, y, 55) - 0.5) * 8)
    if x % 22 == 0 or y % 18 == 0:
        return mul(base, 0.72)
    return c

def floor_pass():
    b = cv.b
    for y in range(PH):
        for x in range(PW):
            c = slabs(x, y) if (x >= 31 * T and y < 8 * T) else planks(x, y)
            i = (y * PW + x) * 3
            b[i] = c[0]; b[i + 1] = c[1]; b[i + 2] = c[2]
    # Druckerschwaerze: Flecken rund um Presse und Setzpult
    rng = random.Random(7)
    for _ in range(40):
        cx = rng.choice([rng.randint(15 * T, 25 * T), rng.randint(2 * T, 8 * T)])
        cy = rng.randint(4 * T, 12 * T)
        r = rng.uniform(1.5, 4.5)
        cv.shade_ellipse(cx, cy, r, r * 0.6, 0.45)

def pool(cx, cy, rx, ry, f):
    for py in range(int(cy - ry), int(cy + ry) + 1):
        for px in range(int(cx - rx), int(cx + rx) + 1):
            d = ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2
            if d < 1:
                cv.shade(px, py, 1 + (f - 1) * (1 - d) ** 1.5)

# ---------------------------------------------------------------- Waende: Fachwerk wie an der Fassade
PUTZ = (234, 222, 196)
BALKEN = (94, 58, 38)

def back_wall():
    hh = 3 * T
    cv.rect(0, 0, PW, 6, O.CAP)
    cv.rect(0, 5, PW, 1, O.CAP_L)
    G.wall(0, 6, PW, hh - 6, PUTZ, "plaster")
    for bx in range(0, PW, 44):                       # Staender
        cv.rect(bx, 6, 5, hh - 8, BALKEN)
        cv.rect(bx + 4, 6, 1, hh - 8, mul(BALKEN, 0.7))
    cv.rect(0, 6, PW, 4, BALKEN)                      # Rahm
    cv.rect(0, 26, PW, 3, BALKEN)                     # Riegel
    for i, bx in enumerate(range(0, PW - 44, 44)):    # Streben im unteren Feld
        if i % 3 == 1:
            cv.line(bx + 5, 44, bx + 43, 29, BALKEN, 3)
    # Fenster: links der Blick auf das Muehlrad, sonst Butzenscheiben
    wheel_window(2 * T + 2, 11)
    for fx in (9 * T + 8, 28 * T + 14, 35 * T + 10):
        G.window(fx, 11, 14, 14, "lit", frame=(110, 70, 44))
    # Leinen mit trocknenden Boegen quer ueber die Wand
    for y0, x0, x1 in ((30, 7 * T, 15 * T), (30, 24 * T, 31 * T), (32, 36 * T, 39 * T)):
        cv.line(x0, y0, x1, y0 + 2, (70, 60, 50))
        for k, sx in enumerate(range(x0 + 4, x1 - 8, 14)):
            sy = y0 + int((sx - x0) / (x1 - x0) * 2)
            cv.rect(sx, sy + 1, 10, 13, (244, 238, 222) if k % 3 else (236, 228, 206))
            for ly in range(sy + 3, sy + 12, 2):
                cv.rect(sx + 2, ly, 6, 1, (120, 112, 104))
            cv.rect(sx + 4, sy, 2, 2, (150, 110, 60))  # Klammer
    # Regalbrett mit Farbtoepfen
    cv.rect(18 * T + 4, 20, 4 * T - 8, 3, (110, 70, 44))
    for k, col in enumerate(((30, 30, 34), (150, 40, 36), (30, 30, 34), (40, 60, 120))):
        px = 18 * T + 10 + k * 14
        cv.rect(px, 14, 8, 6, (90, 84, 78))
        cv.rect(px + 1, 14, 6, 2, col)
    cv.rect(0, hh - 3, PW, 3, (74, 46, 30))
    cv.rect(0, hh - 3, PW, 1, (110, 72, 44))
    cv.shade_rect(0, hh, PW, 4, 0.78)
    for fx in (2 * T + 2, 9 * T + 8, 28 * T + 14, 35 * T + 10):
        O.light_pool(fx, fx + 14, hh + 40, 40)

def wheel_window(x, y):
    """Grosses Fenster: draussen dreht sich das Muehlrad im Bach."""
    w, h = 40, 26
    cv.rect(x - 3, y - 3, w + 6, h + 6, DARK)
    cv.rect(x - 2, y - 2, w + 4, h + 4, (110, 70, 44))
    for py in range(y, y + h):
        cv.rect(x, py, w, 1, lerp((170, 210, 236), (120, 170, 206), (py - y) / h))
    cx, cy = x + 22, y + 22
    for r, col in ((20, (70, 44, 28)), (18, (120, 80, 50))):
        for k in range(120):
            a = k / 120 * math.pi * 2
            px, py = cx + math.cos(a) * r, cy + math.sin(a) * r
            if y <= py < y + h and x <= px < x + w:
                cv.set(px, py, col)
    for k in range(8):
        a = k * math.pi / 4
        for t in range(0, 19):
            px, py = cx + math.cos(a) * t, cy + math.sin(a) * t
            if y <= py < y + h and x <= px < x + w:
                cv.set(px, py, (100, 64, 40))
    for px in range(x, x + w):
        for py in range(y + h - 4, y + h):
            cv.set(px, py, (90, 150, 200) if (px + py) % 5 else (220, 240, 250))
    cv.rect(x + w // 2, y, 2, h, (110, 70, 44))
    cv.rect(x, y + h // 2, w, 1, (110, 70, 44))
    cv.rect(x - 4, y + h + 3, w + 8, 2, (130, 86, 54))

# ---------------------------------------------------------------- Druckerpresse (Sprite-Blatt mit Transparenz)
class Rgba:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.b = bytearray(w * h * 4)
    def set(s, x, y, c, a=255):
        x, y = int(x), int(y)
        if 0 <= x < s.w and 0 <= y < s.h:
            i = (y * s.w + x) * 4
            s.b[i:i + 4] = bytes((c[0], c[1], c[2], a))
    def rect(s, x, y, w, h, c):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                s.set(xx, yy, c)
    def line(s, x0, y0, x1, y1, c, t=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for k in range(n + 1):
            px, py = x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n
            s.rect(px - t // 2, py - t // 2, t, t, c)
    def ellipse(s, cx, cy, rx, ry, c):
        for yy in range(int(cy - ry), int(cy + ry) + 1):
            for xx in range(int(cx - rx), int(cx + rx) + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1:
                    s.set(xx, yy, c)
    def blit(s, o, ox):
        for y in range(o.h):
            for x in range(o.w):
                i = (y * o.w + x) * 4
                if o.b[i + 3]:
                    j = (y * s.w + x + ox) * 4
                    s.b[j:j + 4] = o.b[i:i + 4]
    def save(s, path):
        raw = bytearray()
        for y in range(s.h):
            raw += b"\x00" + s.b[y * s.w * 4:(y + 1) * s.w * 4]
        def chunk(t, d):
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
        data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", s.w, s.h, 8, 6, 0, 0, 0))
        data += chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
        with open(path, "wb") as f:
            f.write(data)

HOLZ, HOLZ_L, HOLZ_D = (122, 78, 46), (156, 104, 62), (78, 48, 30)
EISEN, EISEN_L = (58, 56, 60), (104, 102, 108)
KONTUR = (28, 22, 20)

def press_frame(k, d, a, t, druck):
    """Eine Ansicht der Presse. k: Karren ausgefahren 0..1, d: Tiegel gesenkt 0..1,
    a: Bengel gezogen 0..1, t: Deckel (Rahmen mit Bogen) aufgeklappt 0..1, druck: Bogen bedruckt."""
    s = Rgba(128, 128)
    cx = 64
    # Schienenbahn (Rippen) mit Vorderbein, laeuft nach vorn zum Betrachter
    s.rect(38, 72, 4, 52, HOLZ_D); s.rect(86, 72, 4, 52, HOLZ_D)
    s.rect(37, 72, 2, 52, KONTUR); s.rect(89, 72, 2, 52, KONTUR)
    for yy in range(76, 124, 8):
        s.rect(42, yy, 44, 2, mul(HOLZ_D, 0.9))
    s.rect(40, 118, 48, 6, HOLZ); s.rect(40, 123, 48, 2, KONTUR)
    # Karren mit Form (gesetzte Lettern) faehrt auf den Schienen
    ky = 70 + int(k * 30)
    s.rect(40, ky, 48, 20, KONTUR)
    s.rect(41, ky + 1, 46, 18, HOLZ_L)
    s.rect(46, ky + 4, 36, 12, (54, 50, 52))                   # Form: Bleisatz, eingefaerbt
    for ly in range(ky + 5, ky + 15, 2):
        s.rect(48, ly, 32, 1, (84, 80, 84))
    s.rect(84, ky + 6, 5, 6, (140, 140, 146))                  # Kurbel
    # Deckel (Tympan mit Bogen) am hinteren Rand des Karrens, klappt nach oben
    th = int(20 - t * 36)                                      # 20: zu (liegt auf der Form), -16: offen, steht hoch
    if th >= 0:
        s.rect(42, ky + 1, 44, max(1, th), (236, 230, 214))
        s.rect(42, ky + 1, 44, 1, KONTUR)
    else:
        top = ky + th
        s.rect(42, top, 44, -th + 1, KONTUR)
        s.rect(43, top + 1, 42, -th - 1, (244, 238, 222))
        if druck and -th > 8:
            for ly in range(top + 3, ky - 1, 2):
                s.rect(47, ly, 34, 1, (70, 66, 64))
    # Wangen (Seitenpfosten) und Kopf
    for wx in (26, 90):
        s.rect(wx, 6, 12, 112, KONTUR)
        s.rect(wx + 1, 6, 10, 112, HOLZ)
        s.rect(wx + 1, 6, 3, 112, HOLZ_L)
        s.rect(wx + 8, 6, 3, 112, HOLZ_D)
        s.rect(wx - 3, 114, 18, 8, KONTUR); s.rect(wx - 2, 114, 16, 6, HOLZ_D)   # Fuesse
    s.rect(24, 2, 80, 8, KONTUR); s.rect(25, 3, 78, 6, HOLZ_L)                   # Krone
    s.rect(24, 14, 80, 14, KONTUR); s.rect(25, 15, 78, 12, HOLZ)                 # Kopf
    s.rect(25, 15, 78, 2, HOLZ_L)
    s.rect(38, 50, 52, 7, KONTUR); s.rect(38, 51, 52, 5, HOLZ)                   # Buechse (Fuehrung)
    # Spindel: Gewinde dreht sich mit dem Bengel
    drop = int(d * 8)
    for yy in range(28, 58 + drop):
        s.rect(cx - 3, yy, 7, 1, EISEN if (yy + int(a * 6)) % 4 < 2 else EISEN_L)
    s.rect(cx - 4, 28, 1, 30 + drop, KONTUR); s.rect(cx + 4, 28, 1, 30 + drop, KONTUR)
    # Tiegel (Druckplatte) haengt an der Spindel und senkt sich auf den Karren
    py = 58 + drop
    s.rect(42, py, 44, 7, KONTUR); s.rect(43, py + 1, 42, 5, EISEN_L)
    s.rect(43, py + 1, 42, 1, (150, 150, 156))
    # Bengel: Hebel an der Spindel. In Ruhe zeigt er nach hinten, beim Ziehen schwingt er zum Drucker nach rechts vorn
    ang = -0.9 + a * 1.05
    ex, ey = cx + math.cos(ang) * 58, 40 + math.sin(ang) * 24
    s.line(cx, 40, ex, ey, KONTUR, 4)
    s.line(cx, 40, ex, ey, (80, 78, 84), 2)
    s.ellipse(ex, ey, 3, 3, KONTUR); s.ellipse(ex, ey, 2, 2, HOLZ_L)            # Griff
    s.ellipse(cx, 40, 4, 4, KONTUR); s.ellipse(cx, 40, 3, 3, EISEN_L)
    # Farbballen auf der rechten Wange
    for bx in (95, 103):
        s.rect(bx - 1, 64, 2, 8, HOLZ_D)
        s.ellipse(bx, 62, 4, 3, KONTUR); s.ellipse(bx, 62, 3, 2, (40, 36, 36))
    return s

# Ablauf eines Drucks in 16 Bildern: Deckel zu, einfahren, ziehen, loslassen, ausfahren, Deckel auf
ABLAUF = [(1, 0, 0, 1), (1, 0, 0, 0.5), (1, 0, 0, 0), (0.66, 0, 0, 0), (0.33, 0, 0, 0), (0, 0, 0, 0),
          (0, 0.4, 0.4, 0), (0, 1, 1, 0), (0, 1, 1, 0), (0, 0.4, 0.4, 0), (0, 0, 0, 0),
          (0.33, 0, 0, 0), (0.66, 0, 0, 0), (1, 0, 0, 0), (1, 0, 0, 0.5), (1, 0, 0, 1)]

def export_press():
    blatt = Rgba(128 * len(ABLAUF), 128)
    for i, (k, d, a, t) in enumerate(ABLAUF):
        blatt.blit(press_frame(k, d, a, t, druck=i >= 10), i * 128)
    blatt.save(os.path.join(HERE, "druckerei_presse.png"))

def press_base():
    """Im Raumbild nur Schatten und Standplatz der Presse, die Presse selbst zeichnet das Spiel."""
    x, y = PRESSE["x"], PRESSE["y"]
    cv.shade_rect(x + 26, y + 118, 80, 8, 0.6)
    cv.shade_rect(x + 40, y + 124, 52, 4, 0.7)
    cv.shade_ellipse(x + 64, y + 128, 50, 6, 0.8)

# ---------------------------------------------------------------- Moebel
def type_case(tx, ty):
    """Setzregal mit schraeg gestellten Setzkaesten: hier liegt der Auftrag."""
    x, y, w = tx * T + 2, ty * T - 22, 4 * T - 4
    O.shadow_box(x, y + 20, w, 2 * T + 2)
    cv.rect(x, y, w, 2 * T + 22, KONTUR)
    cv.rect(x + 1, y + 1, w - 2, 2 * T + 20, HOLZ_D)
    for r in range(3):                                   # Setzkaesten mit vielen Faechern
        ry = y + 3 + r * 11
        cv.rect(x + 3, ry, w - 6, 9, HOLZ)
        for fx in range(x + 4, x + w - 4, 4):
            cv.rect(fx, ry + 1, 3, 3, (60, 58, 62))
            cv.rect(fx, ry + 5, 3, 3, (60, 58, 62))
            if h2(fx, ry, 61) < 0.6:
                cv.set(fx + 1, ry + 2, (150, 150, 156))
                cv.set(fx + 1, ry + 6, (150, 150, 156))
    # Schraege Arbeitsflaeche mit Oberkasten und Unterkasten
    ay = y + 36
    cv.rect(x - 2, ay, w + 4, 14, KONTUR)
    cv.rect(x - 1, ay + 1, w + 2, 12, HOLZ_L)
    for fx in range(x + 1, x + w - 2, 5):
        cv.rect(fx, ay + 2, 4, 4, (70, 66, 70))
        cv.rect(fx, ay + 7, 4, 5, (70, 66, 70))
    cv.rect(x + 8, ay + 3, 16, 7, (236, 226, 196))       # Auftrag der Akademie
    cv.ellipse(x + 16, ay + 7, 2, 2, (170, 30, 36))
    cv.rect(x + w - 16, ay + 3, 10, 3, (150, 150, 160))  # Winkelhaken
    cv.rect(x + w - 16, ay + 3, 1, 5, (150, 150, 160))

def composing_desk(tx, ty):
    """Setzpult: Pult mit Papier, Feder und Tintenfass, daneben ein Winkelhaken mit Lettern."""
    x, y, w = tx * T + 2, ty * T, 4 * T - 4
    O.shadow_box(x, y + 2, w, 2 * T - 2)
    cv.rect(x, y, w, 2 * T - 2, KONTUR)
    cv.rect(x + 1, y + 1, w - 2, 2 * T - 4, HOLZ)
    cv.rect(x + 1, y + 1, w - 2, 2, HOLZ_L)
    cv.rect(x + 4, y + 5, 20, 16, (246, 238, 214))
    for ly in range(y + 8, y + 19, 2):
        cv.rect(x + 7, ly, 13, 1, (170, 156, 130))
    cv.ellipse(x + 32, y + 12, 3, 3, (30, 30, 40))
    cv.line(x + 32, y + 11, x + 38, y + 2, (246, 246, 240), 2)
    cv.rect(x + 42, y + 8, 14, 5, (150, 150, 160))
    for fx in range(x + 43, x + 55, 2):
        cv.rect(fx, y + 9, 1, 3, (80, 80, 86))
    cv.rect(x + 6, y + 2 * T - 2, 4, 6, HOLZ_D)
    cv.rect(x + w - 10, y + 2 * T - 2, 4, 6, HOLZ_D)

def furnace(tx, ty):
    """Ofen zum Giessen der Lettern mit Schmelztiegel und Glut."""
    x, y, w, h = tx * T + 2, ty * T - 18, 3 * T - 4, 2 * T + 16
    O.shadow_box(x, y + 16, w, h - 16)
    cv.rect(x, y, w, h, KONTUR)
    G.wall(x + 1, y + 1, w - 2, h - 2, (156, 88, 64), "brick")
    cv.rect(x + 10, y + h - 18, w - 20, 12, (40, 20, 16))
    for k in range(w - 22):
        hh = 3 + int(h2(k, 3, 62) * 6)
        for j in range(hh):
            cv.set(x + 11 + k, y + h - 7 - j, lerp((255, 220, 120), (200, 60, 30), j / hh))
    cv.ellipse(x + w / 2, y + 8, 9, 4, (70, 70, 76))       # Schmelztiegel mit Blei
    cv.ellipse(x + w / 2, y + 8, 7, 3, (190, 196, 206))
    cv.line(x + w / 2 + 6, y + 6, x + w + 6, y - 4, (90, 90, 96), 2)   # Kelle
    O.glow(x + w / 2, y + h - 10, 34, 1.35)

def paper_bales(tx, ty):
    x, y = tx * T + 1, ty * T - 6
    for k in range(4):
        by = y + k * 8
        O.shadow_box(x, by, 2 * T - 2, 8)
        cv.rect(x, by, 2 * T - 2, 8, KONTUR)
        cv.rect(x + 1, by + 1, 2 * T - 4, 6, (240, 232, 212) if k % 2 else (232, 222, 198))
        cv.rect(x + 12, by, 2, 8, (150, 110, 60))

def drying_rack(tx, ty):
    """Trockengestell mit frisch gedruckten Boegen."""
    x, y, w = tx * T, ty * T - 14, 5 * T
    O.shadow_box(x + 2, y + 26, w - 4, 8)
    for px in (x + 2, x + w - 6):
        cv.rect(px, y, 4, 42, KONTUR); cv.rect(px + 1, y, 2, 42, HOLZ)
    for ly in (y + 4, y + 18):
        cv.rect(x + 2, ly, w - 4, 2, HOLZ_D)
        for sx in range(x + 8, x + w - 12, 12):
            cv.rect(sx, ly + 2, 10, 11, (246, 240, 224))
            for ty2 in range(ly + 4, ly + 12, 2):
                cv.rect(sx + 2, ty2, 6, 1, (110, 104, 98))

def book_table(tx, ty):
    """Tisch mit gebundenen Exemplaren von Lockes Essay und einer Schautafel mit dem Titelblatt."""
    x, y, w = tx * T, ty * T, 5 * T
    O.shadow_box(x + 2, y + 2, w - 4, 2 * T - 4)
    cv.rect(x + 2, y + 2, w - 4, 2 * T - 6, KONTUR)
    cv.rect(x + 3, y + 3, w - 6, 2 * T - 8, HOLZ)
    cv.rect(x + 3, y + 3, w - 6, 2, HOLZ_L)
    for k, (bx, n) in enumerate(((x + 8, 4), (x + 24, 3), (x + 40, 5))):   # Buecherstapel
        for j in range(n):
            by = y + 20 - j * 4
            cv.rect(bx, by, 13, 4, KONTUR)
            cv.rect(bx + 1, by + 1, 11, 2, (122, 72, 42) if (j + k) % 2 else (140, 84, 48))
            cv.rect(bx + 1, by + 3, 11, 1, (236, 226, 200))
    cv.rect(x + 8, y + 3, 14, 3, (236, 226, 200))                          # aufgeschlagenes Exemplar
    # Schautafel auf einer Staffelei: Titelblatt des Essay (1690), angeheftet
    ex = x + w - 18
    cv.line(ex, y - 18, ex - 6, y + 2 * T - 4, HOLZ_D, 2)
    cv.line(ex + 12, y - 18, ex + 18, y + 2 * T - 4, HOLZ_D, 2)
    cv.rect(ex - 5, y - 22, 22, 28, KONTUR)
    cv.rect(ex - 4, y - 21, 20, 26, (130, 86, 54))
    cv.rect(ex - 1, y - 18, 14, 20, (246, 240, 222))
    cv.rect(ex + 2, y - 15, 8, 2, (60, 56, 52))                             # Titelzeilen
    cv.rect(ex + 1, y - 11, 10, 1, (90, 86, 80))
    cv.rect(ex + 3, y - 8, 6, 1, (90, 86, 80))
    cv.rect(ex + 5, y - 5, 2, 2, (150, 40, 36))                             # Druckerzeichen
    cv.rect(ex + 1, y - 1, 10, 1, (90, 86, 80))
    cv.rect(ex + 5, y - 20, 2, 2, (200, 60, 50))                            # Reisszwecke

def barrel(tx, ty):
    cx, b = tx * T + 8, ty * T + 14
    cv.shade_ellipse(cx + 3, b, 8, 3, 0.62)
    cv.rect(cx - 6, b - 16, 13, 16, KONTUR)
    cv.rect(cx - 5, b - 15, 11, 14, HOLZ)
    for yy in (b - 13, b - 5):
        cv.rect(cx - 5, yy, 11, 2, (90, 90, 96))
    cv.ellipse(cx, b - 16, 6, 2.5, HOLZ_L)

def crate(tx, ty):
    x, y = tx * T + 1, ty * T - 2
    O.shadow_box(x, y, 14, 16)
    cv.rect(x, y, 14, 16, KONTUR)
    cv.rect(x + 1, y + 1, 12, 14, HOLZ_L)
    cv.line(x + 1, y + 1, x + 13, y + 15, HOLZ_D)
    cv.rect(x + 1, y + 7, 12, 1, HOLZ_D)

def post(tx, ty):
    """Tragender Holzpfosten mit Laterne."""
    cx, b = tx * T + 8, ty * T + 14
    cv.shade_ellipse(cx + 4, b, 7, 3, 0.6)
    cv.rect(cx - 4, b - 44, 8, 44, KONTUR)
    cv.rect(cx - 3, b - 44, 6, 44, HOLZ)
    cv.rect(cx - 3, b - 44, 2, 44, HOLZ_L)
    cv.rect(cx + 3, b - 30, 5, 1, (60, 54, 54))
    cv.rect(cx + 5, b - 29, 5, 7, (60, 54, 54))
    cv.rect(cx + 6, b - 28, 3, 5, (255, 214, 120))
    O.glow(cx + 7, b - 26, 22, 1.25)

def bench(tx, ty, tw):
    """Werkbank des Buchbinders mit kleiner Stockpresse."""
    x, y, w = tx * T, ty * T, tw * T
    O.shadow_box(x + 2, y + 2, w - 4, 2 * T - 6)
    cv.rect(x + 2, y + 2, w - 4, 2 * T - 8, KONTUR)
    cv.rect(x + 3, y + 3, w - 6, 2 * T - 10, HOLZ)
    cv.rect(x + 3, y + 3, w - 6, 2, HOLZ_L)
    cv.rect(x + 8, y + 6, 16, 14, HOLZ_D)                       # Stockpresse
    cv.rect(x + 15, y, 2, 8, (90, 90, 96))
    cv.rect(x + 10, y - 1, 12, 2, (90, 90, 96))
    cv.rect(x + 10, y + 10, 12, 6, (236, 226, 200))
    cv.rect(x + w - 26, y + 8, 18, 10, (140, 84, 48))           # Leder
    cv.rect(x + w - 24, y + 10, 2, 6, (214, 170, 72))

# ---------------------------------------------------------------- Einrichtung
block(3, 3, 4, 2, mk(type_case, 3, 3))
block(1, 3, 1, 2, mk(paper_bales, 1, 3))
block(8, 3, 2, 2, mk(paper_bales, 8, 3))
block(3, 11, 4, 2, mk(composing_desk, 3, 11))
block(1, 17, 1, 1, mk(barrel, 1, 17))
block(1, 20, 1, 1, mk(barrel, 1, 20))
block(3, 17, 5, 2, mk(bench, 3, 17, 5))
block(12, 8, 1, 1, mk(post, 12, 8))
block(27, 8, 1, 1, mk(post, 27, 8))
block(12, 15, 1, 1, mk(post, 12, 15))
block(27, 15, 1, 1, mk(post, 27, 15))
# Mitte: Druckerpresse (vom Spiel gezeichnet) und Standplatz des Druckermeisters am Bengel
block(17, 3, 6, 6, press_base)
block(24, 3, 1, 2, lambda: None)
block(15, 3, 1, 1, mk(O.candelabra, 15, 3))
# Rechts: Ofen, Papier, Trockengestell, Tisch mit Lockes Essay und Schautafel
block(33, 3, 3, 2, mk(furnace, 33, 3))
block(29, 3, 2, 2, mk(paper_bales, 29, 3))
block(37, 3, 2, 2, mk(paper_bales, 37, 3))
block(32, 9, 5, 2, mk(drying_rack, 32, 9))
block(29, 15, 5, 2, mk(book_table, 29, 15))
block(37, 17, 1, 1, mk(crate, 37, 17))
block(37, 20, 1, 1, mk(crate, 37, 20))
block(35, 20, 1, 1, mk(barrel, 35, 20))

for ia in INTERAKTIONEN:
    x0, y0, x1, y1 = ia["flaeche"]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            assert grid[y][x] == "#", ("Interaktionsflaeche belegt", ia["id"], x, y)
    fill(x0, y0, x1, y1, "I")


def render():
    floor_pass()
    O.runner(18 * T, 10 * T, 4 * T, 12 * T, (60, 90, 70))
    back_wall()
    O.side_walls()
    O.front_wall()
    pool(20 * T, 9 * T, 90, 50, 1.12)
    for ia in INTERAKTIONEN:
        if ia["markiert"]:
            O.floor_glow(ia["flaeche"])
    for _, f in sorted(objs, key=lambda o: o[0]):
        f()
    for ia in INTERAKTIONEN:
        if ia["markiert"]:
            x0, y0, x1, y1 = ia["objekt"]
            O.marker_candle((x1 + 1) * T - 6, y0 * T - 24)


COLL = {"#": (40, 200, 80), "X": (220, 40, 40), "A": (230, 40, 220), "S": (40, 210, 230), "I": (250, 150, 30)}

def export():
    cv.save(os.path.join(HERE, "druckerei.png"))
    cv.save(os.path.join(HERE, "druckerei_2x.png"), 2)
    ov = G.Canvas(PW, PH)
    ov.b[:] = cv.b
    for ty in range(H):
        for tx in range(W):
            c = COLL[grid[ty][tx]]
            for py in range(ty * T, ty * T + T):
                for px in range(tx * T, tx * T + T):
                    edge = px % T == 0 or py % T == 0
                    ov.set(px, py, lerp(ov.get(px, py), c, 0.8 if edge else 0.5))
    ov.save(os.path.join(HERE, "druckerei_kollision.png"), 2)
    export_press()
    data = {
        "name": "druckerei",
        "kachelgroesse": T, "breite": W, "hoehe": H,
        "legende": {"#": "Boden, begehbar", "X": "Wand oder Moebel", "A": "Ausgang (Tuer nach draussen)",
                    "S": "Eintrittsstelle, begehbar", "I": "Interaktionsflaeche vor einem Objekt, begehbar"},
        "eintritt": {"x": 19, "y": 20, "blick": "up"},
        "ausgang": [{"x": x, "y": 22} for x in range(18, 22)],
        "interaktionen": [{"id": ia["id"], "markiert": ia["markiert"],
                           "flaeche": dict(zip(("x0", "y0", "x1", "y1"), ia["flaeche"])),
                           "objekt": dict(zip(("x0", "y0", "x1", "y1"), ia["objekt"]))}
                          for ia in INTERAKTIONEN],
        "presse": PRESSE,
        "meister": MEISTER,
        "raster": ["".join(r) for r in grid],
    }
    with open(os.path.join(HERE, "druckerei.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "druckerei_daten.js"), "w", encoding="utf-8") as f:
        f.write("window.INNEN = window.INNEN || {};\nwindow.INNEN.druckerei = " + json.dumps(data, ensure_ascii=False) + ";\n")


if __name__ == "__main__":
    render()
    export()
    print("Fertig:", PW, "x", PH)
