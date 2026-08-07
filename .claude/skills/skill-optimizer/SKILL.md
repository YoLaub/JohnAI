---
name: skill-optimizer
description: >
  Optimise un skill existant par micro-éditions validées (approche SkillOpt).
  Traite le fichier SKILL.md comme du code soumis à un cycle itératif :
  baseline → proposition de micro-éditions → évaluation → commit ou revert.
  Déclenche ce skill dès que l'utilisateur mentionne : "optimiser un skill",
  "améliorer un skill", "mon skill ne marche pas bien", "affiner les instructions
  d'un agent", "le skill produit des résultats moyens", "améliorer un prompt système",
  "mon agent dérive", ou toute demande d'itération sur un fichier SKILL.md existant.
  Ne pas confondre avec skill-creator (création from scratch) — ici le skill existe déjà.
---

# Skill-Optimizer

Optimise un skill existant par petits pas contrôlés. L'idée centrale : traiter SKILL.md
comme du code source, avec des micro-commits validés par des tests, plutôt que de réécrire
en bloc au risque de dégrader ce qui fonctionnait.

## Principes fondamentaux

**Budget d'édition limité** — Chaque itération ne modifie que 1 à 4 blocs ciblés.
Jamais de réécriture complète. Comme un `git commit` atomique sur un prompt.

**Zones protégées** — Le SKILL.md est divisé en deux zones :
- `INVARIANTS` (Slow state) : nom, objectif fondamental, structure des livrables — **jamais modifié automatiquement**
- `OPTIMISABLE` (Fast state) : hints, exemples, nuances, formulations — **zone d'optimisation**

**Validation avant commit** — Une modification n'est acceptée que si le score de
l'eval set s'améliore. Sinon, on reverte et on propose une autre piste.

**Juge explicite** — Pour chaque test, un rubric clair détermine ce qui constitue
un "bon" résultat. Sans juge, la boucle ne peut pas tourner.

---

## Workflow complet

### Phase 0 : Lecture et diagnostic

Commence par lire le skill cible en entier. Puis pose les questions suivantes à l'utilisateur
si elles ne sont pas déjà répondues dans la conversation :

1. **Quel est le problème ?** Qu'est-ce que le skill fait de mal, ou pas assez bien ?
2. **As-tu des exemples de mauvais résultats ?** (optionnel mais précieux)
3. **Quel est le critère de succès ?** Comment savoir qu'une version est meilleure ?

Après lecture, produis un **diagnostic rapide** :

```
Skill analysé : [nom]
Taille actuelle : ~[N] tokens
Zone INVARIANTS identifiée : [oui/non — marquer si absente]
Zone OPTIMISABLE identifiée : [oui/non]
Problèmes potentiels repérés :
  - [observation 1]
  - [observation 2]
Hypothèse principale : [pourquoi le skill sous-performe]
```

Consulte `references/diagnostic-patterns.md` pour les anti-patterns courants.

---

### Phase 1 : Balisage du skill (si absent)

Si le skill cible ne distingue pas encore ses zones Slow/Fast, propose à l'utilisateur
d'ajouter les marqueurs. C'est optionnel mais fortement recommandé pour éviter la dérive.

```markdown
<!-- INVARIANTS — Ne pas modifier automatiquement -->
## Objectif
[règles fondamentales]
<!-- END INVARIANTS -->

<!-- OPTIMISABLE — Zone de micro-éditions -->
## Hints et nuances
[exemples, formulations, heuristiques]
<!-- END OPTIMISABLE -->
```

---

### Phase 2 : Construction de l'eval set

Construis 6 à 12 prompts de test représentatifs. Vise la couverture, pas la quantité :
- Cas nominal (le flux principal du skill)
- Cas limites (entrées ambiguës, incomplètes, ou inhabituelles)
- Cas de régression (ce qui doit absolument rester intact)

Pour chaque prompt, définis un **rubric de jugement** (voir format ci-dessous).
Sauvegarde dans `evals/evals.json`.

**Format evals.json :**
```json
{
  "skill_name": "nom-du-skill",
  "version_baseline": "chemin/vers/SKILL.md",
  "evals": [
    {
      "id": 1,
      "prompt": "Prompt tel que l'utilisateur le taperait",
      "rubric": {
        "criteres": [
          { "nom": "Complétude", "description": "Tous les livrables attendus sont présents", "poids": 3 },
          { "nom": "Précision", "description": "Les informations sont correctes et sourcées", "poids": 2 },
          { "nom": "Compacité", "description": "Pas de redondance ou de remplissage", "poids": 1 }
        ],
        "score_max": 12
      }
    }
  ]
}
```

Présente l'eval set à l'utilisateur avant de continuer. Demande : "Ces cas de test couvrent
bien les situations importantes ? Y a-t-il des manques ?"

---

### Phase 3 : Baseline

Commence par snapshotter le skill dans son état actuel :

```bash
python scripts/snapshot.py snapshot \
  --skill <chemin/vers/SKILL.md> \
  --workspace optimization-workspace/ \
  --iteration 0
```

Ensuite, exécute chaque prompt de l'eval set avec le skill actuel (via subagents ou
séquentiellement). Pour chaque résultat, applique le rubric et sauvegarde un fichier
`scores-eval-N.json` dans `optimization-workspace/iteration-0/` :

