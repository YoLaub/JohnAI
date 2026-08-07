#!/usr/bin/env python3
"""
package_skill.py — Empaquette le skill-optimizer en fichier .skill (zip renommé).

Usage:
    python package_skill.py --source /chemin/vers/skill-optimizer/ --output /chemin/vers/sortie/

Crée skill-optimizer.skill dans le dossier de sortie.
"""

import zipfile
import os
import argparse
import sys
from pathlib import Path


def package_skill(source_dir: Path, output_dir: Path) -> Path:
    """Empaquette un dossier de skill en fichier .skill."""
    
    if not source_dir.exists():
        print(f"Erreur : {source_dir} n'existe pas.")
        sys.exit(1)
    
    skill_name = source_dir.name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{skill_name}.skill"
    
    # Fichiers à exclure
    exclude_patterns = {
        "__pycache__", ".DS_Store", "*.pyc", ".git",
        "optimization-workspace", "*.skill"
    }
    
    def should_exclude(path: Path) -> bool:
        for pattern in exclude_patterns:
            if pattern.startswith("*."):
                if path.suffix == pattern[1:]:
                    return True
            elif path.name == pattern:
                return True
        return False
    
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in source_dir.rglob("*"):
            if file_path.is_file() and not should_exclude(file_path):
                # Chemin relatif dans le zip
                arcname = file_path.relative_to(source_dir.parent)
                zf.write(file_path, arcname)
    
    size_kb = output_path.stat().st_size / 1024
    
    print(f"✅ Skill empaqueté : {output_path}")
    print(f"   Taille : {size_kb:.1f} Ko")
    print(f"\nContenu :")
    with zipfile.ZipFile(output_path) as zf:
        for name in sorted(zf.namelist()):
            print(f"  {name}")
    
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Empaquette un skill en .skill")
    parser.add_argument("--source", default=".", help="Dossier source du skill")
    parser.add_argument("--output", default=".", help="Dossier de sortie")
    
    args = parser.parse_args()
    package_skill(Path(args.source), Path(args.output))
