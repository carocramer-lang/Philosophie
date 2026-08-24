# Die Hoehle, gezogen

Interaktives Hoehlengleichnis nach Platon. Single-File-HTML, Graphic-Novel-Optik.
Der Aufstieg geschieht unter Zwang: narrativ (ziehende Hand) und spielbar (Losreissen scheitert).

## Aufbau
- `index.html` ist das gesamte Spiel. Keine externen Abhaengigkeiten ausser Google Fonts (faellt offline auf Systemschriften zurueck).
- `test.js` faehrt einen kompletten Durchlauf durch alle fuenf Szenen via jsdom.

## Didaktischer Kern
Zweifel-Anzeige, Entdeckt-Zaehler, Gedankenprotokoll pro Station, Auswertung nach fuenf Stationen, Schreibaufgabe, Export als .txt.

## Persistenz
localStorage-Key `hoehle_gezogen_v1`. Vor Geraetewechsel ueber "Protokoll sichern" exportieren.

## Test
Aus dem Repo-Wurzelverzeichnis: `npm test`. Oder direkt: `node projects/hoehle-gezogen/test.js`.

## Deploy
`index.html` bei AWS Amplify hochladen. Fuer eine sprechende URL vorher umbenennen, z. B. `hoehle-gezogen.html`.
