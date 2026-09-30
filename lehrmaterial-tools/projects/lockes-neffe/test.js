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
const salon = JSON.parse(fs.readFileSync(path.join(__dirname, "innen", "salon.json"), "utf8"));
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
  WELT: d, INNEN: { observatorium: innen, lesesaal: saal, salon }, LEIBNIZ: leibniz, document, innerWidth: 1200, innerHeight: 800, devicePixelRatio: 1,
  addEventListener() {}, matchMedia: () => ({ matches: false }),
  requestAnimationFrame: () => 0, setTimeout: () => 0
};
window.window = window;
function Image() {}
vm.runInNewContext(code, { window, document, Image, Math, Object, Array, Uint8ClampedArray, setTimeout: f => { Promise.resolve().then(f); return 0; }, clearTimeout() {}, Promise, String, RegExp, JSON });
const G = window.__game;
check("Spiel: Test-Hook vorhanden", !!G);

// Startbildschirm: sicherer Bereich und Knoepfe in allen Querformaten sichtbar und gross genug
const taste = code => docListeners.keydown({ code, preventDefault() {}, target: null });
check("Start: Spiel beginnt mit dem Startbildschirm", G.state.start === true);
taste("ArrowLeft");
check("Start: Pfeiltasten bewegen Jonny noch nicht", !G.keys.left);
const formate = { "Smartphone 844x390": [844, 390], "Smartphone 740x360": [740, 360], "Smartphone mit Browserleiste 844x340": [844, 340],
  "Tablet 1024x768": [1024, 768], "Tablet 1180x820": [1180, 820], "Desktop 1920x1080": [1920, 1080], "Desktop 1280x800": [1280, 800], "Breitbild 2560x1080": [2560, 1080] };
for (const [name, [W, H]] of Object.entries(formate)) {
  const l = G.startLage(W, H), s = l.sicher, eps = 0.5;
  const drin = b => b.x >= -eps && b.y >= -eps && b.x + b.w <= W + eps && b.y + b.h <= H + eps;
  check("Start " + name + ": sicherer Bereich ganz sichtbar", drin(s) && drin(l.knopf) && drin(l.info));
  check("Start " + name + ": Knoepfe tippbar (mind. 44 px)", l.knopf.h >= 44 && l.info.w >= 44 && l.info.h >= 44);
  check("Start " + name + ": Knoepfe getrennt", l.info.x > l.knopf.x + l.knopf.w + 40);
}
taste("KeyI");
check("Start: I oeffnet die Informationen", G.state.info === true);
taste("Enter");
check("Start: bei offener Info startet Enter das Spiel nicht", G.state.start === true);
taste("Escape");
check("Start: Escape schliesst die Informationen", G.state.info === false && G.state.start === true);
taste("Enter");
check("Start: Enter startet das Spiel", G.state.start === false);
check("Start: Titelbild vorhanden", fs.existsSync(path.join(__dirname, "start", "titelbild.jpg")) && /src="start\/titelbild\.jpg"/.test(html));
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
  await salonAblauf();

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

// ---------- Salon: Brief der Akademie, Analyse schreiben, Platon am Kamin
const ANALYSE = "In der Vorrede zu seinen Neuen Abhandlungen über den menschlichen Verstand (1704) begründet Gottfried Wilhelm Leibniz seine These angeborener Prinzipien gegen Lockes Empirismus. " +
  "Er eröffnet den Text mit einer disjunktiven Gegenüberstellung zweier Positionen (Z. 1–5): Entweder ist die Seele eine leere Tafel, wie Locke und Aristoteles meinen, oder sie enthält ursprünglich Prinzipien, die durch äußere Gegenstände nur aufgeweckt werden. " +
  "Leibniz vertritt die zweite Position und beruft sich dabei auf Platon. Im zweiten Abschnitt (Z. 6–13) kritisiert er die Induktion. " +
  "Die erste Prämisse lautet, dass die Sinne nur Beispiele, also Wahrheiten über Einzelnes liefern (Z. 9–10). " +
  "Die zweite Prämisse besagt, dass aus noch so vielen Einzelfällen keine allgemeine Notwendigkeit folgt, denn was oft geschehen ist, muss nicht immer so geschehen (Z. 11–13). " +
  "Daraus folgert Leibniz im Zwischenschluss, dass notwendige Wahrheiten Prinzipien besitzen müssen, die nicht vom Zeugnis der Sinne abhängen (Z. 14–17). " +
  "Als Beleg dient die reine Mathematik, deren Lehrsätze universell und notwendig gelten (Z. 18–20). Die Sinne geben nur den Anstoß, nach diesen Wahrheiten zu suchen. " +
  "Im letzten Abschnitt (Z. 21–28) veranschaulicht Leibniz seine These durch das Gleichnis vom geäderten Marmorblock. " +
  "Die leere Tafel und die ungestaltete Masse stehen für das empiristische Modell eines passiven Geistes. " +
  "Die Adern symbolisieren dagegen die angeborene Struktur der Seele, die bestimmte Erkenntnisse vorzeichnet. " +
  "Die Arbeit des Bildhauers steht für die Sinneserfahrung, die nichts Neues erschafft, sondern die Adern freilegt und zur Klarheit bringt. " +
  "Das gedankliche Ziel des Gleichnisses ist es zu zeigen, dass Erfahrung und angeborene Ideen keine Gegensätze sind: Die Sinne sind der Anlass, aber nicht das Fundament notwendiger Erkenntnis.";
