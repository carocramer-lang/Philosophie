#!/usr/bin/env python3
# Geist des Platon als Pixel-Art-Sprite, Dreiviertelansicht nach links, in kuehlen Geisterfarben.
# Aufruf: python3 figuren/platon.py
# Ausgabe: platon_32x48.png (transparent), platon_16x24.png (transparent, Spielgroesse),
#          platon_weiss.png und platon_16x24_weiss.png (achtfach vergroessert auf weissem Grund)

import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bibliothekar as B  # noqa: E402  (png, verkleinern)

W, H = 32, 48

PAL = {
    "K": (46, 70, 122),                                                   # Kontur
    "R": (228, 241, 252), "r": (186, 214, 240), "q": (140, 178, 218),     # Himation
    "C": (204, 226, 246), "c": (160, 196, 230),                           # Chiton darunter
    "S": (192, 218, 240), "s": (146, 184, 222),                           # Haut
    "H": (250, 252, 255), "h": (210, 230, 248), "g": (140, 176, 216),     # Haar und Bart
    "Y": (248, 234, 170),                                                 # Stirnband
    "E": (52, 82, 136), "m": (130, 160, 204),                             # Auge, Mund
    "P": (238, 242, 232), "p": (194, 210, 214), "n": (150, 176, 196),     # Schriftrolle
    "F": (120, 152, 196),                                                 # Sandalen
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

# ---- Geisterschweif statt Fuessen: das Gewand loest sich nach unten in Schwaden auf
SCHWEIF = [(10, 22), (11, 21), (11, 20), (12, 19), (13, 19), (14, 18), (15, 18), (16, 17), (17, 17)]
for i, (x0, x1) in enumerate(SCHWEIF):
    y = 37 + i
    for x in range(x0, x1 + 1):
        if (x + y) % 4 == 0 and i > 2:
            continue                                    # Luecken: der Stoff wird durchsichtig
        grid[y][x] = "c" if (x + i) % 3 else "q"
p(12, 37, 1, 3, "q"); p(16, 37, 1, 4, "q"); p(20, 37, 1, 2, "q")

# ---- Himation: um den Koerper geschlungen, ueber die linke Schulter, schraeger Faltenwurf
p(10, 17, 13, 20, "R")
p(9, 26, 15, 11, "R")
p(21, 18, 2, 19, "r"); p(23, 27, 1, 10, "q")
for k in range(12):                                   # Diagonale von der Schulter zur Huefte
    px([(10 + k, 17 + k)], "r")
    px([(10 + k, 18 + k)], "q")
for k in range(6):
    px([(12 + k, 30 + k // 2)], "r")
p(9, 34, 15, 1, "r")
px([(14, 32), (16, 33), (19, 31), (20, 33)], "r")

# ---- Rechter Arm (hinten) haengt, Hand
p(22, 20, 2, 9, "r"); p(22, 29, 2, 2, "S")

# ---- Schriftrolle in der vorderen Hand, quer vor der Brust
p(3, 22, 10, 4, "P"); p(3, 25, 10, 1, "p")
p(2, 21, 2, 6, "n"); p(12, 21, 2, 6, "n")
px([(5, 23), (7, 23), (9, 23)], "p")
p(9, 26, 4, 2, "S"); p(10, 27, 3, 1, "s")               # Hand stuetzt von unten
p(12, 20, 3, 7, "r")                                    # Unterarm im Gewand

# ---- Hals, Kopf mit Stirnband, langer Bart
p(13, 15, 4, 3, "s")
p(11, 6, 8, 9, "S")
p(10, 9, 1, 3, "S"); px([(10, 11)], "s")               # Nase
p(18, 7, 1, 7, "s")
px([(12, 9), (15, 9)], "E")                             # Augen
px([(11, 8), (12, 8), (15, 8), (16, 8)], "g")           # Brauen
p(10, 3, 10, 4, "H"); p(12, 2, 6, 1, "H")               # Haar
p(18, 5, 3, 8, "H"); p(19, 7, 2, 5, "h")                # Haar hinten ueber dem Ohr
p(10, 5, 10, 1, "Y")                                    # Stirnband (Taenia)
px([(20, 5), (21, 6), (21, 7)], "Y")
p(11, 12, 7, 3, "H")                                    # Bart
p(11, 15, 7, 3, "H"); p(12, 18, 5, 2, "H"); p(13, 20, 3, 2, "h")
px([(13, 13), (15, 14), (12, 16), (16, 16), (14, 18), (14, 20)], "h")
px([(13, 12), (14, 12)], "m")                           # Mund im Bart
p(11, 12, 1, 7, "g"); p(17, 12, 1, 6, "g")              # Bartkante
px([(12, 18), (16, 18), (13, 21), (15, 21)], "g")
px([(11, 7), (17, 7), (13, 3), (16, 3), (11, 4)], "h")  # Locken im Haar
px([(12, 10), (15, 10)], "s")                           # Schatten unter den Augen

# ---- Kontur: jeder leere Nachbar eines gefuellten Pixels wird dunkel
out = [row[:] for row in grid]
for y in range(H):
    for x in range(W):
        if grid[y][x] is None and any(0 <= x + dx < W and 0 <= y + dy < H and grid[y + dy][x + dx] is not None
                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            out[y][x] = "K"
grid = out


if __name__ == "__main__":
    B.PAL = PAL
    klein = B.verkleinern(grid)
    B.png(os.path.join(HERE, "platon_32x48.png"), grid)
    B.png(os.path.join(HERE, "platon_16x24.png"), klein)
    B.png(os.path.join(HERE, "platon_weiss.png"), grid, 8, (255, 255, 255))
    B.png(os.path.join(HERE, "platon_16x24_weiss.png"), klein, 8, (255, 255, 255))
    print("Fertig")
