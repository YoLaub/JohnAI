Lis le fichier .claude/skills/archi-diagrams/SKILL.md et suis ses instructions.

Phase 0 : Charge archi-output/INDEX.md. Si absent, propose de lancer /archi-scanner d'abord.
Phase 1 : Propose les diagrammes disponibles (architecture, classes, MCD, séquence, cas d'utilisation) et demande lequel générer. Ne génère JAMAIS tout d'un coup.
Phase 2 : Génère le diagramme Mermaid demandé à partir de l'index, en respectant les limites de lisibilité.
Phase 3 : Sauvegarde dans archi-output/diagrams/ et propose de continuer.

$ARGUMENTS
