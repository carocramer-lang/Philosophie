#!/usr/bin/env python3
# Arbeitsblatt "Die Debatte um die Tabula Rasa" (Leibniz) als eine Quelle fuer alles:
#   material/arbeitsblatt_leibniz.html  -> wird mit Chromium zur PDF gedruckt (siehe drucke_pdf.js)
#   material/leibniz_daten.js           -> Text mit Zeilen fuer das Spiel
#   netlify/lib/leibniz.json            -> derselbe Text fuer den Bibliothekar auf dem Server
# Aufruf: python3 material/arbeitsblatt_leibniz.py && node material/drucke_pdf.js

import html, json, os, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TITEL = "Arbeitsblatt: Die Debatte um die Tabula Rasa"
UNTERTITEL = "Vorbereitung auf die Leistungskontrolle im Fach Philosophie (Q2)"
EINLEITUNG = [
    "In unserer bisherigen Unterrichtsreihe haben wir uns eingehend mit John Lockes empiristischer Erkenntnistheorie beschäftigt. "
    "Locke vertritt die Auffassung, dass der menschliche Geist bei der Geburt ein unbeschriebenes Blatt (tabula rasa) sei und jegliche "
    "Erkenntnis ausschließlich aus der Erfahrung – unterteilt in äußere Wahrnehmung (sensation) und innere Selbstbeobachtung (reflexion) – hervorgehe.",
    "Der nachfolgende Textauszug stammt aus der Vorrede zu den Neuen Abhandlungen über den menschlichen Verstand (1704) von Gottfried Wilhelm Leibniz. "
    "Leibniz setzt sich darin kritisch mit Lockes Versuch über den menschlichen Verstand auseinander. Er hinterfragt, ob die menschliche Vernunft "
    "tatsächlich rein empirisch erklärt werden kann oder ob dem Geist nicht bereits grundlegende Strukturen und Prinzipien innewohnen.",
]
QUELLE = "Gottfried Wilhelm Leibniz: Neue Abhandlungen über den menschlichen Verstand (1704)"
ABSAETZE = [
    "„Es handelt sich um die Frage, ob die Seele an sich ganz leer ist wie eine Tafel, auf der man noch nichts geschrieben hat (tabula rasa), "
    "gemäß der Meinung des Aristoteles und des Verfassers des Versuchs; oder ob die Seele ursprünglich die Prinzipien mehrerer Begriffe und "
    "Lehrsätze enthält, die durch die äußeren Gegenstände bloß aufgeweckt werden, wie ich mit Platon annehme. […]",
    "Hieraus entsteht eine weitere Frage, nämlich ob alle Wahrheiten von der Erfahrung abhängen, d. h. von der Induktion und den Beispielen, "
    "oder ob einige davon einen anderen Ursprung haben. Denn wenn ein Phänomen oft wiederkehrt, so ist das keineswegs ein Beweis dafür, dass es "
    "auch in Zukunft immer so sein wird. Die Sinne geben uns zwar Beispiele, d. h. Wahrheiten über Einzelnes, aber alle Beispiele, welche eine "
    "Wahrheit bestätigen, reichen keineswegs aus, um die allgemeine Notwendigkeit derselben zu begründen; denn daraus, dass etwas geschehen ist, "
    "folgt nicht, dass es immer so geschehen muss.",
    "Daraus erhellt, dass die notwendigen Wahrheiten, wie man sie in der reinen Mathematik und namentlich in der Arithmetik und Geometrie findet, "
    "Prinzipien besitzen müssen, deren Beweis nicht von Beispielen und folglich auch nicht von dem Zeugnis der Sinne abhängt, obgleich ohne die "
    "Sinne niemand je daran gedacht haben würde, sie zu suchen. Die Mathematik ist hierfür ein schlagendes Beispiel: Ihre Lehrsätze gelten "
    "universell und notwendig, was keine rein empirische Beobachtung je leisten könnte.",
    "Daher hat ein Geist wie der unsere die Neigung, sich die Wahrheiten aus sich selbst zu holen; und die angeborenen Begriffe bilden die Seele "
    "wie die Adern den Marmorblock bilden, statt dass sie einer völlig ungestalteten Masse oder einer leeren Tafel gliche. Wenn in dem Stein Adern "
    "wären, welche die Gestalt des Herkules andeuteten, vorzugsweise vor anderen Gestalten, so würde dieser Stein durch sie im Voraus bestimmt "
    "sein, und Herkules wäre ihm gewissermaßen angeboren, obgleich es noch der Arbeit bedürfte, um diese Adern bloßzulegen und sie durch Politur "
    "zur Klarheit zu bringen.“",
]
AUFGABE_KOPF = "Aufgabe 1 (Anforderungsbereich I, 20 Punkte)"
AUFGABE = ("Stellen Sie die Kritik von Gottfried Wilhelm Leibniz an der empiristischen Erkenntnistheorie sowie sein eigenes Konzept "
           "angeborener Ideen dar, indem Sie seine Argumentation zur Begrenzung der Sinneserfahrung und das Gleichnis vom geäderten "
           "Marmorblock aus dem Text herausarbeiten.")
HINWEISE = [
    "Achten Sie auf den Operator „Stellen Sie dar …“: Verfassen Sie eine strukturierte, sachlich präzise Zusammenfassung in eigenen Worten.",
    "Vermeiden Sie bloße Textzitate; geben Sie stattdessen den logischen Argumentationsgang von Leibniz wieder.",
    "Beziehen Sie sich gezielt auf das Bild des Marmorblocks und erklären Sie, worin der Unterschied zu Lockes Tabula Rasa liegt.",
]

BREITE = 84  # Zeichen je Textzeile, passt bei 11 pt Serifenschrift sicher in die 172 mm breite Spalte


