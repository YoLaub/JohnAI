# SOLID transposé aux skills

## Ce qui se transpose

**Single Responsibility** — double lecture pour un skill :
1. *Déclenchement* : la description du frontmatter est l'interface publique ; le modèle
   route dessus. Un skill qui couvre deux intentions sans rapport a une description
   floue, donc se déclenche mal. Un skill = une intention utilisateur reconnaissable.
2. *Raison de changer* : à l'intérieur du skill, chaque fichier a UNE vitesse de
   changement. Le workflow méthodologique (stable, change quand la méthode change) et
   les connaissances accumulées (volatiles, changent à chaque projet) ne cohabitent pas
   dans le même fichier. Symptôme classique : une section « pièges connus » datée dans
   un SKILL.md, avec une phase qui dit « mettre à jour ce skill » — le fichier est
   programmé pour gonfler.

**Interface Segregation** = progressive disclosure. SKILL.md est l'interface mince
chargée au déclenchement ; `references/` n'est lu que si l'étape en cours en a besoin.
Ne pas forcer le contexte à charger ce qu'il ne consomme pas. Corollaire : chaque
pointeur vers une référence précise QUAND la lire.

**Open/Closed** — un skill s'étend par ajout sans modification du cœur : fichiers de
connaissances append-only avec sections datées (par stack, par domaine), nouveau fichier
de phase, nouvelle entrée de catalogue. SKILL.md ne bouge que si la méthodologie change.

**« Une source de vérité par sujet »** (le vrai visage du Singleton ici) : deux skills
aux descriptions chevauchantes se cannibalisent au déclenchement. Soit fusionner, soit
écrire la désambiguïsation dans les deux descriptions (« ne pas confondre avec X — ici
on fait Y »).

## Là où l'analogie CASSE (aussi important que le reste)

**Le coût de l'indirection est inversé.** En code, un appel de fonction est gratuit et
fiable. Entre skills, chaque frontière est une décision de routage probabiliste : trop
de petits skills = déclenchements ratés + contexte gaspillé. Règle : fragmenter en
FICHIERS avant de fragmenter en SKILLS. Ne jamais éclater des phases séquentielles
cohésives (une seule intention utilisateur) en skills séparés.

**DRY est parfois contre-productif.** Répéter une règle critique à deux endroits d'un
skill améliore la conformité du modèle. De même, un script embarque ses templates au
lieu de référencer des assets à côté : l'autonomie prime sur la factorisation.

**Pas de compilateur.** Rien ne signale une référence morte (dossier mentionné mais
absent, option de script documentée mais non implémentée, nom d'outil obsolète). C'est
à la revue (checklist) de jouer ce rôle.
