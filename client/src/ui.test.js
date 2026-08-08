import { describe, it, expect, beforeEach } from 'vitest';
import { renderThoughtsHistory } from './ui.js';

describe('renderThoughtsHistory', () => {
  let container;

  beforeEach(() => {
    container = document.createElement('div');
  });

  it('shows a placeholder when history is empty', () => {
    renderThoughtsHistory(container, []);
    expect(container.textContent).toContain('Aucune pensée enregistrée');
  });

  it('renders the most recent items, newest first', () => {
    const history = [
      { role: 'user', content: 'premier' },
      { role: 'assistant', content: 'deuxième' },
    ];
    renderThoughtsHistory(container, history);
    const cards = container.querySelectorAll('.thought-card');
    expect(cards).toHaveLength(2);
    expect(cards[0].textContent).toContain('deuxième');
    expect(cards[1].textContent).toContain('premier');
  });

  it('escapes user content to avoid HTML injection', () => {
    renderThoughtsHistory(container, [{ role: 'user', content: '<img src=x>' }]);
    expect(container.innerHTML).not.toContain('<img');
    expect(container.innerHTML).toContain('&lt;img');
  });

  it('shows a category badge on user notes that have one', () => {
    renderThoughtsHistory(container, [{ id: 42, role: 'user', content: 'idée', category: 'Projet' }]);
    const badge = container.querySelector('.thought-category-badge');
    expect(badge).not.toBeNull();
    expect(badge.textContent.trim()).toBe('Projet');
    expect(badge.dataset.messageId).toBe('42');
  });

  it('shows "Non classé" for uncategorized user notes, no badge for assistant replies', () => {
    renderThoughtsHistory(container, [
      { id: 1, role: 'user', content: 'sans catégorie', category: null },
      { id: 2, role: 'assistant', content: 'réponse' },
    ]);
    const badges = container.querySelectorAll('.thought-category-badge');
    expect(badges).toHaveLength(1);
    expect(badges[0].textContent.trim()).toBe('Non classé');
  });

  it('shows a reformulate button on user notes only, wired to the message id', () => {
    renderThoughtsHistory(container, [
      { id: 7, role: 'user', content: 'idée floue' },
      { id: 8, role: 'assistant', content: 'réponse' },
    ]);
    const buttons = container.querySelectorAll('.thought-reformulate-btn');
    expect(buttons).toHaveLength(1);
    expect(buttons[0].dataset.messageId).toBe('7');
  });
});
