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
    const deleteBtn = isUserNote
      ? `<button class="thought-delete-btn" data-message-id="${item.id}" title="Supprimer cette pensée">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2m3 0-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6h14Z"/>
          </svg>
        </button>`
      : '';
    const linkBtn = isUserNote
      ? `<button class="thought-link-btn" data-message-id="${item.id}" title="Relier à une autre pensée">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
          </svg>
        </button>`
      : '';
    return `
    <div class="thought-card">
      <div class="thought-tag">
        <span>${item.role === 'user' ? '📝 Pensée' : '✦ JohnAi'}</span>
        <span class="thought-tag-actions">${reformulateBtn}${linkBtn}${deleteBtn}${badge}</span>
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
