"""Export batch_test_results.json to CSV and sync summary copies."""
import csv
import json
import os
import shutil
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.paths import EVALUATION_INTERNAL_DIR, MANIFEST_PATH, PREDICTION_DATA_DIR

JSON_PATH = os.path.join(EVALUATION_INTERNAL_DIR, "batch_test_results.json")
SUMMARY_DIR = r"D:\covid_website_summary\data"

COLUMNS = [
    "variant", "lineage", "accession", "matched_variant", "similarity_pct", "mutation_count",
    "key_mutations", "cocktail_ic50_ug_ml", "escape_risk",
    "casirivimab_ic50_ug_ml", "imdevimab_ic50_ug_ml",
    "casirivimab_fold", "imdevimab_fold", "elapsed_sec",
]


def main():
    with open(JSON_PATH, encoding="utf-8") as f:
        rows = json.load(f)

    csv_rows = []
    for r in rows:
        if r.get("status") != "ok":
            continue
        cas = r["individual_analysis"]["Casirivimab"]
        imd = r["individual_analysis"]["Imdevimab"]
        muts = "; ".join(r["mutations"])
        if len(muts) > 80:
            muts = "; ".join(r["mutations"][:8]) + "..."
        csv_rows.append([
            r["name"], r["lineage"], r["accession"], r["matched_variant"],
            r["similarity"], r["mutation_count"], muts,
            r["cocktail_ic50"], r["summary_risk"],
            cas["predicted_ic50_ug_ml"], imd["predicted_ic50_ug_ml"],
            cas["fold_change"], imd["fold_change"], r["elapsed_sec"],
        ])

    csv_path = os.path.join(EVALUATION_INTERNAL_DIR, "batch_test_summary.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        writer.writerows(csv_rows)

    os.makedirs(SUMMARY_DIR, exist_ok=True)
    shutil.copy2(JSON_PATH, os.path.join(SUMMARY_DIR, "batch_test_results.json"))
    shutil.copy2(csv_path, os.path.join(SUMMARY_DIR, "batch_test_summary.csv"))
    shutil.copy2(MANIFEST_PATH, os.path.join(SUMMARY_DIR, "variant_manifest.json"))

    catalog_path = os.path.join(SUMMARY_DIR, "variant_catalog.csv")
    with open(catalog_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "lineage", "accession", "file", "location"])
        with open(MANIFEST_PATH, encoding="utf-8") as mf:
            for item in json.load(mf)["variants"]:
                writer.writerow([
                    item["name"], item["lineage"], item["accession"],
                    item["file"], "data/prediction",
                ])

    overleaf_src = os.path.join(PROJECT_ROOT, "overleaf")
    overleaf_dst = r"D:\covid_website_summary\overleaf_final_report"
    if os.path.isdir(overleaf_dst):
        shutil.rmtree(overleaf_dst)
    shutil.copytree(overleaf_src, overleaf_dst)
    shutil.make_archive(
        r"D:\covid_website_summary\overleaf_final_report",
        "zip",
        overleaf_src,
    )

    print(f"Exported {len(csv_rows)} rows to {csv_path}")
    print("Synced summary data, manifest, catalog, and overleaf bundle.")


if __name__ == "__main__":
    main()
