// Prueft die Oberwelt: Raster vollstaendig, jede Tuer vom Startpunkt aus zu Fuss erreichbar.
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

ok.forEach(n => console.log("  ok  " + n));
fail.forEach(n => console.log("  FAIL " + n));
process.exit(fail.length ? 1 : 0);
