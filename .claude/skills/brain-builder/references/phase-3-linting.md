# Phase 3 — Linting du cerveau

**Objectif** : garantir la cohérence et l'intégrité du cerveau. Le contrat à vérifier
(frontmatter obligatoire, conventions de nommage et de liens) est défini dans `vault-structure.md`.

## Vérifications minimales

- Liens Markdown cassés (`[[NoteInexistante]]`)
- Notes orphelines (aucun lien entrant ni sortant)
- Champs YAML obligatoires manquants (`created`, `tags`, `source`)
- Duplications sémantiques (deux notes sur le même sujet avec noms proches)
- Notes dans `wiki/` sans aucune référence à une source de `raw/`

## Sortie

Le linting produit un rapport dans `reports/linting/YYYY-MM-DD-lint-report.md` avec une
section "action items" priorisée. Les concepts détectés comme génériques (candidats à la
migration vers le cerveau central) sont listés dans `_meta/CENTRAL_LINKS.md`, section
« Migrations suggérées ».

Détails à enrichir dans CE fichier au fil des usages réels (pas dans SKILL.md).
