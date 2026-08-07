# CLAUDE.md — Conventions du repo JohnAi

## Contexte
Assistant IA personnel omniprésent sous forme de pilule flottante (Floating Pill Widget),
multi-plateforme (macOS, Windows, Android), usage personnel exclusif de l'utilisateur.
**Priorité actuelle : stabiliser l'existant** (STT, sync mémoire, panels) avant d'ajouter
de nouvelles fonctionnalités — pas de scope créep tant que l'existant n'est pas fiable.

## Objectifs
1. Fiabiliser la capture audio/STT (cf. le fix récent sur la race condition MediaRecorder).
2. Fiabiliser la synchronisation mémoire multi-appareils (SQLite centralisé sur le VPS).
3. Nettoyer les artefacts UI/UX identifiés (panels, toasts, permissions macOS).
4. _à décider_ : nouvelles fonctionnalités, une fois l'existant stabilisé.

## Contraintes
- Usage personnel solo — pas de multi-tenant, pas de gestion d'utilisateurs.
- Mobile (Android/PWA) doit rester léger : le mode nomade route vers Gemini Cloud
  pour préserver la batterie, jamais vers les modèles locaux.
- macOS/Windows nécessitent les permissions natives (ex. `NSMicrophoneUsageDescription`
  dans `client/src-tauri`) — à vérifier à chaque changement touchant l'audio natif.
- **Toute route serveur non publique exige la clé API** (`API_KEY` côté serveur,
  header `X-API-Key` ou `?api_key=` pour le websocket) — voir Règles métier clés.
  Le client a `API_KEY = ""` en dur dans `client/src/config.js` (`_à décider_` : sortir
  vers une vraie config avant tout déploiement réel).

## Décisions techniques
- **Client** : Tauri 2.0 (Rust natif) + JS vanilla ESM, pas de framework front.
  `client/app.js` est la composition root (DOM refs, état applicatif, wiring des
  event listeners) — le comportement vit dans `client/src/` :
  - `config.js` : `API_KEY`, URLs serveur (HTTP + WS)
  - `api.js` : appels réseau (`fetchMemoryHistory`, `uploadFile`, `transcribeAudio`)
  - `chat-socket.js` : `createChatSocket()` — WebSocket + reconnect loop
  - `audio-recorder.js` : `createAudioController()` — micro, MediaRecorder, SpeechRecognition
  - `waveform.js` : `createWaveformRenderer()` — visualiseur canvas
  - `ui.js` : rendu (`renderThoughtsHistory`, `renderAssistantResponse`)
  - `utils.js` : `escapeHtml`
  - `index.html` charge `app.js` en `type="module"`. Build : `npm run build`
    (copie `app.js` + `src/*.js` vers `client/dist`, garder les deux en phase).
- **Serveur** : FastAPI + WebSockets, `server/main.py` orchestre seulement (routes +
  websocket) et délègue à :
  - `server/security.py` : `API_KEY`, `require_api_key`, `sanitize_filename`
  - `server/model_router.py` : `is_code_request`, `choose_model` (logique pure de
    sélection provider/modèle)
  - `server/providers.py` : `stream_from_gemini`, `stream_from_ollama`, `get_available_ollama_models`
  - `server/connection_manager.py` : `ConnectionManager`
  - `server/database.py` : mémoire SQLite
  - STT local via faster-whisper (chargé dans `main.py`, pas encore extrait).
  - Import : chaque module interne suit le pattern `try: from server.X import ...
    except ModuleNotFoundError: from X import ...` — le `Dockerfile` copie le contenu
    de `server/` à plat dans `/app` et lance `uvicorn main:app`, donc les deux formes
    d'import doivent rester valables.
- **Smart Model Router** : Gemma 3 12B (local, mode général) / Qwen 2.5 Coder 14B (local,
  mode code) / Gemini 2.5 Flash (cloud, mode mobile) — routing dans `server/main.py`.
- **Hébergement** : VPS via Docker Compose + Coolify (`server/docker-compose.yml`).

## Méthode
- **TDD** : tests écrits avant le code.
  - Serveur (`server/`) : **pytest**, tests dans `server/tests/` (`conftest.py` isole DB/API_KEY de test).
  - Client (`client/`) : **Vitest** + jsdom, tests colocalisés (`client/src/*.test.js`).
    Modules DOM-lourds (`audio-recorder.js`, `waveform.js`, `chat-socket.js`) non
    couverts par des tests unitaires — vérifiés manuellement via le skill `run`
    (navigateur réel + WebSocket vers un vrai serveur JohnAi).
- **Git** : commits directs sur `main`, pas de branche dev/feature (cohérent avec
  l'historique actuel, usage solo).
- **Autonomie** : valider à chaque étape avec l'utilisateur avant d'exécuter, en particulier
  pour tout ce qui touche au natif Tauri (permissions, `src-tauri/`) ou au déploiement VPS.

## Règles métier clés
- La mémoire canonique des pensées/notes vit dans `server/database.py` (SQLite côté VPS) —
  jamais de source de vérité locale divergente sur un device.
- Le choix du modèle (Gemma / Qwen / Gemini) est déterminé côté serveur par le Smart Router,
  jamais codé en dur côté client.
- Auth : `require_api_key` (dépendance FastAPI, `server/main.py`) protège `/api/memory/history`,
  `/api/upload`, `/api/transcribe` et `/ws`. `/api/health` reste public (monitoring).
  Sans `API_KEY` définie côté serveur, tout est refusé — jamais de mode "ouvert" par défaut.
- Upload : les noms de fichiers sont assainis par `sanitize_filename()` avant d'atteindre le
  disque (`server/main.py`) — ne jamais réutiliser `file.filename` brut dans un chemin.

## Commandes
- Serveur : `python3 -m pip install -r server/requirements.txt` puis
  `python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8000`
- Serveur tests : `python3 -m pytest server/tests` (depuis la racine du repo)
- Client dev : `cd client && npm install && npx @tauri-apps/cli dev`
- Client tests : `cd client && npm test`
- Build macOS/Windows : `cd client && npm run tauri build`
- Build Android : `cd client && npx tauri android build`

BRAIN: ~/brain/johnai

## Journal d'erreurs

Quand un bug non trivial est résolu, append une ligne à `$BRAIN/bag.ndjson` :

{"trigger":"", "symptom":"", "root_cause":"", "fix":"", "severity":1, "date":"YYYY-MM-DD"}

- `trigger` : les termes techniques exacts qui identifient le contexte
  ("relation polymorphe Strapi v5"), pas une description du bug.
  C'est la clé de regroupement.
- `severity` : 1 friction · 2 rework · 3 irréversible (perte de données,
  CI verte à tort, prod)
- Append only, jamais d'édition, une ligne par incident.

Si le `trigger` n'est pas formulable en termes techniques précis, le diagnostic
n'est pas terminé : le dire plutôt que de logger une entrée floue.
Un bug résolu par hasard ne se logge pas.
Si aucune ligne `BRAIN:` n'est présente dans ce CLAUDE.md, ne rien logger et le signaler.
