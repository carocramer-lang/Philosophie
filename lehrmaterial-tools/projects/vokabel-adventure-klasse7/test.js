// Funktionstest des Vokabel-Adventure-Startbildschirms (Klasse 7, Green Line 3) via jsdom.
const fs = require("fs"), path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");
const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");

function freshDom() {
  // jsdom kennt window.scrollTo nicht (nur fuers Aufraeumen der Ansicht gedacht,
  // fuer die Tests irrelevant) - eigene VirtualConsole unterdrueckt nur diese Meldung.
  const virtualConsole = new VirtualConsole();
  virtualConsole.on("jsdomError", (e) => { if (!/Not implemented: window.scrollTo/.test(e.message)) console.error(e); });
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "https://localhost/", virtualConsole });
  return { dom, win: dom.window, doc: dom.window.document };
}

let ok = [], fail = [];
const check = (n, c) => (c ? ok : fail).push(n);
const click = (win, e) => e.dispatchEvent(new win.MouseEvent("click", { bubbles: true }));
const key = (win, target, k) => target.dispatchEvent(new win.KeyboardEvent("keydown", { key: k, bubbles: true }));

// --- Grundzustand ---
let { win, doc } = freshDom();
let G = win.__game;
check("Test-Hook vorhanden", !!G);
check("Speicherstand nach erstem Laden vorhanden", !!win.localStorage.getItem(G.STORAGE_KEY));
check("Startzustand: Unit 1 mit echtem Namen", doc.getElementById("unitLabel").textContent === "Unit 1 · Find your place");
const unit1WordCount = G.DATA.unit1.sections.reduce((n, s) => n + s.words.length, 0);
check("Startzustand: 0 / N Vokabeln (aktuelles Kapitel Unit 1)", doc.getElementById("wordsLabel").textContent === "0 / " + unit1WordCount + " Vokabeln");
check("Startzustand: CTA zeigt Start", doc.getElementById("ctaTitle").textContent === "Start");
check("Startzustand: Streak 1 Tag nach erstem Besuch", G.state.streakCount === 1);
check("Merkliste startet leer", doc.getElementById("wordlistSub").textContent === "0 words");
check("Keine Duell-Kachel mehr vorhanden", !doc.getElementById("duelTile"));
check("Keine Uebungen-Kachel vorhanden (nicht angefragt)", !doc.getElementById("exercisesTile"));

// --- Datenstruktur: 4 Units + 2 Zusatzunits ---
check("6 Kapitel definiert (4 Units + 2 Zusatzunits)", G.GROUPS.length === 6);
check("Kapitel-Kachel zeigt 6 Kapitel", doc.getElementById("chaptersSub").textContent === "6 Kapitel");
check("4 echte Units", G.GROUPS.filter(g => g.kind === "unit").length === 4);
check("2 Zusatzunits", G.GROUPS.filter(g => g.kind === "zusatz").length === 2);
check("Alle 6 Kapitel haben Abschnitte in DATA", G.GROUPS.every(g => G.DATA[g.id] && G.DATA[g.id].sections.length > 0));
check("833 Vokabeln insgesamt", G.ALL_WORDS.length === 833);
const allEns = G.ALL_WORDS.map(w => w.en);
check("Keine doppelten Karteikarten-Schluessel", new Set(allEns).size === allEns.length);
check("Jedes Wort hat eine deutsche Uebersetzung", G.ALL_WORDS.every(w => w.de && w.de.length > 0));
check("Jeder Abschnitt hat ein Spiel zugewiesen", G.GROUPS.every(g => G.DATA[g.id].sections.every(s => !!s.game)));
const gameTypes = new Set();
G.GROUPS.forEach(g => G.DATA[g.id].sections.forEach(s => gameTypes.add(s.game.type)));
check("Nur die 3 angefragten Spieltypen kommen vor", [...gameTypes].sort().join(",") === "hangman,memory,tempo");
check("Abschnitte sind ca. 20 Woerter gross (max 24)", G.GROUPS.every(g => G.DATA[g.id].sections.every(s => s.words.length <= 24)));

// --- computeStreak (reine Funktion) ---
const t0 = "2026-09-01";
const t1 = "2026-09-02"; // Folgetag
const gap = "2026-09-10"; // Luecke
check("computeStreak: gleicher Tag haelt Zaehler", G.computeStreak(3, t0, t0).count === 3);
check("computeStreak: Folgetag erhoeht Zaehler", G.computeStreak(3, t0, t1).count === 4);
check("computeStreak: Luecke setzt auf 1 zurueck", G.computeStreak(5, t0, gap).count === 1);
check("computeStreak: kein Vorbesuch startet bei 1", G.computeStreak(0, null, t0).count === 1);

