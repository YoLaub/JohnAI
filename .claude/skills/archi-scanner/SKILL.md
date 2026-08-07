---
name: archi-scanner
description: >
  Scanner d'architecture progressif et générique. Indexe un projet de développement
  en profondeur sans exploser le context window, en procédant par étapes : détection
  du stack → extraction des routes → controllers → services → entités → hooks/helpers/shared.
  Produit un fichier INDEX structuré réutilisable pour intervenir sur le code sans
  rescanner. Utilise ce skill dès que l'utilisateur veut comprendre un projet,
  cartographier un codebase, indexer l'architecture, scanner la structure, ou dit
  "analyse le projet", "cartographie le code", "indexe l'architecture", "scanne
  le codebase", "comprendre ce projet", "mapper l'app". Se déclenche aussi quand
  l'utilisateur arrive sur un nouveau projet et a besoin de s'orienter, ou quand
  le fichier archi-output/INDEX.md n'existe pas encore. Ce skill est le prérequis
  pour archi-diagrams, add-feature et continue-feature. Il fonctionne sur tout
  type de projet (Node, Python, Java, Swift, Go, Ruby, PHP, Rust, etc.).
---

# Archi-Scanner — Indexation progressive d'architecture

Tu es un architecte logiciel méthodique. Ton rôle est de scanner un codebase
en profondeur **sans jamais charger trop de code en mémoire**. Tu procèdes par
étapes, tu indexes, et tu produis un fichier de référence réutilisable.

## Principe fondamental : économie de tokens

**RÈGLE D'OR : Ne lis jamais un fichier entier si tu peux extraire l'info
autrement.**

- Utilise `find`, `grep`, `head`, `wc -l` avant de lire un fichier
- Utilise les configs et manifestes plutôt que le code source
- Utilise le build system pour découvrir les routes
- Ne descends JAMAIS dans `node_modules/`, `vendor/`, `.venv/`, `target/`, `build/`
- Lis les fichiers source uniquement pour extraire les signatures (exports, classes, fonctions), pas l'implémentation

---

## Phase 1 : Détection du stack

**Objectif :** Identifier la technologie en 1-2 commandes, sans lire de code.

```bash
# Commande de démarrage — structure globale
find . -maxdepth 2 -type f \( \
  -name "package.json" -o -name "pyproject.toml" -o -name "requirements.txt" \
  -o -name "Gemfile" -o -name "go.mod" -o -name "Cargo.toml" \
  -o -name "pom.xml" -o -name "build.gradle" -o -name "composer.json" \
  -o -name "Package.swift" -o -name "Makefile" -o -name "docker-compose*.yml" \
  -o -name ".env*" -o -name "tsconfig*.json" -o -name "next.config.*" \
  -o -name "nuxt.config.*" -o -name "vite.config.*" -o -name "turbo.json" \
  -o -name "pnpm-workspace.yaml" -o -name "nx.json" \
\) 2>/dev/null | head -50
```

Puis lis les manifestes détectés (package.json, pyproject.toml, etc.) pour
extraire :
- **Framework principal** (Next.js, Express, FastAPI, Rails, etc.)
- **Dépendances clés** (ORM, test framework, UI lib, auth, etc.)
- **Scripts disponibles** (build, test, dev, lint)
- **Structure** (monorepo ou single-app)

**Si monorepo :** identifier chaque app/package et les traiter séparément.

```bash
# Pour un monorepo — identifier les packages
cat pnpm-workspace.yaml 2>/dev/null || cat lerna.json 2>/dev/null
ls -d apps/* packages/* 2>/dev/null
```

Consulte `references/stack-detection.md` pour les heuristiques par techno.

### Variables d'environnement référencées dans le code

Extraire toutes les env vars utilisées dans le code source (pas seulement celles déclarées dans `.env`) :

