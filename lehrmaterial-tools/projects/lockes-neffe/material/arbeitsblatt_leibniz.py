#!/usr/bin/env python3
# Arbeitsblatt "Die Debatte um die Tabula Rasa" (Leibniz) als eine Quelle fuer alles:
#   material/arbeitsblatt_leibniz.html  -> Lesesaal, Aufgabe 1 (AFB I), wird mit Chromium zur PDF gedruckt (drucke_pdf.js)
#   material/arbeitsblatt_leibniz_analyse.html -> Historischer Salon, Aufgabe 2 (AFB II), ebenso als PDF
#   material/arbeitsblatt_leibniz_kommentar.html -> Buchdruckerei, Aufgabe 3 (AFB III), ebenso als PDF
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

# Historischer Salon: Analyse (AFB II). Erwartungshorizont der Lehrkraft, nicht auf dem Arbeitsblatt.
ANALYSE_KOPF = "Aufgabe 2 (Anforderungsbereich II)"
ANALYSE_AUFGABE = ("Analysieren Sie die Argumentationsstruktur des vorliegenden Textes, indem Sie herausarbeiten, wie Leibniz seine These "
                   "gegen die empiristische Position begründet und mit welchem gedanklichen Ziel er das Gleichnis vom geäderten "
                   "Marmorblock einsetzt.")
ANALYSE_HINWEISE_KOPF = "Hinweise zur Bearbeitung (AFB II)"
ANALYSE_HINWEISE = [
    "Achten Sie auf den Operator „Analysieren Sie …“: Untersuchen Sie den Text kriterienorientiert und systematisch im Hinblick auf "
    "seinen argumentativen Aufbau und die Funktion der sprachlichen Veranschaulichung.",
    "Weisen Sie die gedanklichen Abschnitte und Argumentationsschritte präzise durch Zeilenangaben (bzw. Textstellen) nach.",
    "Stellen Sie explizit heraus, wie Leibniz von der Begrenzung sinnlicher Erfahrung zur Notwendigkeit angeborener "
    "Vernunftprinzipien schlussfolgert.",
]
ANALYSE_ERWARTUNG = """1. Einordnung der Problemstellung und Thesenaufstellung
• Ziel: Gegenüberstellung zweier gegensätzlicher erkenntnistheoretischer Grundkonzepte (Empirismus vs. Rationalismus / Theorie angeborener Ideen).
• Funktion: Leibniz eröffnet den Text mit einer disjunktiven Gegenüberstellung (Entweder-Oder-Logik): Tabula Rasa (Locke) versus angeborene Prinzipien.
2. Rekonstruktion der Argumentationskette (Kritik der Induktion)
• Prämisse 1: Sinneserfahrungen liefern lediglich Aussagen über Einzelnes (Fakten/Induktion).
• Prämisse 2: Aus wiederholten Einzelbeobachtungen lässt sich niemals eine allgemeine, logische Notwendigkeit für die Zukunft ableiten.
• Zwischenschluss: Rein empirische Beobachtung kann die Notwendigkeit und Allgemeingültigkeit von Erkenntnissen nicht begründen.
• Beleg/Exempel: Verweis auf die reine Mathematik (Arithmetik und Geometrie) als Feld notwendiger und universeller Wahrheiten, die nicht bloß aus Sinnesdaten stammen können.
3. Analyse der Funktion der Sprach- und Bildmittel (Marmorblock-Analogie)
• Ungeformter Block / glatte Tafel: symbolisiert das empiristische Modell (Geist als passiver Empfänger).
• Geäderter Marmorblock: symbolisiert das rationalistische Modell (Geist hat eine bereits vorgegebene, innere Struktur/Disposition).
• Arbeit des Bildhauers / Politur: symbolisiert die Sinneserfahrung (sie erschafft das Wissen nicht aus dem Nichts, sondern bringt die latent bereits vorhandenen Adern/Strukturen erst zum Vorschein und zur Klarheit).
• Gedankliches Ziel: Leibniz nutzt das Gleichnis, um zu veranschaulichen, dass Sinneserfahrung und angeborene Ideen keine Gegensätze sein müssen: Sinnesreize sind der Anlass („Aufwecken“), aber nicht das eigentliche Fundament der notwendigen Erkenntnis.
Es müssen nicht alle Aspekte genannt werden. Eine gute Analyse erfasst den Kern der Sache."""

# Buchdruckerei: Stellungnahme (AFB III). Erwartungshorizont der Lehrkraft, nicht auf dem Arbeitsblatt.
KOMMENTAR_KOPF = "Aufgabe 3 (Anforderungsbereich III)"
KOMMENTAR_AUFGABE = ("Nehmen Sie Stellung zu Leibniz' Auffassung, dass empirische Wahrnehmung allein keine allgemeine Notwendigkeit "
                     "begründen könne, indem Sie seine Position kritisch beurteilen und mit John Lockes empiristischem Erkenntnismodell vergleichen.")
