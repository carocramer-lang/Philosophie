// Funktionstest des Vokabel-Adventure-Startbildschirms via jsdom.
const fs = require("fs"), path = require("path");
const { JSDOM } = require("jsdom");
const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");

function freshDom() {
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "https://localhost/" });
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
check("Startzustand: Unit 1 mit echtem Namen", doc.getElementById("unitLabel").textContent === "Unit 1 · Living in America");
check("Startzustand: 0 / 100 Vokabeln", doc.getElementById("wordsLabel").textContent === "0 / 100 Vokabeln");
check("Startzustand: CTA zeigt Loslegen", doc.getElementById("ctaTitle").textContent === "Loslegen");
check("Startzustand: Streak 1 Tag nach erstem Besuch", G.state.streakCount === 1);
check("Merkliste startet leer", doc.getElementById("wordlistSub").textContent === "0 Wörter");

// --- Units (Green Line 4, Across-cultures-Kapitel eingerechnet) ---
check("4 Units definiert", G.UNITS.length === 4);
check("Kapitel-Kachel zeigt 4 Units", doc.getElementById("chaptersSub").textContent === "4 Units");
check("Unit 3 ist New York (Design-Beispiel stimmte)", G.UNITS[2].name === "City of dreams: New York");

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
click(win, doc.querySelector('[data-nav="chapters"]'));
check("Klick auf Menuepunkt schliesst Menue", G.isDrawerOpen() === false);
check("Klick auf Menuepunkt oeffnet Modal", G.isModalOpen() === true);
check("Modal-Titel Kapitel", doc.getElementById("modalTitle").textContent === "Kapitel");
const chapterItems = Array.from(doc.querySelectorAll("#modalBody .achv"));
check("Kapitel-Modal listet alle 4 Units", chapterItems.length === 4);
check("Kapitel-Modal nennt Unit-Namen", chapterItems.some(li => /Living in America/.test(li.textContent)));
click(win, doc.getElementById("modalCloseBtn"));
check("Modal schliesst per Klick", G.isModalOpen() === false);

// --- Kachel-Interaktion + Escape ---
click(win, doc.getElementById("duelTile"));
check("Duell-Kachel oeffnet Modal", G.isModalOpen() === true);
check("Modal-Titel Duell", doc.getElementById("modalTitle").textContent === "Duell");
key(win, doc, "Escape");
check("Escape schliesst Modal", G.isModalOpen() === false);

// --- Erfolge spiegeln Zustand ---
G.state.streakCount = 7;
G.state.wordsLearned = 12;
click(win, doc.getElementById("achievementsBtn"));
let unlocked = Array.from(doc.querySelectorAll("#modalBody .achv:not(.locked)")).length;
check("Erfolge: mehrere Achievements freigeschaltet bei Streak 7 / 12 Woertern", unlocked >= 4);
click(win, doc.getElementById("modalCloseBtn"));

// --- Export ---
const exported = JSON.parse(G.exportProgressData());
check("Export enthaelt Streak", exported.streakCount === 7);
check("Export enthaelt gelernte Vokabeln", exported.wordsLearned === 12);

// --- Reset ist idempotent nutzbar ---
G.resetProgress();
check("Reset setzt Streak zurueck auf 1", G.state.streakCount === 1);
check("Reset setzt gelernte Vokabeln zurueck", G.state.wordsLearned === 0);
check("Reset aktualisiert DOM", doc.getElementById("wordsLabel").textContent === "0 / 100 Vokabeln");

// --- Zweiter Boot am Folgetag erhoeht Streak korrekt ---
{
  const { win: win2, doc: doc2 } = freshDom();
  const G2 = win2.__game;
  G2.state.streakCount = 4;
  G2.state.lastVisitDate = "2020-01-01";
  win2.localStorage.setItem(G2.STORAGE_KEY, JSON.stringify(G2.state));
  const r = G2.computeStreak(4, "2020-01-01", "2020-01-02");
  check("Folgetag-Simulation erhoeht Streak", r.count === 5);
}

console.log("  " + ok.length + "/" + (ok.length + fail.length) + " Checks bestanden");
if (fail.length) { fail.forEach(n => console.log("  XX " + n)); process.exit(1); }
