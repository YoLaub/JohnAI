#!/usr/bin/env python3
"""
snapshot.py — Sauvegarde une version d'un SKILL.md avant modification.

Usage:
    python snapshot.py --skill chemin/vers/SKILL.md --workspace optimization-workspace/ --iteration 0

Crée optimization-workspace/iteration-N/SKILL.md (copie read-only)
et génère un fichier metadata.json avec les infos de la version.
"""

import shutil
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime


def count_tokens_approx(text: str) -> int:
    """Approximation grossière : 1 token ≈ 4 caractères."""
    return len(text) // 4


def snapshot_skill(skill_path: Path, workspace: Path, iteration: int) -> dict:
    """Crée un snapshot d'un skill dans le workspace."""
    iter_dir = workspace / f"iteration-{iteration}"
    iter_dir.mkdir(parents=True, exist_ok=True)
    
    dest = iter_dir / "SKILL.md"
    shutil.copy2(skill_path, dest)
    
    content = skill_path.read_text(encoding="utf-8")
    token_count = count_tokens_approx(content)
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    
    metadata = {
        "iteration": iteration,
        "source_path": str(skill_path),
        "snapshot_path": str(dest),
        "timestamp": datetime.now().isoformat(),
        "tokens_approx": token_count,
        "content_hash": content_hash,
        "lines": len(content.splitlines()),
        "modifications": []  # Sera rempli après application des micro-éditions
    }
    
    meta_path = iter_dir / "metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Snapshot créé : {dest}")
    print(f"   Tokens (approx) : {token_count}")
    print(f"   Hash : {content_hash}")
    print(f"   Lignes : {metadata['lines']}")
    
    return metadata


def diff_snapshots(iter_before: Path, iter_after: Path) -> str:
    """Génère un diff lisible entre deux snapshots."""
    before_file = iter_before / "SKILL.md"
    after_file = iter_after / "SKILL.md"
    
    if not before_file.exists() or not after_file.exists():
        return "Fichiers snapshot manquants."
    
    before_lines = before_file.read_text(encoding="utf-8").splitlines()
    after_lines = after_file.read_text(encoding="utf-8").splitlines()
    
    import difflib
    diff = list(difflib.unified_diff(
        before_lines, after_lines,
        fromfile=f"{iter_before.name}/SKILL.md",
        tofile=f"{iter_after.name}/SKILL.md",
        lineterm=""
    ))
    
    if not diff:
        return "Aucune différence détectée."
    
    return "\n".join(diff)


def save_diff(iter_before: Path, iter_after: Path) -> Path:
    """Sauvegarde le diff dans iter_after/diff.md."""
    diff_text = diff_snapshots(iter_before, iter_after)
    
    before_meta_path = iter_before / "metadata.json"
    after_meta_path = iter_after / "metadata.json"
    
    before_tokens = "?"
    after_tokens = "?"
    
    if before_meta_path.exists():
        before_meta = json.loads(before_meta_path.read_text())
        before_tokens = before_meta.get("tokens_approx", "?")
    
    if after_meta_path.exists():
        after_meta = json.loads(after_meta_path.read_text())
        after_tokens = after_meta.get("tokens_approx", "?")
        modifications = after_meta.get("modifications", [])
    else:
        modifications = []
    
    diff_md = f"""# Diff — {iter_before.name} → {iter_after.name}

**Tokens :** {before_tokens} → {after_tokens} ({'+' if after_tokens > before_tokens else ''}{after_tokens - before_tokens if isinstance(after_tokens, int) and isinstance(before_tokens, int) else '?'})

## Modifications appliquées

"""
    
    for i, mod in enumerate(modifications, 1):
        diff_md += f"### Micro-édition #{i}\n"
        diff_md += f"- **Type :** {mod.get('type', '?')}\n"
        diff_md += f"- **Zone :** {mod.get('zone', '?')}\n"
        diff_md += f"- **Motivation :** {mod.get('motivation', '?')}\n\n"
    
    diff_md += "\n## Diff brut\n\n```diff\n"
    diff_md += diff_text
    diff_md += "\n```\n"
    
    diff_path = iter_after / "diff.md"
    diff_path.write_text(diff_md, encoding="utf-8")
    
    print(f"📄 Diff sauvegardé : {diff_path}")
    return diff_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snapshot et diff de skills")
    subparsers = parser.add_subparsers(dest="command")
    
    snap_parser = subparsers.add_parser("snapshot", help="Créer un snapshot")
    snap_parser.add_argument("--skill", required=True, help="Chemin vers SKILL.md")
    snap_parser.add_argument("--workspace", required=True, help="Dossier workspace")
    snap_parser.add_argument("--iteration", type=int, required=True, help="Numéro d'itération")
    
    diff_parser = subparsers.add_parser("diff", help="Générer un diff entre deux itérations")
    diff_parser.add_argument("--before", required=True, help="Dossier iteration-N")
    diff_parser.add_argument("--after", required=True, help="Dossier iteration-N+1")
    
    args = parser.parse_args()
    
    if args.command == "snapshot":
        snapshot_skill(Path(args.skill), Path(args.workspace), args.iteration)
    
    elif args.command == "diff":
        save_diff(Path(args.before), Path(args.after))
    
    else:
        parser.print_help()
