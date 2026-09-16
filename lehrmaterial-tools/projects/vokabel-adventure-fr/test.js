// Funktionstest des Vokabel-Adventure-Startbildschirms (Französisch) und der Teil-1-Vokabellernstrecke via jsdom.
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
check("Startzustand: Teil 1 mit echtem Namen", doc.getElementById("unitLabel").textContent === "Teil 1 · Wörter 1–180");
check("Startzustand: 0 / N Vokabeln", doc.getElementById("wordsLabel").textContent === "0 / " + G.UNIT1_WORDS.length + " Vokabeln");
check("Startzustand: CTA zeigt Loslegen", doc.getElementById("ctaTitle").textContent === "Loslegen");
check("Startzustand: Streak 1 Tag nach erstem Besuch", G.state.streakCount === 1);
check("Merkliste startet leer", doc.getElementById("wordlistSub").textContent === "0 Wörter");
check("Keine Duell-Kachel mehr vorhanden", !doc.getElementById("duelTile"));
check("Kein Schulname/Logo im Header", !doc.querySelector(".logo-badge"));

// --- Teil 1: Datenstruktur ---
check("4 Teile definiert", G.UNITS.length === 4);
check("Kapitel-Kachel zeigt 4 Teile", doc.getElementById("chaptersSub").textContent === "4 Teile");
check("Teil 2 hat den erwarteten Platzhalter-Namen", G.UNITS[1].name === "Wörter 181–ca. 340");
check("Teil 1 hat 9 Abschnitte", G.UNIT1_SECTIONS.length === 9);
check("Jeder Abschnitt hat genau 20 Wörter", G.UNIT1_SECTIONS.every(s => s.words.length === 20));
check("Teil 1 hat 180 Vokabeln insgesamt", G.UNIT1_WORDS.length === 180);
const wordFrs = G.UNIT1_WORDS.map(w => w.fr);
check("Keine doppelten Karteikarten-Schluessel", new Set(wordFrs).size === wordFrs.length);
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
check("Kein Duell-Menuepunkt mehr", !doc.querySelector('[data-nav="duel"]'));
check("'Spiele' steht im Menue", !!doc.querySelector('[data-nav="games"]'));
click(win, doc.querySelector('[data-nav="achievements"]'));
check("Klick auf Menuepunkt schliesst Menue", G.isDrawerOpen() === false);
check("Klick auf 'Erfolge' oeffnet Modal", G.isModalOpen() === true);
check("Modal-Titel Erfolge", doc.getElementById("modalTitle").textContent === "Erfolge");
key(win, doc, "Escape");
check("Escape schliesst Modal", G.isModalOpen() === false);

// --- Menuepunkt "Spiele" und "Übungen" fuehren zu echten Ansichten (kein Modal) ---
click(win, doc.getElementById("menuBtn"));
click(win, doc.querySelector('[data-nav="games"]'));
check("'Spiele' oeffnet die Spiele-Uebersicht (kein Modal)", G.currentView() === "games" && !G.isModalOpen());
click(win, doc.getElementById("gamesBackBtn"));
click(win, doc.getElementById("menuBtn"));
click(win, doc.querySelector('[data-nav="exercises"]'));
check("'Übungen' oeffnet die Uebungen-Uebersicht (kein Modal)", G.currentView() === "exercises" && !G.isModalOpen());
click(win, doc.getElementById("exercisesBackBtn"));

// --- Kapitel-Modal: Teil 1 klickbar, Teil 2-4 gesperrt ---
click(win, doc.getElementById("chaptersTile"));
check("Kapitel-Modal oeffnet", G.isModalOpen() === true);
const chapterButtons = Array.from(doc.querySelectorAll("#modalBody button.achv"));
check("Genau ein klickbarer Teil im Kapitel-Modal", chapterButtons.length === 1);
check("Teil 2-4 als gesperrt markiert", doc.querySelectorAll("#modalBody .achv.locked").length === 3);
click(win, chapterButtons[0]);
check("Klick auf Teil 1 schliesst Modal", G.isModalOpen() === false);
check("Klick auf Teil 1 oeffnet Unit-Ansicht", G.currentView() === "unit");

