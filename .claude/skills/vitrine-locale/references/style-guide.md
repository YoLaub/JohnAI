# Charte de style — anti-générique / anti-IA

Checklist à dérouler sur tout texte visible (copy, meta description, alt text)
avant de merger une feature. Append-only : ajouter un tell repéré sous sa section,
dater si utile.

## Ponctuation
- **Jamais de tiret cadratin ou demi-cadratin (—, –)**, y compris dans le code
  généré (variables, commentaires visibles côté contenu). Reformuler avec une
  virgule, un point, des parenthèses, ou deux phrases courtes.
- Espace insécable avant `:`, `;`, `!`, `?` en français (`&nbsp;` ou ` `
  selon le contexte), pas d'espace simple.
- Guillemets français « » pour les citations, pas de guillemets droits `"..."`
  dans le contenu visible.

## Icônes
- **Jamais d'emoji dans l'UI** (boutons, listes, indicateurs) — toujours une
  icône SVG dessinée (`currentColor`, `aria-hidden="true"`), cf. mémoire globale
  "no-emoji-ui".

## Tournures à bannir (tells IA / copy générique)
- Ouvertures passe-partout : "Dans un monde où...", "Bienvenue chez...", "Chez
  nous, ...", "Découvrez...", "Plongez dans...".
- Triades de remplissage : "rapide, simple et efficace", "qualité, fraîcheur et
  passion" — si les trois mots ne disent rien de spécifique à CE commerce, les
  couper.
- Superlatifs non étayés : "le meilleur", "unique", "incomparable",
  "incontournable" sans fait vérifiable derrière (un prix, un ingrédient, une
  méthode précise).
- Injonctions creuses : "N'hésitez pas à...", "Venez découvrir...".
- Anglicismes marketing traduits mécaniquement : "élevez votre expérience",
  "à portée de main", "au cœur de".
- Toute phrase qui pourrait être copiée-collée sur le site d'un concurrent sans
  changer un mot : le texte doit contenir un fait spécifique à CE commerce (un
  ingrédient, une adresse, un horaire, un geste de fabrication).

## Test de relecture
Lire chaque paragraphe visible à voix haute : si une phrase sonne comme un
prospectus générique plutôt que comme quelqu'un qui connaît vraiment ce commerce,
la réécrire à partir d'un fait tiré du cadrage (phase 1), pas d'une formule toute
faite.
