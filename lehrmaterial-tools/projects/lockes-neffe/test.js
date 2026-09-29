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
const saal = JSON.parse(fs.readFileSync(path.join(__dirname, "innen", "lesesaal.json"), "utf8"));
const leibniz = JSON.parse(fs.readFileSync(path.join(__dirname, "netlify", "lib", "leibniz.json"), "utf8"));
const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const code = html.match(/<script>\n([\s\S]*?)<\/script>/)[1];
function el() {
  return {
    style: {}, hidden: false, textContent: "", innerHTML: "",
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    addEventListener() {}, setAttribute() {}, getAttribute() { return null; },
    appendChild() {}, removeChild() {}, focus() {}, click() {}, getContext() { return null; },
    disabled: false, offsetWidth: 0, scrollTop: 0, scrollHeight: 0, value: "", className: "papier",
    lastChild: null, spellcheck: false
  };
}
const els = {}, docListeners = {};
const document = {
  getElementById: id => els[id] || (els[id] = el()),
  createElement: () => el(),
  createTextNode: () => el(),
  body: el(),
  querySelectorAll: () => [],
  addEventListener: (t, f) => { docListeners[t] = f; }
};
const window = {
  WELT: d, INNEN: { observatorium: innen, lesesaal: saal }, LEIBNIZ: leibniz, document, innerWidth: 1200, innerHeight: 800, devicePixelRatio: 1,
  addEventListener() {}, matchMedia: () => ({ matches: false }),
  requestAnimationFrame: () => 0
};
window.window = window;
function Image() {}
vm.runInNewContext(code, { window, document, Image, Math, Object, Array, Uint8ClampedArray, setTimeout: f => { Promise.resolve().then(f); return 0; }, clearTimeout() {}, Promise, String, RegExp, JSON });
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
check("Spiel: Teleskop gesperrt, solange Infografiken fehlen", G.state.dialog === "Das große Teleskop" && !G.state.material && G.state.stufe === 0);
G.schliessen();
G.teleport(19, 21); bisWechsel("down", 2);
check("Spiel: Tuer gesperrt ohne alle Materialien", G.state.szene === "observatorium" && Math.floor((G.state.y - 2) / 16) === 21);
G.teleport(24, 12); G.tick(1 / 60);
check("Spiel: freie Flaeche bietet keine Interaktion", G.state.aktion === null);

async function materialAblauf() {
  const stellen = { regal_links: [3, 19], regal_rechts: [9, 19], kartentisch: [36, 8] };
  let erste = true;
  for (const [id, [x, y]] of Object.entries(stellen)) {
    G.teleport(x, y); G.tick(1 / 60);
    check("Material: " + id + " bietet Interaktion", G.state.aktion === id);
    G.benutzen();
    check("Material: " + id + " oeffnet das Materialfenster", G.state.material === id && G.state.gesehen[id] === true);
    if (erste) {
      G.materialSchliessen();
      check("Material: nur angesehen reicht nicht", !G.state.geladen[id]);
      G.benutzen();
      erste = false;
    }
    const ok = await G.herunterladen();
    check("Material: " + id + " heruntergeladen", ok === true && G.state.geladen[id] === true);
    G.materialSchliessen();
  }
  G.teleport(19, 8); G.tick(1 / 60);
  G.benutzen();
  check("Material: Teleskop zeigt nach den Infografiken Lockes Text", G.state.material === "teleskop");
  G.teleport(19, 21);
  await G.herunterladen();
  G.materialSchliessen();
  check("Material: alles gesichert schliesst Etappe 1 ab", G.state.stufe === 1 && G.state.dialog === "Alle Materialien gesichert");
  G.schliessen();
  G.teleport(19, 8); G.tick(1 / 60); G.benutzen(); G.materialSchliessen();
  check("Material: kein doppeltes Zaehlen", G.state.stufe === 1);
  G.teleport(19, 21); bisWechsel("down", 2);
  check("Spiel: Rueckweg fuehrt zurueck vor die Tuer", G.state.szene === "welt" && Math.floor(G.state.y / 16) === 17);
  lauf("left", 1);
  check("Spiel: draussen weiter begehbar", G.state.szene === "welt" && !G.state.dialog);
  await lesesaalAblauf();
}

