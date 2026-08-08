/** Keeps the native (desktop) Tauri window's hitbox matched to the actually
 *  rendered content. Without this, the window stays at its initial fixed
 *  size and — even though its background is visually transparent — the
 *  whole rectangle still intercepts clicks meant for whatever is behind it
 *  on the desktop. */
import { isTauriRuntime } from './local-stt.js';

export function startWindowAutoFit(containerEl) {
  if (!isTauriRuntime() || !window.__TAURI__.window) return;

  const tauriWindow = window.__TAURI__.window.getCurrentWindow();
  const LogicalSize = window.__TAURI__.window.LogicalSize;

  let lastWidth = 0;
  let lastHeight = 0;
  let pending = null;

  function applySize() {
    pending = null;
    const width = Math.ceil(containerEl.scrollWidth);
    const height = Math.ceil(containerEl.scrollHeight);
    if (width === lastWidth && height === lastHeight) return;
    lastWidth = width;
    lastHeight = height;
    tauriWindow.setSize(new LogicalSize(width, height)).catch((e) => {
      console.warn("Impossible de redimensionner la fenêtre:", e);
    });
  }

  const observer = new ResizeObserver(() => {
    // Debounce: CSS transitions fire many resize events in a row.
    if (pending) clearTimeout(pending);
    pending = setTimeout(applySize, 60);
  });
  observer.observe(containerEl);

  applySize();
}
