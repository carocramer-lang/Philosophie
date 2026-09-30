# Lockes Neffe

Topdown-Lernspiel zur Philosophie der fruehen Aufklaerung. Jonny will in die Akademie der Wissenschaften aufgenommen werden.

## Status
Startbildschirm, spielbare Oberwelt mit begehbarem Observatorium, Lesesaal und Historischem Salon. Buchdruckerei mit Aufgabe 3, Druckermeister und Flugschrift, Akademie der Wissenschaften als Abschluss. Das Spiel ist vollstaendig spielbar.
Titel auf dem Startbildschirm: „Lockes Welt“.

## Startbildschirm (`start/`)
- `titelbild_grund.jpg`: Illustration der Lehrkraft, unveraendert.
- `titelbild.html` setzt Titel, „SPIEL STARTEN“ und ⓘ im Pixelraster darueber, `node start/titelbild.js` rendert `titelbild.jpg` (2816 x 1536).
- Im Spiel (`START` in `index.html`) fuellt das Bild den Bildschirm. Der sichere Bereich mit Titel, Knoepfen und Locke bleibt auf Smartphone, Tablet und Desktop immer ganz sichtbar, notfalls mit schmalen dunklen Raendern. Unsichtbare Schaltflaechen liegen genau ueber den gezeichneten Knoepfen.
- Tastatur: Enter oder Leertaste startet, I oeffnet die Informationen, Escape schliesst sie.
- Wer Titel oder Knoepfe verschiebt, muss die Koordinaten in `START` anpassen (Grundbild 1408 x 768).
- Schriften: `schriften/` (IM Fell English) und `start/liberation-serif.ttf` (nur fuer das Erzeugen des Titelbilds) liegen lokal, Lizenz jeweils SIL Open Font License (OFL-Dateien daneben). Die Seite laedt nichts von Google.

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
- Material: Arbeitsblatt „Die Debatte um die Tabula Rasa“ (Leibniz, Neue Abhandlungen, 1704), Aufgabe 1 (AFB I). Quelle fuer alles ist `material/arbeitsblatt_leibniz.py`: erzeugt HTML, PDF (`node material/drucke_pdf.js`), `material/leibniz_daten.js` fuers Spiel und `netlify/lib/leibniz.json` fuer den Server. Zeilennummern im Spiel und im Bibliothekar stimmen mit dem PDF ueberein.
- Bibliothekar-Kriterien nach dem Erwartungshorizont der Lehrkraft: drei Kernbereiche (Problemstellung tabula rasa vs. angeborene Prinzipien, Kritik an der Induktion, Marmorblock-Gleichnis). Ein Bereich gilt als erfasst, sobald sein Kern da ist; Einzelaspekte fragt er nur als Vertiefung ab. Mindestens 80, empfohlen 150 bis 300 Woerter.
- Figur: `figuren/bibliothekar.py` zeichnet den Bibliothekar (32 x 48 und 16 x 24, transparent, dazu Vorschau auf Weiss).
- Ablauf: Am Lesepult (`lesepult`) das Arbeitsblatt ansehen und herunterladen. Dann leuchtet das Schreibpult (`schreibpult`): Papierrolle mit Auftrag, Hinweisen zur Zusammenfassung, Reiter mit Lockes Text und Wortzaehler (mindestens 60 Woerter). Nach der Abgabe erscheint der Bibliothekar neben dem Pult und gibt Rueckmeldung. Jonny kann antworten, nachfragen oder ueberarbeiten. "Gespraech beenden" siegelt die Rolle = Etappe 2. Vorher bleibt die Tuer zu.
- Der Entwurf wird im Browser gemerkt (`localStorage`, Schluessel `lockes-neffe_v1`). "Rolle als Datei sichern" speichert Zusammenfassung und Gespraech als Textdatei.

