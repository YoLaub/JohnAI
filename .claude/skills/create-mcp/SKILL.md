---
name: create-mcp
description: Construire, durcir ou auditer la sécurité d'un serveur MCP (Model Context Protocol) — identité par token personnel, OAuth 2.1 pour connecteurs tiers, cloisonnement multi-tenant par tool, rate-limit par identité, logging des appels, mode sandbox, bearer sur le manifeste agent. Déclenche sur "crée un serveur MCP", "sécurise/durcis mon MCP", "audite mes tools MCP", "ajoute l'auth/le rate-limit/l'OAuth à mon MCP". Ne couvre PAS le bootstrap d'une app entière (voir greenfield-tdd-okf) ni la conception des tools eux-mêmes — uniquement la couche sécurité autour de tools MCP déjà définis ou à définir.
---

# Create MCP — sécuriser un serveur MCP

Généralisé depuis un durcissement réel (CRM_TEAM, 2026-07, 7 itérations). Deux
entrées indépendantes, un même corpus de connaissances.

Références (à lire au moment indiqué, pas avant) :
- `references/couches.md` — la substance de chaque couche de sécurité, générique
  (pas de stack imposée), append-only. Lire la couche courante en phase de construction
  ou d'audit, avant de l'implémenter/vérifier.
- `references/phase-construction.md` — construire ou durcir un serveur MCP couche par
  couche. Lire au démarrage d'une demande "crée/sécurise/durcis mon MCP".
- `references/phase-audit.md` — auditer un serveur MCP existant contre les 7 couches
  sans tout reconstruire. Lire au démarrage d'une demande "audite mes tools MCP".
- `references/pieges.md` — pièges rencontrés, sections datées par stack. Consulter la
  section "Génériques" toujours ; enrichir dès qu'un piège mord.

## Les 7 couches, dans l'ordre de dépendance

1. **Identité** — token personnel par utilisateur (bearer révocable, hashé en base,
   montré une seule fois).
2. **Délégation tierce** — OAuth 2.1 (PKCE, DCR, consentement) pour les connecteurs
   qui ne peuvent pas porter un token statique.
3. **Cloisonnement** — chaque tool vérifie l'appartenance de la ressource à
   l'identité résolue (multi-tenant : jamais un `getById` nu).
4. **Anti-abus** — rate-limit par identité (pas par token brut), en amont ou en
   périphérie des tools.
5. **Observabilité** — chaque appel de tool loggé (identité, tool, résultat).
6. **Isolation** — un mode sandbox/dry-run pour les tools à effet de bord.
7. **Exposition** — le manifeste/discovery agent exige lui-même un bearer, ne
   révèle rien à un appelant anonyme.

Cet ordre n'est pas arbitraire : chaque couche suppose que la précédente existe
(le rate-limit a besoin d'une identité ; l'audit du cloisonnement suppose l'identité
posée). Ne jamais implémenter/auditer une couche avant celles qui la précèdent.

## Choisir l'entrée

- Nouveau serveur MCP, ou durcissement volontaire de bout en bout → `phase-construction.md`.
- "Est-ce que mon MCP existant a des trous ?" / rapport d'incident / doute ponctuel
  → `phase-audit.md` (n'implique pas de reconstruire les couches déjà solides).

## Règles d'évolution

- Une couche générique supplémentaire, un pattern réutilisable (ex. nouvelle forme de
  garde de cloisonnement) → `references/couches.md`.
- Un piège spécifique à une stack/techno → `references/pieges.md`, section datée.
- Ne modifier ce SKILL.md que si l'ORDRE ou le NOMBRE des couches change (méthodologie),
  jamais pour du contenu qui a sa place dans une référence.
