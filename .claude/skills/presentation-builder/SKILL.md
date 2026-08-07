---
name: presentation-builder
description: >
  Construit une présentation orale (soutenance, pitch, talk, démo) en imposant le modèle
  assertion-preuve et un système de design fermé. Déclenche quand l'utilisateur veut
  "faire un diaporama", "faire des slides", "faire une présentation", "faire un support de
  soutenance", "préparer un oral", "refaire mes slides", "préparer ma soutenance", "créer
  un deck", ou se plaint d'un deck "trop technique", "pas assez imagé", "trop chargé",
  "illisible en salle". Produit du Marp exportable en .pptx et PDF, avec schémas générés
  automatiquement (Mermaid) et graphiques sur données réelles, et passe le deck par une
  porte de contrôle visuelle automatisée (sous-agent critique) avant toute livraison.
---

# presentation-builder — Orchestrateur

Ce skill est **autonome** : il n'est pas nécessaire d'invoquer `superpowers:writing-skills`
ni aucun autre skill pour l'utiliser. Toutes les références et commandes sont embarquées
ci-dessous.

---

## Workflow en 7 étapes

### Étape 1 — Intake (BLOQUANT)

Collecter les 6 informations suivantes **avant toute production**. Sans elles, aucune slide
ne peut être rédigée.