Historischer Salon: 40 x 24 Kacheln, erzeugt mit `python3 innen/salon.py` (Bausteine aus `observatorium.py`).
- Aufbau: Fischgraetparkett, rote Seidentapete, Fenster mit roten Vorhaengen wie an der Fassade. Gegenueber der Tuer der Kamin mit Platons Portraet und zwei Ohrensesseln, links oben der Sekretaer mit Kerze, dazu Cembalo, Standuhr, Schachtisch, Kanapee mit Teeservice, Vitrine mit Kuriositaeten, Globus und Buesten am Eingang.
- Material: Brief der Akademie am Sekretaer (`sekretaer`) mit Aufgabe 2 (AFB II, Analyse) und den Hinweisen der Lehrkraft, dazu derselbe Leibniz-Text. PDF `material/arbeitsblatt_leibniz_analyse.pdf`, erzeugt aus `material/arbeitsblatt_leibniz.py` (Feld `analyse` in `leibniz.json`, dort auch der Erwartungshorizont).
- Ablauf: Brief ansehen und herunterladen, dann am Sekretaer die Analyse schreiben (mindestens 120, empfohlen 250 bis 450 Woerter). Bei der Abgabe lodert das Feuer auf und Platon tritt aus seinem Portraet, das Bild bleibt leer. Am Kamin stellt er sich vor und erklaert den Bezug zu Leibniz (Z. 5 „wie ich mit Platon annehme“, Anamnesis, Menon, Aristoteles und Locke in Z. 3), dann gibt er Rueckmeldung. "Gespraech beenden" siegelt die Analyse = Etappe 3, Platon kehrt ins Bild zurueck. Vorher bleibt die Tuer zu.
- Platons Kriterien nach dem Erwartungshorizont: drei Kernbereiche (Entweder-oder-Gegenueberstellung und These, Argumentationskette mit Praemissen, Zwischenschluss und Mathematik als Beleg, Funktion des Marmorblock-Gleichnisses mit gedanklichem Ziel). Deutungen zaehlen nur, wenn Bild und Bedeutung im selben Satz stehen. Zur Form prueft er Fachbegriffe der Analyse (sonst: "eher eine Darstellung"), Zeilenangaben, Wertung, Zitate ohne Anfuehrungszeichen, Praeteritum und Laenge.
- Figur: `figuren/platon.py` zeichnet den Geist (Stirnband, weisser Bart, Schriftrolle, Schweif statt Fuessen, kuehle Geisterfarben).
- Entwurf der Analyse wird wie die Rolle im Browser gemerkt, "Rolle als Datei sichern" speichert `Analyse_Leibniz.txt`.

