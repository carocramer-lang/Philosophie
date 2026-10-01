"""Musik fuer Lockes Welt: liest die Noten (gemeinfreie Stuecke um 1690) und schreibt musik/stuecke.js.

Quellen der Notentexte:
- Tanzmelodien aus James Aird, A Selection of Scotch, English, Irish and Foreign Airs (Glasgow 1782 ff.),
  ABC-Fassung von Jack Campin (2009), mitgeliefert im music21-Korpus (airdsAirs). Die Melodien selbst
  stammen aus dem 17. Jahrhundert und stehen schon in Playfords English Dancing Master.
- Corelli, Sonata da chiesa op. 3 Nr. 1 (Rom 1689), 1. Satz Grave, alle drei Stimmen, aus dem music21-Korpus.
Die Basslinie der einstimmigen Tanzmelodien setzt dieses Skript selbst (einfacher Generalbass: je Taktgruppe
der passendste Dreiklang, Grundton im Bass).

Aufruf: python3 musik/generator.py
"""
import json
import os
import re
from fractions import Fraction as F

HIER = os.path.dirname(os.path.abspath(__file__))
TICKS = 12                       # Zeitraster: 12 Ticks je Viertel (auch Triolen und Sechzehntel ganzzahlig)

# ---------- Notentexte (ABC; Kopf gekuerzt, Notenzeilen unveraendert aus Aird / Campin)
LILLIBURLERO = """
X:0481
T:Lillie Bulera.
M:6/8
L:1/8
Q:3/8=108
K:G
 D| G>AG        B2B     | A>BA      c3 |(B/c/d).G c2B     |A>GF G2::
 d| g2f         g2d     |=fgf       e2d| d>ef     g>fe    |dcB  A2
 d| e>dc        Bcd     | e>dc      Bcd|(e/f/g)G  c2B     |AGF  G2::
 D|(G/A/B).B    B2g     | aAB       c2e| d>BG    (Ec).B   |A>GF G2::
 d|(g/f/g/a/).g gde     |=f>gf     Te2d| B>cd    (e/f/g).e|dBG  A2
=f|(ec/e/).g   (dB/d/).g|(ec/e/).g TdBd|(e/f/g)G  EcB     |A>GF G2:|
"""

GREENSLEEVES = """
X:0130
T:Green Sleeves.
M:6/8
L:1/8
Q:3/8=108
K:A Minor
A/B/|c2c cde |dBG G2B|c2A ABA |G2E E2
B   |c2c cde |dBG G2B|cBA BA^G|A3  A2:|
f/e/|g2g g^fe|dBG G2g|a2a aba |g2e e2
f   |gag g^fe|dBG GAB|cBA BA^G|A3  A2:|
"""

HEALTH_TO_BETTY = """
X:0063
T:A Health to Betty
M:6/8
L:1/8
Q:3/8=90
K:E Minor
B,|E>FE D2B,|G>AG FGA|B>cB A2G |d3 B2
e |dBG  GdB |AFD  DBA|G>FE FDB,|G3 F2:|
B |e>fe d2B |e>fg f2e|dBg  A2G |d3 efg|
   dBG  GdB |AFD  DBA|G>FE FDB,|G3 F2:|
"""

THE_DRUMMER = """
X:0129
T:The Drummer
M:2/4
L:1/8
Q:1/2=84
K:A Dorian
E|ABcA |E2 EF|G2 AB|(d/c/B/A/) GB|AGAB |E2E=f|edcB|A2A:|
B|c>Bce|d>cde|c>Bce|(d/c/B/A/) GB|c>Bce|dcd=f|edcB|A2A:|
"""

TRUMPET_AIR = """
X:0192
T:A Trumpet Air
M:6/8
L:1/8
Q:3/8=120
K:G
D|GDG BGB|d3 c3 | B>cd    d>cB|AAA  A2
D|GDG BGB|d3 c3 |(B/c/d)B AGA |GGG  G2:|
d|dBd dBd|e3 c2A| B>cd    d>cB|A>AA A2
D|GDG BGB|d3 c3 |(B/c/d)B AGA |GGG  G2:|
"""

