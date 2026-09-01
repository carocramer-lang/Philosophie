# Vokabel-Adventure

Vokabellernspiel zu Green Line 4 (Englisch, Jahrgang 8). Single-File-HTML,
kein Build-Schritt. Startbildschirm nach Design-Vorlage aus Claude Design,
Unit 1 komplett mit Vokabeln aus `Vokabelübersicht_GL4.pdf`.

## Aufbau
- `index.html` ist das komplette Tool in acht Ansichten (ein `showView()`-Router
  blendet die passende `.view` ein, kein Reload):
  - **Startbildschirm**: Fortschrittsanzeige, Tagesserie (Streak), vier Kacheln
    (Kapitel, Übungen, Merkliste, Duell), Menü (inkl. „Spiele“), Optionen,
    Erfolge, Hilfe, geräte-lokale Lehrkraft-Ansicht.
  - **Unit-Ansicht**: die 10 Abschnitte von Unit 1 mit Fortschrittsbalken. Ist
    ein Abschnitt vollständig geübt, poppt einmalig (Pop-Animation + Toast)
    ein Abzeichen „Geschafft: Unit 1 · <Abschnitt>!“ auf der Karte auf — reine
    Belohnung, kein Gate: alle Abschnitte bleiben jederzeit frei anklickbar.
  - **Abschnitts-Ansicht**: Karteikarten (Flip-Karte, „Kann ich schon“ /
    „Muss ich üben“) und Übersicht (durchsuchbare Tabelle mit Merk-Stern) —
    umschaltbar, beide zeigen dieselben Wörter.
  - **Merkliste**: alle gemerkten/noch zu übenden Wörter, manuell entfernbar,
    plus „Merkliste wiederholen“ (Karteikarten-Modus nur für diese Wörter).
  - **Spiele**: eine Übersicht mit einem Spiel pro Abschnitt (siehe unten),
    plus die eigentliche Spiel-Ansicht.
  - **Übungen**: eine Übersicht mit Hörübung, Schreibübung und Lückentext pro
    Abschnitt (siehe unten), als Tabs in derselben Abschnitts-Ansicht.
  - Keine externen Abhängigkeiten außer Google Fonts (fällt offline auf
    Systemschriften zurück) und dem Schullogo (fällt bei Netzwerkfehler auf
    einen Text-Badge zurück).
- `hero.jpg` ist die Maskottchen-Illustration aus der Design-Vorlage, für die
  Auslieferung als JPEG komprimiert (aus 1,4 MB PNG → ~145 KB).
- `test.js` prüft Startzustand, Streak-Logik, Menü/Modal-Interaktion, die
  komplette Unit-1-Lernstrecke (Abschnitte, Karteikarten, Übersicht,
  Merkliste inkl. Wiederholung und Meisterschafts-Entfernung), Spiele,
  Übungen (Datenintegrität, Navigation, Multiple-Choice-Umschaltung,
  Lückentext-Bewertung), Erfolge, Export und Zurücksetzen via jsdom.

## Units (Green Line 4)
Vier Units. Die vier „Across cultures“-Zwischenkapitel des Buchs bekommen
keine eigene Unit, sondern werden vokabelseitig der folgenden Unit
zugeschlagen:

1. **Living in America** (mit „The USA: Country of contrasts“) — vollständig
   mit Vokabeln hinterlegt, siehe unten.
