#!/usr/bin/env python3
# Bibliothekar (Aufklaerung, um 1700) als Pixel-Art-Sprite, Dreiviertelansicht nach links.
# Aufruf: python3 figuren/bibliothekar.py
# Ausgabe: bibliothekar_32x48.png (transparent), bibliothekar_16x24.png (transparent, Spielgroesse),
#          bibliothekar_weiss.png (32x48 achtfach vergroessert auf weissem Grund)

import os, struct, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 32, 48

PAL = {
    "K": (28, 22, 36),                                                  # Kontur
    "W": (240, 237, 230), "w": (204, 200, 208), "g": (160, 154, 168),   # Perueckenpuder
    "R": (34, 32, 42),                                                  # Zopfschleife
    "S": (238, 196, 162), "s": (207, 154, 122), "r": (217, 138, 122),   # Haut, Schatten, Wange
    "E": (42, 34, 48), "b": (142, 138, 148), "m": (150, 86, 74), "l": (190, 140, 112),  # Auge, Braue, Mund, Falte
    "C": (36, 50, 102), "c": (24, 33, 72), "L": (58, 76, 146),           # Rock
    "Y": (217, 176, 74), "y": (170, 128, 44),                            # Goldborte, Knoepfe
    "T": (246, 244, 238), "t": (214, 210, 200),                          # Halsbinde
    "V": (122, 42, 52), "v": (90, 30, 38),                               # Weste
    "B": (110, 58, 30), "n": (74, 36, 18), "P": (239, 228, 196), "p": (206, 190, 150), "G": (201, 160, 64),  # Buch
    "N": (42, 36, 48), "O": (232, 232, 232), "o": (196, 196, 204), "F": (30, 26, 28), "f": (201, 160, 64),   # Beine, Schuhe
}

grid = [[None] * W for _ in range(H)]

