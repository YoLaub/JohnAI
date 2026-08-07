# Patterns de diagnostic — Skill-Optimizer

Ce fichier liste les anti-patterns courants dans les skills sous-performants.
Consulte-le pendant la Phase 0 pour orienter le diagnostic.

---

## Anti-patterns structurels

### 1. Le skill "encyclopédie"
**Symptôme :** SKILL.md dépasse 2000 tokens. Chaque section est exhaustive.
**Effet :** L'agent charge trop de contexte inutile et noie les instructions clés.
**Signal dans les outputs :** Résultats corrects mais incomplets, ou qui oublient des
étapes pourtant documentées dans le skill.
**Piste de correction :** Identifier les 20% d'instructions qui produisent 80% de la
valeur. Déplacer le reste dans des fichiers `references/` chargés à la demande.

---

### 2. Le skill "liste de règles"
**Symptôme :** Le skill est une liste de MUST/NEVER/TOUJOURS sans explication du pourquoi.
**Effet :** L'agent suit les règles mécaniquement sans comprendre l'intention, et déraille
dès qu'un cas légèrement différent se présente.
**Signal dans les outputs :** Bon sur les cas nominaux, mauvais sur les cas limites.
**Piste de correction :** Remplacer chaque règle par une explication de l'intention +
un exemple. "Fais X parce que Y" bat "TOUJOURS faire X".

---

### 3. Le skill "sans zone protégée"
**Symptôme :** Pas de distinction entre ce qui est fondamental et ce qui est ajustable.
**Effet :** Lors d'optimisations successives, l'objectif fondamental du skill dérive
progressivement. Le skill devient quelque chose de différent de ce qui était prévu.
**Signal dans les outputs :** Les résultats récents sont différents des anciens sans
raison apparente.
**Piste de correction :** Baliser les INVARIANTS avant toute optimisation (Phase 1).

---

### 4. Le skill "sans exemples"
**Symptôme :** Les instructions sont abstraites, sans cas concrets.
**Effet :** L'agent interprète les instructions différemment selon les sessions.
Résultats incohérents d'une fois à l'autre.
**Signal dans les outputs :** Haute variance — parfois excellent, parfois raté.
**Piste de correction :** Ajouter 1 à 3 exemples "Avant/Après" dans la zone OPTIMISABLE.
Les exemples ancrent l'interprétation mieux que les descriptions abstraites.

---

### 5. Le skill "too clever"
**Symptôme :** Le skill tente de tout anticiper, avec des branches conditionnelles complexes
("si A alors B, sauf si C, dans ce cas D sauf quand E...").
**Effet :** L'agent passe du temps à naviguer la logique conditionnelle plutôt qu'à
exécuter la tâche.
**Signal dans les outputs :** Lenteur, sur-réflexion, parfois paralysie ou demande
de clarification excessive.
**Piste de correction :** Simplifier la logique. Faire confiance au bon sens de l'agent
pour les cas non couverts plutôt que de tout pré-spécifier.

---

### 6. Le skill "description mal calibrée"
**Symptôme :** Le skill ne se déclenche pas quand il devrait, ou se déclenche quand
il ne devrait pas.
**Effet :** Mauvais routage. L'utilisateur doit invoquer le skill manuellement.
**Signal :** Feedbacks du type "j'ai dû rappeler que tu avais ce skill".
**Piste de correction :** Retravailler le champ `description` du frontmatter YAML.
C'est le mécanisme de déclenchement. Voir la section Description Optimization dans skill-creator.

---

## Patterns d'évaluation

### Rubrics adaptés par type de skill

**Skills à output structuré** (livrables fichiers, rapports, diagrammes) :
- Présence des sections attendues (critère binaire, poids élevé)
- Validité syntaxique si applicable (Mermaid, JSON, SQL...)
- Absence de placeholders non remplis
- Respect de la convention de nommage des fichiers

**Skills conversationnels** (analyse, conseil, diagnostic) :
- Réponse à la question posée (critère binaire, poids élevé)
- Profondeur de l'analyse (critère graduel)
- Absence de généralités non actionnables
- Ton adapté au contexte

**Skills de transformation** (reformatage, extraction, conversion) :
- Complétude (rien n'a été perdu)
- Fidélité (pas d'hallucination ajoutée)
- Format de sortie conforme

### Poids recommandés pour le rubric

| Critère         | Poids | Quand l'utiliser |
|-----------------|-------|------------------|
| Complétude      | 3     | Toujours          |
| Précision       | 3     | Quand les faits comptent |
| Structure       | 2     | Skills à livrables |
| Compacité       | 1     | Quand la verbosité est un risque |
| Actionnabilité  | 2     | Skills de conseil |
| Reproductibilité| 2     | Quand la cohérence est critique |

Score_max = somme des poids. Seuil de succès recommandé : 70%.
