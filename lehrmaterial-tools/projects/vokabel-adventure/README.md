# Vokabel-Adventure — Startbildschirm

Startbildschirm für ein geplantes Vokabellernspiel zu Green Line 4 (Englisch, Jahrgang 8,
Unit "In and around the US"). Single-File-HTML nach Design-Vorlage aus Claude Design
("Vokabel-Adventure Startbildschirm"), Maskottchen-Illustration als lokales Asset.

## Aufbau
- `index.html` ist der komplette Startbildschirm: Fortschrittsanzeige, Tagesserie (Streak),
  vier Kacheln (Kapitel, Übungen, Merkliste, Duell), Menü, Optionen, Erfolge, Hilfe und
  eine geräte-lokale Lehrkraft-Ansicht. Keine externen Abhängigkeiten ausser Google Fonts
  (fällt offline auf Systemschriften zurück) und dem Schullogo (fällt bei Netzwerkfehler
  auf einen Text-Badge zurück).
- `hero.jpg` ist die Maskottchen-Illustration aus der Design-Vorlage, für die Auslieferung
  als JPEG komprimiert (aus 1,4 MB PNG → ~145 KB).
- `test.js` prüft Startzustand, Streak-Logik, Menü/Modal-Interaktion, Erfolge, Export und
  Zurücksetzen via jsdom.

## Units
Vier Units nach `Vokabelübersicht_GL4.pdf`. Die vier „Across cultures“-Zwischenkapitel des
Buchs bekommen keine eigene Unit, sondern werden vokabelseitig der folgenden Unit
zugeschlagen:

1. Living in America (mit „The USA: Country of contrasts“)
2. A nation invents itself (mit „School life – dos and don’ts“)
3. City of dreams: New York (mit „At home with an American family“)
4. The Pacific Northwest (mit „What you say and how you say it“)

Die Liste steht als `UNITS`-Array oben im Skript und wird von der Kapitel-Kachel und dem
Kapitel-Modal gelesen — für die eigentlichen Vokabelinhalte pro Unit fehlt noch die
Zuordnung der Wörter aus der PDF.

## Umfang dieser Version
Nur der Startbildschirm ist funktional umgesetzt. Übungen und Merkliste-Funktionen sind
noch offen (siehe frühere Konversation zu Aufgabentypen und Freischalt-Logik). Das Duell
gegen andere Klassen ist bewusst zurückgestellt, bis Partnerklassen feststehen — die
Kachel bleibt als „folgt später“-Hinweis stehen. Bereits echt und getestet:
- Kapitelübersicht mit den vier echten Units (siehe oben).
- Tagesserie (Streak), die bei jedem Besuch tagesgenau und idempotent fortgeschrieben wird.
- Erfolge, abgeleitet aus dem gespeicherten Fortschritt.
- Fortschritt exportieren (.json) und Fortschritt zurücksetzen, unter „Optionen“.
- Lehrkraft-Ansicht zeigt den lokalen Gerätestand (kein geräteübergreifendes Tracking,
  siehe `docs/konventionen.md`).

Anders als in der Design-Vorlage (Beispielwerte: Unit 3, 62/100 Vokabeln, 4 Tage Serie,
14 Wörter auf der Merkliste) startet die ausgelieferte Version mit einem echten leeren
Zustand (Unit 1 · Living in America, 0/100, „Loslegen“), damit keine erfundenen
Lernstände angezeigt werden. Optik, Layout und Farben folgen der Vorlage 1:1.

## Persistenz
localStorage-Key `vokabel_adventure_v1`. Vor Geräte- oder Browserwechsel über
„Optionen → Fortschritt exportieren“ sichern.

## Test
Aus dem Repo-Wurzelverzeichnis: `npm test`. Oder direkt: `node projects/vokabel-adventure/test.js`.

## Deploy
`index.html` und `hero.jpg` gemeinsam bei AWS Amplify hochladen (gleicher Ordner).