| Information | Raison |
|---|---|
| **Public** : non-technique ? mixte ? expert ? | Règle l'altitude du jargon. Public non-technique → altitude renforcée à chaque étape. |
| **Objectif** : décider / ressentir / retenir | Oriente l'arc narratif et le registre des visuels. |
| **Durée** : minutes de présentation | Cadre le nombre de slides (≈ 1 à 1,5 min/slide). |
| **Contexte** : salle projetée, visio, kiosque, impression | Contraste vidéoprojecteur vs écran — impacte les choix visuels. |
| **Matériau source** : fichiers, notes, liens, données brutes | Sans données réelles, aucun graphique ne peut être produit. |
| **Identité visuelle** : couleur accent (#hex ou description), ton (neutre / éditorial) | Pilote `--accent` / `--accent-ink` dans le thème et `--font-sans` optionnel. |

Si public non-technique : toute occurrence de jargon technique doit être soit évitée,
soit glosée sur la slide (pas uniquement en notes) dès lors qu'elle apparaît dans une image
projetée.

---

### Étape 2 — Arc narratif

Construire l'arc en cinq temps **avant** de penser aux slides :

1. **Problème** — quel contexte ou tension motive cette présentation ?
2. **Tension** — qu'est-ce qui coince ou doit changer ?
3. **Résolution** — quelle décision / solution / résultat apportez-vous ?
4. **Preuve** — quelles données ou démonstrations l'étayent ?
5. **Ouverture** — quelle action ou question reste ouverte ?

L'arc est validé à l'oral ou par écrit par le commanditaire avant le storyboard.
Aucune slide n'est rédigée tant que l'arc n'est pas fixé.

---

### Étape 3 — Storyboard (VALIDATION HUMAINE)

Produire un tableau à trois colonnes pour chaque slide prévue.
Référence complète : `references/assertion-evidence.md`.

| # | Titre-assertion | Visuel requis | Intention |
|---|---|---|---|
| 1 | Phrase complète : sujet + verbe + affirmation | Layout Marp + type (schéma / graphique / capture / aucun si text-focal) | Ce que le jury doit retenir |

**Règles de storyboard :**
- Chaque titre doit contenir un verbe conjugué. Un titre sans verbe = label = à réécrire.
- Les layouts text-focaux (`cover`, `section`, `statement`, `quote`) peuvent n'avoir aucun visuel — c'est intentionnel.
- Les layouts `image-caption`, `diagram`, `chart`, `image-full` **doivent** pointer un visuel.
- **Aucun texte de slide n'est rédigé avant que ce tableau soit validé par le commanditaire.**

---

### Étape 4 — Visuels

Référence complète : `references/visuals.md`.

**Schémas (architecture, flux, états, séquences) :**
1. Écrire le diagramme dans `diagrams/<nom>.mmd`.
2. Pré-rendre **avant** l'assemblage :
   ```bash
   npx --yes @mermaid-js/mermaid-cli \
     -i diagrams/<nom>.mmd \
     -o diagrams/<nom>.png \
     -b transparent
   ```
3. Embarquer avec le layout dédié :
   ```markdown
   <!-- _class: diagram -->
   ![](diagrams/<nom>.png)
   ```
   En repli pour diagrammes hors capacités Mermaid : `plantuml -tpng diagrams/<nom>.puml`.

**Graphiques :** uniquement sur données réelles fournies explicitement.
Ne jamais inventer une valeur, une tendance ou une proportion. Si aucune donnée n'est
disponible, poser la question au commanditaire ou remplacer par un placeholder.
Option A — Mermaid `xychart-beta` (pré-rendre comme un schéma ; syntaxe *beta* — vérifier sa disponibilité dans la version de `mmdc` installée, cf. `references/visuals.md`).
Option B — script Python/Node généré à la volée lisant un fichier CSV fourni.

**Captures, maquettes, photos** — format imposé à la lettre :
```
<!-- PLACEHOLDER capture : fichier=images/<nom>.png ; on doit y voir : <description précise> -->
![](images/<nom>.png)
```
La porte de contrôle détecte les placeholders déclarés et les liste comme non-bloquants.
Un placeholder non déclaré dans ce format est une violation bloquante.

---

### Étape 5 — Notes orateur

Chaque slide **doit** comporter au moins un commentaire HTML `<!-- … -->` de notes.
Les notes portent tout ce que le jury ne doit pas lire sur l'écran. Référence :
`references/assertion-evidence.md` §"Ce qui va dans les notes orateur".

Quatre catégories obligatoires selon pertinence :
- **Définitions** — glosser les termes techniques sans les projeter.
- **Anti-sèches** — chiffres, dates, noms d'outils, valeurs.
- **Sources** — tout chiffre ou stat doit avoir sa source ici au minimum.
- **Transitions** — phrase exacte reliant cette slide à la suivante.

---

### Étape 6 — Assemblage Marp

**Thème — procédure obligatoire :**

Marp ne résout pas `@import` local. Le thème final est assemblé par concaténation.

1. Copier `design-system/theme.template.css` dans le dossier de travail sous le nom
   `accent.css`.
2. Dans `accent.css`, remplir uniquement les deux variables imposées :
   - `--accent: #hex;` — couleur principale (issue de l'intake)
   - `--accent-ink: #hex;` — couleur du texte sur fond accent (contraste WCAG AA minimum)
   - Optionnel : décommenter `--font-sans` pour le ton éditorial.
   - **Interdit** : modifier l'échelle typo, la grille ou les contrastes du système.
3. Assembler le thème final :
   ```bash
   bash design-system/build-theme.sh accent.css > theme.css
   ```
   Le script émet : `/* @theme presentation */` + `tokens.css` + `layouts.css` + `accent.css`
   (en dernier → gagne la cascade). *Requiert un shell `bash` (Git Bash ou WSL sous Windows ;
   l'environnement par défaut est PowerShell).*
4. Front-matter de chaque deck :
   ```markdown
   ---
   marp: true
   theme: presentation
   paginate: true
   ---
   ```

**8 layouts disponibles** (invoquer via `<!-- _class: NOM -->`) :

| Layout | Type | Visuel obligatoire |
|---|---|---|
| `cover` | Couverture | Non — text-focal |
| `section` | Intercalaire accent | Non — text-focal |
| `statement` | Assertion seule centrée | Non — text-focal |
| `quote` | Citation | Non — text-focal |
| `image-caption` | 2 colonnes texte + image | Oui |
| `diagram` | Schéma dominant | Oui |
| `chart` | Graphique dominant | Oui |
| `image-full` | Image plein cadre | Oui |

**Export final** (le flag `--allow-local-files` est obligatoire dès qu'il y a des images locales) :
```bash
npx --yes @marp-team/marp-cli deck.md --theme theme.css --allow-local-files -o deck.pptx
npx --yes @marp-team/marp-cli deck.md --theme theme.css --allow-local-files -o deck.pdf
```

Exemple de référence d'un deck conforme : `references/sample-deck/sample-deck.md` + son
`references/sample-deck/theme.css`.

---

### Étape 7 — Porte de contrôle (BLOQUANT)

Dispatcher un sous-agent frais dont les instructions **sont** le contenu intégral de
`references/critique-prompt.md`. Passer en contexte :
- `<deck>` : chemin absolu vers le fichier `.md` du deck
- `<theme>` : chemin absolu vers `theme.css`
- Contexte d'audience (public non-technique ?)

Le sous-agent produit `critique-report.md` dans le répertoire du deck avec un verdict par
slide et un **verdict global** (`CONFORME` ou `À CORRIGER`).

L'orchestrateur **lit le rapport**, corrige toutes les violations (`contenu` / `altitude` /
`visuel`), et relance la porte jusqu'à obtenir le verdict global `CONFORME`.

Les placeholders déclarés (`<!-- PLACEHOLDER capture : … -->`) sont **non-bloquants** :
ne pas bloquer la livraison à cause d'eux, mais les signaler au commanditaire.

**Ne jamais livrer un deck portant le verdict `À CORRIGER`.**

---

## Table des règles dures (rappel permanent)

| # | Règle | Critère de violation |
|---|---|---|
| 1 | **Titre = assertion** | Titre sans verbe conjugué = label = violation. |
| 2 | **Un visuel dominant** | Slide de contenu sans image / schéma / graphique = violation (sauf layouts text-focaux : `cover`, `section`, `statement`, `quote`). |
| 3 | **≤ 3 puces** | Plus de 3 puces dans le corps hors titre = violation. |
| 4 | **≤ 15 mots** | Plus de ~15 mots dans le corps hors titre, hors notes, hors blocs de code = violation. |
| 5 | **Code ≤ 4 lignes** | Bloc de code de 5 lignes ou plus = violation. |
| 6 | **Notes sur chaque slide** | Absence de commentaire HTML `<!-- … -->` sur une slide = violation. |
| 7 | **Jargon glosé** | Terme technique non explicité = violation. Label d'un **schéma généré** (Mermaid) : en clair (français) obligatoire. Terme dans une **capture réelle** : titre-assertion + légende en clair suffisent (on ne réécrit pas la capture). |
| 8 | **Données sourcées** | Chiffre ou stat sans source explicite ni sur la slide ni dans ses notes = violation. |

---

## Références

| Fichier | Rôle |
|---|---|
| `design-system/tokens.css` | Variables CSS de base (couleurs, typo, grille) |
| `design-system/layouts.css` | Règles des 8 layouts |
| `design-system/theme.template.css` | Fragment d'override accent — **à copier sous le nom `accent.css`** dans le dossier de travail (cf. étape 6), puis passé à `build-theme.sh` |
| `design-system/build-theme.sh` | Script d'assemblage du thème final |
| `references/assertion-evidence.md` | Doctrine assertion–preuve + notes orateur |
| `references/visuals.md` | Procédures schémas / graphiques / placeholders |
| `references/critique-prompt.md` | Instructions complètes du sous-agent critique |
| `references/sample-deck/sample-deck.md` | Exemple canonique CONFORME (few-shot) |
| `references/sample-deck/theme.css` | Thème assemblé de l'exemple |
