/* ==========================================================================
   JohnAi Desktop Widget - Interactive Client Script
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const widgetContainer = document.getElementById('widgetContainer');
  const pillBar = document.getElementById('pillBar');
  const dragOverlay = document.getElementById('dragOverlay');
  const waveformCanvas = document.getElementById('waveformCanvas');
  const statusDot = document.getElementById('statusDot');

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

  // View Mode Toggle (Compact Pill vs Full Dashboard)
  let isDashboardOpen = false;
  btnToggleView.addEventListener('click', async () => {
    isDashboardOpen = !isDashboardOpen;
    btnToggleView.classList.toggle('active', isDashboardOpen);
    mobileDashboard.classList.toggle('hidden', !isDashboardOpen);

    if (isDashboardOpen) {
      try {
        const res = await fetch('http://localhost:8000/api/memory/history');
        if (res.ok) {
          const data = await res.json();
          renderThoughtsHistory(data.history || []);
        }
      } catch (e) {
        console.warn("Erreur de récupération mémoire:", e);
      }
    }
  });

  function renderThoughtsHistory(history) {
    if (!history.length) {
      thoughtsList.innerHTML = `<div class="thought-card"><div class="thought-text">Aucune pensée enregistrée pour le moment.</div></div>`;
      return;
    }

    thoughtsList.innerHTML = history.slice(-8).reverse().map(item => `
      <div class="thought-card">
        <div class="thought-tag">${item.role === 'user' ? '📝 Pensée' : '✦ JohnAi'}</div>
        <div class="thought-text">${escapeHtml(item.content)}</div>
      </div>
    `).join('');
  }
  
  const responsePanel = document.getElementById('responsePanel');
  const responseContent = document.getElementById('responseContent');
  const btnCloseResponse = document.getElementById('btnCloseResponse');

  // App State
  let isListening = false;
  let attachedFiles = [];
  let isEditOpen = false;

  // 1. Audio Waveform Visualizer Animation (Canvas)
  const ctx = waveformCanvas.getContext('2d');
  let animationFrameId;
  let phase = 0;

  function drawWaveform() {
    const width = waveformCanvas.width;
    const height = waveformCanvas.height;
    ctx.clearRect(0, 0, width, height);

    const numBars = 16;
    const barWidth = 3;
    const gap = 3.5;
    const startX = (width - (numBars * (barWidth + gap))) / 2;

    if (isListening && micDataArray && analyser) {
      analyser.getByteFrequencyData(micDataArray);
    }

    for (let i = 0; i < numBars; i++) {
      let barHeight;
      if (isListening) {
        if (micDataArray && analyser) {
          const val = micDataArray[i % micDataArray.length] || 0;
          barHeight = Math.max(4, (val / 255) * 22);
        } else {
          const sinVal = Math.sin(phase + i * 0.45);
          const cosVal = Math.cos(phase * 0.8 + i * 0.2);
          barHeight = Math.max(4, Math.abs(sinVal + cosVal) * 9 + 4);
        }
      } else {
        barHeight = 4;
      }

      const x = startX + i * (barWidth + gap);
      const y = (height - barHeight) / 2;

      // Gradient color for each bar
      const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
      if (isListening) {
        gradient.addColorStop(0, '#a855f7'); // Neon Purple
        gradient.addColorStop(1, '#06b6d4'); // Neon Cyan
      } else {
        gradient.addColorStop(0, '#475569');
        gradient.addColorStop(1, '#334155');
      }

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.roundRect(x, y, barWidth, barHeight, 2);
      ctx.fill();
    }

    phase += 0.08;
    animationFrameId = requestAnimationFrame(drawWaveform);
  }

  drawWaveform();

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

    // Attach click listener for remove buttons
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
  const btnToggleMode = document.getElementById('btnToggleMode');
  const modeIcon = document.getElementById('modeIcon');
  const modeLabel = document.getElementById('modeLabel');

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
  let audioStream = null;
  let audioContext = null;
  let analyser = null;
  let microphoneSource = null;
  let micDataArray = null;
  let mediaRecorder = null;
  let audioChunks = [];
  let speechTranscribed = false;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;

  if (SpeechRecognition) {
    try {
      recognition = new SpeechRecognition();
      recognition.lang = 'fr-FR';
      recognition.continuous = true;
      recognition.interimResults = true;

      recognition.onresult = (event) => {
        let interim = '';
        let final = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            final += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }

        if (final) {
          speechTranscribed = true;
          promptInput.value = final;
          sendPrompt();
        } else if (interim) {
          promptInput.value = interim;
        }
      };

      recognition.onerror = (err) => {
        console.warn("Erreur SpeechRecognition:", err);
      };

      recognition.onend = () => {
        if (isListening && recognition) {
          try { recognition.start(); } catch (e) {}
        }
      };
    } catch (e) {
      console.warn("SpeechRecognition non supporté dans cet environnement", e);
    }
  }

  async function startMicrophone() {
    try {
      speechTranscribed = false;
      audioChunks = [];

      // Request mic permission explicitly from macOS / System
      audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Connect real mic to Web Audio API for waveform canvas animation
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 64;
      microphoneSource = audioContext.createMediaStreamSource(audioStream);
      microphoneSource.connect(analyser);
      micDataArray = new Uint8Array(analyser.frequencyBinCount);

      // MediaRecorder audio capture
      if (window.MediaRecorder) {
        mediaRecorder = new MediaRecorder(audioStream);
        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunks.push(e.data);
        };
        mediaRecorder.onstop = async () => {
          if (!speechTranscribed && audioChunks.length > 0) {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            await sendAudioForTranscription(audioBlob);
          }
        };
        mediaRecorder.start();
      }

      if (recognition) {
        try { recognition.start(); } catch (e) {}
      }
    } catch (err) {
      console.error("Accès microphone refusé ou non supporté:", err);
      alert("Permission microphone requise par macOS. Veuillez l'accorder dans Réglages Système > Confidentialité & Sécurité > Microphone.");
      stopMicrophone();
    }
  }

  async function sendAudioForTranscription(audioBlob) {
    const formData = new FormData();
    formData.append("file", audioBlob, "note_vocale.webm");

    responsePanel.classList.remove('hidden');
    responseContent.innerHTML = `<span style="color: #06b6d4;">Transcription de votre note vocale en cours...</span>`;

    try {
      const res = await fetch("http://localhost:8000/api/transcribe", {
        method: "POST",
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        const text = data.text || "Note vocale enregistrée";
        promptInput.value = text;
        sendPrompt();
      }
    } catch (e) {
      console.warn("Erreur transcription serveur:", e);
    }
  }

  function stopMicrophone() {
    isListening = false;
    btnMic.classList.remove('active');
    statusDot.classList.remove('active');

    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }

    if (recognition) {
      try { recognition.stop(); } catch (e) {}
    }

    if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop());
      audioStream = null;
    }

    if (audioContext) {
      audioContext.close();
      audioContext = null;
    }
  }

  btnMic.addEventListener('click', async () => {
    isListening = !isListening;
    btnMic.classList.toggle('active', isListening);
    statusDot.classList.toggle('active', isListening);

    if (isListening) {
      await startMicrophone();
    } else {
      stopMicrophone();
    }
  });

  // 6. Stop Action
  btnStop.addEventListener('click', () => {
    isListening = false;
    btnMic.classList.remove('active');
    statusDot.classList.remove('active');
    responsePanel.classList.add('hidden');
  });

  // 7. WebSocket Server Connection (FastAPI Backend)
  let ws;
  const WS_URL = "ws://localhost:8000/ws";

  function initWebSocket() {
    try {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log("Connecté au serveur VPS JohnAi");
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "status") {
          responsePanel.classList.remove('hidden');
          responseContent.innerHTML = `<span style="color: #06b6d4;">${escapeHtml(data.content)}</span>`;
        } else if (data.type === "stream" || data.type === "done") {
          responsePanel.classList.remove('hidden');
          const rawContent = data.chunk || data.full_text || "";
          if (window.marked) {
            responseContent.innerHTML = marked.parse(rawContent);
          } else {
            responseContent.innerHTML = escapeHtml(rawContent);
          }
        }
      };

      ws.onerror = (err) => {
        console.warn("WebSocket VPS indisponible, mode simulation activé", err);
      };

      ws.onclose = () => {
        setTimeout(initWebSocket, 5000); // Reconnect loop
      };
    } catch (e) {
      console.warn("WebSocket non supporté", e);
    }
  }

  initWebSocket();

  // 8. Send Prompt Action (Text Input)
  async function sendPrompt() {
    const text = promptInput.value.trim();
    if (!text && attachedFiles.length === 0) return;

    responsePanel.classList.remove('hidden');

    if (currentMode === 'note') {
      responseContent.innerHTML = `<span style="color: #10b981;">✓ Pensée enregistrée dans votre Journal de Pensées 📝</span>`;
    } else {
      responseContent.innerHTML = `<span style="color: #06b6d4;">Transmission à JohnAi...</span>`;
    }

    // Upload files if attached
    if (attachedFiles.length > 0) {
      for (const file of attachedFiles) {
        const formData = new FormData();
        formData.append("file", file);
        try {
          await fetch("http://localhost:8000/api/upload", {
            method: "POST",
            body: formData
          });
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
      newCard.innerHTML = `
        <div class="thought-tag">📝 Pensée récente</div>
        <div class="thought-text">${escapeHtml(text)}</div>
      `;
      thoughtsList.prepend(newCard);
      promptInput.value = '';
    }

    // Send via WebSocket if connected, otherwise fallback to simulation
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: "text",
        content: text,
        mode: currentMode,
        device_type: (window.innerWidth <= 600) ? "android" : "desktop",
        files: attachedFiles.map(f => f.name)
      }));
    } else {
      const fileSummary = attachedFiles.length ? ` (Fichiers joints: ${attachedFiles.map(f => f.name).join(', ')})` : '';
      setTimeout(() => {
        streamResponse(`JohnAi (Mode Local) : J'ai bien reçu "${escapeHtml(text)}"${fileSummary}.`);
      }, 500);
    }

    // Reset inputs
    promptInput.value = '';
  }

  btnSend.addEventListener('click', sendPrompt);

  promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendPrompt();
    }
  });

  btnCloseResponse.addEventListener('click', () => {
    responsePanel.classList.add('hidden');
  });

  // Streaming Text Simulation Helper
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

  function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function(m) {
      return {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
      }[m];
    });
  }
});