# Corelli op. 3 Nr. 1, Grave (F-Dur, 4/4, 19 Takte): MIDI-Tonhoehe:Dauer in Vierteln, r = Pause
CORELLI = [
    "84:3/2 84:1/2 82:1 81:1 79:2 81:1/2 82:1/2 84:3/2 77:1/2 82:2 81:1 79:2 77:2 81:3/2 81:1/2 79:3/2 81:1/4 79:1/4 77:3/2 79:1/4 77:1/4 76:3/2 79:1/2 81:1/2 74:1/2 74:1/2 74:1/2 74:1/2 72:1/2 r1/2 79:1/2 81:1/4 79:1/4 77:1/4 76:1/4 74:1 72:1 77:2 76:1 81:3 79:2 77:2 76:3/2 69:1/2 74:2 74:3/4 73:1/4 74:1 70:2 69:2 67:1/2 65:1/2 64:1/2 60:1/2 84:2 82:2 81:1 74:3/2 79:1/2 76:1/2 72:1/2 77:2 77:3/4 76:1/4 77:3/2 72:1/2 74:3/2 62:1/2 64:1 65:2 64:1 65:4",
    "81:3/2 81:1/2 79:1 77:1 76:2 77:3/2 76:1/2 74:3/2 79:1/2 76:1/2 72:1/2 77:2 77:3/4 76:1/4 77:2 84:1 77:3/2 76:1/4 74:1/4 76:3/2 69:1/2 74:3/2 67:1/2 72:2 72:1 72:1 r1/2 76:1/2 69:1/4 71:1/4 72:1/2 72:3/4 71:1/4 72:1 r1 79:3 77:1 82:2 81:2 79:2 77:3/2 81:1/2 82:1/2 76:1/2 76:1 74:2 72:3/2 72:1/2 74:1/2 72:1/2 70:1/2 69:1/2 67:1 r1/2 76:1/2 77:1 79:1 72:1 84:2 82:2 81:1 79:2 77:1 72:3/2 65:1/2 70:2 69:1 67:2 65:4",
    "53:3/2 53:1/2 55:1 57:1/2 58:1/2 60:2 57:1 45:1 46:3/2 46:1/2 48:1/2 60:1/2 62:1/2 57:1/2 58:1/2 55:1/2 60:1/2 48:1/2 53:2 53:1/2 55:1/2 57:1/2 53:1/2 60:1/2 48:1/2 52:1/2 48:1/2 50:1/2 48:1/2 47:1/2 43:1/2 48:3/2 52:1/2 53:1 55:1 57:1 52:1 53:1 55:1 48:1/2 60:1/2 57:1/2 53:1/2 58:1/2 55:1/2 60:1/2 48:1/2 53:1/2 55:1/2 57:1/2 53:1/2 50:1/2 50:1/2 52:1/2 48:1/2 53:1/2 55:1/2 57:1/2 45:1/2 47:1 49:1 50:3/2 53:1/2 55:1/2 52:1/2 57:1/2 45:1/2 50:1 r1 53:3/2 53:1/2 46:3/2 46:1/2 48:3/2 48:1/2 50:1 52:1 53:1/2 55:1/2 57:1/2 45:1/2 46:1/2 48:1/2 50:1/2 46:1/2 48:1/2 60:1/2 62:1/2 57:1/2 58:1/2 55:1/2 60:1/2 48:1/2 53:1/2 55:1/2 57:1/2 45:1/2 46:3/2 46:1/2 48:2 36:2 41:4",
]

# ---------- ABC lesen (nur was diese Melodien brauchen)
STAMM = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
QUINTEN = ["Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#"]
MODI = {"": 0, "maj": 0, "min": -3, "m": -3, "dor": -2, "mix": -1}


def tonart(k):
    m = re.match(r"([A-G][b#]?)\s*([A-Za-z]*)", k.strip())
    grund, modus = m.group(1), m.group(2).lower()[:3]
    n = QUINTEN.index(grund) - 7 + MODI[modus]
    vorz = {}
    for b in ("FCGDAEB"[:n] if n > 0 else "BEADGCF"[:-n]):
        vorz[b] = 1 if n > 0 else -1
    tonika = STAMM[grund[0]] + (1 if grund.endswith("#") else -1 if grund.endswith("b") and len(grund) > 1 else 0)
    return vorz, tonika % 12, modus


def dauer(zahl, striche, nenner):
    d = F(int(zahl) if zahl else 1)
    if striche:
        d /= int(nenner) if nenner else 2 ** len(striche)
    return d


