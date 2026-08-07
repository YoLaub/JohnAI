# Fiche OKF — format

Une fiche par feature dans `docs/index/<feature>.md`. Entête YAML + corps ≤ 15 lignes.
Objectif : recharger le contexte d'une feature en une lecture, sans rescanner le code.

## Template

```markdown
---
id: okf-<numéro séquentiel>
feature: <nom court>
branch: feature/<nom>
status: done | wip | blocked
files:
  - <chemins des fichiers créés/modifiés significatifs>
tests:
  - <chemins des fichiers de tests>
decisions:
  - "<AAAA-MM-JJ> : <décision> (<raison en une phrase>)"
---

**Quoi** : <ce que fait la feature, 2-3 lignes max>

**Pièges** : <ce qui a mordu pendant l'implémentation, un tiret par piège>
```

## Règles
- Corps ≤ 15 lignes : si ça dépasse, la feature est trop grosse ou la fiche trop bavarde.
- Toujours dater les décisions (date absolue, pas « aujourd'hui »).
- Les pièges génériques (réutilisables hors du projet) remontent aussi dans
  `references/pieges.md` du skill ; les pièges spécifiques au projet vont dans `retro.md`.
