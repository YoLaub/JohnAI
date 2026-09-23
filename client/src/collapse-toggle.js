const STORAGE_KEY = 'johnai.collapsed';

/** Reduced mode: folds the widget down to its brand badge. The state is
 *  remembered per device (localStorage); the window itself shrinks through
 *  window-fit.js, which tracks the rendered size of the container. */
export function createCollapseToggle({ container, button }) {
  function apply(collapsed) {
    container.classList.toggle('collapsed', collapsed);
    button.setAttribute('aria-expanded', String(!collapsed));
    button.title = collapsed ? 'Agrandir JohnAi' : 'Réduire JohnAi';
  }

  function toggle() {
    const collapsed = !container.classList.contains('collapsed');
    apply(collapsed);
    localStorage.setItem(STORAGE_KEY, collapsed ? '1' : '0');
  }

  apply(localStorage.getItem(STORAGE_KEY) === '1');
  button.addEventListener('click', toggle);

  return { toggle };
}
