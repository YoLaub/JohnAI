---
name: skill-architect
description: >
  Conçoit l'architecture d'un nouveau skill ou refactore la structure d'un skill existant
  en transposant SOLID et les design patterns aux skills : une intention utilisateur par
  skill, découpage des fichiers par vitesse de changement, progressive disclosure
  (SKILL.md façade mince + references/ chargées à la demande), fichiers de connaissances
  append-only, règles d'évolution écrites dans le skill lui-même. Déclenche quand
  l'utilisateur dit : "crée un skill", "nouveau skill", "architecture d'un skill",
  "découpe ce skill", "refactore ce skill", "mon SKILL.md est trop gros", "applique SOLID
  à ce skill", "structure ce skill". Ne pas confondre avec skill-optimizer (itération sur
  le CONTENU d'un SKILL.md par micro-éditions mesurées) — ici on travaille la STRUCTURE :
  responsabilités, découpage en fichiers, patterns, câblage de la croissance future.
---

# Skill-Architect

Méthode d'architecture de skills éprouvée sur des refactors réels (2026-07). Deux
entrées : **créer** un skill (phases 1→4) ou **refactorer** un skill existant (phase 0
puis 2→4). Ce skill est autonome : tous ses exemples et principes sont auto-portants,
aucune dépendance à d'autres skills.

Références (à lire au moment indiqué, pas avant) :
- `references/principes.md` — SOLID transposé aux skills + les ruptures d'analogie. Lire en phase 2.
- `references/patterns.md` — les 4 patterns de skills + test décisionnel. Lire en phase 2.
- `references/checklist-revue.md` — lint de sortie. Lire en phase 4.

## Phase 0 — Diagnostic (refactor uniquement)

1. Lire le SKILL.md et lister le contenu du dossier (`Glob **/*`).
2. Identifier les responsabilités mélangées : pour chaque bloc, demander « qu'est-ce qui
   le fait changer, et à quelle fréquence ? ». Un fichier qui contient deux vitesses de
   changement (workflow stable + connaissances accumulées) est le symptôme n°1.
3. Chercher le texte qui programme le gonflement : toute instruction du type « mettre à
   jour ce skill avec X » condamne SKILL.md à grossir — X doit aller dans une référence.
4. Traquer les références mortes : fichiers/dossiers mentionnés mais absents, options de
   scripts documentées mais non implémentées, noms d'outils obsolètes.
5. Restituer le diagnostic à l'utilisateur AVANT de toucher aux fichiers.

## Phase 1 — Cadrage (création uniquement)

1. Formuler l'intention utilisateur en une phrase : « quand l'utilisateur veut ___ ».
   Plusieurs intentions sans rapport = plusieurs skills.
2. Vérifier la frontière avec les skills existants (une source de vérité par sujet) :
   si les déclencheurs chevauchent un skill voisin, soit fusionner, soit expliciter la
   désambiguïsation dans les DEUX descriptions.
3. Recenser ce que le skill devra accumuler avec le temps (pièges, exemples, sections
   par stack…) : c'est ça qui dimensionne le découpage, pas la taille initiale.

## Phase 2 — Architecture

1. Choisir le pattern avec le test décisionnel de `references/patterns.md` :
   phases séquentielles = Template Method ; points d'entrée indépendants = Facade +
   un fichier par phase ; orchestration d'agents = Pipeline ; variantes = Strategy.
2. Découper par vitesse de changement (`references/principes.md`) :
   - SKILL.md = le cœur stable (workflow, routage, philosophie). Cible : ≤ 70 lignes.
   - `references/` = ce qui grossit (connaissances append-only, sections datées) et ce
     qui n'est utile qu'à une étape (templates, protocoles, checklists).
   - `scripts/` = ce qui doit être déterministe et rejouable. Un script est AUTONOME :
     templates embarqués, pas de dépendance à des assets à côté.
3. Fragmenter en fichiers avant de fragmenter en skills : l'indirection entre skills
   coûte un déclenchement probabiliste ; l'indirection entre fichiers ne coûte rien.

## Phase 3 — Écriture

1. La description du frontmatter est l'interface publique : verbes d'intention +
   formulations littérales de l'utilisateur ("mon X ne marche pas", "découpe ce Y") +
   désambiguïsation avec les voisins. C'est elle qui décide du déclenchement.
2. Chaque pointeur vers une référence dit QUAND la lire (« à lire en phase N, pas
   avant ») — la progressive disclosure ne marche que si elle est écrite.
3. Écrire les règles d'évolution DANS le skill : quel fichier enrichir pour quel type
   d'ajout, et la clause « ne modifier SKILL.md que si la méthodologie change ».
4. En refactor : déplacement VERBATIM du contenu, zéro perte d'information. Reclasser,
   ne pas réécrire.

## Phase 4 — Revue & intégration

1. Dérouler `references/checklist-revue.md` sur le résultat.
2. Vérifier les scripts modifiés (`python -m py_compile`, `bash -n`…).
3. Intégrer au catalogue du dépôt : tableau + arborescence du README, et entrée
   CATALOGUE + bundle dans install.sh s'il existe.
4. Ne pas committer sans demande explicite de l'utilisateur.
