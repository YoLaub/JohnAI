---
name: compile-rules
description: >
  Compile le journal d'erreurs d'un projet (`bag.ndjson`) en règles projet : regroupement
  par trigger, scoring, promotion, démotion, régénération du MANIFEST de routage.
  Déclenche quand l'utilisateur dit "fais la passe de compilation", "traite le sac
  d'erreurs", "compile le bag", "mets à jour les règles du projet", "compile-rules".
  Ne se déclenche JAMAIS automatiquement : uniquement sur demande explicite.
  Ne pas confondre avec brain-builder (vault Obsidian de connaissances, raw/wiki/reports)
  ni avec init-projet (qui amorce le BRAIN et le bloc de journalisation) — ici on ne fait
  que transformer un journal d'incidents en règles.
---

# Compilation sac → règles

**Écriture interdite.** Ce skill produit un diff proposé. Toute modification de `rules/`
ou de `MANIFEST.md` est validée par l'utilisateur avant application.

## Résolution du projet
Lire la ligne `BRAIN:` du CLAUDE.md courant. Absente → demander, ne pas deviner.
Le global est toujours `~/brain/global/`.

## Entrées
- `$BRAIN/bag.ndjson`
- `$BRAIN/rules/*.md`
- `~/brain/global/rules/*.md`

## Procédure

1. **Regrouper** — grouper par `trigger` (match exact), puis proposer la fusion des
   quasi-doublons. Précondition : ≥ 20 entrées dans le sac, sinon stop et signaler le
   volume insuffisant.
2. **Scorer** — appliquer les seuils de [references/seuils.md](references/seuils.md)
   (à lire à cette étape, pas avant).
3. **Décroissance** — archiver les groupes dormants vers `bag-archive.ndjson` selon les
   mêmes seuils. L'ancienneté ne promeut jamais : elle fait décroître.
4. **Rédiger** — pour chaque candidat : condition d'application explicite (le `trigger`
   devient la condition), action et non anecdote ("faire X" / "ne pas faire Y", jamais
   "on a eu un bug où…"). Si la formulation dépasse ~6 lignes, la cause racine est mal
   cernée → ne pas promouvoir, signaler. Format et frontmatter :
   [references/formats.md](references/formats.md). Vérifier le recouvrement avec les
   règles existantes : deux règles qui se recoupent fusionnent en une règle plus
   générale — ne jamais empiler.
5. **Démotion** — lire le compteur de hits d'index de chaque règle existante ; sous le
   seuil de `references/seuils.md`, proposer suppression ou reformulation du trigger.
   Une règle jamais routée n'atteint rien, indépendamment de sa qualité.
6. **Promotion globale** — une règle monte dans `global/` uniquement si confirmée
   indépendamment dans ≥ 2 projets. "Ça a l'air général" ne suffit pas : une règle
   globale fausse est fausse partout et son effet est diffus. Par défaut, tout naît local.
7. **Régénérer le manifeste** — reconstruire `$BRAIN/MANIFEST.md` intégralement depuis
   les frontmatter de `rules/` (format dans `references/formats.md`). Jamais d'édition
   incrémentale : la dérive manifeste/règles est un échec silencieux.
8. **Rapport** — gabarit dans `references/formats.md`. La métrique principale est le
   **taux de récidive**, pas le nombre de règles.

## Après la première passe réussie
Si `$BRAIN/PENDING-rules-block.md` existe, proposer de coller son contenu dans le
CLAUDE.md du projet et de supprimer le fichier : `rules/` n'est plus vide, le bloc de
routage a désormais un manifeste à lire.

## Évolution de ce skill
- Recalibrage de seuils → `references/seuils.md` (append-only, sections datées).
- Changement de format de règle, de manifeste ou de rapport → `references/formats.md`.
- Ne modifier ce SKILL.md que si la procédure elle-même change.
