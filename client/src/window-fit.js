/** Keeps the native (desktop) Tauri window's hitbox matched to the actually
 *  rendered content. Without this, the window stays at its initial fixed
 *  size and — even though its background is visually transparent — the
 *  whole rectangle still intercepts clicks meant for whatever is behind it
 *  on the desktop. */
import { isTauriRuntime } from './local-stt.js';

const SAFETY_MARGIN_PX = 12;

/** Let the browser's own layout resolve the container's size (handles flex
 *  stretch, gaps, and pseudo-elements correctly) rather than reimplementing
 *  the box model by summing children — that approach double-counted
 *  out-of-flow children (e.g. the absolutely-positioned drag-overlay) and
 *  still needed the exact same margin fudging. scrollWidth/scrollHeight
 *  naturally excludes absolutely-positioned overflow (drag-overlay's
 *  inset:-6px) since out-of-flow elements never contribute to it. */
function measureVisibleContent(containerEl) {
  const rect = containerEl.getBoundingClientRect();
  const width = Math.max(containerEl.scrollWidth, rect.width);
  const height = Math.max(containerEl.scrollHeight, rect.height);

  return {
    width: Math.ceil(width) + SAFETY_MARGIN_PX,
    height: Math.ceil(height) + SAFETY_MARGIN_PX,
  };
}

function nextFrame() {
  return new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
}

export function startWindowAutoFit(containerEl) {
  if (!isTauriRuntime() || !window.__TAURI__.window) return;

  const tauriWindow = window.__TAURI__.window.getCurrentWindow();
  const LogicalSize = window.__TAURI__.window.LogicalSize;

  let lastWidth = 0;
  let lastHeight = 0;
  let pending = null;

  async function applySize() {
    pending = null;
    // Let layout fully settle (DOM mutations from an await'd fetch, class
    // toggles, etc.) before reading sizes — reading mid-layout is how you
    // get a stale, too-small measurement and a window that clips content.
    await nextFrame();

    const { width, height } = measureVisibleContent(containerEl);
    console.log(`[window-fit] mesuré ${width}x${height} (précédent: ${lastWidth}x${lastHeight})`);
    if (width === lastWidth && height === lastHeight) return;
    lastWidth = width;
    lastHeight = height;
    try {
      await tauriWindow.setSize(new LogicalSize(width, height));
      const actual = await tauriWindow.innerSize();
      const scale = await tauriWindow.scaleFactor();
      console.log(`[window-fit] setSize appliqué. Taille physique réelle rapportée par l'OS: ${actual.width}x${actual.height} (scale=${scale}, attendu logique ${width}x${height} → physique ${Math.round(width*scale)}x${Math.round(height*scale)})`);
    } catch (e) {
      console.warn("[window-fit] Impossible de redimensionner la fenêtre:", e);
    }
  }

  const observer = new ResizeObserver(() => {
    // Debounce: CSS transitions / rapid DOM changes fire many resize events in a row.
    if (pending) clearTimeout(pending);
    pending = setTimeout(applySize, 80);
  });
  observer.observe(containerEl);
  for (const child of containerEl.children) {
    observer.observe(child);
  }

  applySize();
}
