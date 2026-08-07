---
name: init-projet
description: >
  Initialise un nouveau projet en rédigeant d'abord son CLAUDE.md via une série de
  questions fermées (QCM), afin de capturer le contexte une bonne fois pour toutes et
  d'optimiser les sessions suivantes. Amorce ensuite le BRAIN du projet
  (`~/brain/<projet>/`) et le bloc de journalisation des erreurs.
  Intentions déclenchantes : "init projet", "initialise le projet", "nouveau projet",
  "démarre le projet", "crée le CLAUDE.md", "bootstrap le projet".
  Ne pas confondre avec compile-rules, qui compile ce journal en règles une fois rempli.
---

# Init Projet — Cadrage par questions fermées → CLAUDE.md

## Principe
Le CLAUDE.md est le contrat de session : tout ce qui y est écrit n'aura plus jamais à
être demandé à l'utilisateur. Ce skill commence donc **toujours** par la rédaction (ou
la mise à jour) du CLAUDE.md, et ne génère **aucun code** tant que le CLAUDE.md n'est
pas validé par l'utilisateur.

## Règles de questionnement
- **Questions fermées uniquement** : oui/non ou choix multiples (2 à 4 options),
  posées via l'outil `AskUserQuestion`. Jamais de question ouverte, sauf pour un fait
  brut impossible à deviner (nom, adresse, téléphone).
- **4 questions maximum par salve**, regroupées par thème. S'arrêter dès que le
  CLAUDE.md peut être rédigé sans inventer.
- **Proposer une option recommandée** en premier, marquée "(Recommandé)", avec la
  raison en description — l'utilisateur doit pouvoir tout valider en un clic.
- Ne jamais demander ce qui est déjà déductible : fichiers existants, git, exemples
  fournis, conversation en cours.

## Déroulé

### 1. Reconnaissance (sans question)
Lire ce qui existe déjà : racine du repo, `CLAUDE.md` ou exemple fourni,
`docs/index/`, `.claude/`. En tirer le maximum de contexte avant toute question.

### 2. Salves de questions fermées
Couvrir dans l'ordre, une salve par thème, en sautant tout thème déjà connu :
1. **Contexte métier** — type de projet, client, problème n°1 à résoudre, public cible.
2. **Périmètre** — fonctionnalités incluses / exclues du premier livrable.
3. **Stack & hébergement** — framework, base de données éventuelle, cible de déploiement.
4. **Méthode** — TDD ou non, stratégie git, niveau d'autonomie accordé à Claude
   (demander validation à chaque étape vs avancer seul et rendre compte).

### 3. Rédaction du CLAUDE.md
Rédiger à la racine du projet en suivant le gabarit et les bonnes pratiques de
[references/bonnes-pratiques-claude-md.md](references/bonnes-pratiques-claude-md.md).
Marquer explicitement `_à décider_` ce qui n'a pas pu être tranché — jamais de valeur
inventée.

Avant de rédiger, vérifier la présence du bloc **Mode de collaboration** dans
`~/.claude/CLAUDE.md` (chercher la ligne « Le désaccord est attendu »).
- **Présent** → ne pas le recopier dans le CLAUDE.md du projet ; il s'applique déjà à
  toutes les sessions de la machine.
- **Absent** (nouvelle machine, `~/.claude/CLAUDE.md` inexistant) → proposer en question
  fermée : l'ajouter à `~/.claude/CLAUDE.md` (recommandé, une seule source pour tous les
  projets) ou l'inscrire dans le CLAUDE.md du projet seul.

Le texte de référence du bloc est dans
[references/bonnes-pratiques-claude-md.md](references/bonnes-pratiques-claude-md.md).
Il est recopié mot pour mot : aucun résumé, aucune reformulation, aucune question sur
son contenu.

### 4. Validation
Présenter le CLAUDE.md, demander une validation (question fermée : valider / ajuster).

### 5. Amorçage du BRAIN et du journal d'erreurs
Une fois le CLAUDE.md validé seulement, dérouler
[references/journal-erreurs.md](references/journal-erreurs.md) : arborescence
`~/brain/<PROJECT_KEY>/`, bloc de journalisation appendé au CLAUDE.md, bloc de routage
laissé dormant. Écriture en APPEND uniquement, jamais de duplication d'un bloc existant.

### 6. Suite
Proposer l'étape suivante (bootstrap du repo, première feature) — par exemple via le
skill `greenfield-tdd-okf` s'il est disponible.

## Sortie
- `CLAUDE.md` à la racine du projet, validé par l'utilisateur.
- `~/brain/<PROJECT_KEY>/` : `rules/`, `bag.ndjson` vide, `PENDING-rules-block.md`.
- `~/brain/global/rules/`.
- Zéro autre fichier généré par ce skill.

## Évolution de ce skill
- Gabarit du CLAUDE.md et règles de rédaction → `references/bonnes-pratiques-claude-md.md`.
- Mécanique BRAIN / journal d'erreurs → `references/journal-erreurs.md`.
- Ne modifier ce SKILL.md que si le déroulé de cadrage change.
