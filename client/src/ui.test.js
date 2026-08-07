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
});
