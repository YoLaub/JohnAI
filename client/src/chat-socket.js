import { getServerConfig } from './config.js';

// Notes typed/dictated while the socket is down (e.g. Android just resumed the
// app from the background) wait here until the next successful connection.
// Persisted so an app kill before reconnecting doesn't lose them either.
const QUEUE_KEY = 'johnai.pending-notes';

function readQueue() {
  try {
    return JSON.parse(localStorage.getItem(QUEUE_KEY)) || [];
  } catch (e) {
    return [];
  }
}

function writeQueue(queue) {
  localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
}

/** WebSocket connection to the JohnAi server, with an automatic reconnect loop. */
export function createChatSocket({ onOpen, onStatus, onStream, onDone, onError, onGenerateLocally }) {
  let ws = null;

  function connect() {
    try {
      ws = new WebSocket(getServerConfig().wsUrl);

      ws.onopen = () => {
        console.log("Connecté au serveur VPS JohnAi");
        flushQueue();
        if (onOpen) onOpen();
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "status") {
          onStatus(data.content);
        } else if (data.type === "stream") {
          onStream(data.chunk || "");
        } else if (data.type === "done") {
          onDone(data.full_text || "");
        } else if (data.type === "generate_locally") {
          if (onGenerateLocally) onGenerateLocally(data.messages || []);
        }
      };

      ws.onerror = (err) => {
        console.warn("WebSocket VPS indisponible, mode simulation activé", err);
        if (onError) onError(err);
      };

      ws.onclose = () => {
        setTimeout(connect, 5000); // Reconnect loop
      };
    } catch (e) {
      console.warn("WebSocket non supporté", e);
    }
  }

  function send(payload) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(payload));
      return true;
    }
    return false;
  }

  function flushQueue() {
    const queue = readQueue();
    if (queue.length === 0) return;
    for (const payload of queue) ws.send(JSON.stringify(payload));
    writeQueue([]);
  }

  /** Like send(), but a payload that can't go out now is kept and delivered
   *  on the next connection instead of being dropped. Returns true if sent now. */
  function sendOrQueue(payload) {
    if (send(payload)) return true;
    writeQueue([...readQueue(), payload]);
    return false;
  }

  return { connect, send, sendOrQueue };
}
