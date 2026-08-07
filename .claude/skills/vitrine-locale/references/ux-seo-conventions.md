# Conventions UX/SEO — vitrine locale one-page

Base établie 2026-07 (en-cas-2-faim). **Ces règles bougent** (Core Web Vitals,
WCAG, Schema.org évoluent) : avant de les appliquer telles quelles sur un nouveau
projet, faire une recherche rapide pour vérifier qu'elles n'ont pas changé de
version/seuil depuis la dernière mise à jour de ce fichier — ne jamais les tenir
pour acquises indéfiniment. Mettre à jour ce fichier (section datée) si un seuil
a changé.

## UX
- Mobile-first : la majorité du trafic d'un commerce local consulte au
  téléphone, souvent en marchant ou en voiture — CTA tél/itinéraire visibles sans
  scroll, cible tactile ≥ 44×44px.
- Contrastes AA vérifiés par calcul (ratio ≥ 4.5:1 texte normal, ≥ 3:1 texte
  large/UI) — jamais "à l'œil", surtout si la charte du client a des couleurs
  vives (vert, orange...).
- Hiérarchie du contenu structuré (menu/prestations) : catégories scannables,
  prix alignés et lisibles, pas de bloc de texte dense pour un tarif.
- Un seul CTA principal par section visible à l'écran (appeler, itinéraire) ;
  les CTA secondaires ne doivent pas concurrencer visuellement le principal.
- Formulaire de contact seulement s'il n'y a pas déjà un canal plus direct
  (téléphone, lien de résa existant) — ne pas ajouter de friction inutile.

## SEO local
- JSON-LD adapté au secteur (`Restaurant`, `HairSalon`, `LocalBusiness`...),
  toujours avec adresse structurée, téléphone, horaires
  (`openingHoursSpecification`).
- Title/meta description uniques par page, incluant la ville et le secteur
  d'activité en langage naturel (pas de bourrage de mots-clés).
- Sitemap dès qu'il y a plus d'une page.
- URLs propres, sans paramètres inutiles.

## Performance
- Lighthouse ≥ 95 visé, images optimisées (`astro:assets`, formats modernes),
  0 JS par défaut (îlots seulement si interaction le justifie réellement).
