# Bonnes pratiques CLAUDE.md

## Ce qu'est un CLAUDE.md
Un fichier chargé automatiquement en début de **chaque** session. Chaque ligne coûte du
contexte à chaque session : il doit être court, dense, et ne contenir que ce que Claude
ne peut pas déduire seul du code.

## Gabarit

```markdown
# CLAUDE.md — Conventions du repo <NOM>

## Contexte
<Qui est le client, quel est le problème n°1 à résoudre, en 3-5 lignes.
Mettre en gras le problème central : c'est lui qui arbitre toutes les décisions.>

## Objectifs
<Liste numérotée, ordonnée par priorité. Le n°1 répond au problème n°1.>

## Contraintes
<Ce qui limite les choix : budget, compétences du client, mobile-first, délais.>

## Décisions techniques
<Stack, hébergement, domaine. Marquer `_à décider_` ce qui n'est pas tranché —
ne JAMAIS inventer une décision.>

## Méthode
<Stratégie git, tests, index de session (ex. OKF dans docs/index/), niveau
d'autonomie accordé à Claude.>

## Mode de collaboration
<Section OMISE si le bloc est déjà présent dans ~/.claude/CLAUDE.md.
Sinon, recopiée telle quelle, jamais reformulée :>

- Les skills et agents sont des outils à ta disposition, pas des scripts à exécuter.
  Si une skill ne colle pas au contexte, dis-le et propose autre chose.
- Le désaccord est attendu. Si mon approche est mauvaise, dis-le avant d'exécuter.
- Incertitude > confiance fabriquée. "Je ne sais pas" est une réponse valide.
- Je te donne le pourquoi, pas seulement le quoi. Si le pourquoi manque, demande-le.
- Ne performe pas d'états internes que tu ne peux pas vérifier, dans un sens
  comme dans l'autre.

## Règles métier clés
<Les règles que le code doit respecter et que Claude ne peut pas deviner :
exigences légales, sources de vérité des données, interdits.>

## Commandes
<dev / test / build / deploy. Compléter dès que la stack est choisie.>
```

La ligne `BRAIN:` et la section `## Journal d'erreurs` sont **appendées après coup**, à
l'étape 5 du skill — ne pas les rédiger ici. Voir
[journal-erreurs.md](journal-erreurs.md).

## Règles de rédaction
1. **Court** : viser ≤ 60 lignes. Si une section grossit, la déplacer dans `docs/` et
   ne garder qu'un pointeur.
2. **Impératif et vérifiable** : « les prix vivent dans `src/data/` », pas « il serait
   bien de centraliser les prix ». Une règle qu'on ne peut pas vérifier ne sert à rien.
3. **Rien de déductible** : pas de description de l'arborescence, pas d'historique —
   le code et git les portent déjà. Le CLAUDE.md porte l'**intention** et les
   **interdits**.
4. **Source de vérité unique** : toute donnée métier (prix, horaires, coordonnées) a
   un emplacement canonique désigné dans le fichier.
5. **Jamais inventer** : un fait métier inconnu (prix, horaire, nom de domaine) est
   marqué `_à décider_` et redemandé au client — jamais rempli avec une valeur plausible.
6. **Mettre à jour, pas empiler** : quand une décision `_à décider_` est tranchée,
   remplacer la mention ; quand une règle change, réécrire la ligne. Le fichier décrit
   l'état courant, pas son historique.
7. **Mode de collaboration non négociable** : ce bloc a une seule source de vérité,
   `~/.claude/CLAUDE.md`. S'il y figure déjà, ne pas le dupliquer dans le projet ; sinon
   l'y écrire (ou, à défaut, dans le CLAUDE.md du projet). Dans tous les cas il est
   recopié mot pour mot, ne se résume pas, et ne compte pas dans le budget de 60 lignes.
8. **Le gras arbitre** : une seule idée en gras par section maximum — celle qui doit
   trancher les conflits de priorité.
