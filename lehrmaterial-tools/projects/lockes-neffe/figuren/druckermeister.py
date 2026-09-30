#!/usr/bin/env python3
# Druckermeister als Pixel-Art-Sprite, Dreiviertelansicht nach links (zur Presse hin).
# Gefaltete Papiermuetze, Hemd mit aufgekrempelten Aermeln, gruene Weste, Lederschuerze, Druckerschwaerze an den Haenden.
# Zwei Posen: stehen und ziehen (am Bengel der Presse).
# Aufruf: python3 figuren/druckermeister.py
# Ausgabe: druckermeister_32x48.png, druckermeister_ziehen_32x48.png, dazu je 16 x 24 und Vorschau auf Weiss

import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bibliothekar as B  # noqa: E402  (png, verkleinern)

W, H = 32, 48

PAL = {
    "K": (30, 24, 22),                                                   # Kontur
    "W": (246, 244, 236), "w": (208, 204, 192),                          # Papiermuetze
    "S": (232, 184, 150), "s": (200, 146, 114), "r": (214, 130, 110),    # Haut, Schatten, Wange
    "H": (120, 96, 80), "M": (96, 74, 60),                               # Haar, Schnurrbart
    "E": (40, 32, 36),                                                   # Auge
    "T": (240, 236, 226), "t": (204, 198, 186),                          # Hemd
    "V": (64, 98, 70), "v": (44, 70, 50),                                # Weste
    "A": (156, 104, 62), "a": (120, 78, 46), "Y": (206, 170, 90),        # Lederschuerze, Schnalle
    "B": (84, 64, 50), "G": (150, 150, 158), "F": (38, 32, 32),          # Hose, Struempfe, Schuhe
    "N": (46, 44, 52),                                                   # Druckerschwaerze an den Haenden
}


def figur(ziehen):
    grid = [[None] * W for _ in range(H)]

    def p(x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if 0 <= xx < W and 0 <= yy < H:
                    grid[yy][xx] = c

    def px(pts, c):
        for x, y in pts:
            grid[y][x] = c

    dx = -1 if ziehen else 0                          # beim Ziehen lehnt er sich zur Presse

    # Beine, Schuhe
    p(12, 35, 3, 9, "G"); p(17, 35, 3, 9, "G"); p(19, 35, 1, 9, "t")
    p(12, 35, 8, 3, "B")
    p(10, 44, 5, 2, "F"); p(16, 44, 5, 2, "F")

    # Rumpf: Hemd, Weste, Schuerze
    p(10 + dx, 17, 12, 18, "T")
    p(11 + dx, 17, 10, 12, "V"); p(18 + dx, 17, 3, 12, "v")
    p(10 + dx, 21, 11, 15, "A"); p(18 + dx, 21, 3, 15, "a")
    p(10 + dx, 21, 11, 1, "a")
    px([(14 + dx, 25), (15 + dx, 25)], "Y")
    for k in range(3):
        px([(12 + dx + k * 3, 32)], "a")
    p(14 + dx, 17, 3, 2, "T")                         # Kragen

    # Arme
    if ziehen:
        p(3, 20, 9, 3, "T"); p(3, 22, 9, 1, "t")      # vorderer Arm nach vorn zum Bengel
        p(1, 19, 3, 4, "N")                            # Hand am Griff
        p(4, 24, 7, 2, "T"); p(2, 24, 2, 3, "N")       # zweiter Arm
    else:
        p(8, 18, 3, 10, "T"); p(8, 26, 3, 1, "t")
        p(8, 28, 3, 3, "N")
        p(21, 18, 2, 10, "t"); p(21, 28, 2, 2, "N")

    # Kopf
    hx = 11 + dx
    p(hx, 7, 7, 9, "S")
    p(hx - 1, 10, 1, 3, "S"); px([(hx - 1, 12)], "s")    # Nase
    p(hx + 6, 8, 1, 7, "s")
    px([(hx + 1, 10), (hx + 4, 10)], "E")
    p(hx, 13, 5, 1, "M"); px([(hx - 1, 13), (hx + 5, 14)], "M")   # Schnurrbart
    px([(hx + 3, 12)], "r")
    p(hx + 1, 15, 4, 1, "s")
    p(hx + 6, 7, 3, 6, "H"); p(hx + 7, 13, 2, 2, "H")      # Haar hinten
    p(hx + 13 - 13, 15, 1, 1, "S")

    # Papiermuetze: gefaltet, flach oben, mit schraeger Kante
    p(hx - 1, 2, 10, 5, "W")
    p(hx - 1, 6, 10, 1, "w")
    px([(hx + 2, 3), (hx + 3, 4), (hx + 4, 5)], "w")
    p(hx, 1, 8, 1, "W")

    out = [row[:] for row in grid]
    for y in range(H):
        for x in range(W):
            if grid[y][x] is None and any(0 <= x + ex < W and 0 <= y + ey < H and grid[y + ey][x + ex] is not None
                                          for ex, ey in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y][x] = "K"
    return out


if __name__ == "__main__":
    B.PAL = PAL
    for name, ziehen in (("druckermeister", False), ("druckermeister_ziehen", True)):
        g = figur(ziehen)
        klein = B.verkleinern(g)
        B.png(os.path.join(HERE, name + "_32x48.png"), g)
        B.png(os.path.join(HERE, name + "_16x24.png"), klein)
        B.png(os.path.join(HERE, name + "_weiss.png"), g, 8, (255, 255, 255))
        B.png(os.path.join(HERE, name + "_16x24_weiss.png"), klein, 8, (255, 255, 255))
    print("Fertig")