// ---------- Lesesaal: Text holen, Rolle schreiben, Bibliothekar
const GUT = "In der Vorrede zu seinen Neuen Abhandlungen über den menschlichen Verstand von 1704 kritisiert Gottfried Wilhelm Leibniz " +
  "Lockes empiristische Erkenntnistheorie. Leibniz stellt zunächst die Streitfrage dar: Locke hält die Seele für eine leere Tafel, eine tabula rasa. " +
  "Leibniz vertritt dagegen die Auffassung, dass die Seele ursprünglich Prinzipien von Begriffen enthält, die durch äußere Gegenstände nur geweckt werden. " +
  "Anschließend kritisiert er die Induktion: Die Sinne liefern nur Einzelfälle. Aus vielen Fällen folgt keine allgemeine Notwendigkeit. " +
  "Notwendige Wahrheiten wie in der Mathematik haben daher Prinzipien, die nicht von den Sinnen abhängen, auch wenn die Sinne den Anstoß geben, nach ihnen zu suchen. " +
  "Zur Veranschaulichung vergleicht Leibniz die Seele mit einem Marmorblock, dessen Adern die Gestalt des Herkules bereits vorgeben. " +
  "Anders als eine leere Tafel ist der Stein im Voraus bestimmt. Die Figur muss aber noch durch Arbeit freigelegt und poliert werden.";
async function lesesaalAblauf() {
  G.teleport(14, 17); bisWechsel("up", 2);
  check("Lesesaal: Tuer fuehrt nach Etappe 1 hinein", G.state.szene === "lesesaal" && !G.state.dialog);
  check("Lesesaal: Eintritt auf der Eintrittsstelle", saal.raster[Math.floor((G.state.y - 2) / 16)][Math.floor(G.state.x / 16)] === "S");
  lauf("up", 3.5);
  check("Lesesaal: Hauptweg fuehrt gerade zum Schreibpult", G.state.aktion === "schreibpult");
  G.benutzen();
  check("Lesesaal: Schreibpult gesperrt ohne Text", G.state.dialog === "Das Schreibpult" && !G.state.fenster);
  G.schliessen();
  G.teleport(19, 21); bisWechsel("down", 2);
  check("Lesesaal: Tuer gesperrt ohne Aufgabe", G.state.szene === "lesesaal");

  G.teleport(29, 19); G.tick(1 / 60);
  check("Lesesaal: Lesepult bietet Interaktion", G.state.aktion === "lesepult");
  G.benutzen();
  check("Lesesaal: Lesepult oeffnet das Leibniz-Arbeitsblatt", G.state.material === "lesepult");
  await G.herunterladen(); G.materialSchliessen();
  check("Lesesaal: Text gesichert", G.state.gesehen.lesepult && G.state.geladen.lesepult);

  G.teleport(19, 7); G.tick(1 / 60); G.benutzen();
  check("Lesesaal: Schreibpult oeffnet die Papierrolle", G.state.fenster === "rolle");
  document.getElementById("rolleText").value = "Locke sagt viel.";
  G.state.rolle = "Locke sagt viel.";
  check("Lesesaal: zu kurze Rolle wird nicht angenommen", (await G.abgeben()) === false && G.state.fenster === "rolle");
  G.state.rolle = GUT;
  const ok = await G.abgeben();
  check("Lesesaal: Abgabe ruft den Bibliothekar", ok === true && G.state.fenster === "gespraech" && G.state.bibSeit != null);
  const erste = G.state.verlauf[G.state.verlauf.length - 1];
  check("Lesesaal: Rueckmeldung vom Bibliothekar", erste.wer === "bib" && /gelingt dir/.test(erste.text));
  check("Lesesaal: Rueckmeldung lobt konkret", /Gegenposition|Induktion|Marmorblock/.test(erste.text));
  check("Lesesaal: gute Rolle erfasst den Kern", /Kern der Sache erfasst/.test(erste.text));
  G.state.fenster = "gespraech";
  const vorTuer = G.state.stufe;
  await G.antworten("Was bedeutet Induktion?");
  check("Lesesaal: Bibliothekar erklaert Begriffe", /Einzelfällen auf eine allgemeine Regel/.test(G.state.verlauf[G.state.verlauf.length - 1].text));
  G.gespraechBeenden();
  check("Lesesaal: Gespraech beenden siegelt die Rolle", G.state.lesesaalFertig && G.state.stufe === 2 && vorTuer === 1);
  G.schliessen();
  G.teleport(19, 21); bisWechsel("down", 2);
  check("Lesesaal: danach ist die Tuer offen", G.state.szene === "welt" && Math.floor(G.state.y / 16) === 17);

  // Rueckmeldungen der eingebauten Fassung
  const u1 = G.urteil(GUT);
  check("Bibliothekar: gute Rolle erfuellt alle Einzelaspekte", u1.fehlt.length === 0 && u1.kernErfasst);
  const knapp = G.urteil("Leibniz meint in den Neuen Abhandlungen (1704), dass es angeborene Ideen gibt. Er vergleicht die Seele mit einem Marmorblock. Das Wissen aus Einzelfällen ist nicht notwendig.");
  check("Bibliothekar: Kern genuegt, Einzelheiten nicht zwingend", knapp.kernErfasst && knapp.fehlt.length > 0);
  const u2 = G.urteil("Leibniz war der Meinung, dass die Seele angeborene Ideen hat. Ich finde das überzeugend. Er hatte recht, denn Locke irrt.");
  check("Bibliothekar: fehlende Kernbereiche erkannt", u2.kernFehlt.map(k => k.bereich).join() === "2,3");
  check("Bibliothekar: Wertung erkannt", u2.form.some(f => /wertest/.test(f)));
  check("Bibliothekar: Praeteritum erkannt", u2.form.some(f => /Präsens/.test(f)));
  const u3 = G.urteil("Leibniz schreibt: die angeborenen Begriffe bilden die Seele wie die Adern den Marmorblock bilden.");
  check("Bibliothekar: woertliche Uebernahme erkannt", !!u3.zitat);
  const hinweis = G.urteil("x").kernFehlt.map(k => k.hilfe).join(" ");
  check("Bibliothekar: Zeilenangaben aus dem Arbeitsblatt", /Z\. \d/.test(hinweis) && !/\(\)/.test(hinweis));
}

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
for (const stelle of innen.interaktionen) {
  const f = stelle.flaeche;
  check("Innen: Flaeche " + stelle.id + " erreichbar", seenI.has(f.x0 + "," + f.y0));
  let allesI = true;
  for (let y = f.y0; y <= f.y1; y++) for (let x = f.x0; x <= f.x1; x++) if (ia(x, y) !== "I") allesI = false;
  check("Innen: Flaeche " + stelle.id + " markiert", allesI);
}
check("Innen: Ausgang erreichbar", innen.ausgang.every(a => seenI.has(a.x + "," + a.y)));
let offen = 0; for (let y = 0; y < innen.hoehe; y++) for (let x = 0; x < innen.breite; x++) if (ia(x, y) !== "X" && !seenI.has(x + "," + y)) offen++;
check("Innen: keine abgeschnittenen Bodenflaechen", offen === 0);