```json
{
  "eval_id": 1,
  "score_obtenu": 6,
  "score_max": 8,
  "criteres_scores": [
    { "nom": "Complétude", "poids": 3, "score_obtenu": 3, "note": "tous les livrables présents" },
    { "nom": "Précision",  "poids": 2, "score_obtenu": 2, "note": "aucune hallucination" },
    { "nom": "Structure",  "poids": 2, "score_obtenu": 1, "note": "section X manquante" },
    { "nom": "Compacité",  "poids": 1, "score_obtenu": 0, "note": "beaucoup de redondance" }
  ]
}
```

Puis agrège :

```bash
python scripts/score_eval.py --aggregate optimization-workspace/iteration-0/
```

Ce score est le zéro de référence. Aucune modification ne sera commitée si elle
n'améliore pas ce score.

---

### Phase 4 : Génération des micro-éditions

C'est le cœur de la boucle. Sur la base des prompts qui ont le moins bien scoré :

1. **Identifie la cause racine** — Pourquoi ce prompt a-t-il échoué ?
   - Instructions manquantes ?
   - Formulation ambiguë ?
   - Exemple contre-productif ?
   - Section trop longue qui noie l'essentiel ?

2. **Propose 1 à 4 modifications ciblées** — Format obligatoire :

```
MICRO-ÉDITION #1
Zone : [OPTIMISABLE / préciser la section]
Type : [ajout / suppression / reformulation / remplacement d'exemple]
Motivation : [quel prompt a échoué et pourquoi cette modification devrait aider]
---
AVANT :
[texte actuel]
---
APRÈS :
[texte proposé]
---
```

3. **Présente à l'utilisateur** — Attends confirmation avant d'appliquer.
   Si l'utilisateur valide :

   a. Snapshotte la version courante AVANT modification :
   ```bash
   python scripts/snapshot.py snapshot \
     --skill <chemin/vers/SKILL.md> \
     --workspace optimization-workspace/ \
     --iteration <N>
   ```

   b. Applique les modifications via `str_replace` sur le SKILL.md cible.

   c. Génère le diff pour garder une trace :
   ```bash
   python scripts/snapshot.py diff \
     --before optimization-workspace/iteration-<N-1>/ \
     --after  optimization-workspace/iteration-<N>/
   ```

   Si l'utilisateur refuse, propose une alternative sans toucher au fichier.

**Règle du budget :** Si tu as envie de faire plus de 4 modifications, c'est le signal
qu'il faut d'abord comprendre mieux le problème. Relis le diagnostic, et choisis les
2 modifications les plus impactantes.

Consulte `references/edit-patterns.md` pour les types de modifications les plus efficaces.

---

### Phase 5 : Validation (score après édition)

Rejoue l'eval set complet sur la version modifiée. Sauvegarde les `scores-eval-N.json`
dans `optimization-workspace/iteration-<N>/`, puis compare :

```bash
python scripts/score_eval.py \
  --compare optimization-workspace/iteration-<N-1>/ \
             optimization-workspace/iteration-<N>/
```

Le script affiche et sauvegarde automatiquement un `comparison.json` avec la décision :

**Règle de décision (appliquée par le script) :**
- Delta positif ET aucune régression → **COMMIT**
- Delta positif MAIS régressions détectées → **DISCUSSION** avec l'utilisateur
- Delta nul ou négatif → **REVERT** + nouvelle hypothèse

En cas de REVERT, restaure le SKILL.md depuis le snapshot :
```bash
cp optimization-workspace/iteration-<N-1>/SKILL.md <chemin/vers/SKILL.md>
```

---

### Phase 6 : Itération

Répète les phases 4 et 5 jusqu'à l'une de ces conditions :

- L'utilisateur est satisfait du résultat
- Le score dépasse 85% sur l'eval set
- 3 itérations consécutives sans amélioration notable (→ signal que l'eval set
  lui-même est peut-être le problème — propose de l'enrichir)
- Le skill a atteint sa taille cible (~700-1000 tokens pour un skill courant)

---

### Phase 7 : Rapport final

```bash
python scripts/generate_report.py \
  --workspace optimization-workspace/ \
  --skill-name <nom-du-skill>
```

Le rapport est sauvegardé dans `optimization-workspace/rapport-optimisation.md`.
Présente-le à l'utilisateur avec `present_files`.

---

## Fichiers de sortie

```
optimization-workspace/
├── iteration-0/
│   ├── SKILL.md          ← snapshot baseline (read-only)
│   └── scores.json       ← résultats eval baseline
├── iteration-1/
│   ├── SKILL.md          ← version après itération 1
│   ├── scores.json
│   └── diff.md           ← les micro-éditions appliquées
├── ...
├── SKILL_final.md        ← version finale optimisée
└── rapport-optimisation.md
```

---

## Rappels importants

- Ne jamais modifier les INVARIANTS sans accord explicite de l'utilisateur.
- Toujours sauvegarder avant de modifier.
- La compacité est une qualité : un skill de 800 tokens bien ciblé bat un skill de 2000 tokens verbeux.
- Si le juge (rubric) est flou, l'optimisation est aveugle. Passe du temps sur la Phase 2.
- Les modifications qui "paraissent bonnes" sans validation par l'eval set sont des
  intuitions, pas des améliorations. Teste toujours.
