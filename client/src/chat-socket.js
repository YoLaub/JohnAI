import { getServerConfig } from './config.js';

/** WebSocket connection to the JohnAi server, with an automatic reconnect loop. */
export function createChatSocket({ onOpen, onStatus, onStream, onDone, onError, onGenerateLocally }) {
  let ws = null;

  function connect() {
    try {
      ws = new WebSocket(getServerConfig().wsUrl);

      ws.onopen = () => {
        console.log("Connecté au serveur VPS JohnAi");
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

  return { connect, send };
}