// --- Unit-Ansicht: 9 Abschnitts-Karten ---
const sectionCards = Array.from(doc.querySelectorAll("#sectionList .sec-card"));
check("9 Abschnitts-Karten gerendert", sectionCards.length === 9);
check("Erste Karte zeigt 0 / 20 Woerter", sectionCards[0].querySelector(".sec-meta").textContent === "0 / 20 Wörter geübt");

// --- Abschnitt oeffnen: Karteikarten ---
click(win, sectionCards[0]);
check("Abschnitts-Ansicht aktiv", G.currentView() === "section");
check("Karteikarte zeigt erstes Wort", doc.querySelector(".fc-front .fc-word").textContent === G.UNIT1_SECTIONS[0].words[0].fr);
check("Karteikarte startet nicht umgedreht", !doc.querySelector(".flashcard").classList.contains("flipped"));
click(win, doc.querySelector(".flashcard"));
check("Klick auf Karte dreht sie um", doc.querySelector(".flashcard").classList.contains("flipped"));

// "Muss ich üben" -> landet auf Merkliste, wird NICHT als bekannt gezaehlt
const firstWordFr = G.UNIT1_SECTIONS[0].words[0].fr;
click(win, doc.querySelector(".fc-assess .practice"));
check("Nach 'Muss ich üben' ist Wort auf Merkliste", G.state.merkliste.some(m => m.fr === firstWordFr));
check("Karte wechselt automatisch weiter", doc.querySelector(".fc-progress").textContent === "2 / 20");
check("wordsLearned zaehlt 'Muss ich üben' nicht mit", G.knownWordCount() === 0);

// "Kann ich schon" fuer zweites Wort -> zaehlt als gelernt, landet NICHT auf Merkliste
const secondWordFr = G.UNIT1_SECTIONS[0].words[1].fr;
click(win, doc.querySelector(".fc-assess .know"));
check("'Kann ich schon' erhoeht wordsLearned", G.knownWordCount() === 1);
check("'Kann ich schon' fuer neues Wort landet nicht auf Merkliste", !G.state.merkliste.some(m => m.fr === secondWordFr));

// --- Übersicht: Stern verbindet direkt mit Merkliste ---
click(win, doc.querySelector('[data-secmode="overview"]'));
check("Übersicht-Panel aktiv", doc.querySelector('[data-mode-panel="overview"]').classList.contains("active"));
const ovStars = Array.from(doc.querySelectorAll("#secOverviewPanel .ov-star"));
check("Übersicht zeigt alle 20 Woerter", ovStars.length === 20);
check("Stern fuer 'Muss ich üben'-Wort zeigt bereits an (Merkliste)", ovStars[0].classList.contains("on"));
const ovRows = Array.from(doc.querySelectorAll("#secOverviewPanel .ov-table tr"));
check("'Kann ich schon'-Wort bekommt Gekonnt-Häkchen in der Übersicht", ovRows[1].classList.contains("ov-row-known") && !!ovRows[1].querySelector(".ov-known-badge"));
check("'Muss ich üben'-Wort bekommt KEIN Gekonnt-Häkchen", !ovRows[0].classList.contains("ov-row-known") && !ovRows[0].querySelector(".ov-known-badge"));
check("Nicht bewertetes Wort bekommt KEIN Gekonnt-Häkchen", !ovRows[3].classList.contains("ov-row-known"));
click(win, ovStars[2]);
const thirdWordFr = G.UNIT1_SECTIONS[0].words[2].fr;
check("Stern-Klick fuegt Wort zur Merkliste hinzu", G.state.merkliste.some(m => m.fr === thirdWordFr));
click(win, ovStars[2]);
check("Erneuter Stern-Klick entfernt Wort wieder", !G.state.merkliste.some(m => m.fr === thirdWordFr));
click(win, ovStars[2]); // wieder hinzufuegen fuer spaeteren Merkliste-Test

