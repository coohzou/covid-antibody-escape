"""
Batch-run all reference variant FASTA files through the analysis pipeline.

NOTE: This runs ALL 14 reference genomes including lineages present in CoV-UniBind
training data (BA.1, BQ.1.1, etc.). For unbiased report metrics, use instead:
  python scripts/evaluate_pipeline_test_set.py
  python scripts/evaluate_ml_test_set.py
"""

import json
import logging
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.paths import EVALUATION_INTERNAL_DIR, MANIFEST_PATH, PREDICTION_DATA_DIR
from utils.sequence_analyzer import SequenceAnalyzer
from utils.neutralization_predictor import neutralization_predictor

logging.basicConfig(level=logging.WARNING)


def load_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_path(item):
    return os.path.join(PREDICTION_DATA_DIR, item["file"])


def run_batch():
    manifest = load_manifest()
    analyzer = SequenceAnalyzer()
    rows = []

    print("Running batch variant analysis...\n")
    print(f"{'Variant':<14} {'Lineage':<16} {'Match':<14} {'Sim%':>6} {'Mut#':>5} {'IC50':>8} {'Risk':<22} Time")
    print("-" * 105)

    for item in manifest["variants"]:
        path = resolve_path(item)
        if not os.path.exists(path):
            rows.append({**item, "status": "missing"})
            print(f"{item['name']:<14} {'-':<16} {'FILE MISSING':<14}")
            continue

        start = time.time()
        result = analyzer.analyze_sequence_file(path)
        elapsed = round(time.time() - start, 1)

        if not result.get("success"):
            rows.append({
                **item,
                "status": "failed",
                "error": result.get("error"),
                "similarity": result.get("similarity_score", 0),
                "elapsed_sec": elapsed,
            })
            print(f"{item['name']:<14} {item.get('lineage', '-'):<16} {'FAILED':<14} {result.get('similarity_score', 0):>6} {'-':>5} {'-':>8} {'-':<22} {elapsed}s")
            continue

        detected = list(result.get("detected_mutations", {}).keys())
        prediction = neutralization_predictor.predict_variant_neutralization(detected)

        row = {
            "name": item["name"],
            "lineage": item.get("lineage", ""),
            "accession": item.get("accession", ""),
            "file": item.get("file", ""),
            "matched_variant": result.get("variant"),
            "similarity": result.get("similarity_score"),
            "variant_confidence": result.get("variant_confidence"),
            "mutation_count": len(detected),
            "mutations": detected,
            "cocktail_ic50": prediction.get("cocktail_prediction"),
            "summary_risk": prediction.get("summary_risk"),
            "individual_analysis": prediction.get("individual_analysis"),
            "elapsed_sec": elapsed,
            "status": "ok",
        }
        rows.append(row)

        mut_preview = ", ".join(detected[:4])
        if len(detected) > 4:
            mut_preview += f" (+{len(detected) - 4})"

        print(
            f"{item['name']:<14} {item.get('lineage', '-'):<16} "
            f"{str(result.get('variant', '-')):<14} "
            f"{result.get('similarity_score', 0):>6} "
            f"{len(detected):>5} "
            f"{prediction.get('cocktail_prediction', 0):>8} "
            f"{prediction.get('summary_risk', '-'):<22} "
            f"{elapsed}s"
        )

    out_path = os.path.join(EVALUATION_INTERNAL_DIR, "batch_test_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f"\nSaved detailed results to {out_path}")
    return rows


if __name__ == "__main__":
    run_batch()
