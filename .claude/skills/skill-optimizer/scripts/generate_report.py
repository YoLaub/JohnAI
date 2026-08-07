#!/usr/bin/env python3
"""
generate_report.py — Génère le rapport final d'optimisation d'un skill.

Usage:
    python generate_report.py --workspace optimization-workspace/ --skill-name mon-skill

Lit tous les fichiers metadata.json, aggregate.json et diff.md de chaque itération
et produit un rapport Markdown de synthèse.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


def load_iteration_data(iter_dir: Path) -> dict:
    """Charge toutes les données disponibles pour une itération."""
    data = {"iteration": iter_dir.name, "path": str(iter_dir)}
    
    meta_path = iter_dir / "metadata.json"
    if meta_path.exists():
        data["metadata"] = json.loads(meta_path.read_text(encoding="utf-8"))
    
    agg_path = iter_dir / "aggregate.json"
    if agg_path.exists():
        data["aggregate"] = json.loads(agg_path.read_text(encoding="utf-8"))
    
    comp_path = iter_dir / "comparison.json"
    if comp_path.exists():
        data["comparison"] = json.loads(comp_path.read_text(encoding="utf-8"))
    
    diff_path = iter_dir / "diff.md"
    if diff_path.exists():
        data["diff"] = diff_path.read_text(encoding="utf-8")
    
    return data


def generate_report(workspace: Path, skill_name: str) -> str:
    """Génère le rapport Markdown complet."""
    
    # Charger toutes les itérations
    iter_dirs = sorted(workspace.glob("iteration-*"), key=lambda p: int(p.name.split("-")[1]))
    iterations_data = [load_iteration_data(d) for d in iter_dirs]
    
    if not iterations_data:
        return "Aucune itération trouvée dans le workspace."
    
    # Stats globales
    baseline = iterations_data[0]
    final = iterations_data[-1]
    
    baseline_pct = baseline.get("aggregate", {}).get("pct_global", "?")
    final_pct = final.get("aggregate", {}).get("pct_global", "?")
    
    baseline_tokens = baseline.get("metadata", {}).get("tokens_approx", "?")
    final_tokens = final.get("metadata", {}).get("tokens_approx", "?")
    
    n_iterations = len(iterations_data) - 1  # -1 car iteration-0 = baseline
    
    if isinstance(baseline_pct, (int, float)) and isinstance(final_pct, (int, float)):
        delta_pct = final_pct - baseline_pct
        delta_str = f"+{delta_pct:.1f}%" if delta_pct >= 0 else f"{delta_pct:.1f}%"
    else:
        delta_str = "N/A"
    
    report = f"""# Rapport d'optimisation — {skill_name}
Date : {datetime.now().strftime("%Y-%m-%d")}

## Résumé

| Métrique | Baseline | Final | Delta |
|----------|----------|-------|-------|
| Score eval set | {baseline_pct}% | {final_pct}% | {delta_str} |
| Tokens (approx) | {baseline_tokens} | {final_tokens} | {f'+{final_tokens - baseline_tokens}' if isinstance(baseline_tokens, int) and isinstance(final_tokens, int) else 'N/A'} |
| Itérations | — | {n_iterations} | — |

"""
    
    # Détail par itération
    report += "## Détail des itérations\n\n"
    
    for i, iter_data in enumerate(iterations_data):
        iter_name = iter_data["iteration"]
        
        if i == 0:
            report += f"### {iter_name} — Baseline\n\n"
        else:
            report += f"### {iter_name}\n\n"
        
        # Score
        agg = iter_data.get("aggregate", {})
        if agg:
            report += f"**Score :** {agg.get('score_total', '?')}/{agg.get('score_max_total', '?')} "
            report += f"({agg.get('pct_global', '?')}%) — "
            report += f"{agg.get('passed', '?')} passés / {agg.get('failed', '?')} échoués\n\n"
        
        # Modifications appliquées
        meta = iter_data.get("metadata", {})
        modifications = meta.get("modifications", [])
        if modifications:
            report += "**Modifications appliquées :**\n\n"
            for j, mod in enumerate(modifications, 1):
                report += f"{j}. **{mod.get('type', '?')}** — Zone : `{mod.get('zone', '?')}`\n"
                report += f"   *Motivation :* {mod.get('motivation', '?')}\n\n"
        elif i > 0:
            report += "*Aucune modification enregistrée pour cette itération.*\n\n"
        
        # Décision de comparaison
        comp = iter_data.get("comparison", {})
        if comp and i > 0:
            report += f"**Décision :** {comp.get('message', '?')}\n\n"
        
        report += "---\n\n"
    
    # Modifications rejetées (si enregistrées)
    report += "## Recommandations\n\n"
    report += "Pour continuer l'optimisation :\n\n"
    report += "1. Enrichir l'eval set avec des cas limites supplémentaires\n"
    report += "2. Vérifier que la zone INVARIANTS est correctement balisée\n"
    report += f"3. Si le score stagne, considérer une refonte partielle (skill-creator)\n"
    report += f"4. Optimiser la description de déclenchement si le skill ne se déclenche pas bien\n"
    
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Génère le rapport d'optimisation")
    parser.add_argument("--workspace", required=True, help="Dossier optimization-workspace/")
    parser.add_argument("--skill-name", required=True, help="Nom du skill")
    parser.add_argument("--output", default=None, help="Fichier de sortie (défaut: workspace/rapport-optimisation.md)")
    
    args = parser.parse_args()
    workspace = Path(args.workspace)
    
    report = generate_report(workspace, args.skill_name)
    
    output_path = Path(args.output) if args.output else workspace / "rapport-optimisation.md"
    output_path.write_text(report, encoding="utf-8")
    
    print(f"✅ Rapport généré : {output_path}")
    print(f"\n--- Aperçu ---\n")
    print(report[:500] + ("..." if len(report) > 500 else ""))
