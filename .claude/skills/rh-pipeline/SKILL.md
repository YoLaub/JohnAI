---
name: rh-pipeline
description: >
  Pipeline RH complet multi-agents pour traiter une candidature de A à Z.
  Déclenche ce skill quand l'utilisateur mentionne : analyser un CV, préparer
  une candidature, simuler un entretien RH ou technique, optimiser pour ATS,
  obtenir un bilan de recrutement, ou "lancer le pipeline RH".
  Orchestre 6 agents dans l'ordre : cv-analyst → cv-designer → cv-recruiter
  → rh-interviewer → tech-interviewer → debrief-agent.
---

# RH Pipeline — Skill d'orchestration

Pipeline de recrutement complet piloté par 6 agents spécialisés. Chaque agent
produit un livrable qui alimente le suivant.

## Vue d'ensemble

```
[CV brut] → cv-analyst → cv-designer → cv-recruiter
                                              ↓
                              rh-interviewer → tech-interviewer
                                              ↓
                                        debrief-agent → [Bilan final]
```

## Étapes du pipeline

| # | Agent | Input | Output |
|---|-------|-------|--------|
| 1 | `cv-analyst` | CV brut + poste visé | Score ATS, mots-clés, CV amélioré |
| 2 | `cv-designer` | CV amélioré + style souhaité | CV mis en forme |
| 3 | `cv-recruiter` | CV stylisé + email recruteur + ATS | Email envoi + rapport ATS |
| 4 | `rh-interviewer` | Profil candidat | Transcript entretien motivation |
| 5 | `tech-interviewer` | Profil + stack technique | Transcript entretien technique |
| 6 | `debrief-agent` | Tous les transcripts + scores | Bilan complet avec recommandation |

## Comment lancer le pipeline

### Pipeline complet (recommandé)
```
Lance le pipeline RH complet pour ce candidat :
- Poste visé : [POSTE]
- CV : [CONTENU CV]
```

### Agent unique
```
Lance uniquement l'agent [NOM_AGENT] avec ces données : [DONNÉES]
```

### Reprendre à une étape
```
Reprends le pipeline RH à l'étape [cv-designer / cv-recruiter / rh-interviewer / tech-interviewer / debrief-agent]
avec les données de contexte suivantes : [CONTEXTE]
```

## Contexte partagé entre agents

Chaque agent doit lire et écrire dans le contexte partagé suivant (à maintenir
en mémoire ou dans un fichier `rh-pipeline/context.json`) :

```json
{
  "candidat": {
    "nom": "",
    "poste_vise": "",
    "cv_brut": "",
    "cv_ameliore": "",
    "cv_style": ""
  },
  "scores": {
    "ats": 0,
    "impact": 0,
    "mots_cles_manquants": [],
    "problemes_structure": []
  },
  "recrutement": {
    "email_recruteur": "",
    "ats_cible": "",
    "email_envoye": "",
    "rapport_ats": ""
  },
  "entretiens": {
    "rh_transcript": [],
    "tech_transcript": []
  },
  "bilan": {
    "note_globale": 0,
    "recommandation": "",
    "points_forts": [],
    "axes_amelioration": [],
    "conclusion": ""
  }
}
```

## Fichiers de sortie

Tous les livrables vont dans `rh-pipeline/output/` :
- `output/cv-ameliore.md` — CV optimisé ATS
- `output/cv-style.md` — CV mis en forme
- `output/email-recruteur.md` — Email de soumission
- `output/rapport-ats.md` — Rapport compatibilité ATS
- `output/transcript-rh.md` — Transcript entretien RH
- `output/transcript-tech.md` — Transcript entretien tech
- `output/bilan-final.md` — Bilan complet avec recommandation

## Notes d'orchestration

- Chaque agent est autonome et peut être relancé indépendamment.
- Si une étape échoue, reprendre avec les données de contexte existantes.
- Les entretiens (RH + tech) sont conversationnels : 4 à 6 échanges chacun.
- Le bilan final synthétise toutes les étapes — ne pas le générer sans au
  moins l'analyse CV ET un entretien complété.
