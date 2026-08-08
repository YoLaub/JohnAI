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
  **Ne plus jamais mettre de vraie clé en dur dans `client/src/config.js`** : le repo
  GitHub (`YoLaub/JohnAI`) est **public**, une clé y a déjà fuité par le passé (incident
  du 2026-08-07, clé rotée depuis) et reste visible dans l'historique git pour toujours.
  La config réelle (URL serveur + clé API) vit exclusivement dans `localStorage`, réglée
  par appareil via le panneau réglages (`client/src/settings-panel.js`) — jamais commitée.
  Client et serveur doivent avoir la même clé, sinon toute route protégée échoue en 401
  silencieusement côté fetch (voir Journal d'erreurs) — le panneau réglages n'empêche pas
  une faute de frappe, à vérifier en cas de 401 inattendu.

## Décisions techniques
- **Client** : Tauri 2.0 (Rust natif) + JS vanilla ESM, pas de framework front.
  `client/app.js` est la composition root (DOM refs, état applicatif, wiring des
  event listeners) — le comportement vit dans `client/src/` :
  - `config.js` : `getServerConfig()`/`saveServerConfig()` — URL serveur + clé API lues
    depuis `localStorage` (clé `johnai.server-config`), défaut = `https://johnai.john-world.store`
    avec `apiKey: ""`. Aucune valeur secrète en dur ici (voir Contraintes).
  - `settings-panel.js` : `createSettingsPanel()` — panneau réglages (bouton engrenage),
    sauvegarde en localStorage puis `location.reload()` (pas de réactivité runtime,
    volontairement simple).
  - `api.js` : appels réseau (`fetchMemoryHistory`, `uploadFile`, `transcribeAudio`),
    lit `getServerConfig()` à chaque appel (jamais une valeur figée à l'import).
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
  - `server/memory_facts.py` : détection des commandes "retiens que" / "oublie que"
  - `server/database.py` : mémoire SQLite (historique + faits durables)
  - STT serveur via faster-whisper (chargé dans `main.py`) — **fallback** pour la PWA
    Android servie via navigateur, et pour l'APK Android (whisper-rs exclu de ce
    target, voir ci-dessous), ou si la transcription locale échoue sur desktop.
- **STT local (prioritaire sur Mac/Windows uniquement)** : `client/src-tauri/src/whisper_stt.rs`
  (whisper-rs/whisper.cpp, Metal+CoreML sur macOS) + `client/src/local-stt.js`
  (décodage audio → PCM mono 16kHz via Web Audio API, puis commande Tauri
  `transcribe_audio`). Modèle `ggml-small.bin` téléchargé une fois au premier usage
  dans le dossier de données de l'app (pas embarqué dans l'installeur). `app.js`
  tente le local en premier si `window.__TAURI__` existe, retombe sur le serveur
  sinon. Choisi plutôt qu'un sidecar Python (faster-whisper local) car ça compile
  directement dans le binaire Tauri existant — pas de process à gérer/lancer.
  **`whisper-rs` est exclu du build Android** (`Cargo.toml`,
  `cfg(not(target_os = "android"))`) : `whisper-rs-sys` 0.15 lie `ggml-blas`
  dès que `cfg!(target_os = "macos")` est vrai dans son `build.rs` — qui reflète
  l'OS de la machine qui compile, pas la cible, donc ça casse le cross-compile
  macOS→Android. Bug amont, pas une régression à corriger ici.
