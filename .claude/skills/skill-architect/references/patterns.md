# Patterns de skills

## Test décisionnel

La question qui choisit le pattern : **les phases du skill sont-elles des points
d'entrée indépendants, ou les étapes d'une même intention ?**

- Étapes séquentielles d'une intention unique → **Template Method**
- Points d'entrée indépendants avec déclencheurs distincts → **Facade**
- Le skill coordonne des agents/sous-tâches en séquence → **Pipeline**
- Une interface, plusieurs variantes interchangeables → **Strategy**

## Template Method — squelette fixe, étapes adaptées

Le SKILL.md décrit les phases dans l'ordre (1→N) ; chaque exécution suit le squelette
et adapte le contenu au contexte. Les phases n'ont de sens qu'ensemble : l'utilisateur
ne demande jamais la phase 3 seule. Un seul SKILL.md porte tout le squelette ; les
références portent les connaissances par étape.

*Exemple générique* — un skill « démarrage de projet » :
```
SKILL.md                    # cadrage → bootstrap → développement → clôture
references/pieges.md        # connaissances accumulées, append-only, sections datées
references/template-doc.md  # format de doc produit en phase 3
```

## Facade — routeur mince vers des workflows indépendants

Le SKILL.md contient la philosophie + une table de routage (déclencheur → fichier de
phase) + les principes transverses ; chaque phase vit dans `references/phase-N-*.md` et
n'est chargée que si elle est demandée. À utiliser dès que l'utilisateur peut invoquer
une phase seule (« initialise X », « audite X », « synchronise X » sont trois demandes
distinctes qui ne doivent pas charger le détail des deux autres).

*Exemple générique* — un skill « base de connaissances » :
```
SKILL.md                          # philosophie + table déclencheur → fichier
references/structure.md           # le contrat commun à toutes les phases
references/phase-1-init.md        # créer la structure
references/phase-2-ingestion.md   # compiler les sources
references/phase-3-audit.md       # vérifier la cohérence
```

## Pipeline — orchestration d'agents en séquence

Le SKILL.md définit l'ordre des agents, le contrat de passage entre étapes (ce que
chaque agent reçoit et produit), et les points de reprise. Chaque agent garde sa propre
définition ; le skill ne duplique jamais leurs instructions, il les enchaîne.

*Exemple générique* — un skill « traitement de candidature » : analyse → mise en forme
→ soumission → simulation d'entretien → bilan, chaque étape étant un agent séparé, le
SKILL.md ne contenant que l'enchaînement et les règles de passage.

## Strategy — variantes derrière une interface unique

Un catalogue de variantes (styles, modes, formats) documenté dans une référence dédiée ;
le SKILL.md définit comment CHOISIR la variante, jamais les variantes elles-mêmes.
Ajouter une variante = ajouter une entrée au catalogue (Open/Closed), sans toucher au
routage.

*Exemple générique* — un skill « génération de rapports » :
```
SKILL.md                 # workflow + règle de choix du format
references/catalogue.md  # N formats de sortie, un bloc par format
```

## Combinaisons

Les patterns se composent : une Facade peut router vers des Template Methods (chaque
fichier de phase est un mini-squelette) ; un Pipeline peut utiliser une Strategy pour
choisir un agent. Choisir le pattern DOMINANT pour la structure du SKILL.md, les autres
vivent dans les références.
