# Checklist de revue d'un skill

À dérouler en phase 4, avant livraison. Chaque ❌ se corrige avant de conclure.

## Déclenchement (l'interface)
- [ ] La description contient des formulations littérales que l'utilisateur emploierait.
- [ ] Aucun chevauchement de déclencheurs avec un skill existant sans désambiguïsation
      explicite dans les descriptions concernées.
- [ ] La description annonce ce que le skill fait ET ce qu'il ne fait pas (si un voisin
      proche existe).

## Structure (le découpage)
- [ ] SKILL.md ≤ ~70 lignes hors frontmatter ; il ne contient que du stable.
- [ ] Chaque fichier a une seule vitesse de changement.
- [ ] Aucune instruction du type « mettre à jour ce skill avec X » où X est une
      connaissance accumulable — elle doit pointer vers un fichier de référence.
- [ ] Chaque pointeur vers `references/` dit QUAND lire le fichier.
- [ ] Les fichiers append-only le déclarent en tête et datent leurs sections.

## Intégrité (le compilateur manuel)
- [ ] Tout fichier/dossier mentionné existe (`Glob **/*` et croiser).
- [ ] Toute option de script documentée est réellement implémentée.
- [ ] Les noms d'outils cités existent dans l'environnement cible (AskUserQuestion,
      pas d'anciens noms).
- [ ] Scripts vérifiés : `python -m py_compile` / `bash -n` selon le langage.
- [ ] En refactor : diff relu pour garantir zéro perte d'information (déplacement
      verbatim, pas de réécriture silencieuse).

## Intégration (le catalogue)
- [ ] README : ligne dans le tableau des skills + arborescence à jour.
- [ ] install.sh (si présent) : entrée CATALOGUE, bundle, menu, mapping du choix.
- [ ] L'installateur récupère bien les sous-dossiers (references/, scripts/) — vérifier
      le mécanisme de téléchargement s'il liste les fichiers un par un.
