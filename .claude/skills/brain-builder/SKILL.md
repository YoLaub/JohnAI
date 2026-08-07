---
name: brain-builder
description: >
  Crée et maintient des "cerveaux projets" sous forme de vaults Obsidian structurés en Markdown,
  inspirés de l'approche LLM Wiki d'Andrej Karpathy. Chaque projet obtient son propre vault isolé
  avec l'architecture 3 couches (raw/wiki/reports), prêt à être connecté à un cerveau central.
  Utilise ce skill dès que l'utilisateur mentionne : "cerveau projet", "mémoire persistante",
  "vault Obsidian", "mini cerveau", "LLM wiki", "mémoire IA structurée", "bootstrap projet",
  "initialiser un nouveau projet avec mémoire", ou toute demande de structure de connaissance
  durable pour un projet. Se déclenche aussi pour les phases suivantes : compiler le raw en wiki,
  linter le vault (détection d'orphelins, liens cassés, incohérences), ou connecter un cerveau
  projet au cerveau central.
---

# Brain-Builder

Skill de construction et maintenance de cerveaux projets basés sur l'approche **LLM Wiki** de Karpathy, déployés comme vaults Obsidian autonomes.

## Philosophie

Chaque projet a son propre cerveau. Un cerveau = un vault Obsidian = un dossier isolé contenant trois couches :

1. **`raw/`** — Sources immuables (PDF, transcripts, dumps de code, notes brutes). L'IA lit, ne modifie jamais.
2. **`wiki/`** — Mémoire active compilée par l'IA. Notes d'entités interconnectées, MOC (Maps of Content), synthèses.
3. **`reports/`** — Conclusions, analyses, rapports de haut niveau. Peuvent nourrir le wiki en retour.

Le format Markdown + YAML garantit la souveraineté des données, la pérennité, et permet à l'humain comme à l'IA de collaborer sur les mêmes fichiers.

## Phases

Quatre phases indépendantes, chacune avec son workflow détaillé. **Ne lire que le fichier
de la phase demandée**, plus `references/vault-structure.md` (le contrat de structure,
commun à toutes les phases).

| Phase | Déclencheur (user) | Workflow détaillé |
|-------|--------------------|-------------------|
| **1. Bootstrap** | "crée un cerveau pour X" / "initialise un vault pour X" | `references/phase-1-bootstrap.md` |
| **2. Compilation** | "compile le raw en wiki" / "synthétise ce que j'ai ajouté" | `references/phase-2-compilation.md` |
| **3. Linting** | "linte le cerveau" / "audit du vault" | `references/phase-3-linting.md` |
| **4. Connexion centrale** | "connecte ce cerveau au central" | `references/central-brain-protocol.md` |

**État** : la phase 1 est complètement implémentée. Les phases 2-4 ont leurs conventions
définies et s'enrichissent au fil des usages réels — enrichir le fichier de phase concerné,
ne modifier ce SKILL.md que si la philosophie ou le découpage en phases change.

## Fichiers du skill

- `references/vault-structure.md` — Arborescence complète + frontmatter + conventions de liens. Le contrat commun : bootstrap la crée, compilation y écrit, linting la vérifie, connexion centrale l'étend.
- `references/note-templates.md` — Templates YAML + squelettes de notes par type (phases 1 et 2).
- `references/central-brain-protocol.md` — Convention de liaison inter-vaults (phase 4).
- `references/phase-*.md` — Workflows détaillés des phases 1 à 3.
- `scripts/bootstrap_brain.py` — Création déterministe de la structure (phase 1). Autonome : templates et config Obsidian embarqués, idempotent.

## Principes de qualité

- **Un cerveau = un vault isolé.** Jamais de fusion forcée, la propreté d'isolation est un feature.
- **Markdown pur + YAML.** Pas de format propriétaire, pas de base de données. Le vault doit rester lisible dans `cat`.
- **L'utilisateur est copilote.** Tous les fichiers créés par l'IA peuvent être édités à la main sans casser le système.
- **Préparer l'avenir.** Même en phase 1, la structure est pensée pour accueillir compilation, linting, et liaison centrale sans refactor ultérieur.
- **Documenter les décisions.** Toute règle ou convention appliquée au cerveau est écrite dans `_meta/CONVENTIONS.md` — la mémoire du système sur lui-même.
