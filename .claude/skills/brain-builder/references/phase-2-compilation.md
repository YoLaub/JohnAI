# Phase 2 — Compilation raw → wiki

**Objectif** : lire le contenu de `raw/`, en extraire les entités et concepts, et mettre à jour les notes dans `wiki/`. Les squelettes de notes sont dans `note-templates.md`.

## Principes directeurs (à respecter même dans les itérations futures)

- **Jamais de modification de `raw/`.** C'est la source de vérité immuable.
- **Incrémental, pas régénératif.** Si une note `wiki/Auth.md` existe déjà, l'enrichir, pas la réécrire.
- **Toujours citer la source.** Chaque fait ajouté dans le wiki doit référencer le fichier raw d'origine via un lien Markdown ou un champ YAML `source:`.
- **Signaler les contradictions.** Si une nouvelle source contredit une note existante, créer une section `## Contradictions` plutôt que d'écraser.
- **Mettre à jour `wiki/INDEX.md`** à chaque compilation (ajout de nouvelles entités).

## Workflow

1. Lister les fichiers de `raw/` avec leur date de modif
2. Comparer avec le `_meta/COMPILATION_LOG.md` pour identifier ce qui est nouveau
3. Pour chaque nouvelle source, extraire les entités et les injecter dans `wiki/`
4. Logger l'opération dans `_meta/COMPILATION_LOG.md`

Détails à enrichir dans CE fichier au fil des usages réels (pas dans SKILL.md).
