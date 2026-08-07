# Templates de notes

Chaque type de note dans `wiki/` a un template standard. Ces templates sont utilisés à la fois au bootstrap (pour les fichiers d'amorce) et pendant la compilation (pour les nouvelles notes créées automatiquement).

## Règle universelle

Toute note commence par un frontmatter YAML. **Pas de note sans frontmatter.** Le linter refusera les notes non conformes.

---

## Template : Entité (`type: entity`)

Pour tout "truc nommé" du projet : un service, une personne, une API, un outil, une librairie.

```markdown
---
title: AuthService
type: entity
category: service
created: 2026-04-16
updated: 2026-04-16
tags: [backend, auth]
source: "[[raw/docs/2026-04-15_auth-spec.md]]"
status: validated
aliases: ["Auth", "Service d'authentification"]
---

# AuthService

> Résumé en 1-2 phrases de ce qu'est cette entité et pourquoi elle existe.

## Rôle

Ce que fait cette entité dans le système.

## Interactions

- Consomme : [[UserService]], [[RedisCache]]
- Exposé à : [[APIGateway]]

## État actuel

Faits établis, version, configuration.

## Décisions liées

- [[2026-04-10-decision-jwt-vs-session]]

## Questions ouvertes

- [ ] Rotation des tokens non implémentée

## Sources

- [[raw/docs/2026-04-15_auth-spec.md]]
```

---

## Template : Concept (`type: concept`)

Pour les notions abstraites, patterns, vocabulaire métier.

```markdown
---
title: Document Service Pattern
type: concept
created: 2026-04-16
updated: 2026-04-16
tags: [strapi, v5, pattern]
source: "[[raw/external/strapi-v5-docs.md]]"
status: validated
---

# Document Service Pattern

> Pattern de Strapi v5 où chaque entité a un `documentId` distinct de l'ID SQL primaire.

## Définition

Explication claire et concise.

## Pourquoi c'est important

Contexte d'application dans le projet.

## Exemples concrets

- Dans [[AuthService]], utiliser `user.documentId` pour les opérations via document service
- Dans les requêtes SQL raw, `user.id` reste l'ID primaire

## Pièges courants

- Confondre `id` et `documentId` dans les tests d'intégration

## Références

- [[raw/external/strapi-v5-docs.md]]
- [[ADR-2026-04-01-strapi-v5-migration]]
```

---

## Template : Décision (`type: decision`)

Format ADR léger. Une décision = une note. Nom de fichier : `YYYY-MM-DD-slug.md`.

```markdown
---
title: Choix de Jest pour les tests d'intégration backend
type: decision
created: 2026-04-16
updated: 2026-04-16
tags: [testing, jest, backend]
status: validated
supersedes: null
superseded_by: null
---

# Choix de Jest pour les tests d'intégration backend

## Contexte

Pourquoi cette décision se pose, quand.

## Options considérées

1. **Jest** — avantages, inconvénients
2. **Vitest** — avantages, inconvénients
3. **Mocha + Chai** — avantages, inconvénients

## Décision

Option retenue et raisons principales.

## Conséquences

- Positives : [...]
- Négatives : [...]

## Notes liées

- [[TestingStrategy]]
- [[JestConfig]]
```

---

## Template : Map of Content — MOC (`type: moc`)

Point d'entrée thématique. Regroupe les notes liées sans les contenir.

```markdown
---
title: Authentication MOC
type: moc
created: 2026-04-16
updated: 2026-04-16
tags: [auth, moc]
status: validated
---

# Authentication — Map of Content

> Point d'entrée pour tout ce qui concerne l'authentification dans ce projet.

## Entités

- [[AuthService]]
- [[JWTManager]]
- [[RefreshTokenStore]]

## Concepts

- [[Document Service Pattern]]
- [[JWT Rotation Strategy]]

## Décisions

- [[2026-04-10-decision-jwt-vs-session]]
- [[2026-03-15-decision-refresh-token-ttl]]

## Sources brutes clés

- [[raw/docs/2026-04-15_auth-spec.md]]

## Questions en suspens

- [ ] Stratégie de révocation en cas de fuite
- [ ] Intégration avec le SSO futur
```

---

## Template : Note meta (`type: meta`)

Pour les fichiers dans `wiki/_meta/`. Documentent le cerveau lui-même.

### `IDENTITY.md`

```markdown
---
title: Identité du cerveau
type: meta
created: 2026-04-16
updated: 2026-04-16
---

# Identité

## Nom du projet

{project_name}

## Description

{1-2 phrases sur le projet}

## Périmètre

Ce qui appartient à ce cerveau :
- ...

## Hors-périmètre

Ce qui N'appartient PAS à ce cerveau (et vit dans le central ou ailleurs) :
- ...

## Stack technique

{stack}

## Rôles utilisateurs

- ...
```

### `CONVENTIONS.md`

```markdown
---
title: Conventions appliquées à ce cerveau
type: meta
created: 2026-04-16
updated: 2026-04-16
---

# Conventions

## Nommage
- Entités : `PascalCase.md`
- MOC : `kebab-case.md`
- Décisions : `YYYY-MM-DD-slug.md`

## Liens
- Wikilinks `[[...]]` pour l'intra-vault
- Références explicites vers `raw/` pour toute source

## Frontmatter
- `title`, `type`, `created`, `updated`, `tags`, `status` : obligatoires
- `source` : obligatoire si la note dérive d'un raw
- `aliases` : recommandé pour les entités

## Workflow
- Compilation incrémentale : les notes existantes sont enrichies, pas réécrites
- Contradictions : section `## Contradictions` plutôt qu'écrasement
```

### `CENTRAL_LINKS.md`

```markdown
---
title: Liens vers le cerveau central
type: meta
created: 2026-04-16
updated: 2026-04-16
---

# Liens vers le cerveau central

> Ce fichier sert d'interface entre ce cerveau projet et le cerveau central.
> Il est initialement vide. Voir `brain-builder/references/central-brain-protocol.md`
> pour la convention de liaison.

## Statut

- [ ] Cerveau central initialisé
- [ ] Chemin du central renseigné ci-dessous
- [ ] Concepts partagés référencés

## Chemin du central

_(à renseigner, ex: `~/ObsidianVaults/central-brain/`)_

## Concepts hébergés dans le central et référencés ici

_(vide pour l'instant)_
```

### `COMPILATION_LOG.md`

```markdown
---
title: Historique des compilations
type: meta
created: 2026-04-16
updated: 2026-04-16
---

# Historique des compilations

Chaque entrée trace un cycle de compilation `raw/` → `wiki/`.

## Format d'entrée

```
## YYYY-MM-DD HH:MM
- Sources lues : [liste]
- Notes créées : [liste]
- Notes mises à jour : [liste]
- Contradictions détectées : [liste]
- Notes : [commentaires libres]
```

## Entrées

_(aucune compilation effectuée — log vide)_
```

---

## INDEX.md racine

Ce fichier est **l'entry point du vault dans Obsidian**. Il doit toujours exister et être à jour.

```markdown
---
title: Index
type: moc
created: 2026-04-16
updated: 2026-04-16
---

# {Project Name} — Cerveau projet

> {Description courte}

## Méta

- [[_meta/IDENTITY|Identité du projet]]
- [[_meta/CONVENTIONS|Conventions]]
- [[_meta/CENTRAL_LINKS|Liens cerveau central]]
- [[_meta/COMPILATION_LOG|Log des compilations]]

## Maps of Content

_(vides au bootstrap — à enrichir au fur et à mesure)_

## Entités principales

_(vides au bootstrap)_

## Décisions récentes

_(vides au bootstrap)_
```