def abc(text):
    """Liefert (noten, laenge, auftakt, tonika, modus); noten = [midi, start, dauer] in Vierteln."""
    kopf, zeilen = {}, []
    for z in text.strip().splitlines():
        if re.match(r"^[A-Z]:", z):
            kopf[z[0]] = z[2:].strip()
        else:
            zeilen.append(z)
    L = F(*map(int, kopf["L"].split("/"))) * 4
    vorz, tonika, modus = tonart(kopf["K"])
    koerper = " ".join(zeilen)
    koerper = re.sub(r'"[^"]*"|\{[^}]*\}', "", koerper)
    koerper = re.sub(r"[().T~]", "", koerper)          # Boegen und Verzierungen (Triller) entfallen
    tok = re.findall(r"\|:|:\||::|\|\]|\|\||\||[<>]|[_=^]*[A-Ga-gz][,']*\d*/*\d*", koerper)
    # Wiederholungen ausrollen
    teile, akt = [], []
    for t in tok:
        if t == "|:":
            if akt:
                teile.append((akt, False))
            akt = []
        elif t in (":|", "::"):
            teile.append((akt, True))
            akt = []
        else:
            akt.append(t)
    if akt:
        teile.append((akt, False))
    folge = []
    for a, wdh in teile:
        folge += a + ["|"] + (a + ["|"] if wdh else [])
    # Noten mit Dauern, punktierte Paare (> <) aufloesen
    roh = []
    for t in folge:
        if t in ("|", "||", "|]"):
            roh.append(("|",))
        elif t in "<>" and len(t) == 1:
            roh.append((t,))
        else:
            m = re.match(r"([_=^]*)([A-Ga-gz])([,']*)(\d*)(/*)(\d*)", t)
            roh.append(("n", m.group(1), m.group(2), m.group(3), dauer(*m.groups()[3:]) * L))
    for i, r in enumerate(roh):
        if r[0] in "<>" and len(r) == 1:
            v, n = roh[i - 1], roh[i + 1]
            f1, f2 = (F(3, 2), F(1, 2)) if r[0] == ">" else (F(1, 2), F(3, 2))
            roh[i - 1] = v[:4] + (v[4] * f1,)
            roh[i + 1] = n[:4] + (n[4] * f2,)
    noten, t, versatz, auftakt = [], F(0), {}, None
    for r in roh:
        if r[0] == "|":
            versatz = {}
            if auftakt is None:
                auftakt = t
            continue
        if r[0] != "n":
            continue
        _, akz, b, okt, d = r
        if b != "z":
            gross = b.upper()
            schluessel = (gross, b.islower(), okt)
            if akz:
                versatz[schluessel] = {"^": 1, "_": -1, "=": 0}[akz]
            p = 60 + STAMM[gross] + (12 if b.islower() else 0) + 12 * (okt.count("'") - okt.count(","))
            noten.append([p + versatz.get(schluessel, vorz.get(gross, 0)), t, d])
        t += d
    return noten, t, auftakt or F(0), tonika, modus


def drehen(noten, laenge, auftakt):
    """Auftakt ans Ende: das Stueck beginnt auf der Eins und schliesst nahtlos an sich selbst an."""
    erg = []
    for p, s, d in noten:
        s2 = s - auftakt
        if s2 < 0:
            s2 += laenge
        erg.append([p, s2, d])
    return sorted(erg, key=lambda n: n[1])


def generalbass(noten, laenge, tonika, modus, gruppe, tief=41):
    """Je Taktgruppe der Dreiklang, der die Melodietoene am besten traegt; der Grundton liegt im Bass."""
    skala = {"": [0, 2, 4, 5, 7, 9, 11], "maj": [0, 2, 4, 5, 7, 9, 11],
             "min": [0, 2, 3, 5, 7, 8, 10], "dor": [0, 2, 3, 5, 7, 9, 10]}[modus]
    akk = {}
    for i in range(7):
        akk[i] = {(tonika + skala[(i + k) % 7]) % 12 for k in (0, 2, 4)}
    if modus in ("min", "dor"):
        akk[4] = {(tonika + 7) % 12, (tonika + 11) % 12, (tonika + 2) % 12}   # Dur-Dominante wie im Barock
        wahl = [0, 4, 3, 2, 6] if modus == "min" else [0, 4, 6, 2]
    else:
        wahl = [0, 4, 3, 5, 1]
    erg, t = [], F(0)
    while t < laenge:
        e = min(t + gruppe, laenge)
        gew = {}
        for p, s, d in noten:
            ueber = min(e, s + d) - max(t, s)
            if ueber <= 0:
                continue
            for k in wahl:
                if p % 12 in akk[k]:
                    gew[k] = gew.get(k, 0) + ueber * (2 if s == t else 1)
        k = max(wahl, key=lambda k: (gew.get(k, 0), -wahl.index(k)))
        grund = (tonika + skala[k]) % 12
        m = tief + (grund - tief) % 12
        if erg and erg[-1][0] == m and erg[-1][1] + erg[-1][2] == t:
            erg[-1][2] += e - t
        else:
            erg.append([m, t, e - t])
        t = e
    return erg


