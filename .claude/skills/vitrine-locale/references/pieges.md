# Pièges connus — vitrine locale Astro

Fichier append-only : ajouter chaque nouveau piège sous sa section, dater.

## Astro / Tailwind (2026-07, projets en-cas-2-faim, sagefemmevannes)
- npm `allow-scripts` bloque les postinstall (esbuild, sharp) → build KO tant
  qu'on n'a pas `npm approve-scripts esbuild sharp` (+ `fsevents` sur macOS) puis
  `npm rebuild`. Vérifier après tout install.
- Tailwind v4 : plus de `tailwind.config.js` ; config CSS-first via `@theme` dans
  le CSS + plugin `@tailwindcss/vite` dans `astro.config`.
- Content Collections : schéma Zod dans un fichier à part (`src/lib/*.schema.ts`),
  importé depuis `zod` — pas `astro:content` (module virtuel non résolvable en
  Vitest) — testable en unitaire ET réutilisé par `content.config.ts`.
- `npm create astro@latest .` refuse un dossier non vide (CLAUDE.md, assets déjà
  présents) → scaffolder dans un sous-dossier temporaire puis fusionner les
  fichiers à la racine, supprimer le `CLAUDE.md`/`AGENTS.md` générés si un
  CLAUDE.md du projet existe déjà.
- La version stable d'Astro change vite : vérifier `npm view astro version`
  avant de scaffolder plutôt que de supposer une version d'un projet précédent
  (constaté 2026-07 : v5 supposée dans un cadrage initial, v7 réellement
  installée — `src/content.config.ts` reste le bon emplacement de config des
  collections, vérifié dans les sources livrées après install).
- E2E d'un site statique = `astro build` + un script Node qui grep le HTML de
  `dist/` (CTA, coordonnées, JSON-LD, catégories attendues) ; testable sans
  navigateur.
- Intl fr-FR : formatage des prix via `Intl.NumberFormat('fr-FR', {style:
  'currency', currency: 'EUR'})`, jamais une chaîne écrite à la main (espace
  insécable différent d'un espace normal, le test doit matcher `\s` pas un
  caractère précis).
- Frontmatter YAML : une valeur contenant « : » doit être quotée, sinon
  gray-matter/js-yaml lève « incomplete explicit mapping pair ».
