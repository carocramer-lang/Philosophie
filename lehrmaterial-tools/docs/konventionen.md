# Konventionen

## Architektur
- Ein Tool, eine Datei: `projects/<name>/index.html`, in sich geschlossen, keine Build-Pipeline.
- Externe Ressourcen nur, wenn sie offline sauber degradieren (z. B. Google Fonts mit System-Fallback).

## Persistenz
- localStorage-Key nach Schema `<projekt>_v<n>`, die Version bei Schema-Aenderungen hochzaehlen.
- Neue Felder abwaertskompatibel ergaenzen, Altdaten duerfen nicht brechen.
- Immer Export anbieten. localStorage ist an Browser und Geraet gebunden, SuS vor Cache-Loeschen oder Geraetewechsel warnen.

## Barrierefreiheit und Robustheit
- Tastaturbedienung (Space/Enter fuer Weiter), sichtbarer Fokus.
- `prefers-reduced-motion` respektieren.
- Mobil bedienbar bis ca. 360 px Breite.
- Nutzereingaben beim Einfuegen ins DOM escapen.

## Validierung vor jedem Commit
- `npm test` muss gruen sein.
- Neue Projekte bekommen eine `test.js` nach dem Muster aus `projects/hoehle-gezogen/test.js`.
- Spiel-Logik, die Punkte oder Laeufe abschliesst, idempotent halten (kein Doppelzaehlen bei Re-Render).

## Neues Projekt anlegen
1. Ordner `projects/<name>/` mit `index.html` und `README.md`.
2. Test-Hook im Spiel exponieren (z. B. `window.__game = {...}`), damit `test.js` den Zustand pruefen kann.
3. `test.js` ergaenzen. Sie laeuft automatisch bei `npm test` mit.
