import { API_KEY, SERVER_HTTP_URL } from './config.js';

export async function fetchMemoryHistory() {
  const res = await fetch(`${SERVER_HTTP_URL}/api/memory/history`, {
    headers: { "X-API-Key": API_KEY }
  });
  if (!res.ok) return null;
  return res.json();
}

export async function transcribeAudio(audioBlob) {
  const formData = new FormData();
  formData.append("file", audioBlob, "note_vocale.webm");

  const res = await fetch(`${SERVER_HTTP_URL}/api/transcribe`, {
    method: "POST",
    headers: { "X-API-Key": API_KEY },
    body: formData
  });
  if (!res.ok) return null;
  return res.json();
}

export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  return fetch(`${SERVER_HTTP_URL}/api/upload`, {
    method: "POST",
    headers: { "X-API-Key": API_KEY },
    body: formData
  });
}
