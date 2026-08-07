# Détection de Stack — Heuristiques par technologie

Guide de référence pour identifier rapidement le stack d'un projet et extraire
ses routes sans lire le code source.

---

## Identification rapide du framework

### Par fichier de config (priorité haute)

| Fichier détecté | Framework | Certitude |
|-----------------|-----------|-----------|
| `next.config.js/ts/mjs` | Next.js | 100% |
| `nuxt.config.ts` | Nuxt | 100% |
| `svelte.config.js` | SvelteKit | 100% |
| `remix.config.js` | Remix | 100% |
| `astro.config.mjs` | Astro | 100% |
| `angular.json` | Angular | 100% |
| `vite.config.ts` + pas de framework above | Vite (vanilla/React/Vue) | 80% |
| `turbo.json` | Turborepo (monorepo) | 100% |
| `pnpm-workspace.yaml` | pnpm monorepo | 100% |
| `nx.json` | Nx monorepo | 100% |
| `strapi/src/admin` ou `src/api` + schema.json | Strapi | 100% |
| `manage.py` | Django | 95% |
| `config/routes.rb` | Rails | 100% |
| `go.mod` | Go | 100% |
| `Cargo.toml` | Rust | 100% |
| `Package.swift` | Swift | 100% |
| `pubspec.yaml` | Flutter/Dart | 100% |
| `composer.json` + `artisan` | Laravel | 100% |

### Par dépendance dans le manifeste

```bash
# Node.js — lire package.json dependencies + devDependencies
cat package.json | grep -E '"(express|fastify|koa|hono|nestjs|strapi|next|nuxt|remix)"'

# Python — lire requirements.txt ou pyproject.toml
grep -E "(fastapi|django|flask|starlette|sanic|tornado)" requirements.txt pyproject.toml 2>/dev/null

# Ruby — lire Gemfile
grep -E "(rails|sinatra|hanami)" Gemfile 2>/dev/null
```

---

## Extraction des routes par framework

### Next.js (App Router)

```bash
# Toutes les pages
find app -name "page.tsx" -o -name "page.ts" -o -name "page.jsx" 2>/dev/null | sort

# Toutes les API routes
find app -name "route.ts" -o -name "route.tsx" 2>/dev/null | sort

# Layouts (pour comprendre la hiérarchie)
find app -name "layout.tsx" -o -name "layout.ts" 2>/dev/null | sort

# Route groups (dossiers avec parenthèses)
find app -type d -name "(*)' 2>/dev/null

# Convertir chemin fichier → URL
# app/(dashboard)/users/page.tsx → /users
# app/(dashboard)/users/[id]/page.tsx → /users/:id
# app/api/auth/route.ts → /api/auth
```

**Conventions :**
- `(group)` = route group, pas dans l'URL
- `[param]` = paramètre dynamique
- `[...slug]` = catch-all
- `_components/` = pas une route

### Next.js (Pages Router)

```bash
find pages -name "*.tsx" -o -name "*.ts" | grep -v "_app\|_document\|_error\|api/" | sort
find pages/api -name "*.ts" -o -name "*.tsx" 2>/dev/null | sort
```

### Nuxt

```bash
find pages -name "*.vue" 2>/dev/null | sort
find server/api -name "*.ts" -o -name "*.js" 2>/dev/null | sort
```

### Express / Fastify / Koa / Hono

```bash
# Trouver les fichiers de routes
grep -rn "Router()\|router\.\(get\|post\|put\|delete\|patch\)" \
  --include="*.ts" --include="*.js" -l src/ 2>/dev/null

# Extraire les déclarations de routes
grep -n "router\.\(get\|post\|put\|delete\|patch\)\|app\.\(get\|post\|put\|delete\)" \
  --include="*.ts" --include="*.js" src/routes/ 2>/dev/null

# Trouver le montage des routes (préfixes)
grep -rn "app.use\|server.register\|app.route" --include="*.ts" --include="*.js" \
  src/index.ts src/app.ts src/server.ts 2>/dev/null
```

### NestJS

```bash
# Controllers (décorateurs de route)
grep -rn "@Controller\|@Get\|@Post\|@Put\|@Delete\|@Patch" \
  --include="*.ts" src/ 2>/dev/null

# Modules (pour comprendre l'organisation)
grep -rn "@Module" --include="*.ts" -l src/ 2>/dev/null
```

### Strapi v5

```bash
# Routes CRUD (auto-générées par content-type)
find src/api -name "schema.json" 2>/dev/null | while read f; do
  dirname "$f" | xargs basename
done

# Routes custom
find src/api -path "*/routes/*.ts" -o -path "*/routes/*.js" 2>/dev/null | \
  xargs grep -l "method\|path" 2>/dev/null

# Extraire les custom routes
grep -A2 "method\|path" src/api/*/routes/*.ts 2>/dev/null
```

### FastAPI

