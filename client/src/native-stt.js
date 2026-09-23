/** On-device dictation for the Android app, through Android's own
 *  SpeechRecognizer (tauri-plugin-stt). No audio file, no server round-trip:
 *  the text comes straight from the phone's recognizer. Desktop keeps
 *  whisper.cpp (local-stt.js). */
import { isTauriRuntime } from './local-stt.js';

export function isNativeDictationAvailable() {
  return isTauriRuntime() && /Android/i.test(navigator.userAgent);
}

/** Continuous mode: Android ends a segment after a short silence and the
 *  plugin restarts listening, so a note arrives as several final segments.
 *  They are joined and delivered once, when the user stops. */
export function createNativeDictation({ invoke, addPluginListener, onText, onDone, settleMs = 500 }) {
  let finals = [];
  let interim = '';
  let listener = null;
  let settle = null;

  function currentText() {
    return [...finals, interim].filter(Boolean).join(' ');
  }

  function handleResult({ transcript, isFinal }) {
    if (isFinal) {
      finals.push(transcript);
      interim = '';
      if (settle) settle();
    } else {
      interim = transcript;
    }
    onText(currentText());
  }

  async function start() {
    finals = [];
    interim = '';
    if (!listener) listener = await addPluginListener('stt', 'result', handleResult);
    await invoke('plugin:stt|start_listening', {
      config: { language: 'fr-FR', interimResults: true, continuous: true },
    });
  }

  async function stop() {
    // Stopping makes Android flush the current segment as a final result:
    // wait for it (bounded) so the end of the sentence isn't cut off.
    const lastFinal = new Promise((resolve) => {
      settle = resolve;
      setTimeout(resolve, settleMs);
    });
    await invoke('plugin:stt|stop_listening');
    if (interim) await lastFinal;
    settle = null;
    onDone(currentText());
  }

  return { start, stop };
}