KOMMENTAR_HINWEISE_KOPF = "Hinweise zur Bearbeitung (AFB III)"
KOMMENTAR_HINWEISE = [
    "Achten Sie auf den Operator „Nehmen Sie Stellung …“: Es wird eine eigenständige, sachlich fundierte und differenzierte Argumentation gefordert.",
    "Vergleichen Sie die Argumente von Leibniz direkt mit den Gegenargumenten aus Lockes Philosophie (z. B. Rolle der Sensation und Reflexion, "
    "Bildung komplexer Ideen aus einfachen Sinnesdaten).",
    "Binden Sie ein klares Fazit / ein eigenes begründetes Sachurteil am Ende Ihrer Bearbeitung ein.",
]
KOMMENTAR_NOTIZ = "Lockes Texte zum Ursprung der Ideen finden Sie auf dem Arbeitsblatt aus dem Observatorium (John Locke: Der Ursprung der Ideen)."
KOMMENTAR_ERWARTUNG = """1. Vergleich und Kontrastierung der Grundansätze
• Lockes empiristisches Gegenargument: Für Locke entsteht jeglicher Gehalt des Denkens erst durch Erfahrung (Sensation als äußere, Reflexion als innere Wahrnehmung). Abstrakte und allgemeine Begriffe sind keine angeborenen Muster, sondern das Resultat aktiver Verstandestätigkeiten (Kombination, Vergleich und Abstraktion einfacher Ideen).
• Leibniz' Rationalismus: Sinnliche Wahrnehmung ist zwar der zeitliche Anlass, reicht aber logisch nicht aus, um Notwendigkeit und Universalität (z. B. in der Logik und Mathematik) zu begründen.
2. Kritische Abwägung (Beurteilung)
• Pro Leibniz: Das Induktionsproblem spricht für Leibniz: Aus rein wiederholter Beobachtung lässt sich keine Allgültigkeit ableiten (nur weil die Sonne bisher jeden Tag aufgegangen ist, ist das kein rein logischer Beweis für die Zukunft). Das menschliche Denken scheint eigene Stützstrukturen/Kategorien zu benötigen.
• Pro Locke / gegen Leibniz: Das Postulieren „angeborener Ideen“ oder vorgegebener Strukturen riskiert Metaphysik; Lockes Modell ist sparsamer (Ockhams Rasiermesser) und erklärt den Wissenserwerb realistisch über Lernprozesse und Gewöhnung.
3. Abschließendes Synthese- / Sachurteil
• Bündelung der Argumente in einer eigenständigen Schlussfolgerung (z. B. dass Leibniz eine wesentliche Lücke des reinen Empirismus offenlegt, die später auch bei Kant zur Synthese von Anschauung und Begriffen führt).
Es müssen nicht alle Aspekte genannt werden. Welche Position am Ende vertreten wird, ist offen: Entscheidend ist ein begründetes, differenziertes Urteil."""
# Lockes Text (wie auf dem Arbeitsblatt im Observatorium) als Vergleichsgrundlage fuer Spiel und Server
LOCKE = [
    ("Text 1: Der Ursprung der Ideen (Buch II, Kapitel 1)", [
        "Nehmen wir also an, der Geist sei, wie man sagt, ein unbeschriebenes Blatt (tabula rasa), ohne alle Schriftzeichen, frei von allen Ideen. "
        "Wie werden ihm diese zugeführt? Wie gelangt er zu dem gewaltigen Vorrat an Ideen, den die geschäftige Phantasie des Menschen mit einer fast "
        "unbegrenzten Abwechslung auf ihn hinmalt? Woher hat er all das Material für seine Vernunft und seine Erkenntnis? Ich antworte darauf mit einem "
        "einzigen Worte: aus der Erfahrung. Auf sie gründet sich unsere gesamte Erkenntnis, von ihr leitet sie sich letztlich her.",
        "Unsere Beobachtung, die entweder auf äußere sinnlich wahrnehmbare Objekte gerichtet ist oder auf innere Operationen des Geistes, liefert "
        "unserem Verstand das gesamte Material des Denkens. Dies sind die beiden Quellen der Erkenntnis.",
        "Erstens: SENSATION. Unsere Sinne, die auf äußere Objekte gerichtet sind, führen dem Geist verschiedene Ideen von Dingen zu, wie Gelb, Weiß, "
        "Warm, Kalt, Weich, Hart, Bitter und Süß. Diese Quelle nennen wir Sensation. Zweitens: REFLEXION. Die andere Quelle ist die Wahrnehmung der "
        "Operationen unseres eigenen Geistes im Innern, wie Denken, Zweifeln, Glauben, Schließen, Wollen. Diese Quelle nennen wir Reflexion.",
    ]),
    ("Text 2: Der Umfang und die Grenzen unseres Wissens (Buch IV, Kapitel 3)", [
        "Da der Geist keine anderen unmittelbaren Objekte seiner Betrachtung hat als seine eigenen Ideen, so ist es klar, dass unsere Erkenntnis nur auf "
        "diese bezogen ist. Erkenntnis ist nichts anderes als die Wahrnehmung des Zusammenhangs und der Übereinstimmung oder des Widerstreits zwischen unseren Ideen.",
        "Daraus folgt unmittelbar: Erstens: Unser Wissen reicht nicht weiter als unsere Ideen. Zweitens: Unser Wissen ist noch enger als unsere Ideen, "
        "weil wir nicht immer die Übereinstimmung oder Nichtübereinstimmung zwischen ihnen wahrnehmen können. Wir besitzen keine intuitive oder "
        "demonstrative Gewissheit über die unendliche Natur der Dinge. Unser sensitives Wissen erstreckt sich nicht einmal so weit wie unsere "
        "Vorstellungen selbst. Wir tappen in vielen Bereichen der Wirklichkeit völlig im Dunkeln.",
    ]),
]

