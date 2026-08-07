# Seuils de compilation

Fichier **append-only** : chaque recalibrage ajoute une section datée sous les seuils
courants, sans réécrire l'historique. À lire aux étapes 2, 3 et 5 de la procédure.

## Seuils courants (2026-07-24 — initiaux, non calibrés)

**Promotion** — `score = Σ severity des occurrences du groupe`
- score ≥ 5 → candidat à la promotion
- toute occurrence severity 3 → candidat immédiat
- sinon → reste au sac

**Décroissance** — dernière occurrence > 90 jours ET score < seuil de promotion →
proposer l'archivage vers `bag-archive.ndjson`. Du bruit, pas un pattern.

**Démotion** — règle existante à 0 hit d'index sur 20 sessions ou 3 mois → proposer
suppression ou reformulation du trigger.

**Promotion globale** — confirmée indépendamment dans ≥ 2 projets.

## Protocole de recalibrage

À la première passe d'un projet, afficher la distribution des scores et proposer un
recalibrage AVANT d'appliquer quoi que ce soit. Les seuils ci-dessus sont des points de
départ, pas des constantes.

Un recalibrage s'écrit ici sous la forme :

```
## <YYYY-MM-DD> — <projet> : <seuil modifié>
Ancienne valeur → nouvelle valeur.
Observation qui l'a motivé (distribution, taux de récidive, volume de rules/).
```

Signal qu'un seuil est trop bas : `rules/` grossit à chaque passe sans que le taux de
récidive baisse. Signal qu'il est trop haut : le même trigger réapparaît au sac passe
après passe sans jamais promouvoir.
