import { reformulateText } from './api.js';
import { escapeHtml } from './utils.js';
import { isLocalOllamaReady, generateLocally } from './local-ollama.js';

// Kept identical in spirit to server/main.py::reformulate_text's system_prompt —
// desktop generates this locally instead of round-tripping to the server.
const REFORMULATE_SYSTEM_PROMPT =
  "Tu reformules la note suivante pour la rendre plus claire et correcte, " +
  "sans changer son sens ni ajouter d'information. Réponds uniquement avec " +
  "le texte reformulé, sans commentaire ni guillemets.";

/** Local Ollama first (desktop Tauri), server (Gemini) otherwise — exact
 *  mirror of the transcribeLocally/transcribeAudio fallback pattern used for
 *  voice notes in app.js. */
async function reformulate(text) {
  if (await isLocalOllamaReady()) {
    try {
      const reformulated = await generateLocally([
        { role: 'system', content: REFORMULATE_SYSTEM_PROMPT },
        { role: 'user', content: text },
      ]);
      if (reformulated && reformulated.trim()) {
        return { status: 'ok', reformulated: reformulated.trim() };
      }
    } catch (e) {
      console.warn("Échec reformulation locale, repli sur le serveur:", e);
    }
  }
  return reformulateText(text);
}

/** Reusable "Reformuler" preview panel: sends text to the server, shows the
 *  original vs the reformulated version side by side, and only calls
 *  onKeep(reformulated) if the user explicitly confirms — never replaces
 *  anything silently. Used both for the not-yet-sent draft (editPanel) and
 *  for a past note (journal card). */
export function createReformulatePicker({ panel, originalEl, resultEl, btnKeep, btnCancel }) {
  let onKeep = null;
  let lastReformulated = '';

  function close() {
    panel.classList.add('hidden');
    onKeep = null;
    lastReformulated = '';
  }

  async function open(text, onKeepCallback) {
    if (!text || !text.trim()) return;
    onKeep = onKeepCallback;
    panel.classList.remove('hidden');
    originalEl.textContent = text;
    resultEl.textContent = 'Reformulation en cours...';
    btnKeep.disabled = true;

    try {
      const data = await reformulate(text);
      if (data.status === 'ok') {
        lastReformulated = data.reformulated;
        resultEl.textContent = data.reformulated;
        btnKeep.disabled = false;
      } else {
        resultEl.innerHTML = `<span style="color:#f59e0b;">⚠️ Reformulation indisponible pour le moment.</span>`;
      }
    } catch (e) {
      resultEl.innerHTML = `<span style="color:#ef4444;">❌ ${escapeHtml(e.message)}</span>`;
    }
  }

  btnKeep.addEventListener('click', () => {
    if (onKeep && lastReformulated) onKeep(lastReformulated);
    close();
  });

  btnCancel.addEventListener('click', close);

  return { open, close };
}