// --- zurueck zur Unit-Ansicht: Fortschritt sichtbar ---
click(win, doc.getElementById("sectionBackBtn"));
check("Zurueck-Button fuehrt zur Unit-Ansicht", G.currentView() === "unit");
const sectionCards2 = Array.from(doc.querySelectorAll("#sectionList .sec-card"));
check("Abschnitt 1 zeigt aktualisierten Fortschritt (Sterne zaehlen nicht als geuebt)", sectionCards2[0].querySelector(".sec-meta").textContent === "2 / 20 Wörter geübt");

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
const frBeforeRemove = G.state.merkliste[0].fr;
click(win, mkRemoveButtons[0]);
check("Manuelles Entfernen von der Merkliste funktioniert", !G.state.merkliste.some(m => m.fr === frBeforeRemove));
check("Merkliste-Liste aktualisiert sich sofort", doc.querySelectorAll("#mkListWrap .mk-row").length === 1);

// --- Merkliste wiederholen: 2x erfolgreich = automatisches Entfernen ---
click(win, doc.getElementById("mkReviewBtn"));
check("Wiederholungs-Karteikarten erscheinen", !!doc.querySelector("#mkReviewPanel .flashcard"));
const remainingFr = G.state.merkliste[0].fr;
click(win, doc.querySelector("#mkReviewPanel .fc-assess .know"));
check("1. erfolgreiche Wiederholung erhoeht reviewCount", G.state.merkliste.find(m => m.fr === remainingFr).reviewCount === 1);
check("Wort bleibt nach 1x auf der Merkliste", G.state.merkliste.some(m => m.fr === remainingFr));
click(win, doc.querySelector("#mkReviewPanel .fc-nav")); // zurueck zur (einzigen) Karte
click(win, doc.querySelector("#mkReviewPanel .fc-assess .know"));
check("Nach 2x erfolgreicher Wiederholung von der Merkliste entfernt", !G.state.merkliste.some(m => m.fr === remainingFr));
check("Merkliste-Liste zeigt jetzt 0 Eintraege", doc.querySelectorAll("#mkListWrap .mk-row").length === 0);

