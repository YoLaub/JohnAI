---
name: vitrine-locale
description: >
  Construit un site vitrine one-page pour un commerce local (fast-food, restaurant,
  artisan, coiffeur, institut...) en Astro + Tailwind : cadrage par question ouverte
  puis questions fermées de réflexion sur les zones d'ambiguïté réelles, recherche
  design actuelle, charte de style anti-générique/anti-emoji/anti-tiret, puis
  développement en git-flow + TDD + index OKF (même principe que greenfield-tdd-okf,
  mais spécialisé site vitrine local Astro one-page). Déclenche quand l'utilisateur
  dit : "site pour [un commerce]", "site vitrine one-page", "refonte du site de
  [client]", "nouveau site pour un restaurant/fast-food/coiffeur/artisan". Ne pas
  confondre avec greenfield-tdd-okf (produit applicatif générique, multi-pages,
  logique métier) : ici toujours Astro statique, toujours one-page, toujours
  commerce local.
---

# Vitrine locale (Astro)

Méthode éprouvée sur en-cas-2-faim et sagefemmevannes (2026-07). Un commerce local,
une page, un cadrage qui creuse avant de coder.

Références (à lire au moment indiqué, pas avant) :
- `references/business-types.md` — catalogue de contenu par type de commerce
  (fast-food, restaurant, coiffeur/institut, artisan...), append-only. Lire en phase 1.
- `references/style-guide.md` — charte anti-générique/anti-IA (tirets, emoji,
  tournures). Lire en phase 3, et à chaque relecture de copy en phase 5.
- `references/ux-seo-conventions.md` — conventions UX/SEO + protocole de
  vérification des règles actuelles. Lire en phase 3.
- `references/pieges.md` — pièges Astro/Tailwind connus, sections datées. Lire en
  phase 4 avant de configurer l'outillage.
- `references/okf-fiche-template.md` — format de fiche OKF. Lire à la première fiche.

## Phase 1 — Cadrage ouvert
Une question ouverte (pas de QCM) pour recueillir : nom du commerce, adresse,
horaires, téléphone, contenu source (menu/prestations/tarifs en pièce jointe ou
texte), identité visuelle existante, ambition ("juste une vitrine" vs "donner
envie/vendre"), sites concurrents ou aimés. Consulter `references/business-types.md`
pour savoir quoi demander selon le secteur. Écrire/mettre à jour CLAUDE.md avec ces
infos comme source de vérité — ne jamais inventer un fait business.

## Phase 2 — Cadrage fermé (réflexion sur la phase 1)
À partir de CE QUI A ÉTÉ DIT en phase 1 — pas d'une checklist générique — identifier
2 à 4 zones d'ambiguïté réelles (ex. fonctionnalité ludique à intégrer, one-page vs
sections, ton de la copy, priorité mobile) et les trancher par AskUserQuestion
fermé. Écrire le plan (contexte, décisions, architecture) et le faire valider
(EnterPlanMode).

## Phase 3 — Recherche design & charte
Recherche web (2-3 références) de sites vitrine récents du même secteur — jamais
copier/scraper une charte, s'en inspirer. Fixer palette (contrastes AA vérifiés par
calcul, jamais à l'œil), typo, conventions UX/SEO (`references/ux-seo-conventions.md`)
et charte de style (`references/style-guide.md`).

## Phase 4 — Bootstrap (branche `feature/bootstrap`)
Avant de scaffolder : vérifier la version Astro stable actuelle et ses conventions
récentes (`npm view astro version`, docs embarquées après install) — ne jamais
supposer d'une session précédente, Astro évolue vite. Puis git-flow `main` → `dev` →
branches feature, Tailwind CSS-first, contenu structuré en Content Collection + Zod,
script E2E = build + grep du HTML. Lire `references/pieges.md` avant de configurer
l'outillage.

## Phase 5 — Chaque feature (TDD, OKF)
Même principe que greenfield-tdd-okf phase 3 : logique pure testée en premier,
suite verte → build → E2E réel, fiche OKF par feature (`docs/index/`), merge
`--no-ff` vers `dev` uniquement si tout est vert. Relire chaque texte visible avec
`references/style-guide.md` avant de merger.

## Phase 6 — Clôture
Rétro dans `retro.md`, pièges génériques remontés dans `references/pieges.md`,
merge `dev` → `main`, tag. Ne modifier ce SKILL.md que si la méthodologie change.
