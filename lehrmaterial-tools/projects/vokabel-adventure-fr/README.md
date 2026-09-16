# Vokabel-Adventure Français

Vokabellernspiel zu Découvertes (Französisch, Jahrgang 8). Single-File-HTML,
kein Build-Schritt — gleiche Architektur und Optik wie `vokabel-adventure`
(Englisch), aber eigenständiges Projekt: eigener localStorage-Key, kein
Duell-Feature, keine Schulname-/Logo-Anzeige.

## Aufbau
- `index.html` ist das komplette Tool in vier Ansichten (ein `showView()`-Router
  blendet die passende `.view` ein, kein Reload):
  - **Startbildschirm**: Fortschrittsanzeige, Tagesserie (Streak), drei Kacheln
    (Kapitel, Übungen, Merkliste — kein Duell), Menü, Optionen, Erfolge, Hilfe,
    geräte-lokale Lehrkraft-Ansicht. Kein Schullogo/-name (auf Wunsch entfernt).
  - **Unit-Ansicht**: die 9 Abschnitte von Teil 1 mit Fortschrittsbalken und
    Abschnitts-Abzeichen (reine Belohnung, kein Gate — wie im Englisch-Tool).
  - **Abschnitts-Ansicht**: Karteikarten (Flip-Karte, „Kann ich schon“ /
    „Muss ich üben“) und Übersicht (durchsuchbare Tabelle mit Merk-Stern) —
    umschaltbar, beide zeigen dieselben Wörter.
  - **Merkliste**: alle gemerkten/noch zu übenden Wörter, manuell entfernbar,
    plus „Merkliste wiederholen“ — identische Logik zum Englisch-Tool.
  - „Übungen“ ist aktuell nur ein Platzhalter-Hinweis (noch nicht gebaut).
- `hero.svg` ist ein **Platzhalter-Titelbild** (stilisierter Eiffelturm) bis
  das endgültige Marianne-Motiv fertig ist.
- `test.js` prüft Startzustand, Streak-Logik, Menü/Modal-Interaktion, die
  komplette Teil-1-Lernstrecke (Abschnitte, Karteikarten, Übersicht,
  Merkliste inkl. Wiederholung und Meisterschafts-Entfernung), Abschnitts-
  Abzeichen, Export und Zurücksetzen via jsdom — sowie explizit, dass keine
  Duell-Kachel/-Menüpunkt und kein Schullogo mehr existieren.

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

## Unterschiede zum Englisch-Tool (auf Wunsch)
- Kein Duell-Feature (Kachel, Menüpunkt, Modal komplett entfernt).
- Kein Schullogo, kein Schulname im Header/Footer.
- Bedienoberfläche bleibt Deutsch (nur die Vokabelinhalte sind Französisch).
- Eigener localStorage-Key (`vokabel_adventure_fr_v1`), eigener Ordner —
  komplett unabhängig vom Englisch-Tool nutzbar.

## Umfang dieser Version / offene Punkte
- **Titelbild**: aktuell nur Platzhalter (`hero.svg`, stilisierter
  Eiffelturm). Das endgültige Marianne-Motiv folgt über den Design-Skill.
- **Spiele**: noch nicht gebaut. Drei Konzept-Prototypen (Artikel-Sortieren
  le/la, Galgenmännchen, Tempo-Runde) wurden als Demo gezeigt — welche(s)
  übernommen wird, ist noch offen.
- **Übungen** (Hör-/Schreibübung, Lückentext): noch nicht gebaut.
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
