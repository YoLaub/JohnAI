# Phase audit — vérifier un serveur MCP existant

Pour "est-ce que mon MCP a des trous ?", un rapport d'incident, ou un doute ponctuel
sur une couche précise — sans reconstruire ce qui est déjà solide.

## Protocole

1. Lire `references/couches.md` en entier une fois (les 7 couches, dans l'ordre).
2. Pour chaque couche, dans l'ordre, vérifier si elle est en place. Ne PAS auditer
   une couche si une couche précédente manque encore (l'audit de la couche 3
   suppose une identité résolue fiable — inutile de l'auditer si la couche 1 est
   absente, le résultat serait trompeur).
3. Couche 3 (cloisonnement) mérite un audit exhaustif, pas un sondage : lister
   TOUTES les entités cloisonnées, puis pour CHACUNE, grep toutes les fonctions qui
   la lisent/modifient/envoient et vérifier que chacune porte la garde d'identité.
   Une seule fonction non couverte par entité = faille à traiter comme les autres.
4. Classer chaque écart trouvé : CONFIRMED (rejouable, faille vérifiée par un appel
   réel) ou PLAUSIBLE (repéré par lecture de code, non rejoué). Ne pas mélanger les
   deux dans le compte rendu.
5. Restituer le rapport AVANT de corriger quoi que ce soit (comme une revue de code) :
   liste des écarts par couche, gravité, preuve. Laisser l'utilisateur prioriser.
6. Correction : appliquer le pattern générique de `references/couches.md` pour la
   couche concernée. Après un fix de cloisonnement, rejouer le grep exhaustif de
   l'étape 3 sur l'entité corrigée ET ses entités sœurs (même piège que la couche 3
   documenté dans `couches.md` — il mord même en mode audit).
7. Vérification end-to-end réelle des écarts corrigés (appel réel rejeté avant,
   accepté après pour le cas légitime) — pas seulement relecture du diff.

## Ce que l'audit ne fait pas

- Il ne réécrit pas une couche qui fonctionne pour la faire "plus proprement" —
  seuls les écarts de sécurité identifiés sont dans le périmètre.
- Il ne suppose jamais qu'une couche est correcte parce qu'elle existe : l'existence
  d'un mécanisme de token n'implique pas que toutes les routes/tools l'utilisent.
