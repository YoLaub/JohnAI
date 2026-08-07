#!/usr/bin/env python3
"""
bootstrap_brain.py — Crée la structure d'un cerveau projet (vault Obsidian).

Idempotent : si le vault existe déjà, ne détruit rien, complète seulement ce qui manque.

Usage:
    python bootstrap_brain.py \\
        --name "mon-app" \\
        --path "~/ObsidianVaults/mon-app-brain" \\
        --description "Backend Strapi v5 + Turborepo frontend" \\
        --stack "strapi,nextjs,postgres"

Les templates (y compris la config .obsidian/) sont embarqués dans ce script
pour qu'il soit autonome.
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path
from textwrap import dedent


# --- Structure de dossiers à créer ---

DIRECTORIES = [
    "raw",
    "raw/docs",
    "raw/code",
    "raw/conversations",
    "raw/external",
    "wiki",
    "wiki/_meta",
    "wiki/entities",
    "wiki/concepts",
    "wiki/decisions",
    "wiki/moc",
    "reports",
    "reports/linting",
    "reports/analysis",
    ".obsidian",
]


# --- Templates embarqués (frontmatter + contenu de base) ---

def tpl_root_readme(name: str, description: str, today: str) -> str:
    return dedent(f"""\
        # {name} — Cerveau projet

        > {description}

        Ce vault est un cerveau projet basé sur l'approche **LLM Wiki** de Karpathy.
        Il suit une architecture en 3 couches :

        - **`raw/`** — Sources immuables (lecture seule pour l'IA)
        - **`wiki/`** — Mémoire active compilée (édité par l'IA, validé par l'humain)
        - **`reports/`** — Analyses et rapports générés

        ## Entry point

        Ouvrir `wiki/INDEX.md` — c'est le point d'entrée du graph de connaissance.

        ## Workflow

        1. Déposer des sources dans `raw/`
        2. Demander à Claude de "compiler le raw en wiki"
        3. Obsidian affiche le graph qui évolue
        4. Demander périodiquement un "linting du cerveau"

        ## Créé le

        {today} via `brain-builder` skill.
        """)


def tpl_raw_readme() -> str:
    return dedent("""\
        # raw/ — Sources immuables

        Ce dossier contient les sources brutes du cerveau projet.

        ## Règles

        - **L'IA est en lecture seule ici.** Elle ne modifie ni ne supprime jamais rien dans `raw/`.
        - **L'humain dépose** : PDF, transcripts, dumps de code, notes brutes, captures web.
        - **Nommage recommandé** : `YYYY-MM-DD_slug-descriptif.ext` pour tracer la chronologie.

        ## Sous-dossiers

        - `docs/` — Documents formels (specs, PDF, docs techniques)
        - `code/` — Dumps de code, fichiers de config
        - `conversations/` — Transcripts de chats, réunions
        - `external/` — Articles web, refs, captures
        """)


def tpl_index(name: str, description: str, today: str) -> str:
    return dedent(f"""\
        ---
        title: Index
        type: moc
        created: {today}
        updated: {today}
        tags: [index, moc]
        status: validated
        ---

        # {name} — Cerveau projet

        > {description}

        ## Méta

        - [[_meta/IDENTITY|Identité du projet]]
        - [[_meta/CONVENTIONS|Conventions]]
        - [[_meta/CENTRAL_LINKS|Liens cerveau central]]
        - [[_meta/COMPILATION_LOG|Log des compilations]]

        ## Maps of Content

        _(vides au bootstrap — à enrichir au fur et à mesure que le wiki grandit)_

        ## Entités principales

        _(vides au bootstrap)_

        ## Décisions récentes

        _(vides au bootstrap)_
        """)


def tpl_identity(name: str, description: str, stack: str, today: str) -> str:
    stack_lines = "\n".join(f"- {s.strip()}" for s in stack.split(",") if s.strip()) or "_(à renseigner)_"
    return (
        f"---\n"
        f"title: Identité du cerveau\n"
        f"type: meta\n"
        f"created: {today}\n"
        f"updated: {today}\n"
        f"tags: [meta, identity]\n"
        f"status: draft\n"
        f"---\n\n"
        f"# Identité\n\n"
        f"## Nom du projet\n\n"
        f"{name}\n\n"
        f"## Description\n\n"
        f"{description}\n\n"
        f"## Périmètre\n\n"
        f"Ce qui appartient à ce cerveau :\n\n"
        f"- _(à renseigner)_\n\n"
        f"## Hors-périmètre\n\n"
        f"Ce qui N'appartient PAS à ce cerveau (vit dans le central ou ailleurs) :\n\n"
        f"- Préférences personnelles transverses\n"
        f"- Méthodes et patterns génériques\n"
        f"- Vocabulaire commun à plusieurs projets\n\n"
        f"## Stack technique\n\n"
        f"{stack_lines}\n\n"
        f"## Rôles utilisateurs\n\n"
        f"- _(à renseigner : User, Admin, etc.)_\n\n"
        f"## Statut du cerveau\n\n"
        f"- **Phase actuelle** : Bootstrap terminé\n"
        f"- **Prochaine étape** : Déposer des sources dans `raw/`\n"
    )


def tpl_conventions(today: str) -> str:
    return dedent(f"""\
        ---
        title: Conventions appliquées à ce cerveau
        type: meta
        created: {today}
        updated: {today}
        tags: [meta, conventions]
        status: validated
        ---

        # Conventions

        Règles que l'IA applique quand elle écrit dans ce cerveau.
        **L'humain peut les modifier**, mais toute modification doit être loggée dans `COMPILATION_LOG.md`.

        ## Nommage

        - Entités : `PascalCase.md` (ex: `AuthService.md`)
        - MOC : `kebab-case.md` (ex: `api-design-moc.md`)
        - Décisions : `YYYY-MM-DD-slug.md` (ex: `2026-04-16-choix-jest.md`)
        - Meta : `UPPERCASE.md` (ex: `IDENTITY.md`)

        ## Liens

        - Wikilinks `[[NomNote]]` pour l'intra-vault
        - Références explicites vers `raw/` : `[[raw/docs/xxx.pdf]]`
        - Refs vers le cerveau central : préfixe `central://` (voir `CENTRAL_LINKS.md`)

        ## Frontmatter YAML obligatoire

        Toute note dans `wiki/` a au minimum :

        ```yaml
        title: ...
        type: entity | concept | decision | moc | meta
        created: YYYY-MM-DD
        updated: YYYY-MM-DD
        tags: [...]
        status: draft | validated | deprecated
        ```

        Le champ `source:` est obligatoire si la note dérive d'un fichier de `raw/`.

        ## Workflow IA

        - **Compilation incrémentale** : les notes existantes sont enrichies, pas réécrites
        - **Contradictions** : créer une section `## Contradictions` plutôt qu'écraser
        - **Citation systématique** : tout fait ajouté au wiki pointe vers sa source
        - **Non-duplication avec le central** : si un concept est générique, il vit dans le central

        ## Règles de non-suppression

        - **Jamais** de suppression auto de notes dans `wiki/`
        - Les notes obsolètes passent en `status: deprecated` mais restent
        - Seul l'humain peut supprimer
        """)


def tpl_central_links(today: str) -> str:
    return dedent(f"""\
        ---
        title: Liens vers le cerveau central
        type: meta
        created: {today}
        updated: {today}
        tags: [meta, central]
        status: draft
        ---

        # Liens vers le cerveau central

        > Ce fichier sert d'interface entre ce cerveau projet et le cerveau central.
        > Initialement vide. Voir le protocole complet dans le skill `brain-builder` :
        > `references/central-brain-protocol.md`.

        ## Statut

        - [ ] Cerveau central initialisé
        - [ ] Chemin du central renseigné ci-dessous
        - [ ] Concepts partagés référencés

        ## Chemin du central

        _(à renseigner quand le cerveau central existera, ex: `~/ObsidianVaults/central-brain/`)_

        ## Concepts hébergés dans le central et référencés ici

        Format de référence :

        ```
        - `central://categorie/nom-du-concept` — Pourquoi c'est utilisé ici
        ```

        _(aucune référence pour l'instant)_

        ## Migrations suggérées vers le central

        _(rempli lors des phases de linting — concepts détectés comme génériques
        qui gagneraient à vivre dans le central)_
        """)


def tpl_compilation_log(today: str) -> str:
    return dedent(f"""\
        ---
        title: Historique des compilations
        type: meta
        created: {today}
        updated: {today}
        tags: [meta, log]
        status: validated
        ---

        # Historique des compilations

        Chaque entrée trace un cycle de compilation `raw/` → `wiki/`.

        ## Format d'une entrée

        ```
        ## YYYY-MM-DD HH:MM

        - **Sources lues** : [liste]
        - **Notes créées** : [liste]
        - **Notes mises à jour** : [liste]
        - **Contradictions détectées** : [liste]
        - **Notes** : [commentaires libres]
        ```

        ---

        ## Entrées

        _(aucune compilation effectuée — log initialisé au bootstrap le {today})_
        """)


def tpl_obsidian_app_json() -> str:
    return dedent("""\
        {
          "alwaysUpdateLinks": true,
          "newLinkFormat": "shortest",
          "useMarkdownLinks": false,
          "attachmentFolderPath": "raw/attachments",
          "showLineNumber": true,
          "readableLineLength": true
        }
        """)


def tpl_obsidian_core_plugins() -> str:
    return dedent("""\
        [
          "file-explorer",
          "global-search",
          "switcher",
          "graph",
          "backlink",
          "outgoing-link",
          "tag-pane",
          "page-preview",
          "markdown-importer",
          "word-count",
          "outline",
          "file-recovery"
        ]
        """)


def tpl_obsidian_graph_json() -> str:
    return dedent("""\
        {
          "collapse-filter": false,
          "search": "",
          "showTags": true,
          "showAttachments": false,
          "hideUnresolved": false,
          "showOrphans": true,
          "collapse-color-groups": false,
          "colorGroups": [
            {
              "query": "path:wiki/entities",
              "color": { "a": 1, "rgb": 5431518 }
            },
            {
              "query": "path:wiki/concepts",
              "color": { "a": 1, "rgb": 14048348 }
            },
            {
              "query": "path:wiki/decisions",
              "color": { "a": 1, "rgb": 14701138 }
            },
            {
              "query": "path:wiki/moc",
              "color": { "a": 1, "rgb": 5419488 }
            },
            {
              "query": "path:wiki/_meta",
              "color": { "a": 1, "rgb": 11053224 }
            },
            {
              "query": "path:raw",
              "color": { "a": 1, "rgb": 7254228 }
            }
          ]
        }
        """)


# --- Logique principale ---

def safe_write(path: Path, content: str, force: bool = False) -> str:
    """
    Écrit le fichier seulement s'il n'existe pas (sauf si force=True).
    Retourne un statut : 'created', 'skipped', 'overwritten'.
    """
    if path.exists() and not force:
        return "skipped"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "overwritten" if path.exists() and force else "created"


def bootstrap(name: str, vault_path: Path, description: str, stack: str, force: bool = False) -> dict:
    today = date.today().isoformat()
    report = {"created": [], "skipped": [], "overwritten": []}

    # 1. Créer les dossiers
    for d in DIRECTORIES:
        (vault_path / d).mkdir(parents=True, exist_ok=True)

    # 2. Écrire les fichiers racine et meta
    files_to_write = [
        (vault_path / "README.md", tpl_root_readme(name, description, today)),
        (vault_path / "raw" / "README.md", tpl_raw_readme()),
        (vault_path / "wiki" / "INDEX.md", tpl_index(name, description, today)),
        (vault_path / "wiki" / "_meta" / "IDENTITY.md", tpl_identity(name, description, stack, today)),
        (vault_path / "wiki" / "_meta" / "CONVENTIONS.md", tpl_conventions(today)),
        (vault_path / "wiki" / "_meta" / "CENTRAL_LINKS.md", tpl_central_links(today)),
        (vault_path / "wiki" / "_meta" / "COMPILATION_LOG.md", tpl_compilation_log(today)),
        (vault_path / ".obsidian" / "app.json", tpl_obsidian_app_json()),
        (vault_path / ".obsidian" / "core-plugins.json", tpl_obsidian_core_plugins()),
        (vault_path / ".obsidian" / "graph.json", tpl_obsidian_graph_json()),
    ]

    for path, content in files_to_write:
        status = safe_write(path, content, force=force)
        rel = path.relative_to(vault_path)
        report[status].append(str(rel))

    # 3. Fichiers .gitkeep dans les dossiers vides pour préserver la structure si versionné
    empty_dirs_to_mark = [
        "raw/docs", "raw/code", "raw/conversations", "raw/external",
        "wiki/entities", "wiki/concepts", "wiki/decisions", "wiki/moc",
        "reports/linting", "reports/analysis",
    ]
    for d in empty_dirs_to_mark:
        gitkeep = vault_path / d / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")
            report["created"].append(str(gitkeep.relative_to(vault_path)))

    return report


def print_report(name: str, vault_path: Path, report: dict) -> None:
    print()
    print(f"✅ Cerveau \"{name}\" initialisé à : {vault_path}")
    print()
    print(f"  {len(report['created'])} fichier(s) créé(s)")
    if report["skipped"]:
        print(f"  {len(report['skipped'])} fichier(s) déjà présent(s) (non modifiés)")
    if report["overwritten"]:
        print(f"  {len(report['overwritten'])} fichier(s) écrasé(s) (mode --force)")
    print()
    print("Structure :")
    print(f"  raw/       ← dépose tes sources ici")
    print(f"  wiki/      ← mémoire active (l'IA écrit ici)")
    print(f"  reports/   ← rapports d'analyse et linting")
    print(f"  .obsidian/ ← config minimale déjà posée")
    print()
    print("Prochaines étapes suggérées :")
    print(f"  1. Ouvrir le vault dans Obsidian : {vault_path}")
    print(f"  2. Déposer tes premières sources dans raw/")
    print(f"  3. Demander à Claude : \"compile le raw en wiki\" quand tu as du contenu")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap un cerveau projet (vault Obsidian structuré)."
    )
    parser.add_argument("--name", required=True, help="Nom court du projet (kebab-case recommandé)")
    parser.add_argument("--path", required=True, help="Chemin du vault à créer")
    parser.add_argument(
        "--description", default="",
        help="Description courte du projet (1-2 phrases)"
    )
    parser.add_argument(
        "--stack", default="",
        help="Stack technique, séparée par virgules (ex: 'strapi,nextjs,postgres')"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Écraser les fichiers existants (par défaut : préservés)"
    )

    args = parser.parse_args()

    vault_path = Path(os.path.expanduser(args.path)).resolve()

    # Garde-fou : refuser de bootstrap sur un dossier qui a du contenu non-cerveau
    if vault_path.exists() and any(vault_path.iterdir()):
        expected_markers = [vault_path / "wiki" / "INDEX.md", vault_path / "raw"]
        if not any(m.exists() for m in expected_markers):
            print(
                f"⚠️  Le dossier {vault_path} existe et contient des fichiers mais ne ressemble "
                f"pas à un cerveau projet existant.\n"
                f"   Refus de bootstrap pour éviter une collision. Utilise un chemin vide ou "
                f"un cerveau existant.",
                file=sys.stderr,
            )
            return 2

    report = bootstrap(
        name=args.name,
        vault_path=vault_path,
        description=args.description or f"Cerveau projet {args.name}",
        stack=args.stack,
        force=args.force,
    )

    print_report(args.name, vault_path, report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
