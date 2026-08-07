# Catalogue par type de commerce

Fichier append-only : un secteur = une section, ajouter sans réécrire les autres.
Sert en phase 1 à savoir quoi demander dans la question ouverte de cadrage, et en
phase 3 à savoir quel schéma de contenu structurer.

## Fast-food / restauration rapide (référence : en-cas-2-faim, 2026-07)
À demander : adresse, téléphone, horaires (souvent coupés midi/soir, jours
différents), sur place/à emporter/livraison, carte source (photo/PDF du menu),
catégories (pizzas, burgers, kebabs, tacos...), prix multi-formats (tailles,
sans/avec frites, pièces), allergènes si affichés, identité visuelle existante.
Contenu structuré : Content Collection `menu` (une catégorie = un fichier, items
avec prix éventuellement multiples/étiquetés — cf. `src/lib/menu.schema.ts` et
`src/content/menu/*.yaml` du projet en-cas-2-faim, réutilisables tels quels comme
patron). JSON-LD `Restaurant` avec `openingHoursSpecification`.

## Restaurant traditionnel
Proche du fast-food mais : réservation à mettre en avant (lien externe ou
téléphone), menu souvent moins volumineux mais avec descriptions plus longues
(ambiance/histoire du plat), photos de salle en plus des plats, mentions
allergènes plus systématiques (obligation légale restauration traditionnelle).

## Coiffeur / institut de beauté
À demander : liste des prestations + tarifs (souvent par catégorie : coupe,
couleur, soin...), durée des prestations si affichée, lien de prise de RDV en
ligne existant (Planity, Treatwell...) à intégrer en CTA principal plutôt qu'un
téléphone seul, photos de réalisations. Contenu structuré : collection
`prestations` (catégorie, nom, durée optionnelle, prix).

## Artisan / commerce (boulanger, primeur, fleuriste...)
À demander : spécialités mises en avant, horaires (souvent avec fermeture
hebdomadaire), zone de chalandise/livraison si applicable, avis clients existants
à reprendre (Google My Business) plutôt qu'en inventer. Contenu structuré plus
léger : pas toujours de "menu" formel, parfois juste une mise en avant de
spécialités + horaires + contact.
