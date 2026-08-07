/** Local (on-device) speech-to-text via the Tauri Rust backend (whisper.cpp).
 *  Only available in the native desktop app — the Android PWA has no Tauri
 *  runtime and must keep using the server's /api/transcribe instead. */

export function isTauriRuntime() {
  return typeof window !== 'undefined' && !!window.__TAURI__;
}

async function decodeToMono16k(audioBlob) {
  const arrayBuffer = await audioBlob.arrayBuffer();
  const decodeCtx = new (window.AudioContext || window.webkitAudioContext)();
  const decoded = await decodeCtx.decodeAudioData(arrayBuffer);
  await decodeCtx.close();

  // Render through an OfflineAudioContext at 16kHz so the browser does the resampling
  // (whisper.cpp requires mono 16kHz PCM).
  const OfflineCtx = window.OfflineAudioContext || window.webkitOfflineAudioContext;
  const offline = new OfflineCtx(1, Math.ceil(decoded.duration * 16000), 16000);
  const source = offline.createBufferSource();
  source.buffer = decoded;
  source.connect(offline.destination);
  source.start();
  const rendered = await offline.startRendering();

  return rendered.getChannelData(0); // Float32Array, mono, 16kHz
}

export async function isLocalModelReady() {
  return window.__TAURI__.core.invoke('is_model_ready');
}

export async function downloadLocalModel(onProgress) {
  let unlisten = null;
  if (onProgress) {
    unlisten = await window.__TAURI__.event.listen('whisper-model-download-progress', (event) => {
      onProgress(event.payload);
    });
  }
  try {
    await window.__TAURI__.core.invoke('download_model');
  } finally {
    if (unlisten) unlisten();
  }
}

export async function transcribeLocally(audioBlob) {
  const samples = await decodeToMono16k(audioBlob);
  const text = await window.__TAURI__.core.invoke('transcribe_audio', {
    samples: Array.from(samples),
  });
  return text;
}