def corelli():
    stimmen = []
    for s in CORELLI:
        t, noten = F(0), []
        for x in s.split():
            if x.startswith("r"):
                t += F(x[1:])
                continue
            p, d = x.split(":")
            noten.append([int(p), t, F(d)])
            t += F(d)
        stimmen.append(noten)
    return stimmen, t


def kodieren(noten):
    flach = []
    for p, s, d in noten:
        for w in (s, d):
            assert (w * TICKS).denominator == 1, w
        flach += [p, int(s * TICKS), int(d * TICKS)]
    return flach


def stueck(titel, herkunft, tempo, laenge, stimmen, pause=0):
    """laenge: Schleifenlaenge in Vierteln; pause: Stille vor der Wiederholung."""
    return {"titel": titel, "herkunft": herkunft, "tempo": tempo, "laenge": int((laenge + pause) * TICKS),
            "stimmen": [{"klang": k, "laut": l, "noten": kodieren(n)} for k, l, n in stimmen]}


def tanz(text, gruppe):
    noten, laenge, auftakt, tonika, modus = abc(text)
    noten = drehen(noten, laenge, auftakt)
    return noten, laenge, generalbass(noten, laenge, tonika, modus, gruppe)


def main():
    erg = {}
    m, l, b = tanz(LILLIBURLERO, F(3, 2))
    erg["welt"] = stueck("Lilliburlero", "Spottlied der Glorious Revolution, 1688; Fassung nach Aird", 132, l,
                         [("floete", 0.9, m), ("cembalo", 0.7, b)])
    m, l, b = tanz(GREENSLEEVES, F(3, 2))
    erg["observatorium"] = stueck("Greensleeves", "in Playfords English Dancing Master seit 1686; Fassung nach Aird", 96, l,
                                  [("floete", 0.8, m), ("cembalo", 0.55, b)])
    st, l = corelli()
    erg["lesesaal"] = stueck("Corelli, Sonata da chiesa op. 3 Nr. 1, Grave", "Rom 1689", 56, l,
                             [("streicher", 0.55, st[0]), ("streicher", 0.5, st[1]), ("cembalo", 0.7, st[2])], pause=2)
    m, l, b = tanz(HEALTH_TO_BETTY, F(3, 2))
    erg["salon"] = stueck("A Health to Betty", "in Playfords English Dancing Master seit 1651; Fassung nach Aird", 120, l,
                          [("cembalo", 0.85, m), ("cembalo", 0.6, b)])
    m, l, b = tanz(THE_DRUMMER, F(2))
    erg["druckerei"] = stueck("The Drummer", "17. Jahrhundert, aus Playfords Sammlungen; Fassung nach Aird", 144, l,
                              [("floete", 0.85, m), ("cembalo", 0.6, b), ("trommel", 0.5, [[1 if i % 2 == 0 else 0, F(i), F(1, 2)] for i in range(int(l))])])
    m, l, b = tanz(TRUMPET_AIR, F(3, 2))
    erg["akademie"] = stueck("A Trumpet Air", "ueberliefert bei Aird, Glasgow 1782", 112, l,
                             [("trompete", 0.75, m), ("cembalo", 0.6, b), ("pauke", 0.6, [[n[0] - 12, n[1], F(1, 2)] for n in b])])
    js = "// Erzeugt von musik/generator.py. Noten: [Tonhoehe (MIDI), Start, Dauer] in 1/" + str(TICKS) + " Vierteln.\n"
    js += "window.MUSIK = " + json.dumps({"ticks": TICKS, "stuecke": erg}, ensure_ascii=False, separators=(",", ":")) + ";\n"
    with open(os.path.join(HIER, "stuecke.js"), "w", encoding="utf-8") as f:
        f.write(js)
    for k, v in erg.items():
        print(k, v["titel"], "Sekunden:", round(v["laenge"] / TICKS * 60 / v["tempo"]), "Noten:", sum(len(s["noten"]) // 3 for s in v["stimmen"]))


if __name__ == "__main__":
    main()
