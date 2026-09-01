# Lehrmaterial-Tools

Interaktive Browser-Lehrmaterialien als Single-File-HTML fuer Philosophie und Praktische Philosophie.
Jedes Tool ist eine eigenstaendige `index.html` und wird einzeln bei AWS Amplify deployt.

## Projekte
- `projects/hoehle-gezogen/` Hoehlengleichnis nach Platon, Graphic-Novel, Zwang-Mechanik. Vollstaendig, getestet.
- `projects/vokabel-adventure/` Startbildschirm fuer ein Vokabellernspiel (Englisch, Green Line 4). Nur Startbildschirm, getestet; Lernrunden folgen spaeter.
- `projects/ki-workshop-sammler/` Sammel-Tool fuer SuS. Platzhalter, bestehende Datei einsetzen.
- `projects/escape-state-of-nature/` Escape-Room politische Philosophie. Platzhalter, bestehende Datei einsetzen.

## Einrichten
```
npm install      # installiert jsdom fuer die Tests
npm test         # faehrt alle vorhandenen Projekt-Tests
```

## Struktur
```
lehrmaterial-tools/
├── projects/
│   ├── hoehle-gezogen/        index.html, test.js, README.md
│   ├── ki-workshop-sammler/   Platzhalter
│   └── escape-state-of-nature/Platzhalter
├── tools/
│   └── run-tests.js           findet und laeuft alle projects/*/test.js
├── docs/
│   └── konventionen.md        Architektur, Persistenz, Barrierefreiheit, Tests
├── package.json
└── .gitignore
```

## Git in Betrieb nehmen
```
git init
git add .
git commit -m "Initiale Repo-Struktur mit Hoehle-Projekt"
```

## Arbeiten mit Claude Code
Repo-Ordner in Claude Code oeffnen. Dann direkt an den Dateien arbeiten lassen,
Aenderungen versionieren und vor dem Commit `npm test` laufen lassen.
Die beiden Platzhalter durch die bestehenden Tools ersetzen und je eine `test.js` ergaenzen.
