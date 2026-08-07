# Formats produits par compile-rules

À lire aux étapes 4, 7 et 8 de la procédure.

## Entrée du sac (`bag.ndjson`)

Une ligne JSON par incident, append only, jamais d'édition :

```json
{"trigger":"", "symptom":"", "root_cause":"", "fix":"", "severity":1, "date":"YYYY-MM-DD"}
```

- `trigger` : les termes techniques exacts qui identifient le contexte
  ("relation polymorphe Strapi v5"), pas une description du bug. Clé de regroupement.
- `severity` : 1 friction · 2 rework · 3 irréversible (perte de données, CI verte à
  tort, prod).

## Règle promue — `$BRAIN/rules/<nom>.md`

Frontmatter OKF-compatible, corps de 6 lignes maximum :

```markdown
---
type: rule
title: <titre court>
description: <une ligne>
tags: [<mots-clés de routage>]
timestamp: <YYYY-MM-DD>
trigger: "<condition d'application>"
severity: <1-3>
scope: <PROJECT_KEY|global>
---

<règle, 6 lignes max>
```

Les `tags` sont ce sur quoi le routage matchera : stack, chemins touchés, type de tâche.
Un tag trop générique ("backend") ne route rien.

## Manifeste — `$BRAIN/MANIFEST.md`

Régénéré intégralement à chaque passe, jamais édité à la main :

```markdown
<!-- généré par compile-rules — ne pas éditer -->
| keywords | fichier |
|---|---|
| <tags> | rules/<fichier>.md |
```

## Rapport de passe

- entrées traitées / promues / archivées / restées au sac
- règles fusionnées, supprimées
- **taux de récidive** : erreurs loggées dont une règle couvrait déjà le trigger.
  Métrique principale — une récidive signifie que la règle existe mais que son trigger
  ne matche pas le contexte réel. Plus informatif que le nombre de règles.
- delta de taille de `rules/` : s'il grossit à chaque passe pendant que le sac grossit
  aussi, la compression ne fonctionne pas.