// Lesesaal-Raster: alles vom Eintritt aus erreichbar
{
  const a = (x, y) => saal.raster[y][x];
  const seen = new Set([saal.eintritt.x + "," + saal.eintritt.y]), q = [[saal.eintritt.x, saal.eintritt.y]];
  while (q.length) {
    const [x, y] = q.shift();
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nx = x + dx, ny = y + dy, k = nx + "," + ny;
      if (ny >= 0 && ny < saal.hoehe && nx >= 0 && nx < saal.breite && a(nx, ny) !== "X" && !seen.has(k)) { seen.add(k); q.push([nx, ny]); }
    }
  }
  check("Lesesaal-Raster: vollstaendig", saal.raster.length === saal.hoehe && saal.raster.every(r => r.length === saal.breite));
  for (const s of saal.interaktionen) check("Lesesaal-Raster: " + s.id + " erreichbar", seen.has(s.flaeche.x0 + "," + s.flaeche.y0));
  check("Lesesaal-Raster: Ausgang erreichbar", saal.ausgang.every(o => seen.has(o.x + "," + o.y)));
  let rest = 0; for (let y = 0; y < saal.hoehe; y++) for (let x = 0; x < saal.breite; x++) if (a(x, y) !== "X" && !seen.has(x + "," + y)) rest++;
  check("Lesesaal-Raster: keine abgeschnittenen Bodenflaechen", rest === 0);
}