Buchdruckerei: 40 x 24 Kacheln, erzeugt mit `python3 innen/druckerei.py`.
- Aufbau: Fachwerk wie an der Fassade, grobe Dielen mit Druckerschwaerze, Steinplatten am Ofen. Links Setzregal (`setzkasten`, Kerze, hier kommt Aufgabe 3) und Setzpult (`setzpult`, schreiben), in der Mitte die Presse (`presse`, Druckermeister), rechts Ofen zum Letterngiessen, Trockengestell und der Buechertisch mit Lockes Essay und Schautafel (`tafel`). Durchs Fenster links sieht man das Muehlrad.
- Presse: `innen/druckerei_presse.png` ist ein Sprite-Blatt mit 16 Bildern (128 x 128). Das Spiel spielt es ab: Deckel zu, Karren faehrt ein, der Meister zieht den Bengel, der Tiegel senkt sich, Karren faehrt aus, Deckel auf mit bedrucktem Bogen. Takt in `presseBild` (index.html). Bei reduzierter Bewegung steht die Presse still.
- Ablauf: Brief der Akademie im Setzkasten (Aufgabe 3, AFB III, Stellungnahme; PDF `material/arbeitsblatt_leibniz_kommentar.pdf`, Feld `kommentar` in `leibniz.json` mit Erwartungshorizont, dazu Lockes Text im Feld `locke`) ansehen und herunterladen. Am Setzpult den Kommentar schreiben (mindestens 150, empfohlen 300 bis 550 Woerter), der Reiter "Texte" zeigt Leibniz und Locke. Nach der Abgabe ruft der Meister an die Presse, stellt sich vor (jede Position ist erlaubt, sie muss begruendet sein) und gibt Rueckmeldung. "Gespraech beenden" startet den Druck: die Presse laeuft einmal schnell durch, dann liegt die Flugschrift mit Vorschau und PDF-Download bereit. Der Download ist Pflicht: Erst danach ist Etappe 4 erreicht und die Tuer offen, das Ziel zeigt auf die Akademie.
- Kriterien des Meisters nach dem Erwartungshorizont: Vergleich (Lockes Sensation und Reflexion, komplexe Ideen, Leibniz' Anlass statt Begruendung), Abwaegung (Induktionsproblem fuer Leibniz, Metaphysik und Sparsamkeit fuer Locke, sichtbares Gegenargument), eigenes Urteil (Fazit, Synthese etwa mit Kant). Zur Form: Urteilssprache statt blosser Darstellung, Begruendungen, Zitate nur in Anfuehrungszeichen, Laenge. Die Position selbst wertet er nie.
- Druckermeister: `figuren/druckermeister.py` (gefaltete Papiermuetze, Lederschuerze, schwarze Haende), zwei Posen: stehen und ziehen.
- Infotafel (freiwillig, leuchtet bis sie gelesen ist): Nachbildung des Titelblatts von 1690 und kurze Texte zu Druck und Verlag (Elizabeth Holt, Thomas Basset), Lockes Namen auf dem Titel, Leibniz' liegengebliebenem Manuskript (gedruckt 1765) und dem Ende der Vorzensur 1695. Inhalte im Objekt `TAFELN` in `index.html`, dasselbe Muster laesst sich in anderen Raeumen nutzen.
- Flugschrift: `FLUGSCHRIFT` in `index.html` setzt einen Text auf A4-Seiten im Stil von 1690 (Titelei, Zierleiste, Initiale, Blocksatz, Kustoden, FINIS, Druckerzeichen, Druckvermerk MDCXC) und speichert sie als PDF (je Seite ein Bild, ohne fremde Bibliothek). Kurze Texte werden bei Bedarf etwas kleiner gesetzt, damit sie auf eine Seite passen.

Akademie der Wissenschaften (Abschluss): 40 x 24 Kacheln, erzeugt mit `python3 innen/akademie.py`.
- Aufbau: Festsaal mit Marmorboden, Baenke mit Gelehrten, Podium mit gruenem Tisch und Zeremonienzepter, Wappen und vier Siegelplaetze an der Wand, Mitgliederbuch am Pult links (`archiv`), Tisch mit Sanduhr unten rechts (`sanduhr`).
- Figuren: `figuren/akademie_figuren.py` zeichnet den Praesidenten (Allongeperuecke, roter Rock, Urkunde) und Onkel John (eigenes langes Haar, schlichter dunkler Rock). Der Praesident nimmt Jonny auf, Locke ist als Mitglied der Akademie dabei (historisch seit 1668 Mitglied der Royal Society) und gratuliert.
- Ablauf: Beim Betreten leuchten die vier Siegel nacheinander auf. Am Podium (`praesident`) zwei kurze Reden, dann die Aufnahmeurkunde (PDF, A4 quer, mit Siegeln der Stationen und Lockes Unterschrift). Nach dem Schliessen gratuliert Onkel John (mit einem Satz aus seinem Essay, II.1.19). Danach: Aufnahme bestanden, Etappe 5, die Tuer ist offen.
- Mappe am Pult: alle drei Texte mit Aufgaben und den Gespraechen mit Bibliothekar, Platon und Druckermeister als mehrseitige PDF.
- Neues Spiel: erst nach der Aufnahme. Die Sanduhr fragt nach, dann werden die gespeicherten Texte auf dem Geraet geloescht und das Spiel beginnt von vorn.

### Bibliothekar und Platon (Rueckmeldung)
Zwei Quellen, das Spiel waehlt automatisch:
1. **Auf Netlify:** `netlify/functions/bibliothekar.mjs` fragt die Claude API (Standardmodell `claude-opus-5-5`). Der API-Schluessel bleibt auf dem Server.
2. **Sonst** (lokal, Vorschau auf claude.ai, Server nicht erreichbar): die eingebaute regelbasierte Fassung. Sie prueft sieben Kernpunkte und die Form (Wertung, woertliche Uebernahmen, Praeteritum, Redewiedergabe, Laenge) und fuehrt mit Rueckfragen und gestuften Hilfen.

Die Function kennt zwei Rollen: `rolle: "bibliothekar"` (Standard) und `rolle: "platon"` mit eigenem Systemtext (`SYSTEM_PLATON`), Aufgabe, Hinweisen und Erwartungshorizont der Analyse.

Beide folgen denselben Regeln: sokratisch fragen statt Loesungen liefern. Die Musterloesung gibt es erst nach einem ausdruecklichen Angebot mit dem Hinweis, dass fertige Loesungen dem Lernen weniger nuetzen, und nur, wenn Jonny zustimmt. Rollenbeschreibung, Locke-Text und Musterloesung stehen in `netlify/lib/bibliothekar-kern.mjs`.

**Einrichten auf Netlify**
1. Bei Netlify die Seite aus dem GitHub-Repository anlegen. Base directory leer lassen, das `netlify.toml` im Wurzelverzeichnis des Repositorys setzt es. Production branch muss der Branch sein, auf dem das Spiel liegt.
2. Einen API-Schluessel in den Environment variables hinterlegen. Die Function nimmt, was da ist:
   - `GEMINI_API_KEY` (Google AI Studio, Rechnungskonto hinterlegen). Modell ueber `GEMINI_MODELL`, Standard `gemini-flash-latest`.
   - oder `ANTHROPIC_API_KEY` (platform.claude.com, Ausgabenlimit setzen). Modell ueber `BIBLIOTHEKAR_MODELL`, Standard `claude-opus-5-5`.
   - Optional `ERLAUBTE_URSPRUENGE`: nur die eigene Spieladresse darf fragen.
3. Neu deployen. Ohne Schluessel oder bei einem Fehler antwortet automatisch die eingebaute Fassung.

Achtung Gemini: Die Gemini API Additional Terms verlangen, dass Nutzer 18 oder aelter sind, und untersagen den Einsatz in Diensten, die sich an Minderjaehrige richten oder von ihnen wahrscheinlich genutzt werden. Vor dem Einsatz mit Schuelerinnen und Schuelern unter 18 klaeren. In der kostenlosen Stufe darf Google Eingaben zur Produktverbesserung nutzen, auch mit menschlicher Pruefung.

Eigene Anbindung ohne Netlify: `window.LESESAAL_BIBLIOTHEKAR = function ({ zusammenfassung, verlauf, quelle, art, rolle }) { return Promise<string> }`.

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