```bash
# Fichiers de routeurs
grep -rn "@router\.\|@app\.\(get\|post\|put\|delete\|patch\)" \
  --include="*.py" -l app/ src/ 2>/dev/null

# Extraire les routes avec leurs paths
grep -n "@router\.\(get\|post\|put\|delete\|patch\)\|@app\.\(get\|post\|put\|delete\)" \
  --include="*.py" app/ src/ 2>/dev/null

# Trouver le montage des routeurs (préfixes)
grep -n "include_router\|prefix=" --include="*.py" app/main.py src/main.py 2>/dev/null
```

### Django

```bash
# Trouver tous les urls.py
find . -name "urls.py" -not -path "*/venv/*" -not -path "*/.venv/*" 2>/dev/null

# Extraire les patterns
grep -n "path(\|url(\|re_path(" */urls.py 2>/dev/null

# Views (le controller Django)
find . -name "views.py" -not -path "*/venv/*" 2>/dev/null
```

### Flask

```bash
grep -rn "@app.route\|@.*blueprint.route\|@.*bp.route" \
  --include="*.py" -not -path "*/venv/*" 2>/dev/null
```

### Rails

```bash
# Routes compilées (le plus fiable)
cat config/routes.rb

# Si rails est dispo
bundle exec rails routes 2>/dev/null | head -100
```

### Go (Gin / Echo / Chi / std)

```bash
# Gin
grep -rn "\.GET\|\.POST\|\.PUT\|\.DELETE\|\.PATCH\|\.Group" \
  --include="*.go" -not -path "*/vendor/*" 2>/dev/null

# Echo
grep -rn "e.GET\|e.POST\|e.PUT\|e.DELETE\|e.Group" \
  --include="*.go" 2>/dev/null

# Chi
grep -rn "r.Get\|r.Post\|r.Put\|r.Delete\|r.Route\|r.Group" \
  --include="*.go" 2>/dev/null

# Standard library
grep -rn "http.HandleFunc\|mux.HandleFunc\|mux.Handle" \
  --include="*.go" 2>/dev/null
```

### Laravel

```bash
# Routes
cat routes/web.php routes/api.php 2>/dev/null

# Ou via artisan
php artisan route:list 2>/dev/null | head -100
```

### Swift (Vapor)

```bash
grep -rn "app.get\|app.post\|app.put\|app.delete\|app.grouped" \
  --include="*.swift" Sources/ 2>/dev/null
```

---

## Extraction des modèles / entités

### Par ORM

| ORM | Commande de détection |
|-----|----------------------|
| Prisma | `cat prisma/schema.prisma \| grep -A 5 "^model "` |
| TypeORM | `grep -rn "@Entity\|@Column" --include="*.ts" src/` |
| MikroORM | `grep -rn "@Entity\|@Property" --include="*.ts" src/` |
| Sequelize | `grep -rn "sequelize.define\|Model.init" --include="*.ts" --include="*.js" src/` |
| Mongoose | `grep -rn "new Schema\|mongoose.model" --include="*.ts" --include="*.js" src/` |
| SQLAlchemy | `grep -rn "class.*Base)\|Column(" --include="*.py" app/models/` |
| Django ORM | `grep -rn "class.*models.Model" --include="*.py" */models.py` |
| ActiveRecord | `find db/migrate -name "*.rb" \| xargs grep "create_table"` |
| GORM | `grep -rn "gorm.Model\|gorm:\"" --include="*.go"` |
| Strapi | `find src/api -name "schema.json" \| xargs cat` |
| Ecto | `grep -rn "schema\|field\|belongs_to\|has_many" --include="*.ex" lib/*/schemas/` |

---

## Détection des couches transversales

### Patterns de dossiers courants

```bash
# Dossiers transversaux fréquents (generique)
find . -maxdepth 3 -type d \( \
  -name "hooks" -o -name "composables" -o -name "helpers" \
  -o -name "utils" -o -name "shared" -o -name "common" \
  -o -name "lib" -o -name "core" -o -name "middleware" \
  -o -name "middlewares" -o -name "plugins" -o -name "config" \
  -o -name "constants" -o -name "types" -o -name "interfaces" \
  -o -name "guards" -o -name "decorators" -o -name "providers" \
  -o -name "interceptors" -o -name "pipes" -o -name "filters" \
  -o -name "modules" -o -name "concerns" -o -name "mixins" \
  -o -name "traits" -o -name "protocols" -o -name "extensions" \
\) -not -path "*/node_modules/*" -not -path "*/.venv/*" \
  -not -path "*/vendor/*" -not -path "*/target/*" 2>/dev/null
```

### Dépendances croisées

```bash
# Qui importe depuis les couches transversales ?
grep -rn "from.*\/\(shared\|hooks\|utils\|helpers\|lib\|common\|core\)" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  src/ app/ 2>/dev/null | awk -F: '{print $1}' | sort | uniq -c | sort -rn
```
