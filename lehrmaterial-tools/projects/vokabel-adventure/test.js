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
check("Startzustand: CTA zeigt Start", doc.getElementById("ctaTitle").textContent === "Start");
check("Startzustand: Streak 1 Tag nach erstem Besuch", G.state.streakCount === 1);
check("Merkliste startet leer", doc.getElementById("wordlistSub").textContent === "0 words");

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

// --- Menuepunkt "Spiele" fuehrt zur Spiele-Uebersicht ---
click(win, doc.getElementById("menuBtn"));
check("'Spiele' steht im Menue", !!doc.querySelector('[data-nav="games"]'));
click(win, doc.querySelector('[data-nav="games"]'));
check("'Spiele' oeffnet die Spiele-Uebersicht (kein Modal mehr)", G.currentView() === "games" && !G.isModalOpen());

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
check("Karteikarte zeigt erstes Wort (Deutsch vorne)", doc.querySelector(".fc-front .fc-word").textContent === G.UNIT1_SECTIONS[0].words[0].de);
check("Karteikarte startet nicht umgedreht", !doc.querySelector(".flashcard").classList.contains("flipped"));
click(win, doc.querySelector(".flashcard"));
check("Klick auf Karte dreht sie um", doc.querySelector(".flashcard").classList.contains("flipped"));
check("Kartenrueckseite zeigt Englisch", doc.querySelector(".fc-back .fc-word").textContent === G.UNIT1_SECTIONS[0].words[0].en);

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
check("CTA zeigt jetzt Continue", doc.getElementById("ctaTitle").textContent === "Continue");
check("Merkliste-Kachel zeigt 2 words", doc.getElementById("wordlistSub").textContent === "2 words");

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

// --- Spiele: ein Spiel pro Abschnitt, Typ wechselt, Daten stimmen mit den Woertern ueberein ---
{
  check("Ein Spiel pro Abschnitt", G.SECTION_GAMES.length === G.UNIT1_SECTIONS.length);
  const types = G.SECTION_GAMES.map(g => g.type);
  check("Alle Spieltypen sind memory/match/truefalse", types.every(t => ["memory", "match", "truefalse"].includes(t)));
  check("Nie zweimal derselbe Spieltyp direkt hintereinander", types.every((t, i) => i === 0 || t !== types[i - 1]));
  check("Alle drei Spieltypen kommen vor", new Set(types).size === 3);

  G.SECTION_GAMES.forEach((game, idx) => {
    const sectionEns = new Set(G.UNIT1_SECTIONS[idx].words.map(w => w.en));
    if (game.type === "memory") {
      check(`Memory Abschnitt ${idx + 1}: alle Emoji-Woerter existieren in der Station`, game.emojis.every(([en]) => sectionEns.has(en)));
      check(`Memory Abschnitt ${idx + 1}: mind. 6 Paare`, game.emojis.length >= 6);
    } else if (game.type === "match") {
      check(`Zuordnung Abschnitt ${idx + 1}: alle Woerter existieren in der Station`, game.wordEns.every(en => sectionEns.has(en)));
      check(`Zuordnung Abschnitt ${idx + 1}: mind. 6 Paare`, game.wordEns.length >= 6);
    } else if (game.type === "truefalse") {
      check(`Wahr/Falsch Abschnitt ${idx + 1}: jede Aussage hat Erklaerung + boolean`, game.items.every(it => typeof it.correct === "boolean" && !!it.statement && !!it.explanation));
      check(`Wahr/Falsch Abschnitt ${idx + 1}: mind. 6 Aussagen`, game.items.length >= 6);
    }
  });
}

