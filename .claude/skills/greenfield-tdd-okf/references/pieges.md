# Pièges connus

Fichier append-only : ajouter chaque nouveau piège sous la section de la stack concernée
(créer la section si besoin, la dater). Ne consulter que les sections correspondant à la
stack du projet en cours — inutile de charger le reste en contexte.

## Génériques (toute stack)
- Webhooks inter-services : HMAC-SHA256 hex + comparaison timing-safe, contrat de payload
  partagé (schéma validé des deux côtés).
- Numérotation légale : transaction + contrainte unique (memberId, year, seq).
- Feature qui a besoin d'un secret/SMTP externe : prévoir un mode simulé (jsonTransport)
  pour que l'app tourne sans config ; le vrai transport s'active si la variable d'env est présente.
- Rendre en headless une page protégée : jeton court (JWT) lié au chemin, autorisé dans le proxy.
- Intl fr-FR : séparateurs = espaces insécables ; comparer via le formateur, pas une chaîne écrite.

## Next 16 / TypeScript (2026-07, projet CRM_TEAM)
- npm workspaces + `exports` + `turbopack.root` pour un package TS partagé.
- jose/crypto sous vitest jsdom → `// @vitest-environment node` sur les tests de services.
- tsx/seeds : `import "dotenv/config"` obligatoire.
- Next : `new Response(new Uint8Array(buffer))` — BodyInit n'accepte pas Buffer directement.
- Drag & drop : HTML5 dataTransfer + useOptimistic + server action typée, zéro dépendance.

## Prisma 7 (2026-07)
- Generator `prisma-client`, prisma.config.ts + dotenv, driver adapter requis.

## Python & interop Python ↔ TS (2026-07)
- pydantic→zod : `by_alias=True, exclude_none=True` (zod `.optional()` refuse null).
- Scrapling : navigateurs via l'exe `scrapling install`, pas `python -m scrapling` ; le
  Playwright ainsi installé est réutilisable pour du rendu PDF (ne pas réembarquer Chromium).
