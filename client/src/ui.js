import { escapeHtml } from './utils.js';

export function renderThoughtsHistory(container, history) {
  if (!history.length) {
    container.innerHTML = `<div class="thought-card"><div class="thought-text">Aucune pensée enregistrée pour le moment.</div></div>`;
    return;
  }

  container.innerHTML = history.slice(-8).reverse().map(item => `
    <div class="thought-card">
      <div class="thought-tag">${item.role === 'user' ? '📝 Pensée' : '✦ JohnAi'}</div>
      <div class="thought-text">${escapeHtml(item.content)}</div>
    </div>
  `).join('');
}

export function renderAssistantResponse(container, rawText) {
  if (window.marked) {
    container.innerHTML = marked.parse(rawText);
  } else {
    container.innerHTML = escapeHtml(rawText);
  }
}
