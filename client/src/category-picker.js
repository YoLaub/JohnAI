import { fetchCategories, createCategory } from './api.js';
import { escapeHtml } from './utils.js';

const UNCATEGORIZED = 'Non classé';

/** Reusable category picker panel: pick an existing category, create a new
 *  one, or clear back to "Non classé". Used both for pre-selecting the
 *  category of the next note and for reassigning a specific past one —
 *  the caller decides what "selecting a category" means via onSelect. */
export function createCategoryPicker({ panel, chipListContainer, newCategoryInput, btnAddCategory }) {
  let onSelect = null;

  async function open(activeCategory, onSelectCallback) {
    onSelect = onSelectCallback;
    panel.classList.remove('hidden');
    await refreshChips(activeCategory || '');
  }

  function close() {
    panel.classList.add('hidden');
    onSelect = null;
  }

  function toggle(activeCategory, onSelectCallback) {
    if (panel.classList.contains('hidden')) {
      open(activeCategory, onSelectCallback);
    } else {
      close();
    }
  }

  function choose(category) {
    if (onSelect) onSelect(category);
    close();
  }

  async function refreshChips(activeCategory) {
    let categories = [];
    try {
      const data = await fetchCategories();
      categories = data.categories || [];
    } catch (e) {
      console.warn("Erreur récupération catégories:", e);
    }

    const options = [{ value: '', label: UNCATEGORIZED }, ...categories.map(c => ({ value: c, label: c }))];
    chipListContainer.innerHTML = options.map(opt => `
      <div class="category-chip ${opt.value === activeCategory ? 'active' : ''}" data-category="${escapeHtml(opt.value)}">
        ${escapeHtml(opt.label)}
      </div>
    `).join('');

    chipListContainer.querySelectorAll('.category-chip').forEach(chip => {
      chip.addEventListener('click', () => choose(chip.getAttribute('data-category')));
    });
  }

  btnAddCategory.addEventListener('click', async () => {
    const name = newCategoryInput.value.trim();
    if (!name) return;
    try {
      await createCategory(name);
      newCategoryInput.value = '';
      choose(name);
    } catch (e) {
      console.warn("Erreur création catégorie:", e);
    }
  });

  return { open, close, toggle };
}