```bash
# Node.js / TypeScript
grep -rh "process\.env\." --include="*.ts" --include="*.tsx" --include="*.js" src/ app/ 2>/dev/null | \
  grep -oP 'process\.env\.\K[A-Z_]+' | sort -u

# Python
grep -rh "os\.getenv\|os\.environ" --include="*.py" . 2>/dev/null | \
  grep -oP "getenv\(['\"]?\K[A-Z_]+|environ\[['\"]?\K[A-Z_]+" | sort -u

# Go
grep -rh "os\.Getenv\|os\.LookupEnv" --include="*.go" . 2>/dev/null | \
  grep -oP 'Getenv\("[^"]+"\)|\K[A-Z_]+' | sort -u
```

**Output de cette phase :**

```
STACK DÉTECTÉ :
  Type : [Monorepo | Single-app]
  Framework(s) : [Next.js 14, Strapi v5, ...]
  Langage(s) : [TypeScript, Python, ...]
  ORM/DB : [Prisma/PostgreSQL, SQLAlchemy/PostgreSQL, ...]
  Tests : [Jest, Vitest, Pytest, ...]
  CI/CD : [GitHub Actions, GitLab CI, ...]
  Infra : [Docker, Vercel, Hetzner, ...]

ENV VARS RÉFÉRENCÉES : (toutes celles trouvées dans le code, avec leur fichier source)
  DATABASE_URL        → prisma/schema.prisma, src/lib/db.ts
  NEXTAUTH_SECRET     → app/api/auth/[...nextauth]/route.ts
  STRIPE_SECRET_KEY   → src/lib/stripe.ts
  ...
  ⚠️  Non déclarées dans .env : [liste des vars présentes dans le code mais absentes du .env]
```

---

## Phase 2 : Extraction des routes (le squelette)

**Objectif :** Obtenir TOUTES les routes/endpoints de l'application en une
opération peu coûteuse. Les routes sont le squelette — tout le reste en découle.

La stratégie dépend du framework détecté en Phase 1.

### Frameworks file-based routing

Pour Next.js, Nuxt, SvelteKit, Remix — la structure de fichiers EST le routage.

```bash
# Next.js App Router
find app -name "page.tsx" -o -name "page.ts" -o -name "page.jsx" -o -name "route.ts" -o -name "route.tsx" | sort

# Next.js Pages Router
find pages -name "*.tsx" -o -name "*.ts" | grep -v "_app\|_document\|_error" | sort

# Nuxt
find pages -name "*.vue" | sort
```

### Frameworks code-based routing

Pour Express, Fastify, Koa, Hono — grep les déclarations de routes.

```bash
# Express / Fastify
grep -rn "router\.\(get\|post\|put\|patch\|delete\|all\)\|app\.\(get\|post\|put\|patch\|delete\)" \
  --include="*.ts" --include="*.js" -l src/ | sort

# Puis extraire les routes de chaque fichier
grep -n "router\.\(get\|post\|put\|patch\|delete\)" src/routes/*.ts
```

### Strapi

```bash
# Routes Strapi — chaque API a sa structure
find src/api -name "*.ts" -o -name "*.js" | sort
# Extraire les custom routes
grep -rn "method\|path" src/api/*/routes/ --include="*.ts" --include="*.js"
```

### FastAPI / Django / Flask

```bash
# FastAPI — chercher les decorators de route
grep -rn "@router\.\|@app\.\(get\|post\|put\|delete\)" --include="*.py" -l src/ app/

# Django — urls.py
find . -name "urls.py" | xargs grep -n "path\|url("

# Flask
grep -rn "@app.route\|@blueprint.route" --include="*.py" -l
```

### Rails

```bash
# Routes Rails
cat config/routes.rb
# Ou la version compilée
rails routes 2>/dev/null || bundle exec rails routes 2>/dev/null
```

### Go (Gin, Echo, Chi)

```bash
grep -rn "\.GET\|\.POST\|\.PUT\|\.DELETE\|\.Handle\|\.HandleFunc" --include="*.go" -l
```

Pour les heuristiques complètes par framework, consulte `references/stack-detection.md`.

**Output de cette phase :**

```
ROUTES DÉTECTÉES : [N] routes

API Routes :
  GET    /api/users              → src/api/user/routes/...
  POST   /api/users              → src/api/user/routes/...
  GET    /api/users/:id          → src/api/user/routes/...
  ...

Pages (si frontend) :
  /                              → app/page.tsx
  /dashboard                     → app/(dashboard)/page.tsx
  /profile                       → app/(profile)/page.tsx
  ...
```

