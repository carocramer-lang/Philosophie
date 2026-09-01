// Funktionstest des Vokabel-Adventure-Startbildschirms und der Unit-1-Vokabellernstrecke via jsdom.
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
check("Startzustand: Unit 1 mit echtem Namen", doc.getElementById("unitLabel").textContent === "Unit 1 · Living in America");
check("Startzustand: 0 / N Vokabeln", doc.getElementById("wordsLabel").textContent === "0 / " + G.UNIT1_WORDS.length + " Vokabeln");
check("Startzustand: CTA zeigt Loslegen", doc.getElementById("ctaTitle").textContent === "Loslegen");
check("Startzustand: Streak 1 Tag nach erstem Besuch", G.state.streakCount === 1);
check("Merkliste startet leer", doc.getElementById("wordlistSub").textContent === "0 Wörter");

// --- Unit 1: Datenstruktur ---
check("4 Units definiert", G.UNITS.length === 4);
check("Kapitel-Kachel zeigt 4 Units", doc.getElementById("chaptersSub").textContent === "4 Units");
check("Unit 3 ist New York (Design-Beispiel stimmte)", G.UNITS[2].name === "City of dreams: New York");
check("Unit 1 hat 10 Abschnitte", G.UNIT1_SECTIONS.length === 10);
check("Jeder Abschnitt hat 14-22 Wörter (ca. 20)", G.UNIT1_SECTIONS.every(s => s.words.length >= 14 && s.words.length <= 22));
check("Unit 1 hat ueber 150 Vokabeln insgesamt", G.UNIT1_WORDS.length > 150);
const wordEns = G.UNIT1_WORDS.map(w => w.en);
check("Keine doppelten Karteikarten-Schluessel", new Set(wordEns).size === wordEns.length);
check("Jedes Wort hat eine deutsche Übersetzung", G.UNIT1_WORDS.every(w => w.de && w.de.length > 0));

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
click(win, doc.querySelector('[data-nav="duel"]'));
check("Klick auf Menuepunkt schliesst Menue", G.isDrawerOpen() === false);
check("Klick auf Menuepunkt oeffnet Modal", G.isModalOpen() === true);
check("Modal-Titel Duell", doc.getElementById("modalTitle").textContent === "Duell");
key(win, doc, "Escape");
check("Escape schliesst Modal", G.isModalOpen() === false);

// --- Menuepunkt "Spiele" (Inhalte folgen, aktuell Platzhalter) ---
click(win, doc.getElementById("menuBtn"));
check("'Spiele' steht im Menue", !!doc.querySelector('[data-nav="games"]'));
click(win, doc.querySelector('[data-nav="games"]'));
check("'Spiele' oeffnet ein Modal", G.isModalOpen() === true);
check("Modal-Titel Spiele", doc.getElementById("modalTitle").textContent === "Spiele");
key(win, doc, "Escape");

// --- Kapitel-Modal: Unit 1 klickbar, Unit 2-4 gesperrt ---
click(win, doc.getElementById("chaptersTile"));
check("Kapitel-Modal oeffnet", G.isModalOpen() === true);
const chapterButtons = Array.from(doc.querySelectorAll("#modalBody button.achv"));
check("Genau eine klickbare Unit im Kapitel-Modal", chapterButtons.length === 1);
check("Unit 2-4 als gesperrt markiert", doc.querySelectorAll("#modalBody .achv.locked").length === 3);
click(win, chapterButtons[0]);
check("Klick auf Unit 1 schliesst Modal", G.isModalOpen() === false);
check("Klick auf Unit 1 oeffnet Unit-Ansicht", G.currentView() === "unit");

// --- Unit-Ansicht: 10 Abschnitts-Karten ---
const sectionCards = Array.from(doc.querySelectorAll("#sectionList .sec-card"));
check("10 Abschnitts-Karten gerendert", sectionCards.length === 10);
check("Erste Karte zeigt 0 / 19 Woerter", sectionCards[0].querySelector(".sec-meta").textContent === "0 / 19 Wörter geübt");

