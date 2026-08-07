# Mémoire — Intégration de pipelines dans skills_stock

## Règle d'intégration d'un nouveau pipeline

À chaque ajout d'un pipeline dans ce dépôt, suivre exactement ces étapes dans l'ordre.

---

## Structure cible d'un pipeline

```
.claude/
├── agents/
│   └── [domaine]/           ← un sous-dossier par domaine métier
│       ├── agent-1.md
│       ├── agent-2.md
│       └── ...
└── skills/
    └── [nom-pipeline]/
        └── SKILL.md
```

**Convention de nommage :**
- Le sous-dossier `agents/` porte le nom court du domaine (`rh`, `cert`, `finance`…)
- Le dossier skill porte le nom du pipeline avec suffixe `-pipeline` (`rh-pipeline`, `cert-pipeline`…)
- Les agents sont nommés en kebab-case, préfixés par le domaine si nécessaire (`cert-intake`, `cv-analyst`…)

---

## Checklist d'intégration

### 1. Copier les fichiers

```bash
# Créer les dossiers
mkdir -p .claude/agents/[domaine] .claude/skills/[nom-pipeline]

# Copier les agents
cp /source/agents/*.md .claude/agents/[domaine]/

# Copier le skill
cp /source/skills/[nom-pipeline]/SKILL.md .claude/skills/[nom-pipeline]/
```

### 2. Mettre à jour `install.sh`

**a) Ajouter les entrées dans `CATALOGUE` :**

```bash
# ── [Nom Pipeline] ────────────────────────
"[nom-pipeline]|[Nom Pipeline] complet (skill orchestrateur)|skill|.claude/skills/[nom-pipeline]/SKILL.md"
"[agent-1]|Agent — [description courte]|agent|.claude/agents/[domaine]/[agent-1].md"
# ... un par agent
```

Format d'une entrée : `"id|label|type(skill|agent)|chemin-dans-repo"`

**b) Ajouter le bundle dans `BUNDLES` :**

```bash
BUNDLES["[domaine]"]="[nom-pipeline] [agent-1] [agent-2] ..."
```

**c) Mettre à jour `BUNDLES["tout"]`** pour inclure les nouveaux IDs.

**d) Ajouter l'entrée dans `show_bundles()` :**

```bash
echo -e "  ${BOLD}[N]${RESET} [domaine]  — [description courte]"
```

**e) Ajouter le cas dans `get_ids_from_selection()` :**

```bash
N) bundle_key="[domaine]" ;;
```

> Incrémenter N en suivant la numérotation existante.

### 3. Mettre à jour `README.md` (racine)

Dans la section **Structure du dépôt**, ajouter le nouveau domaine dans l'arbre :

```
├── agents/
│   ├── [domaine]/              ← [Nom Pipeline] (N agents)
│   │   ├── agent-1.md
│   │   └── ...
```

Et ajouter le skill dans la liste des skills :

```
├── skills/
│   └── [nom-pipeline]/
│       └── SKILL.md
```

### 4. Mettre à jour `.claude/README.md`

Ajouter le pipeline dans la structure `.claude/` et créer une section **Pipeline [Nom]** avec :
- Usage rapide (commande de déclenchement)
- Tableau des outputs avec `[pipeline]/output/` comme dossier cible

---

## Pipelines actifs

| Pipeline | Domaine | Agents | Skill | Bundle |
|----------|---------|--------|-------|--------|
| RH Pipeline | `rh` | 6 agents (`cv-analyst`, `cv-designer`, `cv-recruiter`, `rh-interviewer`, `tech-interviewer`, `debrief-agent`) | `rh-pipeline` | `rh`, `cv-only` |
| Cert Pipeline | `cert` | 6 agents (`cert-intake`, `referentiel-loader`, `gap-analyser`, `exam-preparer`, `cert-interviewer`, `cert-debrief`) | `cert-pipeline` | `cert` |

---

## Règles de structuration des agents

Un agent `.md` suit toujours ce gabarit (frontmatter YAML obligatoire) :

```markdown
---
name: [nom-agent]
description: >
  Ce que fait l'agent.
  Intentions utilisateur qui doivent le déclencher : "...", "...".
---

# Agent : [nom-agent]

## Rôle
## Inputs attendus
## Processus
## Output
## Passage à l'étape suivante  ← optionnel
```

Le champ `description:` est le **déclencheur** lu par Claude Code. Il doit lister les formulations naturelles de l'utilisateur.

## Règles de structuration du SKILL.md

```markdown
---
name: [nom-pipeline]
description: >
  Ce que fait le pipeline. Intentions déclenchantes.
---

# [Nom] Pipeline — Skill d'orchestration

## Vue d'ensemble     ← schéma ASCII du flux
## Étapes du pipeline ← tableau # | Agent | Input | Output
## Contexte partagé  ← JSON de l'état partagé entre agents
## Comment lancer le pipeline
```

---

## Vérification post-intégration

```bash
# Vérifier la structure des fichiers copiés
ls .claude/agents/[domaine]/
ls .claude/skills/[nom-pipeline]/

# Vérifier que le CATALOGUE contient les nouveaux IDs
grep "[nom-pipeline]" install.sh

# Vérifier que le bundle est déclaré
grep "BUNDLES\[\"[domaine]\"\]" install.sh
```
