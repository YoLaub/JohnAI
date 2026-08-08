/** Keeps the native (desktop) Tauri window's hitbox matched to the actually
 *  rendered content. Without this, the window stays at its initial fixed
 *  size and — even though its background is visually transparent — the
 *  whole rectangle still intercepts clicks meant for whatever is behind it
 *  on the desktop. */
import { isTauriRuntime } from './local-stt.js';

const SAFETY_MARGIN_PX = 6;

/** Sum of visible children's own size (bypasses containerEl's own
 *  width:fit-content resolution, which can under-measure: a stretched flex
 *  child's content can need more room than the fit-content width the
 *  browser settled on for the *container*, and containerEl.scrollWidth
 *  reflects that already-too-narrow box, not what the child actually needs). */
function measureVisibleContent(containerEl) {
  let maxWidth = 0;
  let totalHeight = 0;
  let visibleCount = 0;

  for (const child of containerEl.children) {
    if (child.offsetParent === null) continue; // display:none (hidden panels)
    maxWidth = Math.max(maxWidth, child.scrollWidth, child.getBoundingClientRect().width);
    totalHeight += child.getBoundingClientRect().height;
    visibleCount++;
  }

  const gapPx = parseFloat(getComputedStyle(containerEl).rowGap) || 0;
  totalHeight += gapPx * Math.max(0, visibleCount - 1);

  return {
    width: Math.ceil(maxWidth) + SAFETY_MARGIN_PX,
    height: Math.ceil(totalHeight) + SAFETY_MARGIN_PX,
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
