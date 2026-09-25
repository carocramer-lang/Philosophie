# Vokabel-Adventure — Green Line 3 (Klasse 7)

Vokabellernspiel zu Green Line 3 G9 (Englisch, Jahrgang 7). Single-File-HTML,
kein Build-Schritt — gleiche Architektur und Optik wie `vokabel-adventure`
(Klasse 8), aber eigenständiges Projekt mit eigenem localStorage-Key und
eigenem Ordner.

Größter Unterschied zu den beiden anderen Tools: Es gibt nicht nur eine
Unit, sondern **alle sechs Kapitel sind von Anfang an vollständig gebaut**
und über „Kapitel“ frei wählbar (kein „folgt später“).

## Aufbau
- `index.html` ist das komplette Tool in fünf Ansichten (ein `showView()`-
  Router blendet die passende `.view` ein, kein Reload):
  - **Startbildschirm**: Fortschrittsanzeige für das aktuell gewählte
    Kapitel, Tagesserie (Streak), vier Kacheln (Kapitel, Spiele, Merkliste,
    Erfolge), Menü, Optionen, Erfolge, Hilfe, geräte-lokale
    Lehrkraft-Ansicht. Kein Duell, keine Übungen (nicht angefragt).
  - **Kapitel-Ansicht**: die Abschnitte des gerade gewählten Kapitels mit
    Fortschrittsbalken und Abschnitts-Abzeichen (reine Belohnung, kein
    Gate).
  - **Abschnitts-Ansicht**: Karteikarten (Flip-Karte, „Kann ich schon“ /
    „Muss ich üben“) und Übersicht (durchsuchbare Tabelle mit Merk-Stern) —
    umschaltbar, beide zeigen dieselben Wörter.
  - **Merkliste**: alle gemerkten/noch zu übenden Wörter über alle Kapitel
    hinweg, manuell entfernbar, plus „Merkliste wiederholen“.
  - **Spiele**: eine Übersicht mit einem Spiel pro Abschnitt des gerade
    gewählten Kapitels (siehe unten), plus die eigentliche Spiel-Ansicht.
- `hero.svg` ist das Titelbild: eine schlichte Union-Jack-Flagge als
  Platzhalter (auf Wunsch — das endgültige Titelbild wird später ersetzt).
- `test.js` prüft Startzustand, Streak-Logik, Menü/Modal-Interaktion, das
  Kapitel-Modal (alle 6 Kapitel klickbar, Kapitelwechsel), die komplette
  Lernstrecke (Abschnitte, Karteikarten, Übersicht, Merkliste), alle drei
  Spieltypen, Abschnitts-Abzeichen, Erfolge, Export und Zurücksetzen via
  jsdom.

## Vokabelquelle
Die „Vocabulary“-Sektion von Green Line 3 G9 (Klasse 7), Seiten 192–232 der
PDF. Extraktion per PyMuPDF, anhand Schriftschnitt/-position der drei Spalten
(fettes Stichwort, reguläre deutsche Übersetzung, kursiver/leichter
Beispielsatz) sowie der grünen Kapitel-/Abschnittsüberschriften (Unit N,
TMS N = „Text and media smart“, AC N = „Across cultures“, Trailer N, jeweils
mit Check-in/Station/Skills/Unit task/Story/Action UK!/Check-out).

Ausgeschlossen wurden:
- die Dictionary-Randspalten-Referenzkästen ohne Beispielsatz (z. B.
  „Monarchy words“, „Time words“, „Travel words“, „Nouns and verbs with the
  same form“, „History words“) — sie folgen nicht dem Wort|Bedeutung|Satz-
  Muster und sind reines Nachschlagematerial,
- die „Aufgabe“-Übungsseiten (Lautschrift-Zuordnung, Rechtschreibaufgaben) —
  keine Vokabeltabelle,
- Kopf-/Fußzeilen (laufender Seitentitel, Seitenzahlen).