async function salonAblauf() {
  G.teleport(13, 43); bisWechsel("up", 2);
  check("Salon: Tuer fuehrt nach dem Lesesaal hinein", G.state.szene === "salon" && !G.state.dialog);
  check("Salon: Eintritt auf der Eintrittsstelle", salon.raster[Math.floor((G.state.y - 2) / 16)][Math.floor(G.state.x / 16)] === "S");
  G.teleport(19, 21); bisWechsel("down", 2);
  check("Salon: Tuer gesperrt ohne Analyse", G.state.szene === "salon");
  G.teleport(19, 20); lauf("up", 3.5);
  check("Salon: Hauptweg fuehrt gerade zum Kamin", G.state.aktion === "kamin");
  G.benutzen();
  check("Salon: Kamin verweist zuerst auf den Sekretaer", G.state.dialog === "Der Kamin" && !G.state.fenster);
  G.schliessen();

  G.teleport(4, 6); G.tick(1 / 60);
  check("Salon: Sekretaer bietet Interaktion", G.state.aktion === "sekretaer");
  G.benutzen();
  check("Salon: Sekretaer oeffnet den Brief der Akademie", G.state.material === "sekretaer");
  check("Salon: Brief zeigt Analyseauftrag und Hinweise", /Analysieren Sie die Argumentationsstruktur/.test(document.getElementById("materialInhalt").innerHTML) &&
    /Zeilenangaben/.test(document.getElementById("materialInhalt").innerHTML));
  await G.herunterladen(); G.materialSchliessen();
  check("Salon: Brief gesichert", G.state.gesehen.sekretaer && G.state.geladen.sekretaer);
  G.benutzen();
  check("Salon: Sekretaer oeffnet die Rolle fuer die Analyse", G.state.fenster === "rolle" && document.getElementById("rolleTitel").textContent === "Deine Analyse");
  check("Salon: Rolle zeigt den Analyseauftrag", /Analysieren Sie/.test(document.getElementById("rolleAuftrag").textContent));
  G.state.salon.rolle = "Leibniz argumentiert gegen Locke.";
  check("Salon: zu kurze Analyse wird nicht angenommen", (await G.abgeben()) === false && G.state.fenster === "rolle");
  G.state.salon.rolle = ANALYSE;
  await G.abgeben();
  check("Salon: Abgabe ruft Platon aus dem Bild", G.state.dialog === "Das Feuer lodert auf" && G.state.salon.seit != null && !G.state.fenster);
  check("Salon: Lesesaal-Rolle bleibt unberuehrt", G.state.rolle === GUT);
  G.schliessen();
  G.teleport(19, 21); bisWechsel("down", 2);
  check("Salon: Tuer gesperrt, solange Platon wartet", G.state.szene === "salon");

  G.teleport(19, 6); G.tick(1 / 60);
  check("Salon: Kamin bietet Interaktion", G.state.aktion === "kamin");
  await G.platonGespraech();
  const v = G.state.salon.verlauf;
  check("Platon: stellt sich vor", v[0].wer === "bib" && /Ich bin Platon/.test(v[0].text));
  check("Platon: erklaert den Bezug zu Leibniz mit Zeile", /Z\. 5/.test(v[0].text) && /mit Platon/.test(v[0].text) && /Anamnesis/.test(v[0].text));
  const rm = v[v.length - 1].text;
  check("Platon: gibt Rueckmeldung zur Analyse", v[v.length - 1].wer === "bib" && /Das ist dir gelungen/.test(rm));
  check("Platon: gute Analyse erfasst den Kern", /Kern der Sache erfasst/.test(rm));
  await G.antworten("Was ist eine Prämisse?");
  check("Platon: erklaert Begriffe", /Voraussetzung, aus der ein Schluss folgt/.test(v[v.length - 1].text));
  await G.antworten("Kann ich die Musterlösung sehen?");
  check("Platon: Musterloesung nur nach Angebot mit Hinweis", /Wer nur liest, lernt weniger/.test(v[v.length - 1].text) && !/Prämisse 1/.test(v[v.length - 1].text));
  await G.antworten("Ja, bitte");
  check("Platon: Musterloesung nach Zustimmung", /Prämisse 1/.test(v[v.length - 1].text) && /Schreib bitte nicht ab/.test(v[v.length - 1].text));
  G.gespraechBeenden();
  check("Platon: Gespraech beenden siegelt die Analyse", G.state.salon.fertig && G.state.stufe === 3 && G.state.dialog === "Deine Analyse ist gesiegelt");
  G.schliessen();
  G.teleport(19, 21); bisWechsel("down", 2);
  check("Salon: danach ist die Tuer offen", G.state.szene === "welt");

  // Rueckmeldungen der eingebauten Fassung
  const p1 = G.urteilPlaton(ANALYSE);
  check("Platon: gute Analyse ohne Formhinweise", p1.kernErfasst && p1.form.length === 0);
  const p2 = G.urteilPlaton("Leibniz sagt, dass die Seele angeborene Ideen hat. Die Sinne geben nur Beispiele. Der Marmorblock hat Adern.");
  check("Platon: Darstellung statt Analyse erkannt", p2.form.some(f => /eher wie eine Darstellung/.test(f)));
  check("Platon: fehlende Zeilenangaben erkannt", p2.form.some(f => /Zeilenangaben/.test(f)));
  check("Platon: fehlende Deutung des Gleichnisses erkannt", !p2.bereiche[3] && p2.kernFehlt.some(k => k.id === "adern"));
  const hinweisP = G.urteilPlaton("x").kernFehlt.map(k => k.hilfe).join(" ");
  check("Platon: Zeilenangaben aus dem Arbeitsblatt", /Z\. \d/.test(hinweisP) && !/\(\)/.test(hinweisP));
}