// --- Abschnitt oeffnen: Karteikarten ---
click(win, sectionCards[0]);
check("Abschnitts-Ansicht aktiv", G.currentView() === "section");
check("Karteikarte zeigt erstes Wort", doc.querySelector(".fc-front .fc-word").textContent === G.UNIT1_SECTIONS[0].words[0].en);
check("Karteikarte startet nicht umgedreht", !doc.querySelector(".flashcard").classList.contains("flipped"));
click(win, doc.querySelector(".flashcard"));
check("Klick auf Karte dreht sie um", doc.querySelector(".flashcard").classList.contains("flipped"));

// "Muss ich üben" -> landet auf Merkliste, wird NICHT als bekannt gezaehlt
const firstWordEn = G.UNIT1_SECTIONS[0].words[0].en;
click(win, doc.querySelector(".fc-assess .practice"));
check("Nach 'Muss ich üben' ist Wort auf Merkliste", G.state.merkliste.some(m => m.en === firstWordEn));
check("Karte wechselt automatisch weiter", doc.querySelector(".fc-progress").textContent === "2 / 19");
check("wordsLearned zaehlt 'Muss ich üben' nicht mit", G.knownWordCount() === 0);

// "Kann ich schon" fuer zweites Wort -> zaehlt als gelernt, landet NICHT auf Merkliste
const secondWordEn = G.UNIT1_SECTIONS[0].words[1].en;
click(win, doc.querySelector(".fc-assess .know"));
check("'Kann ich schon' erhoeht wordsLearned", G.knownWordCount() === 1);
check("'Kann ich schon' fuer neues Wort landet nicht auf Merkliste", !G.state.merkliste.some(m => m.en === secondWordEn));

// --- Übersicht: Stern verbindet direkt mit Merkliste ---
click(win, doc.querySelector('[data-secmode="overview"]'));
check("Übersicht-Panel aktiv", doc.querySelector('[data-mode-panel="overview"]').classList.contains("active"));
const ovStars = Array.from(doc.querySelectorAll("#secOverviewPanel .ov-star"));
check("Übersicht zeigt alle 19 Woerter", ovStars.length === 19);
check("Stern fuer 'Muss ich üben'-Wort zeigt bereits an (Merkliste)", ovStars[0].classList.contains("on"));
const ovRows = Array.from(doc.querySelectorAll("#secOverviewPanel .ov-table tr"));
check("'Kann ich schon'-Wort bekommt Gekonnt-Häkchen in der Übersicht", ovRows[1].classList.contains("ov-row-known") && !!ovRows[1].querySelector(".ov-known-badge"));
check("'Muss ich üben'-Wort bekommt KEIN Gekonnt-Häkchen", !ovRows[0].classList.contains("ov-row-known") && !ovRows[0].querySelector(".ov-known-badge"));
check("Nicht bewertetes Wort bekommt KEIN Gekonnt-Häkchen", !ovRows[3].classList.contains("ov-row-known"));
click(win, ovStars[2]);
const thirdWordEn = G.UNIT1_SECTIONS[0].words[2].en;
check("Stern-Klick fuegt Wort zur Merkliste hinzu", G.state.merkliste.some(m => m.en === thirdWordEn));
click(win, ovStars[2]);
check("Erneuter Stern-Klick entfernt Wort wieder", !G.state.merkliste.some(m => m.en === thirdWordEn));
click(win, ovStars[2]); // wieder hinzufuegen fuer spaeteren Merkliste-Test

// --- zurueck zur Unit-Ansicht: Fortschritt sichtbar ---
click(win, doc.getElementById("sectionBackBtn"));
check("Zurueck-Button fuehrt zur Unit-Ansicht", G.currentView() === "unit");
const sectionCards2 = Array.from(doc.querySelectorAll("#sectionList .sec-card"));
check("Abschnitt 1 zeigt aktualisierten Fortschritt (Sterne zaehlen nicht als geuebt)", sectionCards2[0].querySelector(".sec-meta").textContent === "2 / 19 Wörter geübt");

// --- Startbildschirm: CTA und Merkliste-Zaehler aktualisiert ---
click(win, doc.getElementById("unitBackBtn"));
check("Zurueck fuehrt zum Startbildschirm", G.currentView() === "start");
check("CTA zeigt jetzt Weiterspielen", doc.getElementById("ctaTitle").textContent === "Weiterspielen");
check("Merkliste-Kachel zeigt 2 Wörter", doc.getElementById("wordlistSub").textContent === "2 Wörter");

