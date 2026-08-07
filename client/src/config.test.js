import { describe, it, expect, beforeEach } from 'vitest';
import { getServerConfig, saveServerConfig } from './config.js';

describe('server config (localStorage-backed)', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('falls back to the default server URL and an empty API key when nothing is stored', () => {
    const { httpUrl, apiKey } = getServerConfig();
    expect(httpUrl).toBe('https://johnai.john-world.store');
    expect(apiKey).toBe('');
  });

  it('persists and returns a saved config', () => {
    saveServerConfig({ httpUrl: 'https://example.test', apiKey: 'secret123' });
    const { httpUrl, apiKey } = getServerConfig();
    expect(httpUrl).toBe('https://example.test');
    expect(apiKey).toBe('secret123');
  });

  it('derives a wss:// URL from an https:// server URL, with the api_key query param', () => {
    saveServerConfig({ httpUrl: 'https://example.test', apiKey: 'secret123' });
    const { wsUrl } = getServerConfig();
    expect(wsUrl).toBe('wss://example.test/ws?api_key=secret123');
  });

  it('derives a ws:// URL from a plain http:// server URL', () => {
    saveServerConfig({ httpUrl: 'http://localhost:8000', apiKey: '' });
    const { wsUrl } = getServerConfig();
    expect(wsUrl).toBe('ws://localhost:8000/ws?api_key=');
  });
});