// Salon-Raster: alles vom Eintritt aus erreichbar
{
  const a = (x, y) => salon.raster[y][x];
  const seen = new Set([salon.eintritt.x + "," + salon.eintritt.y]), q = [[salon.eintritt.x, salon.eintritt.y]];
  while (q.length) {
    const [x, y] = q.shift();
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nx = x + dx, ny = y + dy, k = nx + "," + ny;
      if (ny >= 0 && ny < salon.hoehe && nx >= 0 && nx < salon.breite && a(nx, ny) !== "X" && !seen.has(k)) { seen.add(k); q.push([nx, ny]); }
    }
  }
  check("Salon-Raster: vollstaendig", salon.raster.length === salon.hoehe && salon.raster.every(r => r.length === salon.breite));
  for (const s of salon.interaktionen) {
    check("Salon-Raster: " + s.id + " erreichbar", seen.has(s.flaeche.x0 + "," + s.flaeche.y0));
    let alleI = true;
    for (let y = s.flaeche.y0; y <= s.flaeche.y1; y++) for (let x = s.flaeche.x0; x <= s.flaeche.x1; x++) if (a(x, y) !== "I") alleI = false;
    check("Salon-Raster: " + s.id + " als Interaktionsflaeche markiert", alleI);
  }
  check("Salon-Raster: Ausgang erreichbar", salon.ausgang.every(o => seen.has(o.x + "," + o.y)));
  let rest = 0; for (let y = 0; y < salon.hoehe; y++) for (let x = 0; x < salon.breite; x++) if (a(x, y) !== "X" && !seen.has(x + "," + y)) rest++;
  check("Salon-Raster: keine abgeschnittenen Bodenflaechen", rest === 0);
  check("Salon-Raster: Geist steht vor dem Kamin", a(Math.floor(salon.geist.x), salon.geist.y) === "X");
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
  G.state.werk = "lesesaal";  // wie im Spiel: das Gespraech im Lesesaal gehoert zum Bibliothekar
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
  check("Kern: zu lange Rolle abgewiesen", wirft(() => kern.pruefe({ zusammenfassung: "x".repeat(kern.GRENZEN.zusammenfassung + 1), verlauf: v })));
  // Platon im Salon
  check("Kern: ohne Angabe antwortet der Bibliothekar", kern.pruefe({ zusammenfassung: "x", verlauf: v.slice(0, 1) }).rolle === "bibliothekar");
  check("Kern: unbekannte Rolle faellt auf den Bibliothekar zurueck", kern.pruefe({ zusammenfassung: "x", verlauf: v.slice(0, 1), rolle: "sokrates" }).rolle === "bibliothekar");
  const pl = kern.nachrichten(kern.pruefe({ zusammenfassung: "MEINE ANALYSE", verlauf: v.slice(0, 1), art: "urteil", rolle: "platon" }));
  check("Kern: Platon bekommt die Analyse", pl[0].content.includes("<analyse>\nMEINE ANALYSE"));
  check("Kern: Platon kennt Aufgabe und Erwartungshorizont", kern.ROLLEN.platon.system.includes("Analysieren Sie die Argumentationsstruktur") &&
    kern.ROLLEN.platon.system.includes(kern.MUSTERLOESUNG_ANALYSE) && kern.MUSTERLOESUNG_ANALYSE.includes("Prämisse 1"));
  check("Kern: Platon erklaert den Bezug zu Leibniz", /wie ich mit Platon annehme/.test(kern.SYSTEM_PLATON) && /Anamnesis/.test(kern.SYSTEM_PLATON));
  check("Kern: Platons Musterloesung identisch mit dem Spiel", G.state.salon.verlauf.some(m => m.text.includes(kern.MUSTERLOESUNG_ANALYSE)));
  check("Kern: Erwartungshorizont ohne Tippfehler", !/[一-鿿]|derive|veranschaulichung, dass/.test(kern.MUSTERLOESUNG_ANALYSE));
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