- **Structure crate Tauri (`client/src-tauri/`)** : `src/lib.rs` contient le
  `tauri::Builder` (fonction `run()`, taguée `#[cfg_attr(mobile, tauri::mobile_entry_point)]`) ;
  `src/main.rs` ne fait qu'appeler `johnai_desktop_lib::run()`. Obligatoire pour Android
  (chargé via JNI dans une lib partagée, pas un binaire) — ne jamais remettre toute la
  logique dans `main.rs` seul, ça casse `tauri android build`.
  _Non encore validé avec un vrai micro_ (contrainte de l'environnement de dev) —
  à tester en conditions réelles.
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
  Sans `API_KEY` définie côté serveur (vide compris), tout est refusé — jamais de mode
  "ouvert" par défaut. Config locale : `server/.env` (copié depuis `server/.env.example`,
  jamais commité — voir `.gitignore`), chargé par `python-dotenv` en tout premier dans
  `server/main.py`, avant les imports internes qui lisent `os.getenv()` à l'import.
- Upload : les noms de fichiers sont assainis par `sanitize_filename()` avant d'atteindre le
  disque (`server/main.py`) — ne jamais réutiliser `file.filename` brut dans un chemin.
- Faits durables (`long_term_memory`, au-delà de la fenêtre glissante des 20 derniers
  messages) : déclenchement par phrase-clé déterministe (`server/memory_facts.py`,
  jamais de tool-calling LLM) — "retiens que ..." / "souviens-toi que ..." / "n'oublie
  pas que ..." mémorise (une nouvelle entrée à chaque fois, pas d'upsert par clé —
  `add_memory_fact()`), "oublie que ..." / "efface que ..." supprime les faits dont la
  valeur contient le texte donné (`delete_memory_facts_matching()`, substring
  case-insensitive). Ces commandes court-circuitent Mode Note/Chat et priment dessus.
  Tous les faits mémorisés sont injectés dans le system prompt à chaque génération
  (`get_all_memory_facts()` dans `server/main.py`).
- Catégorisation des notes (`conversation_history.category`, table `categories` —
  Famille/R&D/Évolution personnelle/Philo/Projet par défaut, création libre partout,
  idempotente insensible à la casse) : trois chemins, tous convergent vers
  `create_category()` + `set_message_category()`/`set_category_for_last_message()`
  dans `server/database.py`.
  1. Présélection : bouton catégorie client (à côté du toggle Note/Chat), la valeur
     part dans le payload WS (`category`), mémorisée par appareil (localStorage).
  2. Vocal déterministe (`server/categorization.py`, même style que memory_facts.py) :
     "mets ça dans X" / "classe cette note dans X" / "range ça dans X" / "catégorise
     ça dans X" — **vérifié avant** `save_message()` : la commande elle-même ne doit
     jamais devenir une ligne de conversation_history, sinon elle se catégoriserait
     elle-même au lieu de la pensée précédente.
  3. A posteriori : badge cliquable sur chaque carte du journal (`client/src/ui.js`),
     `PATCH /api/memory/{id}/category` (catégorie vide = déclasse vers Non classé,
     ce n'est pas une erreur).

## Commandes
- Serveur : `cp server/.env.example server/.env` (une fois, puis remplir `API_KEY`) puis
  `python3 -m pip install -r server/requirements.txt` puis
  `python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8000`
- Serveur tests : `python3 -m pytest server/tests` (depuis la racine du repo)
- Client dev : `cd client && npm install && npx @tauri-apps/cli dev`
- Client tests : `cd client && npm test`
- Build macOS/Windows : `cd client && npm run tauri build`
- Build Android : nécessite Android Studio + SDK + NDK installés, et un JDK 17-21
  (**pas** le JBR d'Android Studio si trop récent — Gradle 8.14.3 ne supporte pas Java 25 ;
  `brew install openjdk@21` sans sudo fonctionne). Avant de lancer, exporter dans le shell :
  ```
  export ANDROID_HOME="$HOME/Library/Android/sdk"
  export NDK_HOME="$ANDROID_HOME/ndk/<version installée>"
  export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
  export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$PATH"
  ```
  Puis (une fois, génère `client/src-tauri/gen/android/`, gitignored) :
  `cd client && npx tauri android init`, ensuite `npx tauri android build --debug --target aarch64`.
  APK de sortie : `client/src-tauri/gen/android/app/build/outputs/apk/universal/debug/app-universal-debug.apk`.

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