def zeilen():
    out = []
    for i, a in enumerate(ABSAETZE):
        teile = textwrap.wrap(a, BREITE, break_long_words=False, break_on_hyphens=False)
        for j, t in enumerate(teile):
            out.append({"text": t, "absatz": i, "neu": j == 0})
    return out


def html_seite(z):
    e = html.escape
    rows = []
    for n, zeile in enumerate(z, 1):
        nr = str(n) if n % 5 == 0 else ""
        cls = ' class="neu"' if zeile["neu"] and n > 1 else ""
        rows.append(f'<div{cls}><span class="nr">{nr}</span><span class="t">{e(zeile["text"])}</span></div>')
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><title>{e(TITEL)}</title>
<style>
@page {{ size: A4; margin: 16mm 18mm 16mm 20mm; }}
:root {{ --ink: #1f1f1f; --soft: #555; --rule: #9a9a9a; --fill: #f2f2f2; }}
body {{ margin: 0; color: var(--ink); font: 10.5pt/1.45 "Liberation Sans", Arial, sans-serif; }}
.kopfleiste {{ display: flex; justify-content: space-between; font-size: 8.5pt; letter-spacing: .06em; text-transform: uppercase; color: var(--soft);
  border-bottom: 1.2pt solid var(--ink); padding-bottom: 3pt; }}
.name {{ display: flex; gap: 18pt; margin: 8pt 0 10pt; font-size: 9.5pt; }}
.name span {{ flex: 1; border-bottom: .6pt solid var(--rule); padding-bottom: 1pt; }}
.name span.kurz {{ flex: 0 0 38mm; }}
h1 {{ font-size: 17pt; line-height: 1.15; margin: 4pt 0 1pt; }}
.unter {{ font-size: 10.5pt; color: var(--soft); margin: 0 0 10pt; }}
h2 {{ font-size: 10pt; text-transform: uppercase; letter-spacing: .08em; margin: 12pt 0 4pt; }}
.einleitung {{ background: var(--fill); padding: 7pt 10pt; border-left: 2.5pt solid var(--ink); }}
.einleitung p {{ margin: 0 0 5pt; }}
.einleitung p:last-child {{ margin: 0; }}
.quelle {{ font-weight: bold; margin: 0 0 5pt; }}
.text {{ font: 11pt/1.62 "Liberation Serif", "Times New Roman", serif; }}
.text div {{ display: grid; grid-template-columns: 9mm 1fr; white-space: nowrap; }}
.text div.neu {{ margin-top: 4pt; }}
.text .nr {{ font: 8pt/1 "Liberation Sans", Arial, sans-serif; color: var(--soft); text-align: right; padding-right: 3mm; align-self: center; }}
.aufgabe {{ border: 1pt solid var(--ink); padding: 8pt 10pt; margin-top: 12pt; break-inside: avoid; }}
.aufgabe .k {{ font-weight: bold; margin-bottom: 3pt; }}
.aufgabe p {{ margin: 0; }}
.hinweise {{ margin: 8pt 0 0; padding-left: 14pt; }}
.hinweise li {{ margin-bottom: 3pt; }}
.notizen {{ margin-top: 12pt; break-inside: avoid; }}
.notizen div {{ border-bottom: .6pt solid var(--rule); height: 8.5mm; }}
.fuss {{ margin-top: 8pt; font-size: 8pt; color: var(--soft); }}
</style></head><body>
<div class="kopfleiste"><span>Pelizaeus-Gymnasium Paderborn · Fach Philosophie (Q2)</span><span>Erkenntnistheorie</span></div>
<div class="name"><span>Name:</span><span class="kurz">Datum:</span></div>
<h1>{e(TITEL)}</h1>
<p class="unter">{e(UNTERTITEL)}</p>
<h2>Einleitung und Problemzusammenhang</h2>
<div class="einleitung">{''.join(f'<p>{e(p)}</p>' for p in EINLEITUNG)}</div>
<h2>Textgrundlage</h2>
<p class="quelle">{e(QUELLE)}</p>
<div class="text">{''.join(rows)}</div>
<div class="aufgabe"><div class="k">{e(AUFGABE_KOPF)}</div><p>{e(AUFGABE)}</p>
<ul class="hinweise">{''.join(f'<li>{e(h)}</li>' for h in HINWEISE)}</ul></div>
<div class="notizen"><h2>Notizen</h2>{'<div></div>' * 8}</div>
<p class="fuss">Quelle: G. W. Leibniz, Neue Abhandlungen über den menschlichen Verstand, Vorrede (1704), gekürzt.</p>
</body></html>"""


def main():
    z = zeilen()
    with open(os.path.join(HERE, "arbeitsblatt_leibniz.html"), "w", encoding="utf-8") as f:
        f.write(html_seite(z))
    daten = {
        "titel": TITEL, "quelle": QUELLE, "einleitung": EINLEITUNG,
        "zeilen": [x["text"] for x in z], "absatzAnfang": [i for i, x in enumerate(z) if x["neu"]],
        "aufgabeKopf": AUFGABE_KOPF, "aufgabe": AUFGABE, "hinweise": HINWEISE,
    }
    with open(os.path.join(HERE, "leibniz_daten.js"), "w", encoding="utf-8") as f:
        f.write("window.LEIBNIZ = " + json.dumps(daten, ensure_ascii=False) + ";\n")
    os.makedirs(os.path.join(ROOT, "netlify", "lib"), exist_ok=True)
    with open(os.path.join(ROOT, "netlify", "lib", "leibniz.json"), "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=1)
    for n, t in enumerate(daten["zeilen"], 1):
        print(f"{n:2d} {t}")


if __name__ == "__main__":
    main()