// --- Merkliste-Ansicht: direkte Navigation ueber Kachel ---
click(win, doc.getElementById("wordlistTile"));
check("Merkliste-Kachel fuehrt direkt zur Merkliste (kein Modal)", G.currentView() === "merkliste" && !G.isModalOpen());
check("Merkliste zeigt 2 Eintraege", doc.querySelectorAll("#mkListWrap .mk-row").length === 2);

// manuelles Entfernen durch die/den SuS
const mkRemoveButtons = Array.from(doc.querySelectorAll(".mk-remove"));
const enBeforeRemove = G.state.merkliste[0].en;
click(win, mkRemoveButtons[0]);
check("Manuelles Entfernen von der Merkliste funktioniert", !G.state.merkliste.some(m => m.en === enBeforeRemove));
check("Merkliste-Liste aktualisiert sich sofort", doc.querySelectorAll("#mkListWrap .mk-row").length === 1);

// --- Merkliste wiederholen: 2x erfolgreich = automatisches Entfernen ---
click(win, doc.getElementById("mkReviewBtn"));
check("Wiederholungs-Karteikarten erscheinen", !!doc.querySelector("#mkReviewPanel .flashcard"));
const remainingEn = G.state.merkliste[0].en;
click(win, doc.querySelector("#mkReviewPanel .fc-assess .know"));
check("1. erfolgreiche Wiederholung erhoeht reviewCount", G.state.merkliste.find(m => m.en === remainingEn).reviewCount === 1);
check("Wort bleibt nach 1x auf der Merkliste", G.state.merkliste.some(m => m.en === remainingEn));
click(win, doc.querySelector("#mkReviewPanel .fc-nav")); // zurueck zur (einzigen) Karte
click(win, doc.querySelector("#mkReviewPanel .fc-assess .know"));
check("Nach 2x erfolgreicher Wiederholung von der Merkliste entfernt", !G.state.merkliste.some(m => m.en === remainingEn));
check("Merkliste-Liste zeigt jetzt 0 Eintraege", doc.querySelectorAll("#mkListWrap .mk-row").length === 0);

// --- "Muss ich üben" setzt reviewCount zurueck statt zu entfernen ---
{
  const { win: win3, doc: doc3 } = freshDom();
  const G3 = win3.__game;
  const w = G3.UNIT1_WORDS[5];
  G3.toggleMerkliste(w.en);
  G3.assessWord(w.en, "know");
  check("reviewCount nach 1x know = 1", G3.state.merkliste.find(m => m.en === w.en).reviewCount === 1);
  G3.assessWord(w.en, "practice");
  check("'Muss ich üben' setzt reviewCount zurueck auf 0", G3.state.merkliste.find(m => m.en === w.en).reviewCount === 0);
  check("Wort bleibt bei 'Muss ich üben' auf der Merkliste", G3.state.merkliste.some(m => m.en === w.en));
}

// --- Abschnitts-Abzeichen: reine Belohnung, kein Gate ---
{
  const { win: winB, doc: docB } = freshDom();
  const GB = winB.__game;
  GB.showView("unit");
  let cards = Array.from(docB.querySelectorAll("#sectionList .sec-card"));
  check("Vor Abschluss: kein Abzeichen im ersten Abschnitt", !cards[0].querySelector(".sec-badge"));
  check("Vor Abschluss: zweiter Abschnitt trotzdem anklickbar (kein Gate)", !cards[1].disabled);

  // Abschnitt 1 vollstaendig als gekonnt markieren -> Abzeichen sollte beim naechsten
  // Rendern der Unit-Ansicht mit Pop-Animation auftauchen und dauerhaft gespeichert werden.
  GB.completeSection(0);
  GB.showView("unit");
  cards = Array.from(docB.querySelectorAll("#sectionList .sec-card"));
  const badge0 = cards[0].querySelector(".sec-badge");
  check("Abzeichen erscheint, sobald Abschnitt fertig ist", !!badge0);
  check("Frisch verdientes Abzeichen spielt Pop-Animation ab", badge0.classList.contains("pop"));
  check("Abzeichen wird dauerhaft gemerkt (badgesSeen)", GB.state.badgesSeen.indexOf(GB.UNIT1_SECTIONS[0].name) !== -1);
  check("Toast zeigt 'Geschafft' (nicht 'freigespielt')", docB.getElementById("unitToast").textContent.indexOf("Geschafft") !== -1);
  check("Toast nennt nicht mehr 'freigespielt'", docB.getElementById("unitToast").textContent.indexOf("freigespielt") === -1);
  check("Zweiter Abschnitt bleibt ohne eigenes Abzeichen weiterhin frei anklickbar", !cards[1].disabled);

  // Erneutes Rendern (z.B. nach Zurueck-Navigation) darf die Animation NICHT wiederholen.
  GB.showView("start");
  GB.showView("unit");
  const badge0Again = docB.querySelector("#sectionList .sec-card").querySelector(".sec-badge");
  check("Abzeichen bleibt sichtbar, aber Animation laeuft beim erneuten Rendern nicht erneut", !!badge0Again && !badge0Again.classList.contains("pop"));
}