// --- Menue (Drawer) ---
click(win, doc.getElementById("menuBtn"));
check("Menue oeffnet", G.isDrawerOpen() === true);
check("aria-expanded gesetzt", doc.getElementById("menuBtn").getAttribute("aria-expanded") === "true");
check("Kein Duell-Menuepunkt mehr", !doc.querySelector('[data-nav="duel"]'));
check("Kein Uebungen-Menuepunkt mehr", !doc.querySelector('[data-nav="exercises"]'));
check("'Spiele' steht im Menue", !!doc.querySelector('[data-nav="games"]'));
click(win, doc.querySelector('[data-nav="achievements"]'));
check("Klick auf Menuepunkt schliesst Menue", G.isDrawerOpen() === false);
check("Klick auf 'Erfolge' oeffnet Modal", G.isModalOpen() === true);
check("Modal-Titel Erfolge", doc.getElementById("modalTitle").textContent === "Erfolge");
key(win, doc, "Escape");
check("Escape schliesst Modal", G.isModalOpen() === false);

// --- 'Spiele' fuehrt zu echter Ansicht (kein Modal) ---
click(win, doc.getElementById("menuBtn"));
click(win, doc.querySelector('[data-nav="games"]'));
check("'Spiele' oeffnet die Spiele-Uebersicht (kein Modal)", G.currentView() === "games" && !G.isModalOpen());
click(win, doc.getElementById("gamesBackBtn"));

// --- Kapitel-Modal: alle 6 Kapitel klickbar ---
click(win, doc.getElementById("chaptersTile"));
check("Kapitel-Modal oeffnet", G.isModalOpen() === true);
const chapterButtons = Array.from(doc.querySelectorAll("#modalBody button.achv"));
check("Alle 6 Kapitel sind klickbar", chapterButtons.length === 6);
check("Kein gesperrtes Kapitel (kein .locked)", !doc.querySelector("#modalBody .achv.locked"));
// zweites Kapitel (Unit 2) anklicken -> wechselt currentGroupId und oeffnet Unit-Ansicht
click(win, chapterButtons[1]);
check("Klick auf Kapitel wechselt currentGroupId", G.currentGroupId() === "unit2");
check("Klick auf Kapitel oeffnet Unit-Ansicht", G.currentView() === "unit");
check("Unit-2-Titel korrekt angezeigt", doc.getElementById("unitPageTitle").textContent === G.GROUPS[1].title);
check("Hero-Label zeigt jetzt Unit 2", doc.getElementById("unitLabel").textContent.indexOf("Unit 2") === 0);

// zurueck zu Unit 1 fuer die weiteren Tests
G.setCurrentGroup("unit1");
G.showView("unit");

// --- Unit-Ansicht: Abschnittsliste ---
check("Unit 1 hat Abschnitte in der Liste", doc.querySelectorAll("#sectionList .sec-card").length === G.DATA.unit1.sections.length);
click(win, doc.getElementById("unitBackBtn"));
check("Zurueck-Button fuehrt zum Start", G.currentView() === "start");

// --- Abschnitts-Ansicht: Karteikarten zeigen zuerst Deutsch, dann Englisch ---
G.showView("unit");
G.openSection(0);
check("Abschnitts-Ansicht aktiv", G.currentView() === "section");
const firstWord = G.DATA.unit1.sections[0].words[0];
check("Karteikarte zeigt zuerst Deutsch (Vorderseite)", doc.querySelector(".fc-front .fc-word").textContent === firstWord.de);
check("Kartenrueckseite zeigt Englisch", doc.querySelector(".fc-back .fc-word").textContent === firstWord.en);
click(win, doc.querySelector(".flashcard"));
check("Karte dreht sich per Klick um", doc.querySelector(".flashcard").classList.contains("flipped"));

// --- Uebersicht bleibt Englisch-first ---
const ovFirstRow = doc.querySelector(".ov-table tr");
check("Uebersicht Spalte 1 ist Englisch", ovFirstRow.querySelector("td.en").textContent.trim() === firstWord.en);
check("Uebersicht Spalte 2 ist Deutsch", ovFirstRow.querySelector("td.de").textContent.trim() === firstWord.de);

// Stern in der Uebersicht markiert Merkliste
click(win, ovFirstRow.querySelector(".ov-star"));
check("Stern-Klick fuegt Wort zur Merkliste hinzu", G.state.merkliste.some(m => m.en === firstWord.en));

// "Kann ich schon" bewertet ein Wort als bekannt
const knowBtn = doc.querySelector(".fc-assess .know");
click(win, knowBtn);
check("Karteikarten-Bewertung speichert wordAssessments", G.state.wordAssessments[firstWord.en] === "know");

// --- Merkliste-Ansicht ---
G.showView("merkliste");
check("Merkliste zeigt den gemerkten Eintrag", doc.querySelectorAll(".mk-row").length >= 1);
click(win, doc.getElementById("mkBackBtn"));

// --- Spiele: alle drei Typen pro Kapitel durchspielen (Unit 1) ---
G.setCurrentGroup("unit1");
G.showView("games");
const sectionsU1 = G.DATA.unit1.sections;
const memIdx = sectionsU1.findIndex(s => s.game.type === "memory");
const hangIdx = sectionsU1.findIndex(s => s.game.type === "hangman");
const tempoIdx = sectionsU1.findIndex(s => s.game.type === "tempo");
check("Memory-Abschnitt gefunden", memIdx !== -1);
check("Galgenmaennchen-Abschnitt gefunden", hangIdx !== -1);
check("Tempo-Runde-Abschnitt gefunden", tempoIdx !== -1);