---

## Phase 3 : Chaînage Controllers → Services → Entités

**Objectif :** À partir des routes, remonter la chaîne de dépendances sans
lire le code en entier. On extrait les SIGNATURES, pas l'implémentation.

### Stratégie de scan par couche

Pour chaque route trouvée en Phase 2, identifie le handler/controller associé.
Puis de chaque controller, identifie les services appelés. Puis de chaque
service, identifie les entités/modèles utilisés.

```
Routes → Controllers → Services → Entités/Modèles
  ↓          ↓            ↓            ↓
grep       head -50    grep import   grep schema
les paths  du fichier  + grep fn     ou model
```

### Extraction des signatures (pas de l'implémentation)

```bash
# Extraire les exports/fonctions d'un fichier TS/JS (signatures seulement)
grep -n "export\|async function\|const.*=.*async\|class " src/api/user/controllers/user.ts

# Extraire les méthodes d'un service Python
grep -n "def \|class \|async def " app/services/user_service.py

# Extraire les champs d'un modèle/entité
grep -n "Column\|Field\|attribute\|@Entity\|@Table\|model\|schema" src/models/user.ts
```

### Props des composants exportés (frontend uniquement)

Pour les projets avec des composants UI, capturer les contrats de props des composants exportés :

```bash
# React — interface/type Props (TypeScript)
grep -rn "interface.*Props\|type.*Props\s*=" --include="*.tsx" --include="*.ts" -A 15 src/components/ app/
# Ou avec defineProps (React 19+ / patterns modernes)
grep -rn "export.*function\|export const.*=" --include="*.tsx" src/components/ | head -30

# Vue — defineProps
grep -rn "defineProps" --include="*.vue" -A 10 src/ components/

# Svelte — props déclarées
grep -rn "export let \|export const " --include="*.svelte" src/
```

Capturer pour chaque composant exporté : nom, props obligatoires vs optionnelles, types.

### Conditions métier notables

Identifier les guards et règles métier implémentés dans le code (≠ validation de formulaire) :

```bash
# Guards d'autorisation / accès
grep -rn "throw new.*Forbidden\|throw new.*Unauthorized\|throw new.*ForbiddenException\|403\|401" \
  --include="*.ts" --include="*.js" -B 2 src/ app/ | grep -v "node_modules" | head -40

# Conditions métier clés (role, permission, ownership)
grep -rn "if.*role\|if.*permission\|if.*isOwner\|if.*canAccess\|if.*hasRight\|if.*!user\." \
  --include="*.ts" --include="*.js" src/ app/ | grep -v "test\|spec\|\.d\.ts" | head -30

# Python — guards et raises métier
grep -rn "raise.*Permission\|raise.*Forbidden\|raise.*HTTPException.*40[13]" \
  --include="*.py" -B 2 app/ src/ | head -30
```

**Ce qu'on note dans l'index :** la règle métier (ex: "seul le propriétaire peut modifier"), pas le détail du code.

### Pour les entités / modèles de données

```bash
# Prisma
cat prisma/schema.prisma | grep -A 20 "^model "

# SQLAlchemy
grep -rn "class.*Base\)\|Column\|relationship" --include="*.py" app/models/

# Strapi — content-types
find src/api -name "schema.json" | xargs head -30

# TypeORM / MikroORM
grep -rn "@Entity\|@Column\|@ManyToOne\|@OneToMany" --include="*.ts" src/

# Django
grep -rn "class.*models.Model\|CharField\|IntegerField\|ForeignKey" --include="*.py" */models.py
```

**Output de cette phase :**

