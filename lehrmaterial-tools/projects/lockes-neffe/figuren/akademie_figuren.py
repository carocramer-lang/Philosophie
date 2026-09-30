#!/usr/bin/env python3
# Figuren der Akademie, Vorderansicht (sie schauen Jonny an):
#   praesident: grosse schwarze Allongeperuecke, roter Rock mit Goldknoepfen, Spitzenhalsbinde, Urkunde in der Hand
#   locke: Onkel John ohne Peruecke mit eigenem langen Haar, schmales Gesicht, schlichter dunkler Rock, weisser Kragen
# Aufruf: python3 figuren/akademie_figuren.py
# Ausgabe je Figur: <name>_32x48.png, <name>_16x24.png und Vorschauen auf Weiss

import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bibliothekar as B  # noqa: E402  (png, verkleinern)

W, H = 32, 48

PAL = {
    "K": (28, 22, 24),
    "S": (234, 190, 156), "s": (204, 150, 118), "r": (214, 132, 112), "E": (40, 32, 36), "m": (150, 86, 74),
    "T": (246, 244, 238), "t": (210, 206, 196),                          # Halsbinde, Kragen
    "P": (40, 34, 36), "p": (70, 60, 58), "q": (24, 20, 22),             # schwarze Peruecke
    "R": (150, 34, 44), "o": (112, 22, 32), "Y": (222, 180, 80),         # roter Rock, Gold
    "H": (104, 82, 66), "h": (140, 118, 98), "g": (170, 160, 150),       # Lockes Haar, grau durchzogen
    "C": (54, 44, 40), "c": (36, 30, 28),                                # Lockes dunkler Rock
    "B": (60, 50, 46), "G": (160, 158, 164), "F": (34, 28, 28),          # Hose, Struempfe, Schuhe
    "U": (240, 232, 206), "u": (200, 186, 150), "W": (170, 30, 36),      # Urkunde mit Siegel
}


def neu():
    return [[None] * W for _ in range(H)]


def werkzeug(grid):
    def p(x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if 0 <= xx < W and 0 <= yy < H:
                    grid[yy][xx] = c

    def px(pts, c):
        for x, y in pts:
            grid[y][x] = c
    return p, px


def kontur(grid):
    out = [row[:] for row in grid]
    for y in range(H):
        for x in range(W):
            if grid[y][x] is None and any(0 <= x + dx < W and 0 <= y + dy < H and grid[y + dy][x + dx] is not None
                                          for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y][x] = "K"
    return out


def gesicht(p, px, x, y, schmal=False):
    b = 6 if schmal else 7
    p(x, y, b, 8, "S")
    p(x + b - 1, y + 1, 1, 6, "s")
    px([(x + 1, y + 3), (x + b - 3, y + 3)], "E")
    p(x + (b // 2) - 1, y + 4, 1, 2, "s")
    p(x + 2, y + 6, b - 4, 1, "m")
    if not schmal:
        px([(x + 1, y + 5), (x + b - 2, y + 5)], "r")


def praesident():
    g = neu(); p, px = werkzeug(g)
    p(12, 36, 3, 8, "G"); p(17, 36, 3, 8, "G")
    p(11, 44, 5, 2, "F"); p(16, 44, 5, 2, "F"); px([(13, 44), (18, 44)], "Y")
    p(12, 34, 8, 3, "B")
    p(9, 16, 14, 20, "R"); p(20, 16, 3, 20, "o")
    p(15, 16, 2, 20, "o")                                   # vordere Kante
    for yy in range(19, 34, 3):
        px([(14, yy), (17, yy)], "Y")
    p(9, 34, 14, 2, "o"); p(9, 35, 14, 1, "Y")
    p(6, 18, 3, 12, "R"); p(23, 18, 3, 12, "o")             # Arme
    p(5, 29, 4, 3, "T"); p(23, 29, 4, 3, "T")               # Spitzenmanschetten
    p(6, 31, 3, 2, "S"); p(24, 31, 2, 2, "S")
    p(1, 27, 7, 9, "U"); p(1, 27, 7, 1, "u"); p(1, 35, 7, 1, "u")   # Urkunde
    px([(3, 30), (4, 30), (5, 30), (3, 32), (4, 32)], "u")
    p(3, 34, 3, 3, "W")
    p(13, 14, 6, 6, "T"); p(14, 19, 4, 3, "t"); px([(15, 16), (16, 17)], "t")   # Spitzenhalsbinde
    # grosse Allongeperuecke, rahmt das Gesicht bis auf die Brust
    p(9, 2, 14, 6, "P"); p(11, 1, 10, 1, "P")
    p(7, 6, 5, 16, "P"); p(20, 6, 5, 16, "P")
    p(7, 18, 4, 6, "p"); p(21, 18, 4, 6, "p")
    for yy in range(7, 22, 3):
        px([(8, yy), (10, yy + 1), (21, yy), (23, yy + 1)], "q")
    px([(12, 2), (15, 1), (18, 2)], "p")
    gesicht(p, px, 12, 6)
    return kontur(g)


def locke():
    g = neu(); p, px = werkzeug(g)
    p(12, 36, 3, 8, "G"); p(17, 36, 3, 8, "G")
    p(11, 44, 5, 2, "F"); p(16, 44, 5, 2, "F")
    p(12, 34, 8, 3, "B")
    p(10, 17, 12, 19, "C"); p(19, 17, 3, 19, "c"); p(15, 17, 1, 19, "c")
    for yy in range(20, 34, 4):
        px([(14, yy)], "t")
    p(7, 18, 3, 13, "C"); p(22, 18, 3, 13, "c")
    p(7, 31, 3, 2, "S"); p(22, 31, 3, 2, "S")
    p(12, 15, 8, 3, "T"); p(13, 18, 6, 2, "t")              # schlichter weisser Kragen (Baeffchen)
    # eigenes langes Haar, schulterlang, grau durchzogen, Mittelscheitel
    p(11, 3, 10, 5, "H"); p(12, 2, 8, 1, "H")
    p(10, 6, 3, 11, "H"); p(19, 6, 3, 11, "H")
    p(11, 7, 1, 7, "h"); p(20, 7, 1, 8, "h"); p(13, 3, 1, 3, "h"); p(18, 3, 1, 3, "h")   # graue Straehnen
    px([(11, 10), (20, 11), (18, 4)], "g")
    p(16, 2, 1, 3, "h")
    gesicht(p, px, 13, 6, schmal=True)
    p(15, 10, 1, 3, "s")                                    # lange schmale Nase
    return kontur(g)


if __name__ == "__main__":
    B.PAL = PAL
    for name, g in (("praesident", praesident()), ("locke", locke())):
        klein = B.verkleinern(g)
        B.png(os.path.join(HERE, name + "_32x48.png"), g)
        B.png(os.path.join(HERE, name + "_16x24.png"), klein)
        B.png(os.path.join(HERE, name + "_weiss.png"), g, 8, (255, 255, 255))
        B.png(os.path.join(HERE, name + "_16x24_weiss.png"), klein, 8, (255, 255, 255))
    print("Fertig")
