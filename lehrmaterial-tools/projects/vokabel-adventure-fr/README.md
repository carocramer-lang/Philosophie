# Vokabel-Adventure Français

Vokabellernspiel zu Découvertes (Französisch, Jahrgang 8). Single-File-HTML,
kein Build-Schritt — gleiche Architektur und Optik wie `vokabel-adventure`
(Englisch), aber eigenständiges Projekt: eigener localStorage-Key, kein
Duell-Feature, keine Schulname-/Logo-Anzeige.

## Aufbau
- `index.html` ist das komplette Tool in sechs Ansichten (ein `showView()`-Router
  blendet die passende `.view` ein, kein Reload):
  - **Startbildschirm**: Fortschrittsanzeige, Tagesserie (Streak), drei Kacheln
    (Kapitel, Übungen, Merkliste — kein Duell), Menü (inkl. „Spiele“), Optionen,
    Erfolge, Hilfe, geräte-lokale Lehrkraft-Ansicht. Kein Schullogo/-name (auf
    Wunsch entfernt).
  - **Unit-Ansicht**: die 9 Abschnitte von Teil 1 mit Fortschrittsbalken und
    Abschnitts-Abzeichen (reine Belohnung, kein Gate — wie im Englisch-Tool).
  - **Abschnitts-Ansicht**: Karteikarten (Flip-Karte, „Kann ich schon“ /
    „Muss ich üben“) und Übersicht (durchsuchbare Tabelle mit Merk-Stern) —
    umschaltbar, beide zeigen dieselben Wörter.
  - **Merkliste**: alle gemerkten/noch zu übenden Wörter, manuell entfernbar,
    plus „Merkliste wiederholen“ — identische Logik zum Englisch-Tool.
  - **Spiele**: eine Übersicht mit einem Spiel pro Abschnitt (siehe unten),
    plus die eigentliche Spiel-Ansicht.
  - **Übungen**: eine Übersicht mit einem Lückentext pro Abschnitt (siehe
    unten); Hör- und Schreibübung folgen noch.
- `hero.svg` ist ein **Platzhalter-Titelbild** (stilisierter Eiffelturm) bis
  das endgültige Marianne-Motiv fertig ist.
- `test.js` prüft Startzustand, Streak-Logik, Menü/Modal-Interaktion, die
  komplette Teil-1-Lernstrecke (Abschnitte, Karteikarten, Übersicht,
  Merkliste inkl. Wiederholung und Meisterschafts-Entfernung), Spiele,
  Übungen (Lückentext-Bewertung), Abschnitts-Abzeichen, Export und
  Zurücksetzen via jsdom — sowie explizit, dass keine Duell-Kachel/
  -Menüpunkt und kein Schullogo mehr existieren.

## Vokabelquelle
`Vokabeln_Franzoesisch_Deutsch.pdf` — eine durchgehende Französisch-Deutsch-
Liste ohne eigene Kapitel-/Lektionsnamen (anders als bei Green Line 4).
Extraktion per PyMuPDF (Spalten anhand Schriftschnitt/-position: Französisch
fett bei x≈68, Deutsch regulär bei x≈280).

- **712 Wortpaare** roh extrahiert, davon **44 doppelte** Einträge gefunden:
  - 33 exakte Duplikate → automatisch zusammengeführt (ein Eintrag behalten).
  - 9 mit nur leicht abweichender Formulierung, gleiche Bedeutung → ebenfalls
    zusammengeführt (jeweils die vollständigere Übersetzung behalten).
  - 2 mit echt unterschiedlicher Bedeutung → disambiguiert wie beim Englisch-
    Tool (`right` → `right (= exactly)`): **„un site“** → `un site (= Website)`
    / `un site (= Lage/Ort)`, **„un plat“** → `un plat (= Gericht)` /
    `un plat (= Schale)`.
  - Ergebnis: **665 eindeutige Wortpaare** ohne doppelte Karteikarten-Schlüssel.

## Teile (fortlaufend statt Buchkapitel)
Da die PDF keine Kapitelnamen liefert, sind die Vokabeln fortlaufend in vier
„Teile“ von ca. 165–180 Wörtern gegliedert (`UNITS`-Array):

1. **Wörter 1–180** — vollständig mit Vokabeln hinterlegt, siehe unten.
2. Wörter 181–ca. 340 — noch ohne Vokabeln.
3. Wörter ca. 341–ca. 500 — noch ohne Vokabeln.
4. Wörter ca. 501–665 — noch ohne Vokabeln.

Im Kapitel-Modal ist nur Teil 1 anklickbar, Teile 2–4 sind sichtbar aber als
„folgt später“ markiert.

## Teil 1: Vokabeln
`UNIT1_SECTIONS` (180 Wörter aus der PDF, in der PDF-Reihenfolge) in 9
Abschnitten von je genau 20 Wörtern, fortlaufend benannt „Abschnitt 1“–
„Abschnitt 9“ (keine thematischen Titel, da die Quelle keine liefert).

