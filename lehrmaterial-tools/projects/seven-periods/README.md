# Seven Periods

Lernspiel Englisch Klasse 8 zur Klassenarbeitsvorbereitung (Unit 1, High School Life).
Rahmen: Matt rettet bis 3:15 p.m. das Birchview Yearbook. Sieben Räume, ein Bonusraum.

## Inhalt
- Intro „Matt's Survival Guide“: US-Schulbegriffe mit UK-Variante und deutscher Erklärung, danach im Notizbuch.
- 1st bis 6th period: Gerund und Infinitivkonstruktionen (Sortieren, freie Satzergänzung, Umformung, Lückentext, Fehlerkorrektur, Übersetzung) und Hörverstehen (Podcast).
- 7th period: Writing, zwei Themen, Live-Checkliste, druckbare Yearbook-Seite.
- Janitor's Closet (Bonus): remember/forget/try/stop + Gerund oder Infinitiv, Code 3714.
- 51 Punkte, nur erster Versuch zählt. Abschlusscode `BV<P|T>-<Punkte><Max>-<Prüfzeichen>`.

## AI Feedback (nach dem Writing)
Nach dem Abgeben im 7th period: Button „AI Feedback“ (auch beim erneuten Öffnen des Raums).
Die SuS kopieren Prompt und eigenen Text selbst in ein KI-Tool. Das Spiel sendet nichts.
Kopieren erst nach vier Haken (keine Namen, keine Kontaktdaten, nichts Privates, Eltern Bescheid gesagt).
E-Mail-Adressen und Telefonnummern im Text sperren das Kopieren.
Drei Prompts in `CONTENT.aifeedback.prompts`: Feedback ohne Neuschreiben, Tutor mit Tipp zuerst, Fehlersuche ohne eigenen Text.
Bewusst keine Anbieter genannt: viele KI-Dienste haben Altersgrenzen (Claude z. B. ab 18).

## Study Hall (ohne Wertung)
Freiwillige Zusatzübungen von LearningApps oder LearningSnacks, erreichbar über den Button „Study Hall“ oben in der Leiste.
Eintragen in `CONTENT.studyhall.items`, Feld `url`: Link oder kompletter Einbettungscode (`<iframe …>`).
Nur learningapps.org und learningsnacks.de werden angenommen. Karten ohne Link bleiben unsichtbar.
Die Übungen zählen nicht für Punkte und Hall Pass. In der Claude-Vorschau werden sie blockiert, nur auf Netlify sichtbar.

## URL-Parameter
- `?teacher=1` Lehrkraftansicht: alle Aufgaben mit Lösungen, Podcast-Skript, Glossar, druckbar.
- `?all=1` alle Räume offen, zum Testen.

## Hallway (Startansicht)
EXIT-Tür als Bild (`ASSETS.exit_door`). Links leuchtet gelb der aktuelle Raum, rechts steht der nächste.
Die übrigen Stunden liegen als farbige Kacheln darunter (`TILE_COLORS`), erledigte mit „Page saved“.
Nach sieben Stempeln steht links der Janitor's Closet.

## Szenen und Videos
- Gespräche laufen als Szene: Hintergrundbild, Figur im Polaroid-Rahmen, Sprechblase, Satz für Satz per Tippen.
- Hintergrund: `ASSETS.bg_lockers` (Spindgang). `THEMES` im Skript legt pro Raum Einfärbung und Bildausschnitt fest; eigene Raumbilder dort als `bg` eintragen.
- `VIDEOS`: stumme Loops für Matt, AJ, Zach und Mr. Okafor (`janitor`). Leer = Standbild. Bei „Bewegung reduzieren“ immer Standbild.
- Jedes Video liegt als MP4 und WebM vor (`{mp4, webm}`), der Browser nimmt, was er abspielen kann.
  WebM: `ffmpeg -i out.mp4 -an -c:v libvpx-vp9 -b:v 0 -crf 42 out.webm`
- Gemini-Videos: Zuschnitt 4:3, vorwärts und rückwärts für einen nahtlosen Loop, ohne Ton, ca. 150 KB.
  `ffmpeg -i in.mp4 -an -filter_complex "[0:v]trim=1:8.5,setpts=PTS-STARTPTS,crop=960:720:160:0,scale=400:300,fps=20,split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[v]" -map "[v]" -c:v libx264 -pix_fmt yuv420p -crf 30 -movflags +faststart out.mp4`

## Assets
- `ASSETS` im Skript: Figuren als SVG-Platzhalter. Eigene Bilder als Pfad oder data-URI eintragen.
- `ASSETS.podcast_audio`: MP3 aus ElevenLabs. Solange leer, liest die Sprachausgabe des Browsers vor.

## Offen
- Design-Skin nach Moodboard.
- Podcast-MP3.
- Einmal komplett auf dem iPad durchspielen.
