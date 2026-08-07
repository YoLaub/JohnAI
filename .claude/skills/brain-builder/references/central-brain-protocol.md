# Protocole de connexion au cerveau central

> Ce document définit à l'avance comment les cerveaux projets se connecteront au cerveau central, **même si le cerveau central n'existe pas encore**. L'objectif : permettre aux cerveaux créés aujourd'hui d'être "central-ready" sans refactor ultérieur.

## Modèle mental

```
                  ┌─────────────────────────┐
                  │   CERVEAU CENTRAL       │
                  │   ~/central-brain/      │
                  │                         │
                  │  - Préférences perso    │
                  │  - Méthodes transverses │
                  │  - Leçons apprises      │
                  │  - Vocabulaire commun   │
                  └───────────▲─────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
        ┌───────┴──────┐ ┌───┴────┐ ┌──────┴────────┐
        │   mon-app    │ │ ma-api │ │  autre-projet │
        │   -brain     │ │ -brain │ │    -brain     │
        └──────────────┘ └────────┘ └───────────────┘
```

Chaque cerveau projet est **indépendant** (son propre vault, son propre graph Obsidian) mais **référence** le central pour tout ce qui est transverse.

## Règle d'or : non-duplication

Un concept vit dans UN SEUL cerveau.

- Spécifique au projet → vit dans le cerveau projet (ex: `AuthService` de mon-app)
- Transverse à plusieurs projets → vit dans le central (ex: "Ma préférence : Claude Code pour les fix de bugs", "Pattern : tests fix-one-bug-at-a-time")
- Le cerveau projet ne fait que **référencer** les concepts du central.

Si une note existe des deux côtés, c'est un bug que le linter signalera.

## Mécanisme de liaison

Trois options possibles, classées par robustesse :

### Option 1 : Registre de liens (recommandée)

Le fichier `wiki/_meta/CENTRAL_LINKS.md` de chaque cerveau projet contient une liste de références vers des notes du central. Format :

```markdown
## Concepts hébergés dans le central et référencés ici

- `central://concepts/fix-one-bug-at-a-time` — Utilisé dans toute la stratégie de test backend
- `central://preferences/prompt-style-claude-code` — Appliqué à tous les prompts générés pour ce projet
- `central://methods/bmad-cdc-structure` — Structure utilisée pour le cahier des charges de ma-api
```

Le préfixe `central://` est une convention **purement textuelle** (pas un vrai protocole URI) qui signale au lecteur humain ET aux phases futures du skill qu'il s'agit d'une ref inter-vault.

**Avantages** :
- 100% portable, aucune dépendance système
- Visible dans Obsidian comme du texte
- Le linting peut vérifier que les refs existent dans le central

**Inconvénient** :
- Pas de clic direct depuis Obsidian vers la note centrale (sauf plugin)

### Option 2 : Symlinks (si OS le permet)

Créer un symlink `wiki/_central/` qui pointe vers `~/central-brain/wiki/`. Les notes centrales deviennent accessibles comme si elles étaient dans le vault projet.

```bash
ln -s ~/central-brain/wiki ~/ObsidianVaults/mon-app-brain/wiki/_central
```

**Avantages** :
- Clic direct dans Obsidian
- Graph view unifié possible

**Inconvénients** :
- Windows est capricieux avec les symlinks
- Risque d'édition accidentelle du central depuis un vault projet
- Obsidian peut se perdre avec les symlinks selon la version

### Option 3 : Plugin Obsidian "vault switcher"

Non implémenté par défaut. Mentionné pour mémoire — si l'utilisateur veut une intégration plus poussée, des plugins comme "Another Quick Switcher" permettent de naviguer entre vaults.

**Le skill utilise l'Option 1 par défaut.** C'est la plus robuste et la plus facile à linter.

## Structure attendue du cerveau central

Quand le cerveau central sera créé, il devra suivre une structure compatible :

```
central-brain/
├── wiki/
│   ├── preferences/       # Préférences personnelles (style, outils, workflows)
│   ├── methods/           # Méthodes transverses (BMAD, ADR, etc.)
│   ├── concepts/          # Vocabulaire et patterns communs
│   ├── lessons/           # Leçons apprises cross-projet
│   └── registry/
│       └── PROJECTS.md    # Liste des cerveaux projets connus + chemins
│
├── raw/                   # Sources transverses (articles, refs générales)
└── reports/
```

Le fichier `central-brain/wiki/registry/PROJECTS.md` est **la liste symétrique** des `CENTRAL_LINKS.md` de chaque projet — il sait quels projets existent et où ils sont.

## Workflow de connexion (phase 4 du skill)

Quand l'utilisateur demande "connecte ce cerveau au central", le skill :

1. **Vérifie** que le cerveau central existe au chemin attendu (ou demande le chemin)
2. **Met à jour** `wiki/_meta/CENTRAL_LINKS.md` du projet avec le chemin du central
3. **Met à jour** `central-brain/wiki/registry/PROJECTS.md` pour enregistrer le nouveau projet
4. **Scanne** le wiki du projet pour détecter des notes qui devraient plutôt vivre dans le central (concepts récurrents, préférences génériques)
5. **Propose** une liste de migrations à valider par l'utilisateur (jamais d'auto-migration sans confirmation)

## Garde-fous

- **Jamais** de duplication silencieuse. Si un concept se trouve dans un projet ET dans le central, le linter crie.
- **Jamais** de modification du central depuis un vault projet (seulement lecture).
- **Toujours** un enregistrement bidirectionnel : le projet référence le central, le central liste le projet.
- **Toujours** un fallback gracieux : si le central est inaccessible (déplacé, renommé), le projet reste fonctionnel et les refs `central://...` deviennent juste du texte inerte jusqu'à réparation.

## État actuel de ce protocole

✅ Spécifié
⏳ Non implémenté (le cerveau central n'existe pas encore)
⏳ Phase 4 du skill à activer quand le central sera créé

En attendant, le fichier `wiki/_meta/CENTRAL_LINKS.md` est créé vide dans chaque cerveau projet, prêt à accueillir les refs.
