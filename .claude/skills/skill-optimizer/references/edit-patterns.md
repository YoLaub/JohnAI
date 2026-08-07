# Patterns de micro-édition — Skill-Optimizer

Ce fichier documente les types de modifications les plus efficaces selon le problème
rencontré. Consulte-le pendant la Phase 4 pour choisir le bon type d'intervention.

---

## Catalogue des micro-éditions

### Type A — Injection d'exemple

**Quand l'utiliser :** Les instructions sont abstraites et l'agent interprète différemment
selon les sessions. Haute variance dans les outputs.

**Budget :** 1 modification (ajouter un bloc exemple)

**Format :**
```markdown
**Exemple :**
Entrée : [cas concret représentatif]
Attendu : [output idéal annoté]
À éviter : [erreur courante avec explication courte]
```

**Effet attendu :** Réduction de la variance. L'exemple ancre l'interprétation.

**Piège :** Ne pas choisir un exemple trop spécifique qui surcontraint les autres cas.
Viser l'exemple qui généralise bien.

---

### Type B — Reformulation d'objectif

**Quand l'utiliser :** L'agent produit quelque chose de correct mais qui rate la cible.
Il exécute les instructions à la lettre sans saisir l'intention.

**Budget :** 1 modification (réécrire la section Objectif ou le premier paragraphe)

**Avant :**
```
## Ce skill fait X, Y et Z.
```

**Après :**
```
## Pourquoi ce skill existe
[L'utilisateur a besoin de X parce que Y. Ce skill l'aide en faisant Z.
La valeur produite est mesurable par : ...]
```

**Effet attendu :** L'agent comprend le *pourquoi*, pas juste le *quoi*. Il prend
de meilleures décisions sur les cas ambigus.

---

### Type C — Élagage

**Quand l'utiliser :** Le skill est trop long et certaines instructions entrent en conflit
ou sont redondantes. L'agent semble hésiter ou sur-réfléchir.

**Budget :** 1 modification (supprimer ou fusionner des sections)

**Stratégie :**
1. Identifier les instructions qui couvrent des cas rarissimes (<5% des usages)
2. Identifier les répétitions (même idée formulée deux fois)
3. Supprimer sans remords — si un cas rare se présente, l'agent s'en sortira avec
   son bon sens. Mieux vaut un skill compact et clair.

**Effet attendu :** Meilleure performance sur les cas courants. Le signal noie moins
dans le bruit.

**Règle :** Ne jamais élague en phase de diagnostic. D'abord comprendre ce qui manque,
ensuite élague ce qui est superflu.

---

### Type D — Ajout de contrainte de format

**Quand l'utiliser :** Les livrables sont incohérents d'une session à l'autre.
Structure variable, noms de fichiers différents, sections manquantes aléatoirement.

**Budget :** 1 à 2 modifications

**Format recommandé :**
```markdown
## Structure obligatoire des livrables

TOUJOURS produire ces fichiers, dans cet ordre :
1. `output/[nom].md` — [description courte]
2. `output/[nom].json` — [description courte]

Template de [nom].md :
\```
# [Titre]
## Section A
## Section B
\```
```

**Effet attendu :** Reproductibilité. Les cas de test "présence de section" passent
systématiquement.

---

### Type E — Clarification d'une zone floue

**Quand l'utiliser :** Un prompt de test échoue toujours sur le même point, et le
diagnostic montre que l'instruction est ambiguë (peut être interprétée de deux façons).

**Budget :** 1 modification (reformuler la phrase ambiguë + ajouter une précision)

**Stratégie :**
1. Identifier la phrase ambiguë
2. Écrire les deux interprétations possibles
3. Formuler une version qui exclut l'interprétation indésirable

**Exemple :**
- Ambigu : "Inclure les détails importants"
- Clair : "Inclure uniquement les informations actionnables (éviter les rappels de contexte
  que l'utilisateur connaît déjà)"

---

### Type F — Déplacement vers references/

**Quand l'utiliser :** Le skill contient des sections détaillées qui ne sont utilisées
que dans des cas spécifiques (ex : guide d'installation, liste exhaustive d'options,
documentation d'une API tierce).

**Budget :** 1 modification (déplacer la section + ajouter un pointeur dans SKILL.md)

**Dans SKILL.md :**
```markdown
Pour le détail des options de configuration avancées, consulte
`references/config-avancee.md` — uniquement si l'utilisateur demande une
configuration non standard.
```

**Effet attendu :** Réduction de la taille effective du skill sans perte d'information.

---

## Anti-patterns d'édition

### Ne pas faire : la réécriture déguisée
Proposer "4 petites modifications" qui ensemble réécrivent 80% du skill.
C'est une réécriture avec un budget mal déclaré. Si tu as envie de tout changer,
c'est un signal qu'il faut d'abord mieux comprendre le problème.

### Ne pas faire : l'optimisation pour le test
Modifier le skill pour faire passer un test spécifique sans que la modification
ait du sens pour les autres cas. Par exemple, ajouter "inclure toujours la section X"
parce que le test #3 vérifie la présence de X, alors que X n'est pertinent que
dans 20% des cas réels.

### Ne pas faire : toucher les INVARIANTS sans le dire
Si une modification semble nécessiter de toucher la zone INVARIANTS, arrête-toi
et discute avec l'utilisateur. Ce n'est pas une modification automatique.

### Ne pas faire : accumuler sans valider
Appliquer plusieurs modifications en série sans rejouer l'eval set entre les deux.
On ne sait plus quelle modification a fait quoi. Chaque micro-commit doit être
validé individuellement.
