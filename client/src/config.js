// Per-device runtime config, set via the in-app settings panel and persisted
// in localStorage. Never hardcode a real API_KEY here — this file is
// committed to a public repo, localStorage is not.
const STORAGE_KEY = "johnai.server-config";
const DEFAULT_HTTP_URL = "https://johnai.john-world.store";

function readStoredConfig() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    console.warn("Config serveur illisible dans localStorage, valeurs par défaut utilisées", e);
    return {};
  }
}

export function getServerConfig() {
  const stored = readStoredConfig();
  const httpUrl = stored.httpUrl || DEFAULT_HTTP_URL;
  const apiKey = stored.apiKey || "";
  const wsUrl = `${httpUrl.replace(/^http/, 'ws')}/ws?api_key=${encodeURIComponent(apiKey)}`;
  return { httpUrl, apiKey, wsUrl };
}

export function saveServerConfig({ httpUrl, apiKey }) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ httpUrl, apiKey }));
}
