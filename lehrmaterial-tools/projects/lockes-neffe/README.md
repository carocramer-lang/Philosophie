# Lockes Neffe

Topdown-Lernspiel zur Philosophie der fruehen Aufklaerung. Jonny will in die Akademie der Wissenschaften aufgenommen werden.

## Status
Spielbare Oberwelt: Jonny laeuft durch die Stadt, betritt die Lernorte in der Reihenfolge der Geschichte, der Fortschritt steht oben links. Innenraeume und Aufgaben folgen.

## Spielen
 im Browser oeffnen (auch per Doppelklick, kein Server noetig).
- Pfeiltasten oder WASD: gehen. Am Handy erscheint ein Steuerkreuz.
-  oder Knopf "Karte": ganze Welt anzeigen.
- Der goldene Pfeil zeigt zum naechsten Lernort. Tueren oeffnen sich beim Hineinlaufen.
- Jonny ist vorerst im Code gezeichnet (Funktion  in ). Ein eigenes Spritesheet laesst sich dort spaeter einsetzen.

## Oberwelt (`welt/`)
- `welt.png`: 1536 x 864 px, 96 x 54 Kacheln a 16 px
- `welt_2x.png`: doppelte Groesse (Kacheln 32 px), passend fuer einen Jonny-Sprite von ca. 32 x 48 px
- `welt_kollision.png`: Vorschlag fuer die Begehbarkeit als Overlay
  - gruen Weg/Platz, gelb Wiese (optional sperren), rot Hindernis, blau Wasser, magenta Eingang
- `welt.json`: dasselbe als Raster (`#` Weg, `.` Wiese, `X` Hindernis, `~` Wasser, `E` Tuer), dazu Startpunkt, Tueren und Vorplaetze der Lernorte
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
`npm test` prueft, ob jede Tuer vom Start aus ueber Wege erreichbar ist.
