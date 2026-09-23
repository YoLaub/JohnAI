import { describe, it, expect, vi, afterEach } from 'vitest';
import { createAudioController } from './audio-recorder.js';

describe('createAudioController', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('never uses the browser SpeechRecognition API, even when available', () => {
    // Transcription is whisper.cpp (desktop) or Android's native recognizer:
    // a second, browser-level recognizer would send every note twice.
    const SpeechRecognition = vi.fn();
    vi.stubGlobal('webkitSpeechRecognition', SpeechRecognition);
    vi.stubGlobal('SpeechRecognition', SpeechRecognition);

    createAudioController({ waveform: { setListening() {} }, onAudioReady() {}, onPermissionDenied() {} });

    expect(SpeechRecognition).not.toHaveBeenCalled();
  });
});
