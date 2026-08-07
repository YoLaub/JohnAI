# Oracle — Violations attendues dans bad-deck.md

La critique DOIT remonter exactement les écarts suivants. Tout écart absent ou supplémentaire constitue un échec du gate de critique.

---

## Diapo 1

| Type     | Violation attendue |
|----------|--------------------|
| contenu  | Titre-étiquette : "Architecture logicielle" — aucune assertion, aucun verbe d'action. |
| contenu  | Densité trop élevée : 6 puces (règle : ≤ 3 puces par diapo). |
| visuel   | Aucun visuel dominant (image, schéma ou diagramme) présent. |
| contenu  | Pas de notes orateur (section `<!-- … -->` absente). |

---

## Diapo 2

| Type     | Violation attendue |
|----------|--------------------|
| contenu  | Titre-étiquette : "Sécurité" — aucune assertion, aucun verbe d'action. |
| contenu  | Bloc de code projeté de 8 lignes (règle : un bloc de 5 lignes ou plus est en violation ; ≤ 4 lignes toléré). |
| visuel   | Aucun visuel dominant présent. |
| contenu  | Pas de notes orateur (section `<!-- … -->` absente). |

---

## Diapo 3

| Type     | Violation attendue |
|----------|--------------------|
| contenu  | Titre-étiquette : "Résultats" — aucune assertion, aucun verbe d'action. |
| contenu  | Chiffre précis non sourcé : "92,7 %" sans référence à une donnée source (rapport, outil de couverture, date). |
| contenu  | Pas de notes orateur (section `<!-- … -->` absente). |

---

## Global

| Type           | Violation attendue |
|----------------|--------------------|
| altitude       | Jargon non explicité signalable si le rendu est illisible pour un jury non-technique ("Prisma", "pgvector", "hCaptcha", "safeParse" etc.). |
| notes orateur  | Aucune des 3 diapos ne comporte de notes orateur — signaler le manque de manière globale en plus des mentions par diapo. |

---

## Récapitulatif des violations par règle dure

| Règle dure                              | Violation plantée               | Diapo(s) |
|-----------------------------------------|---------------------------------|----------|
| Titre = assertion (pas étiquette)       | Titres nominaux sans verbe      | 1, 2, 3  |
| Un visuel dominant                      | Aucune image sur les diapos     | 1, 2     |
| Densité ≤ 3 puces ou ≤ 15 mots hors titre | 6 puces diapo 1                | 1        |
| Pas de code projeté (> 4 lignes)        | Bloc TS de 8 lignes             | 2        |
| Notes orateur présentes                 | Aucune note sur aucune diapo    | 1, 2, 3  |
| Données réelles sourcées               | "92,7 %" sans source            | 3        |
| Altitude (jargon explicité)             | Termes techniques non définis   | 1, 2 (global) |
