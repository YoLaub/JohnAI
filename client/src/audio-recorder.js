/**
 * Owns microphone capture: Web Audio analyser (for the waveform), MediaRecorder
 * (server-side Whisper transcription) and the browser's SpeechRecognition API
 * (instant local transcription) when available.
 */
export function createAudioController({ waveform, onFinalTranscript, onInterimTranscript, onAudioReady, onPermissionDenied }) {
  let audioStream = null;
  let audioContext = null;
  let analyser = null;
  let microphoneSource = null;
  let micDataArray = null;
  let mediaRecorder = null;
  let audioChunks = [];
  let listening = false;

  const SpeechRecognitionImpl = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;

  if (SpeechRecognitionImpl) {
    try {
      recognition = new SpeechRecognitionImpl();
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
          onFinalTranscript(final);
        } else if (interim) {
          onInterimTranscript(interim);
        }
      };

      recognition.onerror = (err) => {
        console.warn("Erreur SpeechRecognition:", err);
      };

      recognition.onend = () => {
        if (listening && recognition) {
          try { recognition.start(); } catch (e) {}
        }
      };
    } catch (e) {
      console.warn("SpeechRecognition non supporté dans cet environnement", e);
    }
  }

  async function start() {
    listening = true;
    waveform.setListening(true);

    try {
      audioChunks = [];

      // Request mic with WebRTC Audio Processing (noise suppression, echo cancellation, AGC)
      audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          noiseSuppression: true,
          echoCancellation: true,
          autoGainControl: true,
          channelCount: 1,
          sampleRate: 16000
        }
      });

      // Connect real mic to Web Audio API for waveform canvas animation
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 64;
      microphoneSource = audioContext.createMediaStreamSource(audioStream);
      microphoneSource.connect(analyser);
      micDataArray = new Uint8Array(analyser.frequencyBinCount);
      waveform.setAnalyser(analyser, micDataArray);

      if (window.MediaRecorder) {
        mediaRecorder = new MediaRecorder(audioStream);
        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunks.push(e.data);
        };
        mediaRecorder.onstop = async () => {
          const chunksToProcess = [...audioChunks];
          audioChunks = [];

          // Safely stop stream tracks AFTER recording stops
          if (audioStream) {
            audioStream.getTracks().forEach(track => track.stop());
            audioStream = null;
          }

          if (chunksToProcess.length > 0) {
            const audioBlob = new Blob(chunksToProcess, { type: 'audio/webm' });
            await onAudioReady(audioBlob);
          }
        };
        mediaRecorder.start(100); // Slices data every 100ms
      }

      if (recognition) {
        try { recognition.start(); } catch (e) {}
      }
    } catch (err) {
      console.error("Accès microphone refusé ou non supporté:", err);
      onPermissionDenied(err);
      stop();
    }
  }

  function stop() {
    listening = false;
    waveform.setListening(false);

    if (recognition) {
      try { recognition.stop(); } catch (e) {}
    }

    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    } else if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop());
      audioStream = null;
    }

    if (audioContext) {
      audioContext.close();
      audioContext = null;
    }
  }

  return { start, stop, isListening: () => listening };
}