BREITE = 84  # Zeichen je Textzeile, passt bei 11 pt Serifenschrift sicher in die 172 mm breite Spalte


def zeilen():
    out = []
    for i, a in enumerate(ABSAETZE):
        teile = textwrap.wrap(a, BREITE, break_long_words=False, break_on_hyphens=False)
        for j, t in enumerate(teile):
            out.append({"text": t, "absatz": i, "neu": j == 0})
    return out


def html_seite(z, kopf=AUFGABE_KOPF, aufgabe=AUFGABE, hinweise=HINWEISE, hinweise_kopf=None, notiz=None):
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
.hk {{ font-weight: bold; margin: 8pt 0 0; }}
.aufgabe .notiz {{ margin-top: 6pt; font-style: italic; color: var(--soft); }}
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
<div class="aufgabe"><div class="k">{e(kopf)}</div><p>{e(aufgabe)}</p>
{f'<div class="hk">{e(hinweise_kopf)}</div>' if hinweise_kopf else ''}<ul class="hinweise">{''.join(f'<li>{e(h)}</li>' for h in hinweise)}</ul>
{f'<p class="notiz">{e(notiz)}</p>' if notiz else ''}</div>
<div class="notizen"><h2>Notizen</h2>{'<div></div>' * 8}</div>
<p class="fuss">Quelle: G. W. Leibniz, Neue Abhandlungen über den menschlichen Verstand, Vorrede (1704), gekürzt.</p>
</body></html>"""


def main():
    z = zeilen()
    with open(os.path.join(HERE, "arbeitsblatt_leibniz.html"), "w", encoding="utf-8") as f:
        f.write(html_seite(z))
    with open(os.path.join(HERE, "arbeitsblatt_leibniz_analyse.html"), "w", encoding="utf-8") as f:
        f.write(html_seite(z, ANALYSE_KOPF, ANALYSE_AUFGABE, ANALYSE_HINWEISE, ANALYSE_HINWEISE_KOPF))
    with open(os.path.join(HERE, "arbeitsblatt_leibniz_kommentar.html"), "w", encoding="utf-8") as f:
        f.write(html_seite(z, KOMMENTAR_KOPF, KOMMENTAR_AUFGABE, KOMMENTAR_HINWEISE, KOMMENTAR_HINWEISE_KOPF, KOMMENTAR_NOTIZ))
    daten = {
        "titel": TITEL, "quelle": QUELLE, "einleitung": EINLEITUNG,
        "zeilen": [x["text"] for x in z], "absatzAnfang": [i for i, x in enumerate(z) if x["neu"]],
        "aufgabeKopf": AUFGABE_KOPF, "aufgabe": AUFGABE, "hinweise": HINWEISE,
        "analyse": {"aufgabeKopf": ANALYSE_KOPF, "aufgabe": ANALYSE_AUFGABE, "hinweiseKopf": ANALYSE_HINWEISE_KOPF,
                    "hinweise": ANALYSE_HINWEISE, "erwartung": ANALYSE_ERWARTUNG},
        "kommentar": {"aufgabeKopf": KOMMENTAR_KOPF, "aufgabe": KOMMENTAR_AUFGABE, "hinweiseKopf": KOMMENTAR_HINWEISE_KOPF,
                      "hinweise": KOMMENTAR_HINWEISE, "notiz": KOMMENTAR_NOTIZ, "erwartung": KOMMENTAR_ERWARTUNG},
        "locke": [{"titel": t, "absaetze": a} for t, a in LOCKE],
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
