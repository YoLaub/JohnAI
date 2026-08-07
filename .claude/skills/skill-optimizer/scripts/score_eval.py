#!/usr/bin/env python3
"""
score_eval.py — Applique un rubric à un résultat d'évaluation.

Usage:
    python score_eval.py --eval evals/evals.json --result chemin/vers/output.md --eval-id 1
    python score_eval.py --batch --workspace optimization-workspace/iteration-1/

Le script affiche un score par critère et un score agrégé.
En mode batch, il agrège tous les scores d'une itération et compare avec la baseline.
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime


def score_single(eval_def: dict, result_text: str, model_judge: bool = False) -> dict:
    """
    Score un résultat contre un rubric.
    
    Si model_judge=True, utilise l'API Anthropic pour juger (nécessite une clé API).
    Sinon, retourne une structure vide à remplir manuellement.
    """
    rubric = eval_def.get("rubric", {})
    criteres = rubric.get("criteres", [])
    score_max = rubric.get("score_max", sum(c["poids"] for c in criteres))
    
    scores = []
    for critere in criteres:
        scores.append({
            "nom": critere["nom"],
            "poids": critere["poids"],
            "score_obtenu": None,  # À remplir : 0, 0.5*poids, ou poids
            "note": ""
        })
    
    return {
        "eval_id": eval_def["id"],
        "eval_type": eval_def.get("type", "unknown"),
        "score_max": score_max,
        "score_obtenu": None,  # Calculé après remplissage
        "seuil_succes": rubric.get("seuil_succes", score_max * 0.7),
        "criteres_scores": scores,
        "timestamp": datetime.now().isoformat()
    }


def aggregate_iteration(workspace_dir: Path) -> dict:
    """
    Agrège tous les scores d'une itération.
    Attend des fichiers scores-eval-N.json dans workspace_dir.
    """
    score_files = sorted(workspace_dir.glob("scores-eval-*.json"))
    
    if not score_files:
        print(f"Aucun fichier de scores trouvé dans {workspace_dir}")
        return {}
    
    total_score = 0
    total_max = 0
    passed = 0
    failed = 0
    results = []
    
    for sf in score_files:
        with open(sf) as f:
            data = json.load(f)
        
        score = data.get("score_obtenu", 0) or 0
        max_s = data.get("score_max", 0)
        seuil = data.get("seuil_succes", max_s * 0.7)
        
        total_score += score
        total_max += max_s
        
        if score >= seuil:
            passed += 1
        else:
            failed += 1
        
        results.append({
            "eval_id": data.get("eval_id"),
            "score": score,
            "score_max": max_s,
            "pct": round(score / max_s * 100, 1) if max_s else 0,
            "passed": score >= seuil
        })
    
    pct_global = round(total_score / total_max * 100, 1) if total_max else 0
    
    return {
        "iteration": workspace_dir.name,
        "score_total": total_score,
        "score_max_total": total_max,
        "pct_global": pct_global,
        "passed": passed,
        "failed": failed,
        "total_evals": passed + failed,
        "details": results,
        "timestamp": datetime.now().isoformat()
    }


def compare_iterations(iter_before: Path, iter_after: Path) -> dict:
    """Compare deux itérations et indique si la nouvelle est meilleure."""
    before = aggregate_iteration(iter_before)
    after = aggregate_iteration(iter_after)
    
    if not before or not after:
        return {"error": "Impossible de comparer — données manquantes"}
    
    delta_pct = after["pct_global"] - before["pct_global"]
    
    # Vérifier les régressions : evals qui passaient avant mais échouent maintenant
    regressions = []
    before_map = {d["eval_id"]: d for d in before.get("details", [])}
    after_map = {d["eval_id"]: d for d in after.get("details", [])}
    
    for eval_id, before_d in before_map.items():
        after_d = after_map.get(eval_id)
        if after_d and before_d["passed"] and not after_d["passed"]:
            regressions.append(eval_id)
    
    decision = "COMMIT" if delta_pct > 0 and not regressions else (
        "DISCUSSION" if delta_pct > 0 and regressions else "REVERT"
    )
    
    return {
        "avant": {
            "iteration": before["iteration"],
            "score": f"{before['score_total']}/{before['score_max_total']}",
            "pct": before["pct_global"],
            "passed": before["passed"],
            "failed": before["failed"]
        },
        "apres": {
            "iteration": after["iteration"],
            "score": f"{after['score_total']}/{after['score_max_total']}",
            "pct": after["pct_global"],
            "passed": after["passed"],
            "failed": after["failed"]
        },
        "delta_pct": round(delta_pct, 1),
        "regressions": regressions,
        "decision": decision,
        "message": (
            f"✅ COMMIT — +{delta_pct:.1f}% sans régression" if decision == "COMMIT" else
            f"⚠️ DISCUSSION — +{delta_pct:.1f}% mais {len(regressions)} régression(s) : {regressions}" if decision == "DISCUSSION" else
            f"❌ REVERT — Delta: {delta_pct:.1f}%, Régressions: {regressions}"
        )
    }


def print_comparison(comparison: dict):
    """Affiche une comparaison lisible dans le terminal."""
    print("\n" + "═" * 50)
    print(f"  COMPARAISON D'ITÉRATIONS")
    print("═" * 50)
    print(f"  Avant : {comparison['avant']['iteration']}")
    print(f"    Score : {comparison['avant']['score']} ({comparison['avant']['pct']}%)")
    print(f"    Passés : {comparison['avant']['passed']} | Échoués : {comparison['avant']['failed']}")
    print()
    print(f"  Après : {comparison['apres']['iteration']}")
    print(f"    Score : {comparison['apres']['score']} ({comparison['apres']['pct']}%)")
    print(f"    Passés : {comparison['apres']['passed']} | Échoués : {comparison['apres']['failed']}")
    print()
    print(f"  Delta : {comparison['delta_pct']:+.1f}%")
    if comparison["regressions"]:
        print(f"  ⚠️  Régressions sur evals : {comparison['regressions']}")
    print()
    print(f"  → {comparison['message']}")
    print("═" * 50 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Score des évaluations de skill-optimizer")
    parser.add_argument("--compare", nargs=2, metavar=("ITER_BEFORE", "ITER_AFTER"),
                        help="Comparer deux itérations")
    parser.add_argument("--aggregate", metavar="ITER_DIR",
                        help="Agréger les scores d'une itération")
    
    args = parser.parse_args()
    
    if args.compare:
        before_path = Path(args.compare[0])
        after_path = Path(args.compare[1])
        result = compare_iterations(before_path, after_path)
        print_comparison(result)
        # Sauvegarder le résultat
        output_path = after_path / "comparison.json"
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Résultat sauvegardé : {output_path}")
    
    elif args.aggregate:
        iter_path = Path(args.aggregate)
        result = aggregate_iteration(iter_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        output_path = iter_path / "aggregate.json"
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nAgrégat sauvegardé : {output_path}")
    
    else:
        parser.print_help()
