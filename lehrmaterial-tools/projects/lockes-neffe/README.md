# Lockes Neffe

Topdown-Lernspiel zur Philosophie der fruehen Aufklaerung. Jonny will in die Akademie der Wissenschaften aufgenommen werden.

## Status
Spielbare Oberwelt mit begehbarem Observatorium und Lesesaal. Salon, Druckerei, Akademie und der Startbildschirm folgen.

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
- Materialstellen (Kerze + Lichtschein): Regal links unten (`regal_links`, Infografik Platons Theaetet), Regal daneben (`regal_rechts`, Infografik Meinen und Wissen / Gettier), Sternkartentisch (`kartentisch`, Infografik Rationalismus vs. Empirismus). Dateien in `material/`, Zuordnung im Objekt `MATERIAL` in `index.html`.
- Ablauf: Jede Stelle muss angesehen und heruntergeladen werden. Erst nach allen drei Infografiken leuchtet das Teleskop, dort liegt Lockes Text (Text 1 und 2) mit dem Arbeitsblatt als PDF. Vorher ist die Tuer gesperrt, ein Hinweis leuchtet auf. Alles gesichert = Etappe 1.
- Download: online ueber die Download-Funktion der Plattform (mit Bestaetigung), auf einem Webserver als normaler Download, lokal per Doppelklick oeffnet sich die Datei in einem neuen Tab.
- Aufbau: Tuer unten Mitte, roter Laeufer gerade nach Norden ueber die Kompassrose zum Teleskop-Podest. Links Bibliothek, rechts Instrumentenkammer, beide ueber einen breiten Querweg erreichbar.

Lesesaal: 40 x 24 Kacheln, erzeugt mit `python3 innen/lesesaal.py` (nutzt die Bausteine aus `observatorium.py`).
- Aufbau: Mittelschiff mit Saeulen, roter Laeufer gerade zum Schreibpult auf dem Podest. Links drei Lesetische, rechts Buecherstapel und der Tisch des Bibliothekars, vorne rechts das Kettenpult mit Kerze.
- Ablauf: Am Lesepult (`lesepult`) Lockes Text ansehen und herunterladen. Dann leuchtet das Schreibpult (`schreibpult`): Papierrolle mit Auftrag, Hinweisen zur Zusammenfassung, Reiter mit Lockes Text und Wortzaehler (mindestens 60 Woerter). Nach der Abgabe erscheint der Bibliothekar neben dem Pult und gibt Rueckmeldung. Jonny kann antworten, nachfragen oder ueberarbeiten. "Gespraech beenden" siegelt die Rolle = Etappe 2. Vorher bleibt die Tuer zu.
- Der Entwurf wird im Browser gemerkt (`localStorage`, Schluessel `lockes-neffe_v1`). "Rolle als Datei sichern" speichert Zusammenfassung und Gespraech als Textdatei.

### Bibliothekar (Rueckmeldung)
Eingebaut ist eine regelbasierte Fassung ohne Internet und ohne Datenweitergabe. Sie prueft sieben Kernpunkte (Einleitungssatz, tabula rasa, Erfahrung, Sensation, Reflexion, Erkenntnis als Uebereinstimmung der Ideen, Grenzen des Wissens) und die Form (Wertung, woertliche Uebernahmen, Praeteritum, Redewiedergabe, Laenge). Sie lobt konkret, nennt hoechstens drei Verbesserungen und stellt Rueckfragen mit gestuften Hilfen.
Ein echter Chatbot laesst sich ohne Umbau anschliessen: `window.LESESAAL_BIBLIOTHEKAR = function ({ zusammenfassung, verlauf, quelle, art }) { return Promise<string> }`. Liefert er nichts oder schlaegt fehl, springt die eingebaute Fassung ein.

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
