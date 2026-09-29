// Netlify Function: Antwort des Bibliothekars ueber die Claude API.
// Aufruf aus dem Spiel: POST /.netlify/functions/bibliothekar  { zusammenfassung, verlauf, art }
// Umgebungsvariablen in Netlify (Site configuration > Environment variables):
//   ANTHROPIC_API_KEY      Pflicht. Wird nie an den Browser gegeben.
//   BIBLIOTHEKAR_MODELL    Optional, Standard claude-opus-5-5.
//   ERLAUBTE_URSPRUENGE    Optional, z. B. "https://lockes-neffe.netlify.app". Andere Seiten werden abgewiesen.

import Anthropic from "@anthropic-ai/sdk";
import { SYSTEM, pruefe, nachrichten, antworttext } from "../lib/bibliothekar-kern.mjs";

const client = new Anthropic();
const MODELL = process.env.BIBLIOTHEKAR_MODELL || "claude-opus-5-5";

function antwort(status, daten) {
  return new Response(JSON.stringify(daten), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

export default async (req) => {
  if (req.method !== "POST") return antwort(405, { fehler: "Nur POST" });

  const erlaubt = (process.env.ERLAUBTE_URSPRUENGE || "").split(",").map((s) => s.trim()).filter(Boolean);
  const herkunft = req.headers.get("origin");
  if (erlaubt.length && herkunft && !erlaubt.includes(herkunft)) return antwort(403, { fehler: "Herkunft nicht erlaubt" });

  let eingabe;
  try {
    eingabe = pruefe(await req.json());
  } catch (e) {
    return antwort(e.status || 400, { fehler: e.message });
  }

  // Claude Opus 5 und neuer: Fallback bei Ablehnungen serverseitig, Denktiefe fuer ein Gespraech niedrig
  const neu = /^claude-(opus-5|sonnet-5-5|fable)/.test(MODELL);
  const anfrage = {
    model: MODELL,
    max_tokens: 4000,
    system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
    messages: nachrichten(eingabe),
  };
  if (neu) {
    anfrage.output_config = { effort: "low" };
    anfrage.betas = ["server-side-fallback-2026-07-01"];
    anfrage.fallbacks = "default";
  }

  try {
    const response = neu ? await client.beta.messages.create(anfrage) : await client.messages.create(anfrage);
    const text = antworttext(response);
    if (!text) return antwort(502, { fehler: "Keine Antwort" });
    return antwort(200, { text });
  } catch (e) {
    if (e instanceof Anthropic.AuthenticationError) return antwort(500, { fehler: "API-Schlüssel fehlt oder ist ungültig" });
    if (e instanceof Anthropic.RateLimitError) return antwort(429, { fehler: "Zu viele Anfragen" });
    if (e instanceof Anthropic.APIError) return antwort(502, { fehler: "API-Fehler " + e.status });
    return antwort(502, { fehler: "Verbindung fehlgeschlagen" });
  }
};