```
ARCHITECTURE PAR MODULE :

📦 Module: User
  Routes :
    GET  /api/users        → UserController.find()
    POST /api/users        → UserController.create()
    GET  /api/users/:id    → UserController.findOne()
  Controller : src/api/user/controllers/user.ts
    - find(), create(), findOne(), update(), delete()
  Service : src/api/user/services/user.ts
    - findUsers(), createUser(), findUserById()
  Entité : src/api/user/content-types/user/schema.json
    - email (string, unique), name (string), role (relation)
  Règles métier :
    - Seul un ADMIN peut appeler DELETE /api/users/:id (guard: role === 'admin')
    - Un utilisateur ne peut modifier que son propre profil (guard: user.id === params.id)
  Tests : tests/user/user.test.ts [12 tests]

📦 Module: UserCard (composant)
  Fichier : src/components/UserCard.tsx
  Props obligatoires : userId (string), onSelect (fn)
  Props optionnelles : showAvatar? (bool), compact? (bool)

📦 Module: Auth
  Routes : ...
  ...
```

---

## Phase 4 : Scan des couches transversales

**Objectif :** Identifier tout ce qui n'est pas dans un module métier mais qui
est utilisé partout — hooks, helpers, shared, middleware, utils, config.

```bash
# Trouver les dossiers transversaux
find . -maxdepth 3 -type d \( \
  -name "hooks" -o -name "helpers" -o -name "utils" -o -name "shared" \
  -o -name "common" -o -name "lib" -o -name "middleware" -o -name "middlewares" \
  -o -name "plugins" -o -name "config" -o -name "constants" \
  -o -name "types" -o -name "interfaces" -o -name "guards" \
  -o -name "decorators" -o -name "providers" -o -name "core" \
\) -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null

# Pour chaque dossier trouvé, lister les fichiers avec leur taille
find <dossier> -type f | xargs wc -l | sort -n

# Extraire les exports de chaque fichier (signatures only)
grep -rn "export\|module.exports" --include="*.ts" --include="*.js" <dossier>/
```

### Identifier les dépendances croisées

```bash
# Quels modules importent depuis shared/hooks/utils ?
grep -rn "from.*shared\|from.*hooks\|from.*utils\|from.*helpers\|from.*lib\|from.*common" \
  --include="*.ts" --include="*.tsx" --include="*.js" src/ app/ | \
  awk -F: '{print $1}' | sort -u
```

### Cartographie des call sites (fonctions partagées clés)

Pour chaque fonction partagée importante identifiée en Phase 3/4, lister tous ses points d'appel :

```bash
# Identifier d'abord les fonctions partagées à fort usage
grep -rn "^export.*function\|^export const.*=.*(" --include="*.ts" --include="*.js" \
  src/lib/ src/utils/ src/helpers/ packages/shared/ 2>/dev/null | \
  grep -oP "function \K\w+|const \K\w+" | sort -u

# Pour chaque fonction clé, lister qui l'appelle
FUNC="uploadDocumentFile"  # exemple
grep -rn "\b${FUNC}\b" --include="*.ts" --include="*.tsx" --include="*.js" \
  -l src/ app/ 2>/dev/null
# Puis le contexte d'appel
grep -rn "\b${FUNC}\b" --include="*.ts" --include="*.tsx" --include="*.js" \
  -B 1 src/ app/ 2>/dev/null | grep -v "^.*:.*export\|^.*:.*import" | head -20
```

**Critère de sélection :** cartographier en priorité les fonctions dont la modification aurait le plus grand impact (parseur, upload, auth helper, send-email, etc.). **Ne pas cartographier** les utilitaires triviaux (formatDate, slugify).

**Output de cette phase :**

```
COUCHES TRANSVERSALES :

🔧 Middleware (src/middlewares/)
  - auth.ts : vérification JWT, refresh token
  - rate-limit.ts : rate limiting par IP
  - cors.ts : configuration CORS

🪝 Hooks (app/hooks/)
  - useAuth.ts : authentification côté client
  - useSWRFetch.ts : wrapper SWR avec config
  - useDebounce.ts : debounce générique

🛠️ Utils (packages/shared/utils/)
  - format-date.ts : formatage dates (FR/EN)
  - validate-email.ts : validation email
  - slugify.ts : génération de slugs
  - uploadDocumentFile.ts : upload S3 — appelé par [DocumentForm, AdminPanel, BulkImport]

📐 Types (packages/shared/types/)
  - user.types.ts : User, UserRole, UserStatus
  - api.types.ts : ApiResponse<T>, PaginatedResponse<T>

📡 Call Sites (fonctions partagées à fort impact) :
  - uploadDocumentFile() → appelé dans : DocumentForm.tsx, AdminPanel.tsx, BulkImport.ts
  - sendEmail()          → appelé dans : auth/register.ts, order/confirm.ts, contact/route.ts
  - createAuditLog()     → appelé dans : 12 fichiers (src/api/**/*.ts)
```

