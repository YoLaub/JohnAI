/**
 * Owns microphone capture: Web Audio analyser (for the waveform) and
 * MediaRecorder (audio handed to onAudioReady for Whisper transcription).
 * Deliberately no browser SpeechRecognition: it would transcribe the same
 * note a second time alongside Whisper.
 */
export function createAudioController({ waveform, onAudioReady, onPermissionDenied }) {
  let audioStream = null;
  let audioContext = null;
  let analyser = null;
  let microphoneSource = null;
  let micDataArray = null;
  let mediaRecorder = null;
  let audioChunks = [];
  let listening = false;

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
    } catch (err) {
      console.error("Accès microphone refusé ou non supporté:", err);
      onPermissionDenied(err);
      stop();
    }
  }

  function stop() {
    listening = false;
    waveform.setListening(false);

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
