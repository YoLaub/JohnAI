# ✦ JohnAi - Assistant IA Flottant & Enregistreur de Pensées Multi-Plateforme

**JohnAi** est un assistant IA personnel omniprésent et discret sous forme de **pilule flottante ultra-compacte** (*Floating Pill Widget*), disponible sur **macOS, Windows et Android**, synchronisé en temps réel avec un serveur central VPS.

---

## 🌟 Fonctionnalités Clés

- ✦ **Widget Flottant Desktop (Tauri 2.0)** :
  - Design Glassmorphism dépoli (`backdrop-filter: blur(24px)`) avec contours néon réactifs (Violet / Cyan).
  - Transparence 100% native macOS / Windows sans bordure.
  - Déplacement fluide à la souris (*Window Dragging*) n'importe où sur vos écrans.
- 📝 **Mode Dictaphone & Enregistreur de Pensées** :
  - Capturez vos pensées et notes vocales à la volée en 1 tap.
  - Sauvegarde immédiate dans votre journal de mémoire centralisé SQLite.
- 💬 **Mode Brainstorming & Assistant** :
  - Discutez, réfléchissez ou brainstormez sur vos pensées enregistrées.
- 🧠 **Smart Model Router (Hybride Local / Cloud)** :
  - ✦ **Mode Général** : **Gemma 3 (12B)** (Local sur Mac / Windows).
  - 💻 **Mode Code** : Détection automatique des requêtes techniques ➔ **Qwen 2.5 Coder (14B)** (Local sur Mac / Windows).
  - ⚡ **Mode Mobile / Nomade** : **Google Gemini 2.5 Flash** (Cloud API via le VPS pour préserver la batterie de votre smartphone Android).
- 💾 **Mémoire Centralisée Multi-Appareils** :
  - Historique et notes synchronisés entre vos ordinateurs et votre téléphone via le VPS.
- 📎 **Gestion des Pièces Jointes & Drag & Drop** :
  - Glissez-déposez des PDF, documents texte, images ou fichiers de code directement sur le widget.
- 🎙️ **Reconnaissance Vocale (Speech-to-Text)** :
  - Enregistrement audio et transcription en temps réel en français (`fr-FR`).
- 🔀 **Double Mode d'Affichage** :
  - Vue Pilule Flottante Compacte ou Tableau de Bord complet des pensées (`[ ⛶ ]`).

---

## 📁 Architecture du Dépôt

```
JohnAi/
├── client/                      # Application Client Desktop (Tauri 2.0) & Web PWA
│   ├── index.html               # Structure HTML de la Floating Pill & du Dashboard
│   ├── styles.css               # Design System Glassmorphism & Responsive Mobile
│   ├── app.js                   # Visualiseur Canvas, STT, WebSockets, Drag & Drop
│   ├── manifest.json            # Configuration PWA Android
│   └── src-tauri/               # Runner Native Desktop (Rust / macOSPrivateApi)
│
└── server/                      # Serveur Central VPS & API (FastAPI)
    ├── main.py                  # API REST & WebSockets, Smart Router (Gemma 3 / Qwen / Gemini)
    ├── database.py              # Base de données mémoire centralisée SQLite
    ├── Dockerfile               # Conteneurisation Docker pour Coolify
    └── docker-compose.yml       # Fichier de déploiement Docker Compose
```

---

## 🚀 Démarrage Rapide en Local (macOS / Windows)

### 1. Démarrer le Serveur Backend (FastAPI + Ollama)
```bash
# Dans le dossier racine du projet
python3 -m pip install -r server/requirements.txt
python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8000
```

### 2. Démarrer le Widget Desktop (Tauri 2.0)
```bash
cd client
npm install
npx @tauri-apps/cli dev
```

---

## 🐳 Déploiement sur votre VPS (Coolify)

1. Ouvrez votre tableau de bord **Coolify**.
2. Créez un nouveau service de type **Docker Compose** en sélectionnant le dossier `server/`.
3. Configurez les variables d'environnement (optionnel) :
   ```env
   PORT=8000
   OLLAMA_URL=http://localhost:11434
   GEMINI_API_KEY=votre_cle_google_ai_studio  # Pour Android & Mode Cloud
   API_KEY=un_secret_partage_fort  # Obligatoire : protège toutes les routes non publiques
   ```
4. Déployez ! Coolify générera l'URL sécurisée HTTPS (`https://johnai.votre-domaine.com`).

---

## 📱 Installation sur Smartphone Android (PWA)

1. Depuis le navigateur de votre smartphone, rendez-vous sur l'URL de votre serveur VPS (`https://johnai.votre-domaine.com`).
2. Appuyez sur le menu du navigateur et choisissez **"Ajouter à l'écran d'accueil"**.
3. L'application **JohnAi** s'installe comme une app native avec de grands boutons tactiles d'enregistrement en 1 tap !

---

## 📦 Générer les Fichiers d'Installation (Build)

- **macOS (`.dmg` / `.app`)** :
  ```bash
  cd client && npm run tauri build
  ```
- **Windows (`.msi` / `.exe`)** :
  ```bash
  cd client && npm run tauri build
  ```
- **Android (`.apk`)** :
  ```bash
  cd client && npx tauri android build
  ```

---

## 📜 Licence
Projet sous licence MIT - Développé avec ❤️ pour un usage personnel omniprésent.
