// Druckt material/arbeitsblatt_leibniz.html mit Chromium (Playwright) zur PDF.
const path = require("path");
const pw = (() => { try { return require("playwright"); } catch (e) { return require("/opt/node22/lib/node_modules/playwright"); } })();
(async () => {
  const b = await pw.chromium.launch();
  const p = await b.newPage();
  await p.goto("file://" + path.join(__dirname, "arbeitsblatt_leibniz.html"));
  await p.pdf({ path: path.join(__dirname, "arbeitsblatt_leibniz_tabula_rasa.pdf"), format: "A4", printBackground: true, preferCSSPageSize: true });
  await p.setViewportSize({ width: 650, height: 1000 }); // Druckbreite A4 minus Raender
  await p.screenshot({ path: path.join(process.argv[2] || __dirname, "vorschau_arbeitsblatt.png"), fullPage: true });
  await b.close();
})();
