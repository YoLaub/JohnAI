import { fetchNoteLinks, createNoteLink, deleteNoteLink, fetchRelatedNotes } from './api.js';
import { escapeHtml } from './utils.js';

function snippet(content, max = 60) {
  const flat = content.replace(/\s+/g, ' ').trim();
  return flat.length > max ? `${flat.slice(0, max)}…` : flat;
}

function timeAgo(isoString) {
  // SQLite CURRENT_TIMESTAMP is UTC without a "Z" suffix — without it, Date()
  // parses it as local time and every "since when" is off by the UTC offset.
  const then = new Date(`${isoString}Z`).getTime();
  const diffMs = Date.now() - then;
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return "à l'instant";
  if (minutes < 60) return `il y a ${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `il y a ${hours} h`;
  const days = Math.floor(hours / 24);
  return `il y a ${days} j`;
}

/** Reusable "link this note to another one" panel: lists existing links
 *  (with an unlink button and "since when") and a searchable list of other
 *  notes to add as a new link. Undirected — no relation type, just "these
 *  two are connected". */
export function createLinkPicker({ panel, existingListEl, candidateListEl, searchInput, btnRelated, relatedListEl }) {
  let messageId = null;
  let allNotes = [];
  let onChange = null;
  let linkedIds = new Set();
  let relatedLoaded = false;

  function close() {
    panel.classList.add('hidden');
    messageId = null;
    allNotes = [];
    onChange = null;
    linkedIds = new Set();
    searchInput.value = '';
    relatedLoaded = false;
    if (relatedListEl) relatedListEl.classList.add('hidden');
  }

  async function refreshExisting() {
    let links = [];
    try {
      const data = await fetchNoteLinks(messageId);
      links = data.links || [];
    } catch (e) {
      console.warn("Erreur récupération des liens:", e);
    }
    linkedIds = new Set(links.map(l => l.message_id));

    existingListEl.innerHTML = links.length
      ? links.map(l => `
        <div class="link-item">
          <span class="link-item-text">${escapeHtml(snippet(l.content))}</span>
          <span class="link-item-meta">${escapeHtml(timeAgo(l.created_at))}</span>
          <button class="link-item-remove" data-link-id="${l.link_id}" title="Délier">✕</button>
        </div>
      `).join('')
      : `<div class="link-item-empty">Aucun lien pour l'instant.</div>`;

    existingListEl.querySelectorAll('.link-item-remove').forEach(btn => {
      btn.addEventListener('click', async () => {
        try {
          await deleteNoteLink(btn.getAttribute('data-link-id'));
          await refreshExisting();
          renderCandidates();
          if (onChange) onChange();
        } catch (e) {
          console.warn("Erreur suppression du lien:", e);
        }
      });
    });
  }

  function renderCandidates() {
    const query = searchInput.value.trim().toLowerCase();
    const candidates = allNotes
      .filter(n => n.id !== messageId && n.role === 'user' && !linkedIds.has(n.id))
      .filter(n => !query || n.content.toLowerCase().includes(query))
      .slice(0, 20);

    candidateListEl.innerHTML = candidates.length
      ? candidates.map(n => `
        <div class="link-candidate" data-candidate-id="${n.id}">
          ${escapeHtml(snippet(n.content))}
        </div>
      `).join('')
      : `<div class="link-item-empty">Aucune note correspondante.</div>`;

    candidateListEl.querySelectorAll('.link-candidate').forEach(el => {
      el.addEventListener('click', async () => {
        const toId = parseInt(el.getAttribute('data-candidate-id'), 10);
        try {
          await createNoteLink(messageId, toId);
          await refreshExisting();
          renderCandidates();
          if (onChange) onChange();
        } catch (e) {
          console.warn("Erreur création du lien:", e);
        }
      });
    });
  }

  async function loadRelated() {
    if (!relatedListEl) return;
    relatedListEl.classList.remove('hidden');
    relatedListEl.innerHTML = `<div class="link-item-empty">Chargement...</div>`;
    try {
      const data = await fetchRelatedNotes(messageId);
      const related = data.related || [];
      relatedListEl.innerHTML = related.length
        ? related.map(n => `
          <div class="link-item">
            <span class="link-item-hops">${n.hops === 1 ? '1 saut' : `${n.hops} sauts`}</span>
            <span class="link-item-text">${escapeHtml(snippet(n.content))}</span>
          </div>
        `).join('')
        : `<div class="link-item-empty">Aucune note connectée à 2 sauts.</div>`;
    } catch (e) {
      console.warn("Erreur récupération des notes connectées:", e);
      relatedListEl.innerHTML = `<div class="link-item-empty">Erreur de chargement.</div>`;
    }
  }

  if (btnRelated && relatedListEl) {
    btnRelated.addEventListener('click', () => {
      if (messageId === null) return;
      if (relatedListEl.classList.contains('hidden') || !relatedLoaded) {
        relatedLoaded = true;
        loadRelated();
      } else {
        relatedListEl.classList.add('hidden');
      }
    });
  }

  async function open(noteId, notes, onChangeCallback) {
    messageId = noteId;
    allNotes = notes || [];
    onChange = onChangeCallback;
    relatedLoaded = false;
    if (relatedListEl) relatedListEl.classList.add('hidden');
    panel.classList.remove('hidden');
    await refreshExisting();
    renderCandidates();
  }

  function toggle(noteId, notes, onChangeCallback) {
    if (!panel.classList.contains('hidden') && messageId === noteId) {
      close();
    } else {
      open(noteId, notes, onChangeCallback);
    }
  }

  searchInput.addEventListener('input', () => {
    if (messageId !== null) renderCandidates();
  });

  return { open, close, toggle };
}