// Memory
G.openGame(memIdx);
const memPairCount = sectionsU1[memIdx].game.pairs.length;
check("Memory zeigt doppelt so viele Karten wie Paare", doc.querySelectorAll(".mem-card").length === memPairCount * 2);
click(win, doc.querySelectorAll(".mem-card")[0]);
check("Memory-Karte dreht sich beim Klick um", doc.querySelectorAll(".mem-card")[0].classList.contains("flipped"));

// Hangman
G.showView("games");
G.openGame(hangIdx);
check("Galgenmaennchen zeigt Hinweis (Deutsch)", doc.querySelector(".hang-hint").textContent.indexOf("Hinweis:") === 0);
check("Galgenmaennchen hat 26 Tasten (a-z)", doc.querySelectorAll(".hang-key").length === 26);
const hangWordLen = doc.querySelector(".hang-word").textContent.split(" ").length;
check("Galgenmaennchen-Wort besteht nur aus Platzhaltern am Anfang", doc.querySelector(".hang-word").textContent.split(" ").every(ch => ch === "_"));
// richtigen ersten Buchstaben raten (Pool wird gemischt, daher ueber den
// angezeigten Hinweis das tatsaechlich gezeigte Wort ermitteln)
const pool0 = sectionsU1[hangIdx].game.pool;
const shownHint = doc.querySelector(".hang-hint").textContent.replace("Hinweis: ", "");
const target = pool0.find(p => p.de === shownHint);
const firstLetterBtn = Array.from(doc.querySelectorAll(".hang-key")).find(b => b.textContent === target.spell[0]);
click(win, firstLetterBtn);
check("Richtiger Buchstabe wird als 'used-right' markiert", firstLetterBtn.classList.contains("used-right"));

// Tempo-Runde
G.showView("games");
G.openGame(tempoIdx);
click(win, doc.querySelector(".tempo-start"));
check("Tempo-Runde zeigt ein deutsches Wort", doc.querySelector(".tempo-word").textContent.length > 0);
check("Tempo-Runde zeigt 4 Optionen", doc.querySelectorAll(".tempo-opt").length === 4);
const tempoItems = sectionsU1[tempoIdx].game.items;
const shownDe = doc.querySelector(".tempo-word").textContent;
const optsTexts = Array.from(doc.querySelectorAll(".tempo-opt")).map(b => b.textContent);
const matching = tempoItems.find(it => it.de === shownDe);
check("Die richtige englische Uebersetzung ist unter den Optionen", !!matching && optsTexts.indexOf(matching.en) !== -1);

// --- Erfolge (global über alle Kapitel) ---
const achBefore = G.computeAchievements(G.state);
check("computeAchievements liefert mehrere Erfolge", achBefore.length >= 5);
check("'Erster Besuch' ist bereits freigeschaltet", achBefore.find(a => a.id === "first-visit").unlocked === true);

// --- Export ---
const exported = JSON.parse(G.exportProgressData());
check("Export enthaelt Streak", exported.streakCount === 1);
check("Export enthaelt gelernte Vokabeln", exported.wordsLearned === G.knownWordCount());
check("Export enthaelt Abschnittsfortschritt (gesamt)", typeof exported.abschnitteGesamt === "number" && exported.abschnitteGesamt > 0);
check("Export nennt aktuelles Kapitel", exported.aktuellesKapitel.indexOf("Unit 1") === 0);

// --- Reset ist idempotent nutzbar ---
G.resetProgress();
check("Reset setzt Streak zurueck auf 1", G.state.streakCount === 1);
check("Reset setzt gelernte Vokabeln zurueck", G.knownWordCount() === 0);
check("Reset leert die Merkliste", G.state.merkliste.length === 0);
check("Reset setzt currentGroupId zurueck auf erstes Kapitel", G.state.currentGroupId === G.GROUPS[0].id);
check("Reset aktualisiert DOM", doc.getElementById("wordsLabel").textContent === "0 / " + unit1WordCount + " Vokabeln");

// --- Zweiter Boot am Folgetag erhoeht Streak korrekt ---
{
  const { win: win2 } = freshDom();
  const G2 = win2.__game;
  const r = G2.computeStreak(4, "2020-01-01", "2020-01-02");
  check("Folgetag-Simulation erhoeht Streak", r.count === 5);
}

// --- Kapitelwahl wird persistiert (state.currentGroupId landet im localStorage) ---
{
  const { win: win3 } = freshDom();
  const G3 = win3.__game;
  G3.setCurrentGroup("zusatz1");
  const raw = JSON.parse(win3.localStorage.getItem(G3.STORAGE_KEY));
  check("currentGroupId wird gespeichert", raw.currentGroupId === "zusatz1");
}

console.log("  " + ok.length + "/" + (ok.length + fail.length) + " Checks bestanden");
if (fail.length) { fail.forEach(n => console.log("  XX " + n)); process.exit(1); }
