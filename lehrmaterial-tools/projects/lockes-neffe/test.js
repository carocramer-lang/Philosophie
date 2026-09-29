// Prueft Oberwelt und Innenraeume (Raster, Erreichbarkeit) und die Spiellogik (Kollision, Tueren, Szenenwechsel, Interaktion).
const fs = require("fs"), path = require("path");
const d = JSON.parse(fs.readFileSync(path.join(__dirname, "welt", "welt.json"), "utf8"));
let ok = [], fail = [];
const check = (n, c) => (c ? ok : fail).push(n);

check("Raster hat " + d.hoehe + " Zeilen", d.raster.length === d.hoehe);
check("Alle Zeilen " + d.breite + " breit", d.raster.every(r => r.length === d.breite));
const at = (x, y) => (d.raster[y] || "")[x];
check("Start liegt auf Weg", at(d.start.x, d.start.y) === "#");

// Breitensuche nur ueber Wege, damit die Lernorte auch bei gesperrter Wiese erreichbar bleiben
const seen = new Set([d.start.x + "," + d.start.y]), queue = [[d.start.x, d.start.y]];
while (queue.length) {
  const [x, y] = queue.shift();
  if (at(x, y) === "E") continue;
  for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
    const nx = x + dx, ny = y + dy, k = nx + "," + ny, t = at(nx, ny);
    if ((t === "#" || t === "E") && !seen.has(k)) { seen.add(k); queue.push([nx, ny]); }
  }
}
for (const [name, o] of Object.entries(d.lernorte)) {
  check(name + ": Tuer markiert", o.tuer.every(t => at(t.x, t.y) === "E"));
  check(name + ": Tuer erreichbar", o.tuer.some(t => seen.has(t.x + "," + t.y)));
}

// ---------- Spiel: Inline-Skript aus index.html mit Browser-Attrappen in Node ausfuehren
const vm = require("vm");
const innen = JSON.parse(fs.readFileSync(path.join(__dirname, "innen", "observatorium.json"), "utf8"));
const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const code = html.match(/<script>\n([\s\S]*?)<\/script>/)[1];
function el() {
  return {
    style: {}, hidden: false, textContent: "", innerHTML: "",
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    addEventListener() {}, setAttribute() {}, getAttribute() { return null; },
    appendChild() {}, focus() {}, getContext() { return null; }
  };
}
const els = {}, docListeners = {};
const document = {
  getElementById: id => els[id] || (els[id] = el()),
  createElement: () => el(),
  querySelectorAll: () => [],
  addEventListener: (t, f) => { docListeners[t] = f; }
};
const window = {
  WELT: d, INNEN: { observatorium: innen }, document, innerWidth: 1200, innerHeight: 800, devicePixelRatio: 1,
  addEventListener() {}, matchMedia: () => ({ matches: false }),
  requestAnimationFrame: () => 0
};
window.window = window;
function Image() {}
vm.runInNewContext(code, { window, document, Image, Math, Object, Array, Uint8ClampedArray });
const G = window.__game;
check("Spiel: Test-Hook vorhanden", !!G);
// Laeuft, bis sich die Szene aendert (hoechstens sek Sekunden)
const bisWechsel = (dir, sek) => {
  const vorher = G.state.szene; G.keys[dir] = true;
  for (let i = 0; i < sek * 60 && G.state.szene === vorher; i++) G.tick(1 / 60);
  G.keys[dir] = false;
};
const lauf = (dir, sek) => { G.keys[dir] = true; for (let i = 0; i < sek * 60; i++) G.tick(1 / 60); G.keys[dir] = false; };

const y0 = G.state.y;
lauf("up", 2);
check("Spiel: Brunnen blockiert den Weg nach Norden", G.state.y < y0 && G.state.y > 33 * 16);

G.teleport(14, 18); lauf("up", 1);
check("Spiel: falsche Reihenfolge oeffnet Hinweis", G.state.dialog === "Lesesaal" && G.state.stufe === 0);
G.schliessen();
check("Spiel: nach dem Dialog steht Jonny vor der Tuer", !G.state.dialog && Math.floor(G.state.y / 16) === 17);

G.teleport(12, 17); lauf("up", 2);
check("Spiel: Gebaeudewand blockiert", !G.state.dialog && Math.floor((G.state.y - 1) / 16) >= 16);

G.teleport(47, 18); bisWechsel("up", 2);
check("Spiel: Tuer fuehrt ins Observatorium", G.state.szene === "observatorium" && !G.state.dialog);
check("Spiel: Eintritt auf der Eintrittsstelle", innen.raster[Math.floor((G.state.y - 2) / 16)][Math.floor(G.state.x / 16)] === "S");
G.benutzen();
check("Spiel: E ohne Interaktionsflaeche bewirkt nichts", !G.state.dialog && G.state.stufe === 0);
lauf("up", 3);
check("Spiel: Hauptweg fuehrt gerade zum Teleskop", G.state.aktion === "teleskop");
check("Spiel: Podest blockiert", Math.floor((G.state.y - 1) / 16) >= 8);
G.benutzen();
check("Spiel: Teleskop benutzen zaehlt als Schritt 1", G.state.dialog && G.state.stufe === 1);
G.benutzen(); G.schliessen();
check("Spiel: kein doppeltes Zaehlen", G.state.stufe === 1);
bisWechsel("down", 5);
check("Spiel: Rueckweg fuehrt zurueck vor die Tuer", G.state.szene === "welt" && Math.floor(G.state.y / 16) === 17);
lauf("left", 1);
check("Spiel: draussen weiter begehbar", G.state.szene === "welt" && !G.state.dialog);

// Innenraum-Raster
check("Innen: Raster vollstaendig", innen.raster.length === innen.hoehe && innen.raster.every(r => r.length === innen.breite));
const ia = (x, y) => innen.raster[y][x];
const seenI = new Set([innen.eintritt.x + "," + innen.eintritt.y]), qI = [[innen.eintritt.x, innen.eintritt.y]];
while (qI.length) {
  const [x, y] = qI.shift();
  for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
    const nx = x + dx, ny = y + dy, k = nx + "," + ny;
    if (ny >= 0 && ny < innen.hoehe && nx >= 0 && nx < innen.breite && ia(nx, ny) !== "X" && !seenI.has(k)) { seenI.add(k); qI.push([nx, ny]); }
  }
}
const fl = innen.interaktionen[0].flaeche;
check("Innen: Teleskop-Flaeche erreichbar", seenI.has(fl.x0 + "," + fl.y0));
check("Innen: Ausgang erreichbar", innen.ausgang.every(a => seenI.has(a.x + "," + a.y)));
let offen = 0; for (let y = 0; y < innen.hoehe; y++) for (let x = 0; x < innen.breite; x++) if (ia(x, y) !== "X" && !seenI.has(x + "," + y)) offen++;
check("Innen: keine abgeschnittenen Bodenflaechen", offen === 0);

ok.forEach(n => console.log("  ok  " + n));
fail.forEach(n => console.log("  FAIL " + n));
process.exit(fail.length ? 1 : 0);