// Materialdateien vorhanden
const src = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
for (const m of src.matchAll(/datei: "(material\/[^"]+)"/g)) {
  check("Datei vorhanden: " + m[1], fs.existsSync(path.join(__dirname, m[1])));
}

// ---------- Musterloesung in der eingebauten Fassung und Serverkern (Netlify Function)
async function musterUndKern() {
  const ende = () => G.state.verlauf[G.state.verlauf.length - 1].text;
  G.state.fenster = "gespraech";
  await G.antworten("Kann ich eine Musterlösung sehen?");
  check("Muster: erst Warnung und Rueckfrage", /lernt weniger/.test(ende()) && /Möchtest du sie trotzdem sehen/.test(ende()) && G.state.musterAngebot);
  await G.antworten("Nein, ich versuche es selbst.");
  check("Muster: Ablehnung zeigt keine Loesung", !/erwartet deine Lehrkraft/.test(ende()) && !G.state.musterGezeigt);
  await G.antworten("Doch, zeig mir bitte die Musterlösung");
  await G.antworten("Ja");
  check("Muster: nach Zustimmung wird sie gezeigt", /erwartet deine Lehrkraft/.test(ende()) && G.state.musterGezeigt);
  check("Muster: erfasst alle Kernbereiche", G.urteil(ende()).kernErfasst);
  G.gespraechBeenden();

  const kern = await import(path.join(__dirname, "netlify", "lib", "bibliothekar-kern.mjs"));
  check("Kern: Musterloesung identisch mit dem Spiel", ende().includes(kern.MUSTERLOESUNG));
  check("Kern: Leibniz-Text mit Zeilennummern", /\[Z\. 28\] Klarheit zu bringen/.test(kern.QUELLTEXT) && kern.SYSTEM.includes("Marmorblock"));
  check("Kern: Systemtext enthaelt Regeln zur Musterloesung", /Musterlösung \(streng einhalten\)/.test(kern.SYSTEM) && kern.SYSTEM.includes(kern.MUSTERLOESUNG));
  const v = [{ wer: "jonny", text: "Ich habe meine Zusammenfassung geschrieben." }, { wer: "bib", text: "Lass sehen." },
             { wer: "jonny", text: "Was ist Reflexion?" }, { wer: "jonny", text: "Und Sensation?" }];
  const msgs = kern.nachrichten(kern.pruefe({ zusammenfassung: "Locke …", verlauf: v, art: "antwort" }));
  check("Kern: Rollen wechseln streng ab", msgs.every((m, i) => i === 0 || m.role !== msgs[i - 1].role) && msgs[0].role === "user" && msgs[msgs.length - 1].role === "user");
  const u = kern.nachrichten(kern.pruefe({ zusammenfassung: "MEINE ROLLE", verlauf: v.slice(0, 1), art: "urteil" }));
  check("Kern: Urteil haengt die Zusammenfassung an", u.length === 1 && u[0].content.includes("<zusammenfassung>\nMEINE ROLLE"));
  const wirft = f => { try { f(); return false; } catch (e) { return e.status === 400; } };
  check("Kern: zu lange Rolle abgewiesen", wirft(() => kern.pruefe({ zusammenfassung: "x".repeat(5000), verlauf: v })));
  check("Kern: letzte Nachricht muss von Jonny sein", wirft(() => kern.pruefe({ zusammenfassung: "x", verlauf: v.slice(0, 2) })));
  check("Kern: falsche Rolle abgewiesen", wirft(() => kern.pruefe({ zusammenfassung: "x", verlauf: [{ wer: "system", text: "x" }] })));
  check("Kern: Ablehnung ergibt keinen Text", kern.antworttext({ stop_reason: "refusal", content: [] }) === null);
  check("Kern: Text wird ausgelesen", kern.antworttext({ stop_reason: "end_turn", content: [{ type: "thinking", thinking: "" }, { type: "text", text: "Hallo" }] }) === "Hallo");
}

materialAblauf().then(musterUndKern).catch(e => fail.push("Ablauf: " + e.message)).then(() => {
  ok.forEach(n => console.log("  ok  " + n));
  fail.forEach(n => console.log("  FAIL " + n));
  process.exit(fail.length ? 1 : 0);
});
