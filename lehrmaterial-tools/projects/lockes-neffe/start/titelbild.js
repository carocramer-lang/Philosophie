// Rendert start/titelbild.html zu start/titelbild.jpg (2816 x 1536, doppelte Groesse des Grundbilds).
// Aufruf: node start/titelbild.js
const path = require("path");
let pw;
try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }
(async () => {
  const b = await pw.chromium.launch();
  const p = await b.newPage({ viewport: { width: 2816, height: 1536 } });
  await p.goto("file://" + path.join(__dirname, "titelbild.html"));
  await p.waitForFunction(() => window.FERTIG || window.FEHLER, null, { timeout: 30000 });
  console.log(await p.evaluate(() => JSON.stringify(window.FERTIG || window.FEHLER)));
  await p.locator("#c").screenshot({ path: path.join(__dirname, "titelbild.jpg"), type: "jpeg", quality: 90 });
  await b.close();
})();
