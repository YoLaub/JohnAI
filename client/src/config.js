// Server connection: must match the JohnAi server's API_KEY env var.
// TODO(sécurité): en dur pour l'instant. À sortir vers une vraie config
// (fichier local non commité / prefs Tauri) avant tout déploiement réel.
export const API_KEY = "Qp0ITDwMea7ONdMFinjtHPGwj5hWehZ9GojKSpXIUAk";
export const SERVER_HTTP_URL = "http://localhost:8000";
export const SERVER_WS_URL = `ws://localhost:8000/ws?api_key=${encodeURIComponent(API_KEY)}`;
