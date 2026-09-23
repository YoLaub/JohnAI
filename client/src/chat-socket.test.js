import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createChatSocket } from './chat-socket.js';

const QUEUE_KEY = 'johnai.pending-notes';

class FakeWebSocket {
  static OPEN = 1;
  static instances = [];
  constructor(url) {
    this.url = url;
    this.readyState = 0;
    this.sent = [];
    FakeWebSocket.instances.push(this);
  }
  send(data) { this.sent.push(JSON.parse(data)); }
  open() { this.readyState = FakeWebSocket.OPEN; this.onopen && this.onopen(); }
}

function createSocket() {
  const socket = createChatSocket({ onStatus() {}, onStream() {}, onDone() {} });
  socket.connect();
  return { socket, ws: FakeWebSocket.instances.at(-1) };
}

describe('createChatSocket — notes while disconnected', () => {
  beforeEach(() => {
    localStorage.clear();
    FakeWebSocket.instances = [];
    vi.stubGlobal('WebSocket', FakeWebSocket);
  });

  it('sends a note immediately when the socket is open', () => {
    const { socket, ws } = createSocket();
    ws.open();
    expect(socket.sendOrQueue({ type: 'text', content: 'a' })).toBe(true);
    expect(ws.sent).toEqual([{ type: 'text', content: 'a' }]);
  });

  it('queues a note while disconnected and flushes it once connected', () => {
    const { socket, ws } = createSocket();
    expect(socket.sendOrQueue({ type: 'text', content: 'a' })).toBe(false);
    expect(ws.sent).toEqual([]);

    ws.open();
    expect(ws.sent).toEqual([{ type: 'text', content: 'a' }]);
    expect(JSON.parse(localStorage.getItem(QUEUE_KEY))).toEqual([]);
  });

  it('keeps queued notes across an app restart', () => {
    const first = createSocket();
    first.socket.sendOrQueue({ type: 'text', content: 'a' });

    const second = createSocket();
    second.ws.open();
    expect(second.ws.sent).toEqual([{ type: 'text', content: 'a' }]);
  });
});
