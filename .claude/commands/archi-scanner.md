Lis le fichier .claude/skills/archi-scanner/SKILL.md et suis son workflow complet.

Phase 1 : Détecte le stack technique via les fichiers de config (jamais via le code source).
Phase 2 : Extrais toutes les routes en utilisant les heuristiques adaptées au framework détecté.
Phase 3 : Chaîne Routes → Controllers → Services → Entités en lisant uniquement les signatures.
Phase 4 : Scanne les couches transversales (hooks, utils, middleware, shared).
Phase 5 : Génère archi-output/INDEX.md + archi-output/PROJECT_MEMORY.md.

Économise les tokens : grep et find avant de lire, signatures uniquement, jamais l'implémentation.

$ARGUMENTS
