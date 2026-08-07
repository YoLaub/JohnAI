# Amorçage du BRAIN et du journal d'erreurs

À lire à l'étape 5 du déroulé, une fois le CLAUDE.md validé.

`PROJECT_KEY` = identifiant court du projet (par défaut le nom du dossier du repo, en
kebab-case). Le confirmer en question fermée, ne jamais l'inventer silencieusement.
`BRAIN` = `~/brain/<PROJECT_KEY>`.

## Contraintes
- Aucune écriture destructive. Le CLAUDE.md est modifié en **APPEND uniquement**.
- Si un fichier ou un bloc existe déjà, ne pas le dupliquer : le signaler et passer.
- Rapport final : fichiers créés, modifiés, ignorés (et pourquoi).

## Étape A — Arborescence

Créer si absent, et rien d'autre :
```
~/brain/<PROJECT_KEY>/rules/
~/brain/<PROJECT_KEY>/bag.ndjson   (fichier vide)
~/brain/global/rules/
```
Ne PAS créer d'autres dossiers projet. Ils naîtront quand ils auront une raison d'exister.

## Étape B — Bloc ACTIF, appendé au CLAUDE.md du projet

Recopié tel quel, `<PROJECT_KEY>` substitué :

```markdown
BRAIN: ~/brain/<PROJECT_KEY>

## Journal d'erreurs

Quand un bug non trivial est résolu, append une ligne à `$BRAIN/bag.ndjson` :

{"trigger":"", "symptom":"", "root_cause":"", "fix":"", "severity":1, "date":"YYYY-MM-DD"}

- `trigger` : les termes techniques exacts qui identifient le contexte
  ("relation polymorphe Strapi v5"), pas une description du bug.
  C'est la clé de regroupement.
- `severity` : 1 friction · 2 rework · 3 irréversible (perte de données,
  CI verte à tort, prod)
- Append only, jamais d'édition, une ligne par incident.

Si le `trigger` n'est pas formulable en termes techniques précis, le diagnostic
n'est pas terminé : le dire plutôt que de logger une entrée floue.
Un bug résolu par hasard ne se logge pas.
Si aucune ligne `BRAIN:` n'est présente dans ce CLAUDE.md, ne rien logger et le signaler.
```

`$BRAIN` n'est pas une variable shell : c'est une référence textuelle, résolue en lisant
la ligne `BRAIN:` du CLAUDE.md.

## Étape C — Bloc DORMANT, hors CLAUDE.md

Écrire dans `~/brain/<PROJECT_KEY>/PENDING-rules-block.md`. Ne surtout pas le mettre
dans le CLAUDE.md maintenant : tant que `rules/` est vide, il envoie chercher un
manifeste inexistant.

```markdown
<!-- À coller dans CLAUDE.md APRÈS la première compilation réussie.
     Tant que rules/ est vide, ce bloc envoie chercher un manifeste inexistant. -->

## Règles projet

Au début d'une tâche, lire `$BRAIN/MANIFEST.md` et `~/brain/global/MANIFEST.md`,
charger uniquement les fichiers dont les mots-clés matchent la stack, les chemins
touchés ou le type de tâche.

- Match exact sur mots-clés, pas d'interprétation large.
- Ne jamais charger `rules/` en entier ni `bag.ndjson`.
- Règle chargée inapplicable : le signaler, ne pas la contourner silencieusement.
```

La bascule du bloc dormant vers le CLAUDE.md est proposée par le skill `compile-rules`
après sa première passe réussie — jamais ici.

## Vérification finale
Relire le CLAUDE.md du projet et confirmer qu'aucun contenu préexistant n'a été modifié.