// --- Gekonnt-Status bleibt erhalten, auch wenn das Wort von der Merkliste verschwindet ---
{
  const { win: win4, doc: doc4 } = freshDom();
  const G4 = win4.__game;
  const w = G4.UNIT1_WORDS[10];
  G4.toggleMerkliste(w.en);
  G4.assessWord(w.en, "know"); // reviewCount 1
  G4.assessWord(w.en, "know"); // reviewCount 2 -> Meisterschaft, von Merkliste entfernt
  check("Wort ist nach Meisterschaft von der Merkliste verschwunden", !G4.state.merkliste.some(m => m.en === w.en));
  check("Wort zaehlt weiterhin als gelernt (wordAssessments bleibt)", G4.knownWordCount() >= 1 && win4.localStorage.getItem(G4.STORAGE_KEY).includes('"' + w.en.replace(/"/g, '\\"') + '":"know"'));
  // Übersicht des zugehoerigen Abschnitts zeigt weiterhin das Haekchen
  const secIdx = G4.UNIT1_SECTIONS.findIndex(s => s.words.some(x => x.en === w.en));
  G4.openSection(secIdx);
  doc4.querySelector('[data-secmode="overview"]').dispatchEvent(new win4.MouseEvent("click", { bubbles: true }));
  const row = Array.from(doc4.querySelectorAll("#secOverviewPanel .ov-table tr")).find(tr => tr.querySelector(".en").textContent.indexOf(w.en) === 0);
  check("Übersicht zeigt Gekonnt-Häkchen auch nach Entfernen von der Merkliste", !!row && row.classList.contains("ov-row-known"));
  check("Stern ist nach Meisterschaft wieder aus (nicht mehr auf Merkliste)", !!row && !row.querySelector(".ov-star").classList.contains("on"));
}

// --- Export ---
const exported = JSON.parse(G.exportProgressData());
check("Export enthaelt Streak", exported.streakCount === 1);
check("Export enthaelt gelernte Vokabeln", exported.wordsLearned === G.knownWordCount());
check("Export enthaelt Abschnittsfortschritt", exported.abschnitteGesamt === 10);

// --- Reset ist idempotent nutzbar ---
G.resetProgress();
check("Reset setzt Streak zurueck auf 1", G.state.streakCount === 1);
check("Reset setzt gelernte Vokabeln zurueck", G.knownWordCount() === 0);
check("Reset leert die Merkliste", G.state.merkliste.length === 0);
check("Reset aktualisiert DOM", doc.getElementById("wordsLabel").textContent === "0 / " + G.UNIT1_WORDS.length + " Vokabeln");

// --- Zweiter Boot am Folgetag erhoeht Streak korrekt ---
{
  const { win: win2 } = freshDom();
  const G2 = win2.__game;
  const r = G2.computeStreak(4, "2020-01-01", "2020-01-02");
  check("Folgetag-Simulation erhoeht Streak", r.count === 5);
}

console.log("  " + ok.length + "/" + (ok.length + fail.length) + " Checks bestanden");
if (fail.length) { fail.forEach(n => console.log("  XX " + n)); process.exit(1); }