2. A nation invents itself (mit „School life – dos and don'ts“) — noch ohne Vokabeln.
3. City of dreams: New York (mit „At home with an American family“) — noch ohne Vokabeln.
4. The Pacific Northwest (mit „What you say and how you say it“) — noch ohne Vokabeln.

Die Liste steht als `UNITS`-Array oben im Skript (Kapitel-Kachel/-Modal).
Im Kapitel-Modal ist nur Unit 1 anklickbar, Units 2–4 sind sichtbar aber als
„folgt später“ markiert — wir arbeiten Unit für Unit.

## Unit 1: Vokabeln
`UNIT1_SECTIONS` (im Skript, aus `Vokabelübersicht_GL4.pdf` extrahiert, keine
Buchtexte/Beispielsätze übernommen — nur die Wort-Übersetzungs-Paare) in
10 Abschnitten von ca. 20 Wörtern, nach Buchstruktur benannt:

Einstieg (1/3–3/3) · Check-in · Station 1 (1/2–2/2) · Station 2 · Station 3 ·
Story: Nightmare at the mall! · Skills & Unit task — zusammen 189 Wörter.

Ein Homonym-Paar (`right` = „Recht“ vs. „direkt; genau“) wurde zur eindeutigen
Karteikarten-Zuordnung als `right (= exactly)` disambiguiert.

## Lern- und Merklisten-Logik
- **Karteikarte umdrehen**: Klick/Tippen oder Leertaste. Pfeiltasten/Buttons
  blättern weiter.
- **„Kann ich schon“**: zählt das Wort als gelernt (`wordAssessments`). Steht
  das Wort zu diesem Zeitpunkt auf der Merkliste, zählt das als eine
  erfolgreiche Wiederholung.
- **„Muss ich üben“**: das Wort landet (neu) auf der Merkliste, ein
  begonnener Wiederholungs-Fortschritt wird zurückgesetzt.
- **Stern in der Übersicht**: schaltet die Merkliste direkt um (an/aus) —
  unabhängig von „Kann ich schon“/„Muss ich üben“.
- **Meisterschaft**: nach 2× erfolgreicher Wiederholung (`MASTERY_REPEATS`)
  verschwindet ein Wort von der Merkliste — bleibt aber ganz normal im
  Abschnitt (Karteikarten/Übersicht) stehen, für Wiederholung z. B. vor
  einer Klassenarbeit. In der Übersicht markiert ein dauerhaftes grünes
  Häkchen jedes Wort, das mindestens einmal als „Kann ich schon“ bewertet
  wurde — unabhängig vom Stern/Merkliste-Status, verschwindet also nicht
  mit der Merkliste.
- **Manuelles Entfernen**: jeder Merkliste-Eintrag hat einen eigenen
  Entfernen-Button — SuS können jederzeit selbst aufräumen.
- **Merkliste wiederholen**: eigener Karteikarten-Durchlauf nur über die
  aktuelle Merkliste, mit derselben Bewertungslogik.
- **Abschnitts-Abzeichen**: rein motivational, kein Gate. Sobald ein Abschnitt
  vollständig geübt ist (jedes Wort mindestens einmal bewertet), erscheint auf
  der Karte in der Unit-Ansicht einmalig ein Abzeichen mit Pop-Animation und
  Toast „Geschafft: Unit 1 · <Abschnitt>!“. Alle Abschnitte bleiben davon
  unabhängig jederzeit frei anklickbar (freies Tempo bleibt erhalten). Der
  „gesehen“-Status wird dauerhaft gespeichert (`badgesSeen`), damit die
  Animation nicht bei jedem Besuch erneut abspielt.

## Spiele
Ein Spiel pro Abschnitt (`SECTION_GAMES`, 1:1 zu `UNIT1_SECTIONS`), Typ
wechselt bewusst durch: Memory → Zuordnung → Wahr/Falsch → Memory → …
(nie zweimal derselbe Typ direkt hintereinander). Alle Inhalte kommen aus
den vorhandenen Vokabellisten; nur die Wahr/Falsch-Aussagen und ihre
Erklärungen sind selbst formuliert (nicht aus dem Buch übernommen).

- **Memory** (Abschnitte 1, 4, 7, 10): 8 Wortpaare mit passendem Emoji,
  verdeckte Karten mit Flip-Animation, Paar- und Zug-Zähler. Zwei
  aufgedeckte gleiche Karten bleiben offen (grün), ungleiche drehen sich
  nach kurzer Verzögerung zurück.
- **Zuordnung** (Abschnitte 2, 5, 8): links 8 englische Begriffe, rechts
  ihre deutschen Übersetzungen (gemischt). Klick links + Klick rechts
  bildet ein Paar; richtig wird grün und gesperrt, falsch blinkt kurz rot
  und beide werden wieder frei wählbar.
- **Wahr/Falsch** (Abschnitte 3, 6, 9): 8 selbst geschriebene
  Englisch-Aussagen pro Abschnitt, je mit True/False-Buttons. Nach der
  Antwort sofort Feedback in Grün/Rot mit kurzer Erklärung auf Englisch,
  die Buttons sind danach für diese Aussage gesperrt; „›“ blättert weiter.

Erreichbar über „Spiele“ im Hauptmenü → Abschnitt auswählen. Fortschritt in
den Spielen selbst wird aktuell nicht gespeichert (kein Einfluss auf
Karteikarten/Übersicht/Merkliste) — reines Zusatzangebot zum Üben.

## Übungen
Drei Übungstypen pro Abschnitt (`SECTION_EXERCISES`, 1:1 zu
`UNIT1_SECTIONS`), als Tabs nebeneinander in derselben Ansicht wählbar —
alle Beispielsätze, Hinweise und der Lückentext-Fließtext sind selbst
formuliert (nicht aus dem Buch übernommen), nur die Zielwörter stammen aus
den vorhandenen Vokabellisten:

- **Hörübung**: alle Wörter des Abschnitts (Lautsprecher-Button + Web
  Speech API des Browsers, spielt beim Öffnen der Karte automatisch einmal
  ab). Wort eintippen, „Prüfen“ vergleicht ohne Rücksicht auf Groß-/
  Kleinschreibung.
- **Schreibübung**: 8 kuratierte Wörter pro Abschnitt, je in einem
  selbst geschriebenen Lückensatz auf Englisch mit optionalem Hint
  („💡 Hint“ zeigt eine englische Bedeutungserklärung, kein deutsches
  Wort).
- **Lückentext**: ein zusammenhängender, selbst verfasster englischer
  Fließtext pro Abschnitt mit mehreren Lücken direkt im Text. Ein
  „Prüfen“-Button färbt jedes Eingabefeld grün (richtig) oder rot
  (falsch, aber ausgefüllt) — leere Felder bleiben neutral. „Zurücksetzen“
  leert alle Felder wieder.

Bei Hör- und Schreibübung gilt dieselbe Regel: nach 2× falscher
Texteingabe schaltet die Aufgabe automatisch auf Multiple-Choice (die
richtige Antwort + 3 zufällige Distraktoren aus demselben Abschnitt) um,
bis die richtige Antwort ausgewählt wird. Erreichbar über die Kachel
„Übungen“ auf dem Startbildschirm oder „Übungen“ im Hauptmenü →
Abschnitt auswählen. Fortschritt wird aktuell nicht gespeichert (wie bei
den Spielen) — reines Zusatzangebot zum Üben.

## Umfang dieser Version
Start- und Unit-1-Lernstrecke sind funktional umgesetzt und getestet. Offen:
- Vokabeln für Units 2–4 (und damit auch: Spiele/Übungen für Units 2–4).
- Teacher-Freischaltung units-übergreifend („erst wenn ich freigebe“) — bislang
  nicht nötig, da nur Unit 1 Inhalte hat. Geplanter Ansatz laut Absprache:
  innerhalb einer Unit bleibt alles frei (siehe Abschnitts-Abzeichen oben), nur
  der Übergang zur nächsten Unit wird von der Lehrkraft manuell freigegeben
  (Signal dafür: alle Abzeichen einer Unit gesammelt, sichtbar in der
  Lehrkraft-Ansicht) — noch nicht gebaut, da Unit 2 noch keine Vokabeln hat.
- Duell gegen andere Klassen ist bewusst zurückgestellt, bis Partnerklassen
  feststehen — die Kachel bleibt als „folgt später“-Hinweis stehen.

Anders als in der ursprünglichen Design-Vorlage (Beispielwerte: Unit 3,
62/100 Vokabeln, 4 Tage Serie, 14 Wörter auf der Merkliste) startet die
ausgelieferte Version mit einem echten leeren Zustand (Unit 1 · Living in
America, 0/189, „Loslegen“), damit keine erfundenen Lernstände angezeigt
werden. Optik, Layout und Farben folgen der Vorlage 1:1.

## Persistenz
localStorage-Key `vokabel_adventure_v1`. Enthält `wordAssessments` (Wort →
„know“/„practice“), `merkliste` (mit `reviewCount`) und `badgesSeen` (welche
Abschnitts-Abzeichen ihre Animation schon gezeigt haben). Vor Geräte- oder
Browserwechsel über „Optionen → Fortschritt exportieren“ sichern.

## Test
Aus dem Repo-Wurzelverzeichnis: `npm test`. Oder direkt: `node projects/vokabel-adventure/test.js`.

## Deploy
`index.html` und `hero.jpg` gemeinsam bei AWS Amplify hochladen (gleicher Ordner).
