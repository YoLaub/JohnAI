import { reformulateText } from './api.js';
import { escapeHtml } from './utils.js';

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
      const data = await reformulateText(text);
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