def p(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if 0 <= xx < W and 0 <= yy < H:
                grid[yy][xx] = c

def px(pts, c):
    for x, y in pts:
        grid[y][x] = c

# ---- Beine und Schuhe (hinteres Bein rechts, vorderes links)
p(17, 37, 3, 7, "o"); p(13, 37, 3, 7, "O"); p(15, 37, 1, 7, "o")
p(16, 44, 4, 2, "F"); p(11, 44, 5, 2, "F"); px([(13, 44), (18, 44)], "f")
p(13, 34, 7, 3, "N")

# ---- Gehrock: Rumpf, weite Schoesse bis ans Knie
p(10, 18, 13, 16, "C")
p(9, 28, 15, 9, "C")
p(22, 20, 2, 16, "c"); p(19, 30, 1, 7, "c")        # Rueckenschatten, Rueckenschlitz
p(9, 36, 15, 1, "Y")                                 # Saumborte
p(10, 18, 2, 12, "L")                                # Licht von links
# Weste mit Knopfleiste, vorne offener Rock mit Goldkante
p(11, 19, 4, 12, "V"); p(11, 29, 4, 2, "v"); p(14, 19, 1, 12, "v")
px([(12, 21), (12, 24), (12, 27)], "Y")
p(15, 18, 1, 19, "Y"); p(10, 30, 1, 6, "y")
# Hinterer Arm haengt, grosser Aufschlag, Hand
p(21, 19, 3, 11, "C"); p(23, 20, 1, 10, "c"); p(20, 29, 4, 2, "Y"); p(21, 31, 2, 2, "S"); p(22, 32, 1, 1, "s")

# ---- Buch: dicker Lederfoliant vor der Brust, Seitenblock oben sichtbar
# Vorderer Arm (Oberarm am Koerper, Unterarm nach vorn unter das Buch)
p(12, 19, 4, 7, "L"); p(15, 20, 1, 6, "C")
p(4, 18, 10, 2, "P"); p(4, 18, 10, 1, "p")           # Seitenblock (Dicke des Buchs)
px([(6, 19), (8, 19), (10, 19), (12, 19)], "p")
p(3, 20, 11, 10, "B")                                # Vorderdeckel
p(13, 19, 2, 11, "n")                                # Buchruecken, Dreiviertel
p(3, 20, 11, 1, "n"); p(3, 29, 11, 1, "n")
p(4, 21, 1, 8, "n")                                  # Falz
for gx, gy in ((5, 21), (12, 21), (5, 28), (12, 28)):
    px([(gx, gy)], "G")                              # Goldecken
p(7, 23, 4, 1, "G"); p(7, 26, 4, 1, "G"); px([(8, 24), (9, 25), (9, 24), (8, 25)], "G")   # Praegung
p(13, 24, 2, 2, "G")                                 # Schliesse
p(8, 30, 6, 2, "Y"); p(9, 30, 5, 3, "S"); p(9, 32, 5, 1, "s")   # Aufschlag und Hand stuetzen von unten
p(14, 26, 2, 4, "L")                                 # Unterarm

# ---- Halsbinde mit Jabot
p(11, 15, 5, 3, "T"); p(12, 18, 3, 3, "T"); p(13, 18, 1, 3, "t"); p(15, 16, 1, 2, "t")

# ---- Kopf, Dreiviertel nach links
p(10, 6, 7, 9, "S")
p(9, 9, 1, 3, "S")                                   # Nase
px([(9, 11)], "s")
p(11, 14, 5, 1, "S"); p(12, 15, 3, 1, "s")           # Kinn, Hals
p(16, 7, 1, 7, "s")                                  # Schatten zur Wange hin
px([(11, 9), (14, 9)], "E")                          # Augen
px([(10, 8), (11, 8), (14, 8), (15, 8)], "b")        # graue Brauen
px([(12, 10), (15, 11), (12, 11)], "l")              # Falten, Traenensack
px([(13, 12)], "r")                                  # Wange
p(11, 13, 2, 1, "m")                                 # Mund
px([(10, 12)], "l")                                  # Nasolabialfalte

# ---- Kleine gepuderte Zopfperuecke
p(10, 2, 10, 4, "W"); p(12, 1, 6, 1, "W"); p(10, 5, 2, 1, "W")
p(16, 4, 6, 10, "W")                                 # Hinterkopf
p(17, 8, 4, 5, "w"); px([(17, 9), (20, 9), (17, 11), (20, 11)], "g")   # Seitenrolle ueber dem Ohr
p(19, 3, 3, 5, "w"); p(21, 5, 1, 8, "g")
p(12, 2, 4, 1, "T")                                  # Glanz
p(21, 12, 3, 3, "R"); px([(22, 13)], "K")            # Schleife
p(22, 15, 2, 3, "w"); px([(22, 17)], "g")            # Zopf

# ---- Kontur: jeder leere Nachbar eines gefuellten Pixels wird dunkel
out = [row[:] for row in grid]
for y in range(H):
    for x in range(W):
        if grid[y][x] is None and any(0 <= x + dx < W and 0 <= y + dy < H and grid[y + dy][x + dx] is not None
                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            out[y][x] = "K"
grid = out


def verkleinern(g):
    """16 x 24 fuer das Spiel: je 2x2-Block die haeufigste Innenfarbe, danach neue Kontur."""
    h, w = len(g) // 2, len(g[0]) // 2
    k = [[None] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            werte = [g[2 * y + dy][2 * x + dx] for dy in (0, 1) for dx in (0, 1)]
            innen = [v for v in werte if v not in (None, "K")]
            if len(innen) >= 2 or (innen and werte.count("K") < 3):
                # Gesichtsdetails (Augen, Mund) gewinnen, damit das Gesicht lesbar bleibt
                for vorrang in ("E", "m", "Y", "R", "G"):
                    if vorrang in innen:
                        k[y][x] = vorrang
                        break
                else:
                    k[y][x] = max(set(innen), key=innen.count)
    res = [row[:] for row in k]
    for y in range(h):
        for x in range(w):
            if k[y][x] is None and any(0 <= x + dx < w and 0 <= y + dy < h and k[y + dy][x + dx] is not None
                                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                res[y][x] = "K"
    return res


def png(path, g, scale=1, hintergrund=None):
    h, w = len(g), len(g[0])
    raw = bytearray()
    for y in range(h):
        row = bytearray()
        for x in range(w):
            v = g[y][x]
            if v is None:
                c = (hintergrund + (255,)) if hintergrund else (0, 0, 0, 0)
            else:
                c = PAL[v] + (255,)
            row += bytes(c) * scale
        for _ in range(scale):
            raw += b"\x00" + bytes(row)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w * scale, h * scale, 8, 6, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    klein = verkleinern(grid)
    png(os.path.join(HERE, "bibliothekar_32x48.png"), grid)
    png(os.path.join(HERE, "bibliothekar_16x24.png"), klein)
    png(os.path.join(HERE, "bibliothekar_weiss.png"), grid, 8, (255, 255, 255))
    png(os.path.join(HERE, "bibliothekar_16x24_weiss.png"), klein, 8, (255, 255, 255))
    print("Fertig")
