// Findet und laeuft alle projects/*/test.js. Projekte ohne test.js werden uebersprungen.
const fs = require("fs"), path = require("path"), cp = require("child_process");
const projectsDir = path.join(__dirname, "..", "projects");

const dirs = fs.readdirSync(projectsDir)
  .filter(d => fs.existsSync(path.join(projectsDir, d, "test.js")));

if (!dirs.length) { console.log("Keine Tests gefunden."); process.exit(0); }

let failed = 0;
for (const d of dirs) {
  console.log("\n=== " + d + " ===");
  const r = cp.spawnSync("node", [path.join(projectsDir, d, "test.js")], { stdio: "inherit" });
  if (r.status !== 0) failed++;
}
console.log(failed ? ("\n" + failed + " Projekt(e) fehlgeschlagen.") : "\nAlle Tests bestanden.");
process.exit(failed ? 1 : 0);
