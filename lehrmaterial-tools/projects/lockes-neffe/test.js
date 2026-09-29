// Prueft die Oberwelt (Raster, Erreichbarkeit) und die Spiellogik (Kollision, Tueren, Reihenfolge).
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
  WELT: d, document, innerWidth: 1200, innerHeight: 800, devicePixelRatio: 1,
  addEventListener() {}, matchMedia: () => ({ matches: false }),
  requestAnimationFrame: () => 0
};
window.window = window;
function Image() {}
vm.runInNewContext(code, { window, document, Image, Math, Object, Array, Uint8ClampedArray });
const G = window.__game;
check("Spiel: Test-Hook vorhanden", !!G);
const lauf = (dir, sek) => { G.keys[dir] = true; for (let i = 0; i < sek * 60; i++) G.tick(1 / 60); G.keys[dir] = false; };

const y0 = G.state.y;
lauf("up", 2);
check("Spiel: Brunnen blockiert den Weg nach Norden", G.state.y < y0 && G.state.y > 33 * 16);

G.teleport(14, 18); lauf("up", 1);
check("Spiel: falsche Reihenfolge oeffnet Hinweis", G.state.dialog === "lesesaal" && G.state.stufe === 0);
G.schliessen();
check("Spiel: nach dem Dialog steht Jonny vor der Tuer", !G.state.dialog && Math.floor(G.state.y / 16) === 17);

G.teleport(47, 18); lauf("up", 1);
check("Spiel: Observatorium betreten zaehlt als Schritt 1", G.state.dialog === "observatorium" && G.state.stufe === 1);
lauf("left", 1);
check("Spiel: bei offenem Dialog steht Jonny still", G.state.dialog === "observatorium");
G.schliessen();

G.teleport(12, 17); lauf("up", 2);
check("Spiel: Gebaeudewand blockiert", !G.state.dialog && Math.floor((G.state.y - 1) / 16) >= 16);

ok.forEach(n => console.log("  ok  " + n));
fail.forEach(n => console.log("  FAIL " + n));
process.exit(fail.length ? 1 : 0);
