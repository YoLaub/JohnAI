import { isTauriRuntime } from './local-stt.js';

export { isTauriRuntime };

/** True only on a Tauri desktop build with a local Ollama reachable and the
 *  general model pulled — Android has no such runtime (see ollama.rs's
 *  #[cfg(not(target_os = "android"))] gating) and always returns false. */
export async function isLocalOllamaReady() {
  if (!isTauriRuntime()) return false;
  try {
    return await window.__TAURI__.core.invoke('is_ollama_ready');
  } catch (e) {
    console.warn("Ollama local non disponible:", e);
    return false;
  }
}

/** messages: [{role: 'system'|'user'|'assistant', content: string}] */
export async function generateLocally(messages) {
  return window.__TAURI__.core.invoke('ollama_generate', { messages });
}
