// Funktionstest Seven Periods: Pruefung der offenen Formate, Durchlauf Practice und Test Run, Bonus, Lehrkraftansicht.
const fs = require("fs"), path = require("path");
const { JSDOM } = require("jsdom");
const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");

let ok = [], fail = [];
const check = (n, c) => (c ? ok : fail).push(n);

function boot(query) {
  const errors = [];
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "https://localhost/" + (query || ""),
    beforeParse(w) { w.addEventListener("error", e => errors.push(e.message)); w.confirm = () => true; w.prompt = () => ""; w.print = () => {}; w.scrollTo = () => {}; } });
  const win = dom.window, doc = win.document;
  const q = s => doc.querySelector(s), qa = s => Array.from(doc.querySelectorAll(s));
  const click = e => e.dispatchEvent(new win.MouseEvent("click", { bubbles: true }));
  const type = (inp, v) => { inp.value = v; inp.dispatchEvent(new win.Event("input")); };
  return { win, doc, q, qa, click, type, errors, G: win.__game };
}

// Musterantwort ohne "Zach's answer:"; Satzanfang/-ende bleibt drin und wird vom Spiel abgeschnitten.
const modelAnswer = it => it.sol.replace(/^Zach's answer:\s*/, "");

function playRooms(t, correct) {
  const { q, qa, click, G } = t;
  const R = G.CONTENT.rooms;
  for (const r of R) {
    click(q(`.door[data-room="${r.id}"]`));
    click(q("#enterBtn"));
    if (r.writing) {
      if (q("[data-prompt]")) click(q('[data-prompt="A"]'));
      t.type(q("#writeText"), "The best thing about this year was the pep rally. I'm looking forward to seeing the yearbook. " + "word ".repeat(110));
      check("Writing: Submit aktiv", !q("#submitWriting").disabled);
      click(q("#submitWriting")); click(q("#backBtn"));
      continue;
    }
    const items = qa(".task .item");
    r.items.forEach((it, i) => {
      const el = items[i];
      if (!correct) {
        // dreimal falsch bzw. einmal im Test Run, bis gesperrt
        for (let k = 0; k < 3 && !el.querySelector("button").disabled; k++) {
          if (it.kind === "sort") click(el.querySelector(`[data-key="${it.a === "g" ? "i" : "g"}"]`));
          else if (it.kind === "mc") click(el.querySelector(`[data-opt="${(it.a + 1) % it.opts.length}"]`));
          else if (it.kind === "fix") { click(el.querySelectorAll(".chunk")[0]); click(el.querySelector(".row button")); }
          else { el.querySelector("input").value = "123"; click(Array.from(el.querySelectorAll("button")).pop()); }
        }
        return;
      }
      if (it.kind === "sort") click(el.querySelector(`[data-key="${it.a}"]`));
      else if (it.kind === "mc") click(el.querySelector(`[data-opt="${it.a}"]`));
      else if (it.kind === "gap") { el.querySelector("input").value = it.a[0]; click(el.querySelector("button")); }
      else if (it.kind === "fix") { click(el.querySelectorAll(".chunk")[it.err]); el.querySelector("input").value = it.a[0]; click(el.querySelector(".row button")); }
      else { el.querySelector("input").value = modelAnswer(it); click(Array.from(el.querySelectorAll("button")).pop()); }
    });
    check(`${r.id}: alle Items erledigt`, !q("#finishBtn").disabled);
    click(q("#finishBtn")); click(q("#backBtn"));
  }
}

// 1. Pruefung der offenen Formate
{
  const { G } = boot();
  const all = G.CONTENT.rooms.flatMap(r => r.items).filter(it => it.kind === "open");
  check("alle Musterloesungen akzeptiert", all.every(it => G.checkOpen(it, modelAnswer(it))));
  const r1 = G.CONTENT.rooms[0].items, r6 = G.CONTENT.rooms[5].items;
  check("good at draw abgelehnt", !G.checkOpen(r1[4], "draw"));
  check("good at everything abgelehnt", !G.checkOpen(r1[4], "everything"));
  check("good at not giving up akzeptiert", G.checkOpen(r1[4], "not giving up"));
  check("looking forward to see abgelehnt", !G.checkOpen(r1[5], "see my friends"));
  check("I'd like to changing abgelehnt", !G.checkOpen(r1[6], "changing the rules"));
  check("want me do abgelehnt", !G.checkOpen(r1[8], "do my homework"));
  check("Apostroph-Variante akzeptiert", G.checkOpen(r6[4], "We don’t know where to sit"));
  check("tired of lose abgelehnt", !G.checkOpen(r6[7], "We're tired of lose!"));
}

// 2. Practice: alles richtig, Bonus loesen
{
  const t = boot(); const { q, click, G } = t;
  click(q("#practiceBtn"));
  while (q("#nextBtn")) click(q("#nextBtn"));
  check("Intro durchlaufen", G.state.introDone);
  check("Raum 2 anfangs gesperrt", q('.door[data-room="r2"]').disabled);
  playRooms(t, true);
  check("7 Stempel", Object.keys(G.state.stamps).length === 7);
  check("volle Punktzahl 51", G.total() === 51 && G.maxPoints() === 51);
  check("Abschlusscode sichtbar", /^BVP-5151-[A-Z]{2}$/.test(q("#completionCode").textContent));
  check("Bestzeit Gym gespeichert", typeof G.state.best.r6 === "number");
  click(q('.door[data-room="bonus"]')); click(q("#enterBtn"));
  [0, 1, 0, 1].forEach((j, i) => click(q(`[data-puzzle="${i}"][data-opt="${j}"]`)));
  click(q("#unlockBtn"));
  check("Bonus geloest, goldener Stempel", G.state.gold === true);
  check("Speicherstand vorhanden", !!t.win.localStorage.getItem(G.KEY));
  check("keine JS-Fehler (Practice)", !t.errors.length);
}

// 3. Test Run: alles falsch, keine Hilfen
{
  const t = boot(); const { q, click, G } = t;
  click(q("#testBtn"));
  while (q("#nextBtn")) click(q("#nextBtn"));
  click(q('.door[data-room="r1"]')); click(q("#enterBtn"));
  check("Test Run ohne Rule Card", !Array.from(t.doc.querySelectorAll("button")).some(b => /Rule Card/.test(b.textContent)));
  check("Test Run ohne Tardy-Anzeige", !q("#tardy"));
  click(q(".topbar button"));
  playRooms(t, false);
  check("Test Run: 0 Punkte", G.total() === 0);
  check("Abschlusscode Test Run", /^BVT-0051-[A-Z]{2}$/.test(q("#completionCode").textContent));
  check("keine JS-Fehler (Test Run)", !t.errors.length);
}

// 4. Lehrkraftansicht
{
  const t = boot("?teacher=1");
  check("Lehrkraftansicht mit Podcast-Skript", /Podcast-Skript/.test(t.doc.body.textContent) && /Principal Harris/.test(t.doc.body.textContent));
  check("Lehrkraftansicht Bonus-Code", /3714/.test(t.doc.body.textContent));
  check("keine JS-Fehler (Lehrkraft)", !t.errors.length);
}

console.log("  " + ok.length + "/" + (ok.length + fail.length) + " Checks bestanden");
if (fail.length) { fail.forEach(n => console.log("  XX " + n)); process.exit(1); }
