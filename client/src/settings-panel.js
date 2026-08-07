import { getServerConfig, saveServerConfig } from './config.js';

/** Wires the server settings panel (URL + API key per device, persisted in localStorage). */
export function createSettingsPanel({ panel, urlInput, keyInput, btnToggle, btnSave }) {
  function isOpen() {
    return !panel.classList.contains('hidden');
  }

  function open() {
    const { httpUrl, apiKey } = getServerConfig();
    urlInput.value = httpUrl;
    keyInput.value = apiKey;
    panel.classList.remove('hidden');
  }

  function close() {
    panel.classList.add('hidden');
  }

  function toggle() {
    if (isOpen()) {
      close();
    } else {
      open();
    }
  }

  function save() {
    saveServerConfig({
      httpUrl: urlInput.value.trim(),
      apiKey: keyInput.value.trim(),
    });
    // Simplest correct way to make every module (chat socket, api calls) pick up
    // the new config: reload rather than trying to make them reactive at runtime.
    window.location.reload();
  }

  btnToggle.addEventListener('click', toggle);
  btnSave.addEventListener('click', save);

  return { open, close, toggle };
}
