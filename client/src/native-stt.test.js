import { describe, it, expect, vi } from 'vitest';
import { createNativeDictation } from './native-stt.js';

function setup() {
  let emit = null;
  const invoke = vi.fn(async () => {});
  const addPluginListener = vi.fn(async (plugin, event, handler) => {
    emit = handler;
    return { unregister: vi.fn() };
  });
  const onText = vi.fn();
  const onDone = vi.fn();
  const dictation = createNativeDictation({ invoke, addPluginListener, onText, onDone, settleMs: 20 });
  return { dictation, invoke, onText, onDone, emit: (r) => emit(r) };
}

describe('createNativeDictation', () => {
  it('starts the Android recognizer in French, continuous, with interim results', async () => {
    const { dictation, invoke } = setup();
    await dictation.start();
    expect(invoke).toHaveBeenCalledWith('plugin:stt|start_listening', {
      config: { language: 'fr-FR', interimResults: true, continuous: true },
    });
  });

  it('shows interim text live and accumulates final segments across pauses', async () => {
    const { dictation, emit, onText } = setup();
    await dictation.start();

    emit({ transcript: 'bonjour', isFinal: false });
    expect(onText).toHaveBeenLastCalledWith('bonjour');

    emit({ transcript: 'bonjour à tous', isFinal: true });
    emit({ transcript: 'deuxième', isFinal: false });
    expect(onText).toHaveBeenLastCalledWith('bonjour à tous deuxième');
  });

  it('on stop, waits for the last final result then delivers the whole note once', async () => {
    const { dictation, emit, invoke, onDone } = setup();
    await dictation.start();
    emit({ transcript: 'première phrase', isFinal: true });
    emit({ transcript: 'seconde', isFinal: false });

    const stopping = dictation.stop();
    expect(invoke).toHaveBeenCalledWith('plugin:stt|stop_listening');
    emit({ transcript: 'seconde phrase', isFinal: true });
    await stopping;

    expect(onDone).toHaveBeenCalledTimes(1);
    expect(onDone).toHaveBeenCalledWith('première phrase seconde phrase');
  });

  it('keeps the last interim text if no final result arrives after stop', async () => {
    const { dictation, emit, onDone } = setup();
    await dictation.start();
    emit({ transcript: 'coupé net', isFinal: false });
    await dictation.stop();
    expect(onDone).toHaveBeenCalledWith('coupé net');
  });

  it('starts each dictation from an empty note', async () => {
    const { dictation, emit, onDone } = setup();
    await dictation.start();
    emit({ transcript: 'note un', isFinal: true });
    await dictation.stop();

    await dictation.start();
    emit({ transcript: 'note deux', isFinal: true });
    await dictation.stop();
    expect(onDone).toHaveBeenLastCalledWith('note deux');
  });
});
