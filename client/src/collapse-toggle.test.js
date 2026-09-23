import { describe, it, expect, beforeEach } from 'vitest';
import { createCollapseToggle } from './collapse-toggle.js';

const STORAGE_KEY = 'johnai.collapsed';

function setup() {
  document.body.innerHTML = `
    <main id="widgetContainer"></main>
    <button id="btnCollapse"></button>
  `;
  return {
    container: document.getElementById('widgetContainer'),
    button: document.getElementById('btnCollapse'),
  };
}

describe('createCollapseToggle', () => {
  beforeEach(() => localStorage.clear());

  it('starts expanded by default', () => {
    const { container, button } = setup();
    createCollapseToggle({ container, button });
    expect(container.classList.contains('collapsed')).toBe(false);
    expect(button.getAttribute('aria-expanded')).toBe('true');
  });

  it('collapses on click and expands on a second click', () => {
    const { container, button } = setup();
    createCollapseToggle({ container, button });

    button.click();
    expect(container.classList.contains('collapsed')).toBe(true);
    expect(button.getAttribute('aria-expanded')).toBe('false');

    button.click();
    expect(container.classList.contains('collapsed')).toBe(false);
    expect(button.getAttribute('aria-expanded')).toBe('true');
  });

  it('remembers the collapsed state per device', () => {
    const first = setup();
    createCollapseToggle(first);
    first.button.click();
    expect(localStorage.getItem(STORAGE_KEY)).toBe('1');

    const second = setup();
    createCollapseToggle(second);
    expect(second.container.classList.contains('collapsed')).toBe(true);
  });
});
