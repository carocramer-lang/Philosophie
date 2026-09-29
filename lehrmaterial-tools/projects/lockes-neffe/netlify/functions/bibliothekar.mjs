// Netlify Function: Antwort des Bibliothekars ueber eine KI-API.
// Aufruf aus dem Spiel: POST /.netlify/functions/bibliothekar  { zusammenfassung, verlauf, art }
// Anbieter je nach hinterlegtem Schluessel (Netlify: Site configuration > Environment variables):
//   GEMINI_API_KEY      -> Google Gemini   (Modell: GEMINI_MODELL, Standard gemini-flash-latest)
//   ANTHROPIC_API_KEY   -> Anthropic Claude (Modell: BIBLIOTHEKAR_MODELL, Standard claude-opus-5-5)
//   ERLAUBTE_URSPRUENGE optional, z. B. "https://lockes-neffe.netlify.app". Andere Seiten werden abgewiesen.
// Die Schluessel bleiben auf dem Server und erreichen nie den Browser.

import Anthropic from "@anthropic-ai/sdk";
import { GoogleGenAI, ApiError } from "@google/genai";
import { SYSTEM, pruefe, nachrichten, antworttext } from "../lib/bibliothekar-kern.mjs";

// Umgebungsvariablen ueber Netlify.env (auf Netlify), sonst process.env (lokale Tests)
function env(name) {
  return globalThis.Netlify && globalThis.Netlify.env ? globalThis.Netlify.env.get(name) : process.env[name];
}

function antwort(status, daten) {
  return new Response(JSON.stringify(daten), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

// ---------- Google Gemini
async function mitGemini(msgs) {
  const ai = new GoogleGenAI({
    apiKey: env("GEMINI_API_KEY"),
    httpOptions: env("GEMINI_BASE_URL") ? { baseUrl: env("GEMINI_BASE_URL") } : undefined, // nur fuer Tests
  });
  try {
    const r = await ai.models.generateContent({
      model: env("GEMINI_MODELL") || "gemini-flash-latest",
      contents: msgs.map((m) => ({ role: m.role === "assistant" ? "model" : "user", parts: [{ text: m.content }] })),
      config: { systemInstruction: SYSTEM, maxOutputTokens: 4096, temperature: 0.6 },
    });
    const text = (r.text || "").trim();
    return text ? antwort(200, { text }) : antwort(502, { fehler: "Keine Antwort" });
  } catch (e) {
    if (e instanceof ApiError && (e.status === 401 || e.status === 403)) return antwort(500, { fehler: "API-Schlüssel fehlt oder ist ungültig" });
    if (e instanceof ApiError && e.status === 429) return antwort(429, { fehler: "Zu viele Anfragen" });
    if (e instanceof ApiError) return antwort(502, { fehler: "API-Fehler " + e.status });
    return antwort(502, { fehler: "Verbindung fehlgeschlagen" });
  }
}

// ---------- Anthropic Claude
async function mitClaude(msgs) {
  const client = new Anthropic({ apiKey: env("ANTHROPIC_API_KEY") });
  const modell = env("BIBLIOTHEKAR_MODELL") || "claude-opus-5-5";
  // Claude Opus 5 und neuer: Fallback bei Ablehnungen serverseitig, Denktiefe fuer ein Gespraech niedrig
  const neu = /^claude-(opus-5|sonnet-5-5|fable)/.test(modell);
  const anfrage = {
    model: modell,
    max_tokens: 4000,
    system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
    messages: msgs,
  };
  if (neu) {
    anfrage.output_config = { effort: "low" };
    anfrage.betas = ["server-side-fallback-2026-07-01"];
    anfrage.fallbacks = "default";
  }
  try {
    const response = neu ? await client.beta.messages.create(anfrage) : await client.messages.create(anfrage);
    const text = antworttext(response);
    return text ? antwort(200, { text }) : antwort(502, { fehler: "Keine Antwort" });
  } catch (e) {
    if (e instanceof Anthropic.AuthenticationError) return antwort(500, { fehler: "API-Schlüssel fehlt oder ist ungültig" });
    if (e instanceof Anthropic.RateLimitError) return antwort(429, { fehler: "Zu viele Anfragen" });
    if (e instanceof Anthropic.APIError) return antwort(502, { fehler: "API-Fehler " + e.status });
    return antwort(502, { fehler: "Verbindung fehlgeschlagen" });
  }
}

export default async (req) => {
  if (req.method !== "POST") return antwort(405, { fehler: "Nur POST" });

  const erlaubt = (env("ERLAUBTE_URSPRUENGE") || "").split(",").map((s) => s.trim()).filter(Boolean);
  const herkunft = req.headers.get("origin");
  if (erlaubt.length && herkunft && !erlaubt.includes(herkunft)) return antwort(403, { fehler: "Herkunft nicht erlaubt" });

  let eingabe;
  try {
    eingabe = pruefe(await req.json());
  } catch (e) {
    return antwort(e.status || 400, { fehler: e.message });
  }
  const msgs = nachrichten(eingabe);

  if (env("GEMINI_API_KEY")) return mitGemini(msgs);
  if (env("ANTHROPIC_API_KEY")) return mitClaude(msgs);
  // Ohne Schluessel: 503, das Spiel antwortet dann mit der eingebauten Fassung
  return antwort(503, { fehler: "Kein API-Schlüssel hinterlegt" });
};