// --- Spiele-Uebersicht: Navigation und Kachel pro Abschnitt ---
{
  const { win: winG, doc: docG } = freshDom();
  const GG = winG.__game;
  GG.showView("games");
  const gameCards = Array.from(docG.querySelectorAll("#gameList .sec-card"));
  check("Spiele-Uebersicht zeigt 10 Karten", gameCards.length === 10);
  check("Erste Karte zeigt Memory-Chip", !!gameCards[0].querySelector(".game-type-chip.memory"));
  check("Zweite Karte zeigt Zuordnung-Chip", !!gameCards[1].querySelector(".game-type-chip.match"));
  check("Dritte Karte zeigt Wahr/Falsch-Chip", !!gameCards[2].querySelector(".game-type-chip.truefalse"));

  // --- Memory: Klick auf zwei identische Karten bleibt offen und zaehlt als Paar ---
  click(winG, gameCards[0]);
  check("Klick auf Memory-Karte oeffnet die Spiel-Ansicht", GG.currentView() === "gameplay");
  const memCards = Array.from(docG.querySelectorAll(".mem-card"));
  check("Memory-Grid hat 16 Karten (8 Paare)", memCards.length === 16);
  const firstWord = memCards[0].querySelector(".mem-word").textContent;
  const matchIdx = memCards.findIndex((c, i) => i !== 0 && c.querySelector(".mem-word").textContent === firstWord);
  click(winG, memCards[0]);
  click(winG, memCards[matchIdx]);
  check("Gefundenes Paar bekommt 'matched'", memCards[0].classList.contains("matched") && memCards[matchIdx].classList.contains("matched"));
  check("Paarzaehler steht auf 1 / 8", docG.getElementById("memPairs").textContent === "1 / 8");
  check("Zugzaehler steht auf 1", docG.getElementById("memMoves").textContent === "1");

  // --- zurueck zur Spiele-Uebersicht, dann Zuordnung oeffnen ---
  click(winG, docG.getElementById("gamePlayBackBtn"));
  check("Zurueck fuehrt zur Spiele-Uebersicht", GG.currentView() === "games");
  const gameCards2 = Array.from(docG.querySelectorAll("#gameList .sec-card"));
  click(winG, gameCards2[1]);
  const leftItems = Array.from(docG.querySelectorAll(".match-col"))[0].querySelectorAll(".match-item");
  const rightItems = Array.from(docG.querySelectorAll(".match-col"))[1].querySelectorAll(".match-item");
  check("Zuordnung zeigt 8 Begriffe links und rechts", leftItems.length === 8 && rightItems.length === 8);
  // richtiges Paar finden: linkes Wort mit seiner deutschen Übersetzung verknuepfen
  const wordObj = GG.SECTION_GAMES[1].wordEns.map(en => ({ en, de: GG.UNIT1_WORDS.find(w => w.en === en).de })).find(w => w.en === leftItems[0].textContent);
  const rightMatch = Array.from(rightItems).find(r => r.textContent === wordObj.de);
  click(winG, leftItems[0]);
  click(winG, rightMatch);
  check("Richtiges Paar wird gruen markiert und gesperrt", leftItems[0].classList.contains("correct") && rightMatch.classList.contains("correct"));
  check("Status zeigt 1 / 8 Paare", docG.getElementById("matchStatus").textContent === "1 / 8 Paare");

  // --- zurueck, dann Wahr/Falsch oeffnen ---
  click(winG, docG.getElementById("gamePlayBackBtn"));
  const gameCards3 = Array.from(docG.querySelectorAll("#gameList .sec-card"));
  click(winG, gameCards3[2]);
  const tfItem = GG.SECTION_GAMES[2].items[0];
  const trueBtn = docG.querySelector(".tf-buttons button:first-child");
  const falseBtn = docG.querySelector(".tf-buttons button:last-child");
  const rightBtn = tfItem.correct ? trueBtn : falseBtn;
  const wrongBtn = tfItem.correct ? falseBtn : trueBtn;
  click(winG, rightBtn);
  check("Richtige Antwort wird als 'chosen-correct' markiert", rightBtn.classList.contains("chosen-correct"));
  check("Feedback zeigt die Erklaerung", docG.querySelector(".tf-feedback").textContent.indexOf(tfItem.explanation) !== -1);
  check("Buttons sind danach gesperrt", trueBtn.disabled && falseBtn.disabled);
  click(winG, wrongBtn); // gesperrt: darf nichts mehr aendern
  check("Erneuter Klick nach Antwort aendert nichts mehr", rightBtn.classList.contains("chosen-correct") && !wrongBtn.classList.contains("chosen-wrong"));
  const nextBtn = docG.querySelector(".tf-nav .fc-nav");
  click(winG, nextBtn);
  check("Weiter-Button zeigt die naechste Aussage", docG.querySelector(".tf-progress").textContent === "2 / " + GG.SECTION_GAMES[2].items.length);
}

// --- Uebungen: Datenstruktur ---
{
  check("Ein Uebungs-Datensatz pro Abschnitt", G.SECTION_EXERCISES.length === G.UNIT1_SECTIONS.length);
  G.SECTION_EXERCISES.forEach((ex, idx) => {
    check(`Abschnitt ${idx + 1}: 8 Schreibuebungs-Items`, ex.write.length === 8);
    check(`Abschnitt ${idx + 1}: jedes Schreibuebungs-Item hat before/after/answer/hint`,
      ex.write.every(it => typeof it.before === "string" && typeof it.after === "string" && !!it.answer && !!it.hint));
    const blanks = (ex.cloze.match(/\{[^}]+\}/g) || []);
    check(`Abschnitt ${idx + 1}: Luekentext hat mindestens 5 Luecken`, blanks.length >= 5);
    check(`Abschnitt ${idx + 1}: Luekentext ist Fliesstext ohne rohe Klammer-Reste`, !/[{}]/.test(ex.cloze.replace(/\{[^}]+\}/g, "")));
  });
}

