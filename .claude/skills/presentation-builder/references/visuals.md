# Guide visuels — Présentation Builder

Ce document est la référence d'autorité sur la production de visuels dans le skill.
Chaque type de visuel suit une procédure précise. Le SKILL.md y pointe à l'étape « Visuels ».

---

## 1. Schémas (Mermaid → image)

Les schémas d'architecture, de séquence, de flux ou d'état sont écrits en Mermaid
puis pré-rendus en PNG avant d'être embarqués dans la diapo.

### Procédure

1. Écrire le diagramme dans `diagrams/<nom>.mmd` (un fichier par diagramme).
2. Lancer le rendu :
   ```bash
   npx --yes @mermaid-js/mermaid-cli \
     -i diagrams/<nom>.mmd \
     -o diagrams/<nom>.png \
     -b transparent
   ```
3. Embarquer dans la diapo avec la classe dédiée :
   ```markdown
   <!-- _class: diagram -->
   ![](diagrams/<nom>.png)
   ```

### Règles

- Le rendu se fait toujours **avant** de monter la présentation finale ; ne jamais
  laisser un `.mmd` non résolu dans un deck livré.
- Fond transparent (`-b transparent`) pour s'intégrer proprement sur les fonds
  sombres comme clairs du thème.
- Si le diagramme dépasse les capacités de Mermaid (exemple : diagramme C4,
  BPMN complexe), utiliser **PlantUML** en repli :
  ```bash
  plantuml -tpng diagrams/<nom>.puml
  ```
  (Installer : `choco install plantuml` sur Windows, `brew install plantuml` sur macOS, ou télécharger depuis plantuml.com)
  et embarquer le PNG résultant de la même façon.

### Types de diagrammes Mermaid supportés

| Besoin | Type Mermaid |
|---|---|
| Architecture composants | `graph LR` / `graph TD` |
| Flux d'appels API | `sequenceDiagram` |
| Machine à états | `stateDiagram-v2` |
| Cycle de vie | `flowchart` |
| Entités-relations | `erDiagram` |

---

## 2. Graphiques (données uniquement)

Un graphique ne peut être produit que si des **données réelles** sont fournies
explicitement : chiffres bruts, fichier CSV, sortie d'un outil, tableau du client.

### Règle absolue — interdiction d'inventer

**Il est absolument interdit d'inventer un chiffre, une valeur d'axe, une tendance
ou une proportion.** Un graphique avec des données fictives est pire qu'une absence
de graphique : il induit le public en erreur. Si aucune donnée n'est disponible,
voir l'alternative ci-dessous.

### Procédure quand les données sont fournies

1. Vérifier que toutes les valeurs des axes et légendes proviennent des données
   fournies — pas d'extrapolation, pas d'arrondi non déclaré.
2. Option A — **Mermaid xychart** (simple, intégré) :
   ```markdown
   ```mermaid
   xychart-beta
     title "Titre issu des données"
     x-axis [jan, fev, mar, avr]
     y-axis "Unité (source : <origine>)" 0 --> 100
     bar [valeur1, valeur2, valeur3, valeur4]
   ```
   ```
   **Caution** : `xychart-beta` est une syntaxe beta ; vérifier sa disponibilité dans la version de mmdc installée.
   Puis pré-rendre comme tout diagramme Mermaid (voir Section 1).
3. Option B — **script Python/Node** pour des graphiques plus élaborés
   (histogrammes, courbes multi-séries) :
   Le skill génère ce script à la volée selon les données fournies (il n'existe pas de script pré-livré).
   Exemple de script généré à la volée :
   ```bash
   python charts/generate.py --data data.csv --out charts/<nom>.png
   ```
   Le script généré doit lire les données depuis un fichier fourni, jamais les coder en dur.

### Alternative si les données sont absentes

Réclamer la donnée au commanditaire **avant** de produire quoi que ce soit, ou
remplacer par :
- un schéma illustrant la structure (Section 1), ou
- un placeholder de capture (Section 3).

Ne jamais générer un graphique "à titre illustratif" avec des valeurs inventées.

---

## 3. Captures, maquettes, photos

Quand un visuel ne peut pas être produit automatiquement (capture d'écran d'une
interface, photo de terrain, export d'un outil tiers), on insère un **placeholder
actionnable** qui maintient la validité structurelle de la diapo.

### Format imposé — à respecter à la lettre

```
<!-- PLACEHOLDER capture : fichier=images/<nom>.png ; on doit y voir : <description précise> -->
![](images/<nom>.png)
```

- `fichier=images/<nom>.png` : chemin relatif à la racine du deck.
- `on doit y voir :` suivi d'une description précise et non ambiguë de ce que
  l'image doit montrer (exemple : « la page d'accueil de l'application avec la
  barre de navigation dépliée et le menu Compte actif »).
- La balise `![](...)` reste présente même si le fichier n'existe pas encore :
  la porte de contrôle du skill détecte les placeholders non résolus et les signale
  dans son rapport avant livraison.

### Exemples

Capture d'écran d'interface :
```
<!-- PLACEHOLDER capture : fichier=images/dashboard-home.png ; on doit y voir : le tableau de bord principal avec les 4 KPI en haut et le graphique de tendance mensuelle -->
![](images/dashboard-home.png)
```

Photo de salle de formation :
```
<!-- PLACEHOLDER capture : fichier=images/salle-formation.png ; on doit y voir : la salle de 20 postes avec les écrans allumés sur l'interface de TP -->
![](images/salle-formation.png)
```

Maquette Figma exportée :
```
<!-- PLACEHOLDER capture : fichier=images/wireframe-login.png ; on doit y voir : le wireframe de la page de connexion avec les champs email et mot de passe et le bouton CTA principal -->
![](images/wireframe-login.png)
```

---

## Récapitulatif des règles non négociables

| Règle | Conséquence si violée |
|---|---|
| Pré-rendre tous les `.mmd` avant livraison | La diapo affiche du texte brut au lieu du schéma |
| Ne jamais inventer un chiffre de graphique | Présentation invalide, risque de désinformation |
| Utiliser le format imposé pour les placeholders | La porte de contrôle ne détecte pas le manquant |
