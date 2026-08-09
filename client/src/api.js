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

export async function fetchCategories() {
  const { httpUrl, apiKey } = getServerConfig();
  const res = await fetch(`${httpUrl}/api/categories`, {
    headers: { "X-API-Key": apiKey }
  });
  await assertOk(res, "Récupération des catégories");
  return res.json();
}

export async function createCategory(name) {
  const { httpUrl, apiKey } = getServerConfig();
  const res = await fetch(`${httpUrl}/api/categories`, {
    method: "POST",
    headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });
  await assertOk(res, "Création de catégorie");
  return res.json();
}

export async function reformulateText(text) {
  const { httpUrl, apiKey } = getServerConfig();
  const res = await fetch(`${httpUrl}/api/reformulate`, {
    method: "POST",
    headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });
  await assertOk(res, "Reformulation");
  return res.json();
}

export async function setMessageCategory(messageId, category) {
  const { httpUrl, apiKey } = getServerConfig();
  const res = await fetch(`${httpUrl}/api/memory/${messageId}/category`, {
    method: "PATCH",
    headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({ category })
  });
  await assertOk(res, "Reclassement de la note");
  return res.json();
}

export async function setMessageContent(messageId, content) {
  const { httpUrl, apiKey } = getServerConfig();
  const res = await fetch(`${httpUrl}/api/memory/${messageId}/content`, {
    method: "PATCH",
    headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({ content })
  });
  await assertOk(res, "Mise à jour de la note");
  return res.json();
}

export async function deleteMessage(messageId) {
  const { httpUrl, apiKey } = getServerConfig();
  const res = await fetch(`${httpUrl}/api/memory/${messageId}`, {
    method: "DELETE",
    headers: { "X-API-Key": apiKey }
  });
  await assertOk(res, "Suppression de la note");
  return res.json();
}

export async function fetchNoteLinks(messageId) {
  const { httpUrl, apiKey } = getServerConfig();
  const res = await fetch(`${httpUrl}/api/memory/${messageId}/links`, {
    headers: { "X-API-Key": apiKey }
  });
  await assertOk(res, "Récupération des liens");
  return res.json();
}

export async function createNoteLink(messageId, toId) {
  const { httpUrl, apiKey } = getServerConfig();
  const res = await fetch(`${httpUrl}/api/memory/${messageId}/links`, {
    method: "POST",
    headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
    body: JSON.stringify({ to_id: toId })
  });
  await assertOk(res, "Création du lien");
  return res.json();
}

export async function deleteNoteLink(linkId) {
  const { httpUrl, apiKey } = getServerConfig();
  const res = await fetch(`${httpUrl}/api/memory/links/${linkId}`, {
    method: "DELETE",
    headers: { "X-API-Key": apiKey }
  });
  await assertOk(res, "Suppression du lien");
  return res.json();
}

export async function fetchRelatedNotes(messageId) {
  const { httpUrl, apiKey } = getServerConfig();
  const res = await fetch(`${httpUrl}/api/memory/${messageId}/related`, {
    headers: { "X-API-Key": apiKey }
  });
  await assertOk(res, "Récupération des notes connectées");
  return res.json();
}
