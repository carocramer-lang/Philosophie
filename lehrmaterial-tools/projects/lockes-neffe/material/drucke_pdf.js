// Druckt die Leibniz-Arbeitsblaetter mit Chromium (Playwright) zur PDF.
// Aufruf: node material/drucke_pdf.js [Ordner fuer Vorschaubilder] [lesesaal|analyse|kommentar]
// Ohne zweites Argument werden alle Blaetter gedruckt.
const path = require("path");
const pw = (() => { try { return require("playwright"); } catch (e) { return require("/opt/node22/lib/node_modules/playwright"); } })();
const BLAETTER = {
  lesesaal: ["arbeitsblatt_leibniz.html", "arbeitsblatt_leibniz_tabula_rasa.pdf", "vorschau_arbeitsblatt.png"],
  analyse: ["arbeitsblatt_leibniz_analyse.html", "arbeitsblatt_leibniz_analyse.pdf", "vorschau_arbeitsblatt_analyse.png"],
  kommentar: ["arbeitsblatt_leibniz_kommentar.html", "arbeitsblatt_leibniz_kommentar.pdf", "vorschau_arbeitsblatt_kommentar.png"]
};
(async () => {
  const b = await pw.chromium.launch();
  const nur = process.argv[3];
  for (const [name, [html, pdf, bild]] of Object.entries(BLAETTER)) {
    if (nur && nur !== name) continue;
    const p = await b.newPage();
    await p.goto("file://" + path.join(__dirname, html));
    await p.pdf({ path: path.join(__dirname, pdf), format: "A4", printBackground: true, preferCSSPageSize: true });
    await p.setViewportSize({ width: 650, height: 1000 }); // Druckbreite A4 minus Raender
    await p.screenshot({ path: path.join(process.argv[2] || __dirname, bild), fullPage: true });
    await p.close();
  }
  await b.close();
})();
