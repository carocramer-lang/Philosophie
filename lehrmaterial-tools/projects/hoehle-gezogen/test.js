// Funktionstest der Hoehle: kompletter Durchlauf durch alle fuenf Szenen via jsdom.
const fs = require("fs"), path = require("path");
const { JSDOM } = require("jsdom");
const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "https://localhost/" });
const win = dom.window, doc = win.document;
const q = s => doc.querySelector(s), qa = s => Array.from(doc.querySelectorAll(s));
const click = e => e.dispatchEvent(new win.MouseEvent("click", { bubbles: true }));
function proto() {
  const ta = q("#protoText");
  ta.value = "Testeintrag mit ausreichend vielen Zeichen zur Reflexion.";
  ta.dispatchEvent(new win.Event("input"));
  if (q("#protoSave").disabled) throw new Error("protoSave bleibt disabled trotz 20+ Zeichen");
  click(q("#protoSave"));
}
let ok = [], fail = [];
const check = (n, c) => (c ? ok : fail).push(n);

const G = win.__game; check("Test-Hook vorhanden", !!G);
click(q("#startBtn"));
check("Szene 1 aktiv", G.state.scene === "s1");
check("6 Glutpunkte", qa("#artHost .glut").length === 6);

let los = 0;
function step() {
  if (q("#auswertung").style.display !== "none") return "done";
  if (q("#protoModal").classList.contains("on")) { proto(); return true; }
  const b = qa("#controls .btn"); const by = re => b.find(x => re.test(x.textContent)); let t;
  if (t = by(/Weiterklicken/)) { click(t); return true; }
  if (t = by(/Schulter/))      { click(t); return true; }
  if (t = by(/Gezogen/))       { click(t); return true; }
  if (t = by(/Sonne/))         { click(t); return true; }
  if ((t = by(/losreißen/)) && los < 2) { los++; click(t); return true; }
  if (t = by(/nachgeben/))     { click(t); return true; }
  if (t = by(/greifen/))       { click(t); return true; }
  if (t = by(/überzeugen/))    { click(t); return true; }
  if (G.state.scene === "s1" && G.state.discCount < 4) {
    const g = qa("#artHost .glut:not(.found)")[0]; if (g) { click(g); return true; }
  }
  if (b.length) { click(b[0]); return true; }
  return "stuck";
}
let res, guard = 0;
while ((res = step()) === true) { if (++guard > 300) { res = "loop"; break; } }

check("Auswertung erreicht", res === "done");
check("Zwang getestet (2x losgerissen)", los === 2);
check("5 Protokolleintraege", G.state.protocol.length === 5);
const keys = new Set(G.state.protocol.map(e => e.key));
check("alle 5 Stationen", ["schein","umwendung","aufstieg","erkenntnis","rueckkehr"].every(k => keys.has(k)));
const ex = G.buildExport();
check("Export Kopf", /GEDANKENPROTOKOLL/.test(ex));
check("Export Schreibaufgabe", /SCHREIBAUFGABE/.test(ex));
check("Export alle Stationen", ["Schein","Umwendung","Aufstieg","Erkenntnis","Rückkehr"].every(s => ex.includes(s)));
check("5 Stationskoepfe in Auswertung", qa("#stations .stationhead").length === 5);
check("Speicherstand vorhanden", !!win.localStorage.getItem("hoehle_gezogen_v1"));

console.log("  " + ok.length + "/" + (ok.length + fail.length) + " Checks bestanden");
if (fail.length) { fail.forEach(n => console.log("  XX " + n)); process.exit(1); }
