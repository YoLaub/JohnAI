# Phase 1 — Bootstrap

Créer la structure 3 couches d'un nouveau cerveau projet + fichiers d'amorce.
Lire aussi `vault-structure.md` (le contrat de structure) avant d'exécuter.

## Étape 1.1 — Capture d'intention

Avant de créer quoi que ce soit, collecter les informations essentielles. Si elles ne sont pas déjà dans la conversation, demander (idéalement en une seule passe avec AskUserQuestion) :

1. **Nom du projet** (identifiant court, kebab-case de préférence : `mon-app`, `ma-api`, `boutique-x`)
2. **Chemin du vault** (ex: `~/ObsidianVaults/mon-app-brain/` — par défaut suggérer ce pattern)
3. **Description courte** (1-2 phrases, sera la racine de l'identité du cerveau)
4. **Stack / domaine** (pour calibrer les premières entités : "Strapi + Next.js", "SwiftUI + FastAPI", "recherche bio", etc.)
5. **Sources initiales disponibles** (optionnel : l'utilisateur a-t-il déjà des docs à poser dans `raw/` dès le bootstrap ?)

## Étape 1.2 — Exécution du bootstrap

Deux voies possibles selon l'environnement :

**Voie A — Script Python (préférée, déterministe, rejouable)**

```bash
python <dossier-du-skill>/scripts/bootstrap_brain.py \
  --name "mon-app" \
  --path "~/ObsidianVaults/mon-app-brain" \
  --description "Backend Strapi v5 + Turborepo frontend" \
  --stack "strapi,nextjs,postgres"
```

Le script est autonome (templates embarqués, y compris la config `.obsidian/`) et **idempotent** : si le vault existe déjà, il ne détruit rien, il complète uniquement ce qui manque.

**Voie B — Création manuelle via tools de fichiers (fallback si pas d'accès shell ou MCP Obsidian uniquement)**

Suivre l'arborescence décrite dans `vault-structure.md` et créer les fichiers d'amorce un par un à partir de `note-templates.md`.

## Étape 1.3 — Personnalisation post-bootstrap

Une fois la structure créée, personnaliser les fichiers d'amorce :

1. **`wiki/INDEX.md`** — Map of Content racine. Renseigner les premières entités prévisibles selon la stack (ex: pour Strapi → `Auth`, `User`, `Content-Types`, `Plugins`).
2. **`wiki/_meta/IDENTITY.md`** — Carte d'identité du cerveau. Nom, objectif, périmètre, hors-périmètre.
3. **`wiki/_meta/CENTRAL_LINKS.md`** — Déjà créé vide, prêt à accueillir les liens vers le cerveau central quand il existera (voir `central-brain-protocol.md`).

## Étape 1.4 — Vérification

Après bootstrap, toujours produire un récapitulatif à l'utilisateur :

```
✅ Cerveau "mon-app" créé à ~/ObsidianVaults/mon-app-brain/

Structure :
  raw/          (0 fichiers — à remplir)
  wiki/         (4 fichiers d'amorce)
  reports/      (vide)
  .obsidian/    (config minimale)

Prochaines étapes suggérées :
  1. Ouvrir le vault dans Obsidian
  2. Déposer tes premières sources dans raw/
  3. Me demander "compile le raw en wiki" quand tu as du contenu
```
