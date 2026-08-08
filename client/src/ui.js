import { escapeHtml } from './utils.js';

export function renderThoughtsHistory(container, history) {
  if (!history.length) {
    container.innerHTML = `<div class="thought-card"><div class="thought-text">Aucune pensée enregistrée pour le moment.</div></div>`;
    return;
  }

  container.innerHTML = history.slice(-8).reverse().map(item => {
    const badge = (item.role === 'user' && item.id !== undefined)
      ? `<span class="thought-category-badge" data-message-id="${item.id}" data-current-category="${escapeHtml(item.category || '')}">${escapeHtml(item.category || 'Non classé')}</span>`
      : '';
    return `
    <div class="thought-card">
      <div class="thought-tag">
        <span>${item.role === 'user' ? '📝 Pensée' : '✦ JohnAi'}</span>
        ${badge}
      </div>
      <div class="thought-text">${escapeHtml(item.content)}</div>
    </div>
  `;
  }).join('');
}

export function renderAssistantResponse(container, rawText) {
  if (window.marked) {
    container.innerHTML = marked.parse(rawText);
  } else {
    container.innerHTML = escapeHtml(rawText);
  }
}
