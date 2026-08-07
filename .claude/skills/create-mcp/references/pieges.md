# Pièges connus — create-mcp

Append-only. Sections par stack, datées. Consulter "Génériques" systématiquement ;
la section de la stack du projet en cours si elle existe, sinon l'ignorer (ne pas
inventer une stack qui n'a pas encore mordu).

## Génériques

- (2026-07) Un id "déclaré" par l'appelant dans le schéma d'un tool (userId, tenantId,
  memberId...) rend l'identité dérivée du token inutile si un seul tool continue de
  le lire — le retirer de TOUS les schémas d'un coup, pas au fil de l'eau.
- (2026-07) Corriger le cloisonnement d'une fonction ne corrige pas ses fonctions
  sœurs (create/get/update/delete/send sur la même entité) — grep systématique après
  chaque fix, y compris en mode audit.
- (2026-07) Le rate-limit doit être un singleton créé une fois au démarrage du
  processus serveur, jamais recréé par requête — sinon chaque appel repart avec un
  bucket plein.

## Notes par stack (exemples à réutiliser tels quels si la stack correspond)

### Next.js + mcp-handler (vu sur CRM_TEAM, 2026-07)

- `withMcpAuth` (mcp-handler) émet déjà le header `WWW-Authenticate` avec le pointeur
  vers les métadonnées OAuth sur un 401 — ne pas le réécrire à la main.
- Un proxy/middleware Next qui protège `/api/*` par un cookie de session doit exclure
  explicitement les routes `/.well-known/*` (découverte OAuth), sinon les clients
  tiers ne peuvent jamais découvrir le serveur d'autorisation.
- `prisma migrate dev` refuse un shell non interactif → utiliser
  `migrate diff --from-config-datasource --to-schema ... --script` dans un dossier de
  migration daté, puis `migrate deploy`.