---

## Phase 5 : Génération de l'index

**Objectif :** Produire le fichier `archi-output/INDEX.md` — la source de
vérité réutilisable par tous les autres skills.

### Structure de l'index

L'index DOIT contenir ces sections dans cet ordre :

```markdown
# Index d'Architecture — [Nom du projet]
> Généré le [date] — Scanner v2

## Stack
[Output de la Phase 1]

## Env Vars
[Toutes les vars référencées dans le code, avec fichier source et statut .env]

## Routes
[Output de la Phase 2 — tableau de toutes les routes]

## Modules
[Output de la Phase 3 — par module métier, incluant props des composants et règles métier]

### Props des Composants Exportés
[Composant → props obligatoires | props optionnelles | types]

### Règles Métier Identifiées
[Liste des conditions métier notables : qui, quoi, où]

## Transversal
[Output de la Phase 4 — hooks, utils, middleware, call sites]

### Call Sites (fonctions à fort impact)
[Fonction → liste des fichiers appelants]

## Métriques
- Nombre total de routes : N
- Nombre de modules métier : N
- Nombre de fichiers source : N
- Couverture de test détectée : [oui/non, framework]
- Taille du projet : N fichiers, ~N lignes

## Points d'attention
[Anomalies détectées pendant le scan : fichiers > 500 lignes,
modules sans tests, dépendances circulaires, env vars non déclarées, etc.]
```

### Fichier compagnon : PROJECT_MEMORY.md

En plus de l'index, produis un `PROJECT_MEMORY.md` résumé (< 200 lignes)
utilisable par les autres skills sans charger tout l'index :

```markdown
# Mémoire Projet — [Nom]

## En bref
[3-5 lignes : stack, architecture, taille]

## Structure
[Arbre simplifié des dossiers principaux]

## Conventions détectées
[Nommage, patterns, imports, etc.]

## Risques identifiés
[Anomalies, dettes, fichiers critiques]
```

### Sauvegarde

```bash
mkdir -p archi-output
# INDEX.md = référence complète
# PROJECT_MEMORY.md = résumé pour les autres skills
```

---

## Workflow conversationnel

### Si l'utilisateur lance un scan complet

```
"Scanne le projet" / "Indexe l'architecture" / "Analyse le codebase"
```

1. Exécute les 5 phases séquentiellement
2. Affiche un résumé à chaque phase (pas le détail complet)
3. Demande confirmation avant de passer à la suivante si le projet est gros
4. Produit l'index final

### Si l'utilisateur veut scanner une partie

```
"Scanne juste le module auth" / "Indexe les routes API"
```

→ Exécute uniquement les phases pertinentes, mais mets à jour l'index
existant (ne l'écrase pas).

### Si l'index existe déjà

```
"Rescanne le projet" / "Mets à jour l'index"
```

→ Lis l'index existant, détecte ce qui a changé (nouveaux fichiers, routes
modifiées), mets à jour uniquement les sections impactées.

---

## Anti-patterns à éviter

❌ **Lire un fichier de 500 lignes en entier** pour en extraire 3 exports
→ Utilise `grep -n "export"` à la place

❌ **Lire tous les fichiers d'un module d'un coup** pour "comprendre"
→ Lis les signatures, puis lis le détail seulement si nécessaire

❌ **Scanner node_modules / vendor / .venv**
→ Lis package.json / requirements.txt pour les dépendances

❌ **Générer l'index en une seule passe** sur un gros projet
→ Phase par phase, avec résumé intermédiaire

❌ **Mettre du code source dans l'index**
→ L'index contient des SIGNATURES et des CHEMINS, pas de l'implémentation

❌ **Rescanner tout quand un fichier change**
→ Mise à jour incrémentale de la section concernée
