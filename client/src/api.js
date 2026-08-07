import { getServerConfig } from './config.js';

async function assertOk(res, label) {
  if (!res.ok) {
    throw new Error(`${label} : le serveur a répondu HTTP ${res.status}${res.status === 401 ? " (clé API invalide ou manquante)" : ""}`);
  }
  return res;
}

export async function fetchMemoryHistory() {
  const { httpUrl, apiKey } = getServerConfig();
  const res = await fetch(`${httpUrl}/api/memory/history`, {
    headers: { "X-API-Key": apiKey }
  });
  await assertOk(res, "Récupération de la mémoire");
  return res.json();
}

export async function transcribeAudio(audioBlob) {
  const { httpUrl, apiKey } = getServerConfig();
  const formData = new FormData();
  formData.append("file", audioBlob, "note_vocale.webm");

  const res = await fetch(`${httpUrl}/api/transcribe`, {
    method: "POST",
    headers: { "X-API-Key": apiKey },
    body: formData
  });
  await assertOk(res, "Transcription audio");
  return res.json();
}

export async function uploadFile(file) {
  const { httpUrl, apiKey } = getServerConfig();
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${httpUrl}/api/upload`, {
    method: "POST",
    headers: { "X-API-Key": apiKey },
    body: formData
  });
  return assertOk(res, "Envoi du fichier");
}