## Lern- und Merklisten-Logik
Identisch zum Englisch-Tool (`vokabel-adventure`): Karteikarte umdrehen per
Klick/Leertaste, „Kann ich schon“/„Muss ich üben“ steuern Merkliste und
Meisterschaft (2× erfolgreiche Wiederholung → Wort verschwindet von der
Merkliste, bleibt aber im Abschnitt mit dauerhaftem Gekonnt-Häkchen stehen),
Stern in der Übersicht schaltet die Merkliste direkt um, Abschnitts-Abzeichen
sind reine Belohnung ohne Gate. Details siehe README von `vokabel-adventure`.

## Spiele
Ein Spiel pro Abschnitt (`SECTION_GAMES`, 1:1 zu `UNIT1_SECTIONS`), Typ
wechselt bewusst durch: Tempo-Runde → Artikel-Sortieren → Galgenmännchen →
Tempo-Runde → … (nie zweimal derselbe Typ direkt hintereinander, jeder Typ
kommt 3× vor). Alle Inhalte kommen aus den vorhandenen Vokabeln des
jeweiligen Abschnitts.

- **Artikel-Sortieren „le/la“** (Abschnitte 2, 5, 7): ein französisches
  Substantiv (ohne Artikel) erscheint, per Klick in den „le“- oder „la“-Korb
  einsortieren. Richtig färbt den Korb grün, falsch rot mit sofortiger
  Anzeige der Lösung. Trainiert gezielt das grammatische Geschlecht — anders
  als beim Englisch-Tool eine französisch-spezifische Übung. Pro Abschnitt
  alle Substantive mit eindeutigem „le“/„la“ bzw. „un“/„une“ (6–12 je nach
  Abschnitt).
- **Galgenmännchen** (Abschnitte 3, 6, 9): ein einzelnes französisches Wort
  Buchstabe für Buchstabe erraten (inkl. Akzentbuchstaben é/è/ê/à/â/ç/û/î/ï/
  ô/œ als Tasten), deutsche Bedeutung als Dauer-Hinweis, 6 Fehlversuche
  erlaubt. Wortpool: einzelne Substantive (ohne Artikel) plus einzelne
  Adjektive/Verben des Abschnitts ohne Leerzeichen.
- **Tempo-Runde** (Abschnitte 1, 4, 8): 60-Sekunden-Sprint durch alle 20
  Wörter des Abschnitts, Multiple-Choice-Bedeutung wählen (4 Optionen),
  Punktezähler läuft mit, am Ende Endstand mit Neustart-Option.

Erreichbar über „Spiele“ im Hauptmenü → Abschnitt auswählen. Fortschritt in
den Spielen selbst wird aktuell nicht gespeichert (kein Einfluss auf
Karteikarten/Übersicht/Merkliste) — reines Zusatzangebot zum Üben.

## Übungen
Ein selbst verfasster Lückentext pro Abschnitt (`SECTION_CLOZE`, 1:1 zu
`UNIT1_SECTIONS`) — ein zusammenhängender französischer Fließtext mit
Lücken direkt im Text (Format `{Lösung}`), baut auf den Vokabeln des
jeweiligen Abschnitts auf. Kein Text ist aus dem Lehrwerk übernommen.

Ein „Prüfen“-Button färbt jedes Eingabefeld grün (richtig) oder rot
(falsch, aber ausgefüllt) — Groß-/Kleinschreibung ist egal, leere Felder
bleiben neutral. „Zurücksetzen“ leert alle Felder wieder. Erreichbar über
„Übungen“ im Hauptmenü → Abschnitt auswählen. Hör- und Schreibübung mit
echter französischer Aussprache sind in Recherche (siehe unten).

## Unterschiede zum Englisch-Tool (auf Wunsch)
- Kein Duell-Feature (Kachel, Menüpunkt, Modal komplett entfernt).
- Kein Schullogo, kein Schulname im Header/Footer.
- Bedienoberfläche bleibt Deutsch (nur die Vokabelinhalte sind Französisch).
- Eigener localStorage-Key (`vokabel_adventure_fr_v1`), eigener Ordner —
  komplett unabhängig vom Englisch-Tool nutzbar.

## Umfang dieser Version / offene Punkte
- **Titelbild**: aktuell nur Platzhalter (`hero.svg`, stilisierter
  Eiffelturm). Das endgültige Marianne-Motiv wird über den Design-Skill
  gestaltet.
- **Hör-/Schreibübung mit echter französischer Aussprache**: in Recherche —
  die Web Speech API liefert nur synthetische Stimmen, eine Alternative mit
  echten Muttersprachler-Aufnahmen wird geprüft.
- **Teile 2–4** (ca. 485 weitere Wörter): noch nicht gebaut, folgen
  schrittweise wie Teil 1.

## Persistenz
localStorage-Key `vokabel_adventure_fr_v1`. Enthält `wordAssessments`,
`merkliste` (mit `reviewCount`) und `badgesSeen`. Vor Geräte- oder
Browserwechsel über „Optionen → Fortschritt exportieren“ sichern.

## Test
Aus dem Repo-Wurzelverzeichnis: `npm test`. Oder direkt:
`node projects/vokabel-adventure-fr/test.js`.

## Deploy
`index.html` und `hero.svg` (bzw. das finale Titelbild) gemeinsam im
gleichen Ordner hochladen.
