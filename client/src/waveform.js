/** Canvas audio waveform visualizer. Owns its own animation loop and analyser state. */
export function createWaveformRenderer(canvas) {
  const ctx = canvas.getContext('2d');
  let phase = 0;
  let listening = false;
  let analyser = null;
  let dataArray = null;

  function setListening(value) {
    listening = value;
  }

  function setAnalyser(newAnalyser, newDataArray) {
    analyser = newAnalyser;
    dataArray = newDataArray;
  }

  function draw() {
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    const numBars = 16;
    const barWidth = 3;
    const gap = 3.5;
    const startX = (width - (numBars * (barWidth + gap))) / 2;

    if (listening && dataArray && analyser) {
      analyser.getByteFrequencyData(dataArray);
    }

    for (let i = 0; i < numBars; i++) {
      let barHeight;
      if (listening) {
        if (dataArray && analyser) {
          const val = dataArray[i % dataArray.length] || 0;
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

      const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
      if (listening) {
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
    requestAnimationFrame(draw);
  }

  function start() {
    draw();
  }

  return { start, setListening, setAnalyser };
}