// --- Uebungen: Navigation ueber Kachel und Menue (kein Modal mehr) ---
{
  const { win: winE, doc: docE } = freshDom();
  const GE = winE.__game;
  click(winE, docE.getElementById("exercisesTile"));
  check("'Übungen'-Kachel fuehrt direkt zur Uebungen-Uebersicht (kein Modal)", GE.currentView() === "exercises" && !GE.isModalOpen());
  const exCards = Array.from(docE.querySelectorAll("#exerciseList .sec-card"));
  check("Uebungen-Uebersicht zeigt 10 Karten", exCards.length === 10);

  click(winE, exCards[0]);
  check("Klick auf Abschnitts-Karte oeffnet die Uebungs-Ansicht", GE.currentView() === "exerciseplay");
  check("Hoerübung-Tab ist zu Beginn aktiv", docE.querySelector('[data-exmode="listen"]').classList.contains("active"));
  check("Hoerübung-Panel ist sichtbar", docE.querySelector('[data-mode-panel="listen"]').classList.contains("active"));

  click(winE, docE.querySelector('[data-exmode="write"]'));
  check("Klick auf Schreibuebung-Tab aktiviert dessen Panel", docE.querySelector('[data-mode-panel="write"]').classList.contains("active"));
  check("Hoerübung-Panel wird dabei deaktiviert", !docE.querySelector('[data-mode-panel="listen"]').classList.contains("active"));

  click(winE, docE.querySelector('[data-exmode="cloze"]'));
  check("Klick auf Luekentext-Tab aktiviert dessen Panel", docE.querySelector('[data-mode-panel="cloze"]').classList.contains("active"));

  click(winE, docE.getElementById("exercisePlayBackBtn"));
  check("Zurueck aus der Uebungs-Ansicht fuehrt zur Uebungen-Uebersicht", GE.currentView() === "exercises");
  click(winE, docE.getElementById("exercisesBackBtn"));
  check("Zurueck aus der Uebungen-Uebersicht fuehrt zum Startbildschirm", GE.currentView() === "start");
}

// --- Schreibuebung: 2x falsch schaltet auf Multiple-Choice um ---
{
  const { win: winW, doc: docW } = freshDom();
  const GW = winW.__game;
  GW.openExercise(0);
  click(winW, docW.querySelector('[data-exmode="write"]'));
  const panel = docW.getElementById("exWritePanel");
  const item = GW.SECTION_EXERCISES[0].write[0];
  const input = panel.querySelector(".answer-input");
  const checkBtn = panel.querySelector(".check-btn");

  input.value = "totally wrong";
  click(winW, checkBtn);
  check("1. falsche Eingabe: Eingabefeld bleibt aktiv", !panel.querySelector(".mc-grid").children.length);
  input.value = "still wrong";
  click(winW, checkBtn);
  check("2. falsche Eingabe: Multiple-Choice erscheint", panel.querySelector(".mc-grid").children.length === 4);
  check("Multiple-Choice enthaelt die richtige Antwort", Array.from(panel.querySelectorAll(".mc-btn")).some(b => b.textContent === item.answer));
  const correctBtn = Array.from(panel.querySelectorAll(".mc-btn")).find(b => b.textContent === item.answer);
  click(winW, correctBtn);
  check("Richtige MC-Auswahl wird als geloest markiert", correctBtn.classList.contains("correct"));
  check("Punktestand zaehlt geloeste Aufgabe", panel.querySelector(".ex-score").textContent === "Richtig: 1 / 1");
}

// --- Schreibuebung: sofort richtige Eingabe (Groß-/Kleinschreibung egal) ---
{
  const { win: winW2, doc: docW2 } = freshDom();
  const GW2 = winW2.__game;
  GW2.openExercise(0);
  const panel = docW2.getElementById("exWritePanel");
  const item = GW2.SECTION_EXERCISES[0].write[0];
  panel.querySelector(".answer-input").value = item.answer.toUpperCase();
  click(winW2, panel.querySelector(".check-btn"));
  check("Richtige Eingabe (andere Groß-/Kleinschreibung) wird akzeptiert", panel.querySelector(".ex-score").textContent === "Richtig: 1 / 1");
  check("Eingabefeld wird nach richtiger Antwort gesperrt", panel.querySelector(".answer-input").disabled);
}

// --- Luekentext: Pruefen faerbt Felder gruen/rot, leere Felder bleiben neutral ---
{
  const { win: winC, doc: docC } = freshDom();
  const GC = winC.__game;
  GC.openExercise(0);
  click(winC, docC.querySelector('[data-exmode="cloze"]'));
  const clozePanel = docC.getElementById("exClozePanel");
  const blanks = Array.from(clozePanel.querySelectorAll(".blank-input"));
  check("Luekentext zeigt Eingabefelder fuer jede Luecke", blanks.length >= 5);
  blanks[0].value = blanks[0].dataset.answer.toUpperCase();
  blanks[1].value = "definitiv falsch";
  // blanks[2] bleibt leer
  click(winC, clozePanel.querySelector(".check-btn"));
  check("Richtig ausgefuellte Luecke wird gruen markiert", blanks[0].classList.contains("correct"));
  check("Falsch ausgefuellte Luecke wird rot markiert", blanks[1].classList.contains("wrong"));
  check("Leere Luecke bleibt neutral (weder gruen noch rot)", !blanks[2].classList.contains("correct") && !blanks[2].classList.contains("wrong"));
  check("Ergebnis-Anzeige zaehlt richtige Luecken", clozePanel.querySelector(".cloze-result").textContent === "1 von " + blanks.length + " richtig");

  click(winC, clozePanel.querySelector(".next-btn"));
  check("Zuruecksetzen leert alle Felder", blanks.every(b => b.value === "" && !b.classList.contains("correct") && !b.classList.contains("wrong")));
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
