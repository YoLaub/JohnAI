---
name: cert-pipeline
description: >
  Pipeline complet de préparation à une certification ou titre professionnel.
  Déclenche ce skill quand l'utilisateur mentionne : préparer une certification,
  passer un titre pro, préparer un examen RNCP, réviser pour une certification
  technique, "je passe ma certification", "aide-moi à préparer mon titre",
  ou "lance le pipeline certification".
  Orchestre 6 agents : cert-intake → referentiel-loader → gap-analyser
  → exam-preparer → cert-interviewer → cert-debrief.
---

# Cert Pipeline — Skill d'orchestration

Pipeline de préparation à la certification piloté par 6 agents spécialisés.
Conçu pour rester léger en contexte : jamais de document chargé en entier,
toujours un résumé structuré comme source de vérité partagée.

## Vue d'ensemble

```
[Quelle certification ?]
        ↓
  cert-intake          → Profil candidat + compte rendu année (500 mots max)
        ↓
  referentiel-loader   → Référentiel docs/ OU recherche web officielle
        ↓                 → Résumé structuré 1-2 pages (jamais le doc brut)
  gap-analyser         → Profil vs compétences requises → carte des écarts
        ↓
  exam-preparer        → Fiches de révision + questions probables par compétence
        ↓
  cert-interviewer     → Simulation entretien jury (conversationnel)
        ↓
  cert-debrief         → Bilan oral + points à consolider + probabilité de validation
```

## Étapes du pipeline

| # | Agent | Input | Output |
|---|-------|-------|--------|
| 1 | `cert-intake` | Nom certification + profil candidat | Fiche candidat + compte rendu structuré |
| 2 | `referentiel-loader` | Fichiers docs/ ou recherche web | Résumé référentiel (compétences + critères) |
| 3 | `gap-analyser` | Fiche candidat + résumé référentiel | Carte des écarts compétences |
| 4 | `exam-preparer` | Carte des écarts + résumé référentiel | Fiches révision + questions probables |
| 5 | `cert-interviewer` | Résumé référentiel + profil | Transcript entretien jury simulé |
| 6 | `cert-debrief` | Tous les outputs précédents | Bilan + axes + probabilité de validation |

## Règle critique — Gestion du contexte

> **Ne jamais charger un document de référentiel en entier dans le contexte.**

- `referentiel-loader` est le seul agent qui touche au document brut
- Il en extrait un **résumé structuré de 600 mots maximum**
- Tous les agents suivants travaillent uniquement sur ce résumé
- Le compte rendu candidat est limité à **500 mots** — l'agent refuse et
  demande une reformulation si c'est plus long
- Ces deux contraintes protègent contre les hallucinations et la dérive

## Contexte partagé entre agents

```json
{
  "certification": {
    "nom": "",
    "code_rncp": "",
    "organisme": "",
    "niveau": "",
    "source_referentiel": "docs/ | web"
  },
  "candidat": {
    "nom": "",
    "compte_rendu": "",
    "experience_annees": 0,
    "stack_ou_domaine": ""
  },
  "referentiel_resume": {
    "competences": [],
    "blocs": [],
    "criteres_evaluation": [],
    "format_examen": ""
  },
  "gaps": {
    "competences_maitrisees": [],
    "competences_partielles": [],
    "competences_manquantes": []
  },
  "entretien": {
    "transcript": [],
    "nb_tours": 0
  },
  "bilan": {
    "note_globale": 0,
    "probabilite_validation": "",
    "points_forts": [],
    "axes_consolidation": [],
    "conclusion": ""
  }
}
```

## Structure des fichiers du projet

```
mon-projet/
├── docs/                          ← déposer le référentiel ici (PDF ou MD)
│   └── referentiel-[CERTIFICATION].pdf
├── cert-pipeline/
│   └── output/
│       ├── referentiel-resume.md  ← résumé extrait par referentiel-loader
│       ├── gap-analysis.md        ← carte des écarts
│       ├── fiches-revision.md     ← fiches par compétence
│       ├── questions-probables.md ← banque de questions
│       ├── transcript-jury.md     ← transcript entretien simulé
│       └── bilan-final.md         ← bilan complet
└── .claude/
    └── ...
```

## Comment lancer le pipeline

### Pipeline complet
```
Lance le pipeline certification.
```
L'agent `cert-intake` prend la main et pose les questions.

### Reprendre à une étape
```
Reprends le pipeline certification à l'étape [nom-agent]
avec ce contexte : [résumé du contexte existant]
```

### Agent seul
```
Lance uniquement l'agent referentiel-loader pour la certification [NOM].
```
