/* ==========================================================================
   JohnAi Desktop Widget - Entry point / composition root.
   Wiring only: DOM refs, event listeners and app state live here; behavior
   is implemented in client/src/*.js.
   ========================================================================== */
import { fetchMemoryHistory, transcribeAudio, uploadFile, setMessageCategory } from './src/api.js';
import { createChatSocket } from './src/chat-socket.js';
import { createWaveformRenderer } from './src/waveform.js';
import { createAudioController } from './src/audio-recorder.js';
import { renderThoughtsHistory, renderAssistantResponse } from './src/ui.js';
import { escapeHtml } from './src/utils.js';
import { createSettingsPanel } from './src/settings-panel.js';
import { createCategoryPicker } from './src/category-picker.js';
import { isTauriRuntime, isLocalModelReady, downloadLocalModel, transcribeLocally } from './src/local-stt.js';
import { startWindowAutoFit } from './src/window-fit.js';

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const widgetContainer = document.getElementById('widgetContainer');
  const pillBar = document.getElementById('pillBar');
  const dragOverlay = document.getElementById('dragOverlay');
  const waveformCanvas = document.getElementById('waveformCanvas');
  const statusDot = document.getElementById('statusDot');
  const btnAttach = document.getElementById('btnAttach');
  const btnToggleEdit = document.getElementById('btnToggleEdit');
  const btnToggleView = document.getElementById('btnToggleView');
  const btnMic = document.getElementById('btnMic');
  const fileInput = document.getElementById('fileInput');
  const attachmentBar = document.getElementById('attachmentBar');
  const attachmentList = document.getElementById('attachmentList');
  const editPanel = document.getElementById('editPanel');
  const mobileDashboard = document.getElementById('mobileDashboard');
  const thoughtsList = document.getElementById('thoughtsList');
  const promptInput = document.getElementById('promptInput');
  const btnSend = document.getElementById('btnSend');
  const responsePanel = document.getElementById('responsePanel');
  const responseContent = document.getElementById('responseContent');
  const btnCloseResponse = document.getElementById('btnCloseResponse');
  const btnToggleMode = document.getElementById('btnToggleMode');
  const modeIcon = document.getElementById('modeIcon');
  const modeLabel = document.getElementById('modeLabel');
  const btnCloseApp = document.getElementById('btnCloseApp');
  const btnSettings = document.getElementById('btnSettings');
  const settingsPanel = document.getElementById('settingsPanel');
  const settingsServerUrl = document.getElementById('settingsServerUrl');
  const settingsApiKey = document.getElementById('settingsApiKey');
  const btnSaveSettings = document.getElementById('btnSaveSettings');
  const btnCategory = document.getElementById('btnCategory');
  const categoryLabel = document.getElementById('categoryLabel');
  const categoryPanel = document.getElementById('categoryPanel');
  const categoryChipList = document.getElementById('categoryChipList');
  const newCategoryInput = document.getElementById('newCategoryInput');
  const btnAddCategory = document.getElementById('btnAddCategory');

  createSettingsPanel({
    panel: settingsPanel,
    urlInput: settingsServerUrl,
    keyInput: settingsApiKey,
    btnToggle: btnSettings,
    btnSave: btnSaveSettings,
  });

  // Category selector: applies to the next note/message sent, remembered
  // across restarts. Also reused by the journal to reclassify past notes.
  const categoryPicker = createCategoryPicker({
    panel: categoryPanel,
    chipListContainer: categoryChipList,
    newCategoryInput,
    btnAddCategory,
  });

  let currentCategory = localStorage.getItem('johnai.current-category') || '';
  categoryLabel.textContent = currentCategory || 'Non classé';

  btnCategory.addEventListener('click', () => {
    categoryPicker.toggle(currentCategory, (selected) => {
      currentCategory = selected;
      categoryLabel.textContent = selected || 'Non classé';
      localStorage.setItem('johnai.current-category', selected);
    });
  });

  // Native Tauri Window Dragging on Mouse Down
  function triggerWindowDrag() {
    try {
      if (window.__TAURI_INTERNALS__ && window.__TAURI_INTERNALS__.invoke) {
        window.__TAURI_INTERNALS__.invoke("plugin:window|start_dragging");
      } else if (window.__TAURI__ && window.__TAURI__.window) {
        window.__TAURI__.window.getCurrentWindow().startDragging();
      }
    } catch (err) {
      console.warn("Tauri drag error:", err);
    }
  }

  pillBar.addEventListener('mousedown', (e) => {
    if (e.target.closest('button, input, textarea, .action-buttons, .icon-btn')) return;
    triggerWindowDrag();
  });

  // View Mode Toggle (Compact Pill vs Full Dashboard)
  let isDashboardOpen = false;

  async function openDashboard() {
    isDashboardOpen = true;
    btnToggleView.classList.add('active');
    mobileDashboard.classList.remove('hidden');
    try {
      const data = await fetchMemoryHistory();
      renderThoughtsHistory(thoughtsList, data.history || []);
    } catch (e) {
      console.warn("Erreur de récupération mémoire:", e);
      thoughtsList.innerHTML = `<div class="thought-card"><div class="thought-text" style="color:#ef4444;">⚠️ ${escapeHtml(e.message)}</div></div>`;
    }
  }

  function closeDashboard() {
    isDashboardOpen = false;
    btnToggleView.classList.remove('active');
    mobileDashboard.classList.add('hidden');
  }

  // Post-hoc reclassification: tap a note's category badge in the journal.
  thoughtsList.addEventListener('click', (e) => {
    const badge = e.target.closest('.thought-category-badge[data-message-id]');
    if (!badge) return;
    e.stopPropagation();
    const messageId = badge.getAttribute('data-message-id');
    const current = badge.getAttribute('data-current-category') || '';
    categoryPicker.toggle(current, async (selected) => {
      try {
        await setMessageCategory(messageId, selected);
        await openDashboard();
      } catch (err) {
        console.warn("Erreur reclassement de la note:", err);
      }
    });
  });

  btnToggleView.addEventListener('click', () => {
    if (isDashboardOpen) {
      closeDashboard();
    } else {
      openDashboard();
    }
  });

  // Mobile (portrait or landscape phone): the notes journal fills the screen
  // by default instead of waiting for a toggle tap — this is the "note-taking
  // widget" surface, not a hidden panel.
  // Must match styles.css's breakpoint exactly: pointer type, not viewport
  // size — a short *desktop* window (collapsed pill) isn't "mobile", and a
  // width/height threshold can't tell the difference. See styles.css comment.
  const isMobileLayout = () => window.matchMedia('(pointer: coarse)').matches;
  if (isMobileLayout()) {
    openDashboard();
  }

  // Same for the mic button: relocate it (same DOM node, same listeners — no
  // duplication) into a large dedicated tap target below the pill on mobile,
  // instead of leaving it as one small icon among six.
  const micLauncherRow = document.getElementById('micLauncherRow');
  function relocateMicForLayout() {
    if (!micLauncherRow) return;
    if (isMobileLayout()) {
      if (btnMic.parentElement !== micLauncherRow) micLauncherRow.appendChild(btnMic);
    } else if (btnMic.parentElement === micLauncherRow) {
      btnSettings.parentElement.insertBefore(btnMic, btnSettings);
    }
  }
  relocateMicForLayout();
  window.addEventListener('resize', relocateMicForLayout);

  // Desktop only: Android is fullscreen, resizing the window there is meaningless.
  if (!isMobileLayout()) {
    startWindowAutoFit(widgetContainer);
  }

  // App State
  let attachedFiles = [];
  let isEditOpen = false;

  // 1. Audio Waveform Visualizer Animation (Canvas)
  const waveform = createWaveformRenderer(waveformCanvas);
  waveform.start();

  // 2. Toggle Text Input Panel (Pencil Button ✏️)
  btnToggleEdit.addEventListener('click', () => {
    isEditOpen = !isEditOpen;
    btnToggleEdit.classList.toggle('active', isEditOpen);
    editPanel.classList.toggle('hidden', !isEditOpen);

    if (isEditOpen) {
      promptInput.focus();
    }
  });

  // 3. Document Attachment (+ Button)
  btnAttach.addEventListener('click', () => {
    fileInput.click();
  });

  fileInput.addEventListener('change', (e) => {
    handleFiles(Array.from(e.target.files));
  });

  // 4. Drag & Drop Handling
  ['dragenter', 'dragover'].forEach(eventName => {
    widgetContainer.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dragOverlay.classList.add('active');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dragOverlay.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dragOverlay.classList.remove('active');
    }, false);
  });

  dragOverlay.addEventListener('drop', (e) => {
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  });

  function handleFiles(files) {
    if (!files.length) return;

    files.forEach(file => {
      if (!attachedFiles.some(f => f.name === file.name)) {
        attachedFiles.push(file);
      }
    });

    renderAttachments();
  }

  function renderAttachments() {
    if (attachedFiles.length === 0) {
      attachmentBar.classList.add('hidden');
      attachmentList.innerHTML = '';
      return;
    }

    attachmentBar.classList.remove('hidden');
    attachmentList.innerHTML = attachedFiles.map((file, index) => `
      <div class="chip">
        📄 ${escapeHtml(file.name)}
        <span class="chip-remove" data-index="${index}">&times;</span>
      </div>
    `).join('');

    document.querySelectorAll('.chip-remove').forEach(el => {
      el.addEventListener('click', (e) => {
        const idx = parseInt(e.target.getAttribute('data-index'), 10);
        attachedFiles.splice(idx, 1);
        renderAttachments();
      });
    });
  }

  // Mode State (Note vs Chat)
  let currentMode = 'note'; // 'note' or 'chat'
  btnToggleMode.addEventListener('click', () => {
    currentMode = (currentMode === 'note') ? 'chat' : 'note';
    if (currentMode === 'chat') {
      modeIcon.textContent = '💬';
      modeLabel.textContent = 'Chat';
      btnToggleMode.classList.add('chat-mode');
    } else {
      modeIcon.textContent = '📝';
      modeLabel.textContent = 'Note';
      btnToggleMode.classList.remove('chat-mode');
    }
  });

  // 5. Real Microphone Capture, MediaRecorder & Speech-to-Text
  const audioController = createAudioController({
    waveform,
    onFinalTranscript: (text) => {
      promptInput.value = text;
      sendPrompt();
    },
    onInterimTranscript: (text) => {
      promptInput.value = text;
    },
    onAudioReady: async (audioBlob) => {
      responsePanel.classList.remove('hidden');

      if (!audioBlob || audioBlob.size < 100) {
        responseContent.innerHTML = `<span style="color: #f59e0b;">⚠️ Enregistrement trop court, rien n'a été transcrit.</span>`;
        return;
      }

      // Prefer on-device Whisper (whisper.cpp via Tauri) when available: no network
      // round-trip, uses the Mac's own hardware. Falls back to the server otherwise
      // (Android PWA has no Tauri runtime, or local transcription failed).
      if (isTauriRuntime()) {
        try {
          if (!(await isLocalModelReady())) {
            responseContent.innerHTML = `<span style="color: #06b6d4;">Téléchargement du modèle Whisper local (une seule fois)...</span>`;
            await downloadLocalModel((progress) => {
              if (progress.total > 0) {
                const pct = Math.round((progress.downloaded / progress.total) * 100);
                responseContent.innerHTML = `<span style="color: #06b6d4;">Téléchargement du modèle Whisper local... ${pct}%</span>`;
              }
            });
          }

          responseContent.innerHTML = `<span style="color: #06b6d4;">Transcription locale en cours...</span>`;
          const localText = await transcribeLocally(audioBlob);
          if (localText) {
            await sendPrompt(localText);
            return;
          }
          console.warn("Transcription locale vide, repli sur le serveur");
        } catch (e) {
          console.warn("Échec transcription locale, repli sur le serveur:", e);
        }
      }

      responseContent.innerHTML = `<span style="color: #06b6d4;">Transcription de votre note vocale en cours...</span>`;

      try {
        const data = await transcribeAudio(audioBlob);
        const text = data && data.text || "";
        if (text) {
          await sendPrompt(text);
        } else {
          responseContent.innerHTML = `<span style="color: #f59e0b;">⚠️ Le serveur n'a renvoyé aucun texte transcrit.</span>`;
        }
      } catch (e) {
        console.warn("Erreur transcription serveur:", e);
        responseContent.innerHTML = `<span style="color: #ef4444;">❌ Échec de la transcription : ${escapeHtml(e.message)}</span>`;
      }
    },
    onPermissionDenied: () => {
      alert("Permission microphone requise. Accordez-la dans les réglages de votre appareil (Confidentialité/Autorisations > Microphone) pour JohnAi.");
    }
  });

  btnMic.addEventListener('click', async () => {
    const nowListening = !audioController.isListening();
    btnMic.classList.toggle('active', nowListening);
    statusDot.classList.toggle('active', nowListening);

    if (nowListening) {
      await audioController.start();
    } else {
      audioController.stop();
    }
  });

  // 6. WebSocket Server Connection (FastAPI Backend)
  const chatSocket = createChatSocket({
    onStatus: (content) => {
      responsePanel.classList.remove('hidden');
      responseContent.innerHTML = `<span style="color: #06b6d4;">${escapeHtml(content)}</span>`;
    },
    onStream: (chunk) => {
      responsePanel.classList.remove('hidden');
      renderAssistantResponse(responseContent, chunk);
    },
    onDone: (fullText) => {
      responsePanel.classList.remove('hidden');
      renderAssistantResponse(responseContent, fullText);
    }
  });
  chatSocket.connect();

  if (btnCloseApp) {
    btnCloseApp.addEventListener('click', () => {
      responsePanel.classList.add('hidden');
      if (editPanel) editPanel.classList.add('hidden');
      if (mobileDashboard) mobileDashboard.classList.add('hidden');
      if (window.__TAURI_INTERNALS__) {
        try { window.__TAURI_INTERNALS__.invoke('plugin:window|hide'); } catch (e) {}
      }
    });
  }

  let responseAutoCloseTimer = null;

  // 7. Send Prompt Action (Text Input or Voice Transcription)
  async function sendPrompt(overrideText) {
    const text = (typeof overrideText === 'string') ? overrideText.trim() : promptInput.value.trim();
    if (!text && attachedFiles.length === 0) return;

    if (responseAutoCloseTimer) {
      clearTimeout(responseAutoCloseTimer);
      responseAutoCloseTimer = null;
    }

    responsePanel.classList.remove('hidden');

    if (currentMode === 'note') {
      responseContent.innerHTML = `<span style="color: #10b981; font-weight: 600;">✓ Pensée enregistrée dans votre Journal de Pensées 📝</span>`;
      // Auto-close confirmation popup after 2.5s
      responseAutoCloseTimer = setTimeout(() => {
        responsePanel.classList.add('hidden');
      }, 2500);
    } else {
      responseContent.innerHTML = `<span style="color: #06b6d4;">Transmission à JohnAi...</span>`;
    }

    // Upload files if attached
    if (attachedFiles.length > 0) {
      for (const file of attachedFiles) {
        try {
          await uploadFile(file);
        } catch (e) {
          console.warn("Erreur d'upload vers le VPS:", e);
        }
      }
    }

    // If in Mode Note, immediately prepend note to Journal de Pensées UI
    if (currentMode === 'note' && text && thoughtsList) {
      if (thoughtsList.innerText.includes('Aucune pensée')) {
        thoughtsList.innerHTML = '';
      }
      const newCard = document.createElement('div');
      newCard.className = 'thought-card';
      const categoryBadgeHtml = currentCategory
        ? `<span class="thought-category-badge">${escapeHtml(currentCategory)}</span>`
        : '';
      newCard.innerHTML = `
        <div class="thought-tag">
          <span>📝 Pensée récente</span>
          ${categoryBadgeHtml}
        </div>
        <div class="thought-text">${escapeHtml(text)}</div>
      `;
      thoughtsList.prepend(newCard);
    }

    // Send via WebSocket if connected, otherwise fallback to simulation
    const sent = chatSocket.send({
      type: "text",
      content: text,
      mode: currentMode,
      device_type: (window.innerWidth <= 600) ? "android" : "desktop",
      files: attachedFiles.map(f => f.name),
      category: currentCategory
    });

    if (!sent) {
      const fileSummary = attachedFiles.length ? ` (Fichiers joints: ${attachedFiles.map(f => f.name).join(', ')})` : '';
      if (currentMode !== 'note') {
        setTimeout(() => {
          streamResponse(`JohnAi (Mode Local) : J'ai bien reçu "${escapeHtml(text)}"${fileSummary}.`);
        }, 500);
      }
    }

    // Reset inputs
    promptInput.value = '';
    attachedFiles = [];
    if (attachmentBar) attachmentBar.classList.add('hidden');
  }

  btnSend.addEventListener('click', sendPrompt);

  promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendPrompt();
    }
  });

  btnCloseResponse.addEventListener('click', () => {
    if (responseAutoCloseTimer) clearTimeout(responseAutoCloseTimer);
    responsePanel.classList.add('hidden');
  });

  // Streaming Text Simulation Helper (offline fallback when the websocket is down)
  function streamResponse(fullText) {
    responseContent.innerHTML = '';
    let i = 0;
    const interval = setInterval(() => {
      if (i < fullText.length) {
        responseContent.innerHTML += fullText.charAt(i);
        i++;
      } else {
        clearInterval(interval);
      }
    }, 25);
  }
});
