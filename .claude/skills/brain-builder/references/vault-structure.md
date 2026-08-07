# Arborescence d'un cerveau projet

Structure standard créée au bootstrap. Cette structure est **le contrat** entre toutes les phases du skill : bootstrap la crée, compilation y écrit, linting la vérifie, connexion centrale l'étend.

## Vue d'ensemble

```
<project-name>-brain/
├── .obsidian/                    # Config Obsidian (optionnelle mais recommandée)
│   ├── app.json
│   ├── core-plugins.json
│   └── graph.json
│
├── raw/                          # COUCHE 1 : Sources immuables
│   ├── README.md                 # Règles d'utilisation du dossier
│   ├── docs/                     # PDF, transcripts, notes reçues
│   ├── code/                     # Dumps de code, fichiers de config
│   ├── conversations/            # Transcripts de chats importants
│   └── external/                 # Captures web, articles, refs
│
├── wiki/                         # COUCHE 2 : Mémoire active (l'IA écrit ici)
│   ├── INDEX.md                  # Map of Content racine — ENTRY POINT
│   │
│   ├── _meta/                    # Métadonnées du cerveau lui-même
│   │   ├── IDENTITY.md           # Qui/quoi est ce cerveau
│   │   ├── CONVENTIONS.md        # Règles appliquées par l'IA
│   │   ├── CENTRAL_LINKS.md      # Liens vers le cerveau central
│   │   └── COMPILATION_LOG.md    # Historique des compilations
│   │
│   ├── entities/                 # Entités nommées (personnes, services, outils)
│   ├── concepts/                 # Concepts abstraits, patterns, principes
│   ├── decisions/                # ADR — Architecture Decision Records
│   └── moc/                      # Maps of Content thématiques
│
├── reports/                      # COUCHE 3 : Analyses et conclusions
│   ├── linting/                  # Rapports de linting datés
│   └── analysis/                 # Analyses ponctuelles demandées
│
└── README.md                     # Doc du vault pour un humain qui arrive
```

## Règles par dossier

### `raw/`

- **Propriétaire** : humain uniquement (l'IA est en lecture seule)
- **Format** : n'importe lequel (PDF, MD, TXT, images, JSON, CSV…)
- **Convention de nommage** : `YYYY-MM-DD_slug-descriptif.ext` de préférence, pour tracer la chronologie
- **Ne JAMAIS** : supprimer automatiquement, modifier, réécrire

### `wiki/`

- **Propriétaire** : IA (l'humain peut éditer, mais le flux principal est IA-écrit)
- **Format** : Markdown uniquement, avec frontmatter YAML obligatoire
- **Convention de nommage** : `PascalCase.md` pour les entités (`AuthService.md`), `kebab-case.md` pour les MOC (`api-design-moc.md`)
- **Règle d'or** : chaque note est reliée à au moins une autre note du wiki OU à une source de `raw/`

#### Sous-dossiers de `wiki/`

- **`_meta/`** : ce dossier commence par `_` pour apparaître en haut dans Obsidian. Contient la mémoire du système sur lui-même.
- **`entities/`** : toute chose nommée qui existe dans le monde du projet (un utilisateur, un service, une API, un outil, une équipe)
- **`concepts/`** : notions abstraites, patterns, principes, vocabulaire métier
- **`decisions/`** : une note = une décision (ADR légère). Format : `YYYY-MM-DD-decision-slug.md`
- **`moc/`** : Maps of Content — index thématiques qui regroupent des notes par sujet

### `reports/`

- **Propriétaire** : IA (générés), humain (consultés)
- **Format** : Markdown avec frontmatter
- **Convention de nommage** : `YYYY-MM-DD_type-slug.md`
- **Durée de vie** : archivables sans perte (ce ne sont pas des sources primaires)

### `.obsidian/`

- Config minimale posée au bootstrap pour que l'ouverture du vault soit agréable immédiatement
- Ne pas versionner les fichiers de workspace (position des panneaux, etc.)

## Frontmatter YAML obligatoire

Toute note dans `wiki/` DOIT avoir ce frontmatter minimum :

```yaml
---
title: Nom lisible de la note
type: entity | concept | decision | moc | meta
created: 2026-04-16
updated: 2026-04-16
tags: [tag1, tag2]
source: "[[raw/docs/xxx.pdf]]"   # optionnel mais recommandé
status: draft | validated | deprecated
---
```

Les champs `source:` et `tags:` permettent aux phases ultérieures (compilation, linting) de faire leur travail de manière programmatique. Le linter signalera toute note sans frontmatter valide.

## Convention de liens

- **Liens internes au vault** : `[[NomDeNote]]` (style Obsidian wikilink)
- **Liens vers `raw/`** : `[[raw/docs/fichier.pdf]]` (chemin relatif depuis la racine du vault)
- **Liens inter-vaults (vers cerveau central)** : voir `central-brain-protocol.md` — pas de wikilink direct, utilisation d'un fichier de registre

## Qu'est-ce qui ne va PAS dans cette structure

Pour éviter les pièges classiques :

- ❌ Pas de `daily-notes/` — ce n'est pas un journal personnel, c'est une mémoire projet
- ❌ Pas de `templates/` dans le vault — les templates vivent dans le skill, pas dans chaque cerveau
- ❌ Pas de `attachments/` — les assets vont dans `raw/` avec leur source
- ❌ Pas d'imbrication profonde dans `wiki/` — maximum 2 niveaux, préférer les tags et les MOC