**833 Wortpaare** wurden extrahiert. Sechs Wörter kamen im Buch doppelt vor:
drei mit identischer Bedeutung wurden automatisch zusammengeführt (die
spätere Dopplung entfernt: `husband`, `travel`, `to fly, flew, flown`), drei
mit unterschiedlicher Bedeutung wurden disambiguiert wie im Englisch-Tool
(`vegetarian` → `vegetarian (= Person)` / `vegetarian (= Adjektiv)`, ebenso
`official` und `view`).

## Kapitel: 4 Units + 2 Zusatzunits
Der Nutzer wünschte ausdrücklich **4 Units und 2 separate Zusatzunits**
(anders als beim Englisch-Tool, wo die „Across cultures“-Kapitel jeweils in
die folgende Unit eingerechnet wurden). Die Zwischenkapitel des Buchs (TMS,
AC, Trailer) wurden dafür thematisch zu zwei Zusatzunits gebündelt:

1. **Unit 1** — Find your place
2. **Unit 2** — Let's go to Scotland!
3. **Unit 3** — What was it like?
4. **Unit 4** — On the move
5. **Zusatzunit 1: Text and media smart** — TMS 1 (Songs and poems) +
   TMS 2 (On- & offline communication)
6. **Zusatzunit 2: Across cultures & Trailer** — AC 1–3 (Reacting to a new
   situation, Making small talk, Dos and don'ts) + Trailer 1–3 (Walking in
   the Highlands feels great!, Robin Hood's diary, A trip to Dublin)

Diese Gruppierung ist eine sinnvolle, aber freie Zuordnung (das Buch selbst
nennt keine „2 Zusatzunits“) — bei Bedarf lässt sich die Aufteilung in
`GROUPS`/`DATA` in `index.html` leicht ändern.

Jedes Kapitel ist in Abschnitte von ca. 20 Wörtern gegliedert (`DATA[id].
sections`), die den Unterüberschriften des Buchs folgen (Check-in, Station
N, Skills, Unit task, Story, Action UK!, Check-out). Längere Unterkapitel
wurden in zwei bzw. vier gleich große Teile gesplittet (z. B. „Check-in
(1/2)“), sehr kurze mit dem direkten Nachbarabschnitt zusammengelegt — beides
automatisiert, mit „ca. 20, ggf. kürzer“ als Zielgröße. Insgesamt **49
Abschnitte** zwischen 9 und 23 Wörtern.

## Lern- und Merklisten-Logik
Wie im Englisch-Tool (Klasse 8): **Karteikarten-Vorderseite zeigt zuerst
Deutsch**, beim Umdrehen erscheint Englisch. Die **Übersicht bleibt
Englisch-first** (Spalte 1 Englisch, Spalte 2 Deutsch) — dieselbe Konvention,
die die SuS aus dem Klasse-8-Tool schon kennen.

Karteikarte umdrehen per Klick/Leertaste, „Kann ich schon“/„Muss ich üben“
steuern Merkliste und Meisterschaft (2× erfolgreiche Wiederholung → Wort
verschwindet von der Merkliste, bleibt aber im Abschnitt mit dauerhaftem
Gekonnt-Häkchen stehen), Stern in der Übersicht schaltet die Merkliste
direkt um, Abschnitts-Abzeichen sind reine Belohnung ohne Gate. Der
Fortschritt (`wordAssessments`) ist global über alle 6 Kapitel hinweg
gespeichert; die Fortschrittsanzeige im Startbildschirm bezieht sich auf das
gerade gewählte Kapitel, Erfolge/Lehrkraft-Ansicht/Export zeigen die Summe
über alle Kapitel.

## Spiele
Genau die drei angefragten Spiele, pro Abschnitt fest zugeordnet und
durchwechselnd (Memory → Galgenmännchen → Tempo-Runde → Memory → …). Alle
Inhalte kommen aus den vorhandenen Vokabeln des jeweiligen Abschnitts.

- **Memory** (deutsch/englisch-Paare statt Emoji, da GL3-Vokabular oft zu
  abstrakt für ein Emoji-Rätsel ist — z. B. „unnecessary“, „purpose“,
  „conflict“): 8 Wortpaare (bzw. weniger bei kürzeren Abschnitten), Karten
  zeigen Kurzform des deutschen bzw. englischen Worts, passende Paare
  finden.
- **Galgenmännchen**: ein englisches Wort Buchstabe für Buchstabe erraten
  (nur a–z, keine Sonderzeichen nötig), deutsche Bedeutung als
  Dauer-Hinweis, 6 Fehlversuche erlaubt. Wortpool: alle Wörter des
  Abschnitts, deren Stichwort (nach Entfernen von „to “ und Klammerzusätzen)
  ein einzelnes reines Buchstabenwort ist — mehrteilige Wendungen wie „to
  wake up, woke up, woken up“ fallen dafür automatisch raus.
- **Tempo-Runde**: 60-Sekunden-Sprint durch die Wörter des Abschnitts — das
  deutsche Wort erscheint, die englische Übersetzung per Multiple-Choice
  wählen (4 Optionen), Punktezähler läuft mit, am Ende Endstand mit
  Neustart-Option.

Galgenmännchen und Tempo-Runde fragen beide von Deutsch (Hinweis/Frage) nach
Englisch (zu erratendes/zu wählendes Wort) — konsistent mit der
Karteikarten-Richtung.

Erreichbar über „Spiele“ im Hauptmenü → Abschnitt auswählen. Fortschritt in
den Spielen selbst wird aktuell nicht gespeichert (kein Einfluss auf
Karteikarten/Übersicht/Merkliste) — reines Zusatzangebot zum Üben.

## Unterschiede zum Englisch-Tool (Klasse 8)
- Alle 6 Kapitel von Anfang an vollständig gebaut und wählbar (kein
  „folgt später“) — passend zur ausdrücklichen Anfrage, die komplette
  Struktur auf einmal umzusetzen.
- 4 Units + 2 separate Zusatzunits statt 4 Units mit eingerechneten
  „Across cultures“-Kapiteln.
- Andere Spiele: Memory, Galgenmännchen, Tempo-Runde statt Memory,
  Zuordnung, Wahr/Falsch.
- Kein Duell-Feature, keine Übungen (Hör-/Schreibübung, Lückentext) — beide
  nicht angefragt.
- Eigener localStorage-Key (`vokabel_adventure_klasse7_v1`), eigener
  Ordner — komplett unabhängig von den beiden anderen Tools nutzbar.
- „Jahrgang 7“ statt „Jahrgang 8“ im Header, Buch-Badge „Green Line 3“.

## Umfang dieser Version / offene Punkte
- **Titelbild**: aktuell nur eine schlichte Union-Jack-Flagge als
  Platzhalter (`hero.svg`), auf ausdrücklichen Wunsch — ein gestaltetes
  Titelbild folgt später.
- Achievements/Teacher-View/Export sind bewusst global über alle Kapitel
  ausgelegt (nicht pro Kapitel), da sich „Vokabeln gelernt“ auf das ganze
  Schuljahr bezieht.

## Persistenz
localStorage-Key `vokabel_adventure_klasse7_v1`. Enthält `currentGroupId`,
`wordAssessments`, `merkliste` (mit `reviewCount`) und `badgesSeen`. Vor
Geräte- oder Browserwechsel über „Optionen → Fortschritt exportieren“
sichern.

## Test
Aus dem Repo-Wurzelverzeichnis: `npm test` (bzw. `node
lehrmaterial-tools/tools/run-tests.js`). Oder direkt:
`node projects/vokabel-adventure-klasse7/test.js`.

## Deploy
`index.html` und `hero.svg` gemeinsam im gleichen Ordner hochladen.
