import { escapeHtml } from './utils.js';

export function renderThoughtsHistory(container, history) {
  if (!history.length) {
    container.innerHTML = `<div class="thought-card"><div class="thought-text">Aucune pensée enregistrée pour le moment.</div></div>`;
    return;
  }

  container.innerHTML = history.slice(-8).reverse().map(item => {
    const isUserNote = item.role === 'user' && item.id !== undefined;
    const badge = isUserNote
      ? `<span class="thought-category-badge" data-message-id="${item.id}" data-current-category="${escapeHtml(item.category || '')}">${escapeHtml(item.category || 'Non classé')}</span>`
      : '';
    const reformulateBtn = isUserNote
      ? `<button class="thought-reformulate-btn" data-message-id="${item.id}" title="Reformuler cette pensée">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 3v3m0 12v3m9-9h-3M6 12H3m14.95-6.36-2.12 2.12M8.17 15.24l-2.12 2.12m0-12.72 2.12 2.12m9.66 9.66-2.12-2.12"/>
          </svg>
        </button>`
      : '';
    return `
    <div class="thought-card">
      <div class="thought-tag">
        <span>${item.role === 'user' ? '📝 Pensée' : '✦ JohnAi'}</span>
        <span class="thought-tag-actions">${reformulateBtn}${badge}</span>
      </div>
      <div class="thought-text" data-message-id="${isUserNote ? item.id : ''}">${escapeHtml(item.content)}</div>
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