// --- "Muss ich üben" setzt reviewCount zurueck statt zu entfernen ---
{
  const { win: win3, doc: doc3 } = freshDom();
  const G3 = win3.__game;
  const w = G3.UNIT1_WORDS[5];
  G3.toggleMerkliste(w.fr);
  G3.assessWord(w.fr, "know");
  check("reviewCount nach 1x know = 1", G3.state.merkliste.find(m => m.fr === w.fr).reviewCount === 1);
  G3.assessWord(w.fr, "practice");
  check("'Muss ich üben' setzt reviewCount zurueck auf 0", G3.state.merkliste.find(m => m.fr === w.fr).reviewCount === 0);
  check("Wort bleibt bei 'Muss ich üben' auf der Merkliste", G3.state.merkliste.some(m => m.fr === w.fr));
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
  G4.toggleMerkliste(w.fr);
  G4.assessWord(w.fr, "know"); // reviewCount 1
  G4.assessWord(w.fr, "know"); // reviewCount 2 -> Meisterschaft, von Merkliste entfernt
  check("Wort ist nach Meisterschaft von der Merkliste verschwunden", !G4.state.merkliste.some(m => m.fr === w.fr));
  check("Wort zaehlt weiterhin als gelernt (wordAssessments bleibt)", G4.knownWordCount() >= 1 && win4.localStorage.getItem(G4.STORAGE_KEY).includes('"' + w.fr.replace(/"/g, '\\"') + '":"know"'));
  // Übersicht des zugehoerigen Abschnitts zeigt weiterhin das Haekchen
  const secIdx = G4.UNIT1_SECTIONS.findIndex(s => s.words.some(x => x.fr === w.fr));
  G4.openSection(secIdx);
  doc4.querySelector('[data-secmode="overview"]').dispatchEvent(new win4.MouseEvent("click", { bubbles: true }));
  const row = Array.from(doc4.querySelectorAll("#secOverviewPanel .ov-table tr")).find(tr => tr.querySelector(".fr").textContent.indexOf(w.fr) === 0);
  check("Übersicht zeigt Gekonnt-Häkchen auch nach Entfernen von der Merkliste", !!row && row.classList.contains("ov-row-known"));
  check("Stern ist nach Meisterschaft wieder aus (nicht mehr auf Merkliste)", !!row && !row.querySelector(".ov-star").classList.contains("on"));
}

// --- Spiele: Datenstruktur ---
{
  check("Ein Spiel pro Abschnitt", G.SECTION_GAMES.length === G.UNIT1_SECTIONS.length);
  const types = G.SECTION_GAMES.map(g => g.type);
  check("Alle Spieltypen sind lela/hangman/tempo", types.every(t => ["lela", "hangman", "tempo"].includes(t)));
  check("Nie zweimal derselbe Spieltyp direkt hintereinander", types.every((t, i) => i === 0 || t !== types[i - 1]));
  check("Alle drei Spieltypen kommen vor", new Set(types).size === 3);
  check("Jeder Typ kommt 3x vor", ["lela", "hangman", "tempo"].every(t => types.filter(x => x === t).length === 3));

  G.SECTION_GAMES.forEach((game, idx) => {
    if (game.type === "lela") {
      check(`Artikel-Sortieren Abschnitt ${idx + 1}: mind. 6 Woerter`, game.items.length >= 6);
      check(`Artikel-Sortieren Abschnitt ${idx + 1}: jedes Item hat le/la`, game.items.every(it => it.art === "le" || it.art === "la"));
    } else if (game.type === "hangman") {
      check(`Galgenmaennchen Abschnitt ${idx + 1}: mind. 6 Woerter`, game.items.length >= 6);
      check(`Galgenmaennchen Abschnitt ${idx + 1}: keine Leerzeichen in den Woertern`, game.items.every(it => !/\s/.test(it.fr)));
    } else {
      check(`Tempo-Runde Abschnitt ${idx + 1}: alle 20 Woerter des Abschnitts`, game.items.length === 20);
    }
  });
}

// --- Spiele-Uebersicht: Navigation und Kachel pro Abschnitt ---
{
  const { win: winG, doc: docG } = freshDom();
  const GG = winG.__game;
  GG.showView("games");
  const gameCards = Array.from(docG.querySelectorAll("#gameList .sec-card"));
  check("Spiele-Uebersicht zeigt 9 Karten", gameCards.length === 9);
  check("Erste Karte zeigt Tempo-Runde-Chip", !!gameCards[0].querySelector(".game-type-chip.tempo"));
  check("Zweite Karte zeigt Artikel-Sortieren-Chip", !!gameCards[1].querySelector(".game-type-chip.lela"));
  check("Dritte Karte zeigt Galgenmaennchen-Chip", !!gameCards[2].querySelector(".game-type-chip.hangman"));

  // --- Artikel-Sortieren: richtige und falsche Zuordnung ---
  click(winG, gameCards[1]);
  check("Klick auf Karte oeffnet die Spiel-Ansicht", GG.currentView() === "gameplay");
  const lelaWord = docG.querySelector(".lela-word").textContent;
  const lelaItem = GG.SECTION_GAMES[1].items.find(it => it.fr === lelaWord);
  const bins = Array.from(docG.querySelectorAll(".lela-bin"));
  const correctBin = lelaItem.art === "le" ? bins[0] : bins[1];
  click(winG, correctBin);
  check("Richtige le/la-Wahl faerbt den Korb gruen", correctBin.classList.contains("pulse-good"));
  check("Punktestand zaehlt 1/1", docG.querySelector(".game-score").textContent === "Richtig: 1 / 1");

  // --- Galgenmaennchen: richtiger und falscher Buchstabe ---
  click(winG, docG.getElementById("gamePlayBackBtn"));
  const gameCards2 = Array.from(docG.querySelectorAll("#gameList .sec-card"));
  click(winG, gameCards2[2]);
  const hangHint = docG.querySelector(".hang-hint").textContent.replace("Hinweis: ", "");
  const hangItem = GG.SECTION_GAMES[2].items.find(it => it.de === hangHint);
  const firstLetter = hangItem.fr[0];
  const keyBtn = Array.from(docG.querySelectorAll(".hang-key")).find(k => k.textContent === firstLetter);
  click(winG, keyBtn);
  check("Richtiger Buchstabe wird aufgedeckt", docG.querySelector(".hang-word").textContent.replace(/\s/g, "").startsWith(firstLetter));
  check("Richtiger Buchstabe markiert den Button gruen", keyBtn.classList.contains("used-right"));

  // --- Tempo-Runde: Start startet Timer und zeigt Multiple-Choice ---
  click(winG, docG.getElementById("gamePlayBackBtn"));
  const gameCards3 = Array.from(docG.querySelectorAll("#gameList .sec-card"));
  click(winG, gameCards3[0]);
  click(winG, docG.querySelector(".tempo-start"));
  check("Tempo-Runde zeigt nach Start 4 Antwortoptionen", docG.querySelectorAll(".tempo-opt").length === 4);
  check("Tempo-Runde zeigt laufenden Timer", docG.querySelector(".tempo-timer").textContent === "60s");
}

// --- Uebungen: Datenstruktur ---
{
  check("Ein Luekentext pro Abschnitt", G.SECTION_CLOZE.length === G.UNIT1_SECTIONS.length);
  G.SECTION_CLOZE.forEach((text, idx) => {
    const blanks = (text.match(/\{[^}]+\}/g) || []);
    check(`Abschnitt ${idx + 1}: Luekentext hat mindestens 5 Luecken`, blanks.length >= 5);
    check(`Abschnitt ${idx + 1}: Luekentext ist Fliesstext ohne rohe Klammer-Reste`, !/[{}]/.test(text.replace(/\{[^}]+\}/g, "")));
  });
}

// --- Uebungen: Navigation ueber Kachel und Menue (kein Modal mehr) ---
{
  const { win: winE, doc: docE } = freshDom();
  const GE = winE.__game;
  click(winE, docE.getElementById("exercisesTile"));
  check("'Übungen'-Kachel fuehrt direkt zur Uebungen-Uebersicht (kein Modal)", GE.currentView() === "exercises" && !GE.isModalOpen());
  const exCards = Array.from(docE.querySelectorAll("#exerciseList .sec-card"));
  check("Uebungen-Uebersicht zeigt 9 Karten", exCards.length === 9);

  click(winE, exCards[0]);
  check("Klick auf Abschnitts-Karte oeffnet die Uebungs-Ansicht", GE.currentView() === "exerciseplay");
  check("Luekentext-Panel zeigt Eingabefelder", docE.querySelectorAll(".blank-input").length >= 5);

  click(winE, docE.getElementById("exercisePlayBackBtn"));
  check("Zurueck aus der Uebungs-Ansicht fuehrt zur Uebungen-Uebersicht", GE.currentView() === "exercises");
  click(winE, docE.getElementById("exercisesBackBtn"));
  check("Zurueck aus der Uebungen-Uebersicht fuehrt zum Startbildschirm", GE.currentView() === "start");
}

// --- Luekentext: Pruefen faerbt Felder gruen/rot, leere Felder bleiben neutral ---
{
  const { win: winC, doc: docC } = freshDom();
  const GC = winC.__game;
  GC.openExercise(0);
  const panel = docC.getElementById("exClozePanel");
  const blanks = Array.from(panel.querySelectorAll(".blank-input"));
  check("Luekentext zeigt Eingabefelder fuer jede Luecke", blanks.length >= 5);
  blanks[0].value = blanks[0].dataset.answer.toUpperCase();
  blanks[1].value = "definitiv falsch";
  // blanks[2] bleibt leer
  click(winC, panel.querySelector(".cloze-check"));
  check("Richtig ausgefuellte Luecke wird gruen markiert", blanks[0].classList.contains("correct"));
  check("Falsch ausgefuellte Luecke wird rot markiert", blanks[1].classList.contains("wrong"));
  check("Leere Luecke bleibt neutral (weder gruen noch rot)", !blanks[2].classList.contains("correct") && !blanks[2].classList.contains("wrong"));
  check("Ergebnis-Anzeige zaehlt richtige Luecken", panel.querySelector(".cloze-result").textContent === "1 von " + blanks.length + " richtig");

  click(winC, panel.querySelector(".cloze-reset"));
  check("Zuruecksetzen leert alle Felder", blanks.every(b => b.value === "" && !b.classList.contains("correct") && !b.classList.contains("wrong")));
}

// --- Export ---
const exported = JSON.parse(G.exportProgressData());
check("Export enthaelt Streak", exported.streakCount === 1);
check("Export enthaelt gelernte Vokabeln", exported.wordsLearned === G.knownWordCount());
check("Export enthaelt Abschnittsfortschritt", exported.abschnitteGesamt === 9);

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
