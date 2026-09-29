# Lockes Neffe

Topdown-Lernspiel zur Philosophie der fruehen Aufklaerung. Jonny will in die Akademie der Wissenschaften aufgenommen werden.

## Status
Spielbare Oberwelt mit begehbarem Observatorium. Die uebrigen Innenraeume, das Material am Teleskop und der Startbildschirm folgen.

## Spielen
`index.html` im Browser oeffnen (auch per Doppelklick, kein Server noetig).
- Pfeiltasten oder WASD: gehen, E: benutzen. Am Handy (quer): Steuerkreuz links, E-Knopf rechts.
- Die Tuer des Observatoriums fuehrt in den Innenraum. Das Teleskop zaehlt als erste Etappe.
- `M` oder Knopf "Karte": ganze Welt anzeigen.
- Der goldene Pfeil zeigt zum naechsten Lernort. Tueren oeffnen sich beim Hineinlaufen.
- Jonny ist vorerst im Code gezeichnet (Funktion `sprite` in `index.html`). Ein eigenes Spritesheet laesst sich dort spaeter einsetzen.

Verbindliche Vorgaben zu Geraeten, Ausrichtung und Steuerung: `PROJEKTVORGABEN.md`.

## Innenraeume (`innen/`)
Observatorium: 40 x 24 Kacheln a 16 px, erzeugt mit `python3 innen/observatorium.py`.
- `observatorium.png`, `observatorium_2x.png`: Grafik ohne Schrift
- `observatorium_kollision.png`: gruen Boden, rot Wand/Moebel, cyan Eintrittsstelle, magenta Ausgang, orange Flaeche vor dem Teleskop
- `observatorium.json` und `observatorium_daten.js`: Raster (`#`, `X`, `S`, `A`, `I`), Eintritt, Ausgang, Interaktionen
- Aufbau: Tuer unten Mitte, roter Laeufer gerade nach Norden ueber die Kompassrose zum Teleskop-Podest. Links Bibliothek, rechts Instrumentenkammer, beide ueber einen breiten Querweg erreichbar.

## Oberwelt (`welt/`)
- `welt.png`: 1536 x 864 px, 96 x 54 Kacheln a 16 px
- `welt_2x.png`: doppelte Groesse (Kacheln 32 px), passend fuer einen Jonny-Sprite von ca. 32 x 48 px
- `welt_kollision.png`: Vorschlag fuer die Begehbarkeit als Overlay
  - gruen Weg/Platz, gelb Wiese (optional sperren), rot Hindernis, blau Wasser, magenta Eingang
- `welt.json`: dasselbe als Raster (`#` Weg, `.` Wiese, `X` Hindernis, `~` Wasser, `E` Tuer), dazu Startpunkt, Tueren und Vorplaetze der Lernorte
- `welt_daten.js`: dieselben Daten als Skript, damit das Spiel auch ohne Server laeuft
- `generator.py`: erzeugt alles neu, reines Python ohne Pakete: `python3 welt/generator.py`

## Lernorte (Reihenfolge der Geschichte)
| Ort | Lage | Funktion |
|---|---|---|
| Observatorium | Mitte Nord | Zentrale Bibliothek: Texte und Uebersichten |
| Lesesaal | Nordwest | Zusammenfassung (AFB I) |
| Historischer Salon | Suedwest | Textanalyse, Feedback vom Philosophengeist |
| Buchdruckerei | Suedost, am Muehlrad | Kommentar veroeffentlichen |
| Akademie der Wissenschaften | Nordost | Ziel, Aufnahmepruefung |

Start ist der Zentralplatz suedlich des Brunnens. Alle Tueren liegen an der Unterkante der Gebaeude, davor ein gepflasterter Vorplatz direkt an einer Strasse.

## Test
`npm test` prueft, ob jede Tuer vom Start aus ueber Wege erreichbar ist, und testet die Spiellogik (Kollision, Tueren, Reihenfolge) ohne Browser.
