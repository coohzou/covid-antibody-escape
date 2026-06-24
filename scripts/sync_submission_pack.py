"""
Sync project artifacts to D:\\covid_website_summary for submission hand-in.
Run after run_evaluation.py to refresh test results and Overleaf bundle.
"""

import os
import shutil
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.paths import (
    EVALUATION_DIR,
    EVALUATION_INTERNAL_DIR,
    MANIFEST_PATH,
    ML_TEST_CSV,
    ML_TRAIN_CSV,
    PREDICTION_DATA_DIR,
    SPLIT_CONFIG_PATH,
)

SUMMARY_ROOT = Path(r"D:\covid_website_summary")

COPY_PAIRS = [
    (PROJECT_ROOT / "README.md", SUMMARY_ROOT / "PROJECT_README.md"),
    (PROJECT_ROOT / "data" / "README.md", SUMMARY_ROOT / "data" / "DATA_README.md"),
    (PROJECT_ROOT / "requirements.txt", SUMMARY_ROOT / "requirements.txt"),
    (Path(ML_TRAIN_CSV), SUMMARY_ROOT / "data" / "training" / "ml_train.csv"),
    (Path(ML_TEST_CSV), SUMMARY_ROOT / "data" / "training" / "ml_test.csv"),
    (Path(MANIFEST_PATH), SUMMARY_ROOT / "data" / "prediction" / "variant_manifest.json"),
    (Path(SPLIT_CONFIG_PATH), SUMMARY_ROOT / "data" / "evaluation" / "split_config.json"),
    (Path(EVALUATION_DIR) / "split_summary.json", SUMMARY_ROOT / "data" / "evaluation" / "split_summary.json"),
    (Path(EVALUATION_DIR) / "ml_test_results.json", SUMMARY_ROOT / "data" / "evaluation" / "ml_test_results.json"),
    (Path(EVALUATION_DIR) / "pipeline_test_results.json", SUMMARY_ROOT / "data" / "evaluation" / "pipeline_test_results.json"),
    (Path(EVALUATION_DIR) / "pipeline_test_summary.csv", SUMMARY_ROOT / "data" / "evaluation" / "pipeline_test_summary.csv"),
    (Path(EVALUATION_DIR) / "README.md", SUMMARY_ROOT / "data" / "evaluation" / "README.md"),
    (Path(EVALUATION_INTERNAL_DIR) / "batch_test_results.json", SUMMARY_ROOT / "data" / "evaluation" / "internal" / "batch_test_results.json"),
    (Path(EVALUATION_INTERNAL_DIR) / "batch_test_summary.csv", SUMMARY_ROOT / "data" / "evaluation" / "internal" / "batch_test_summary.csv"),
]

def copy_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  {dst.relative_to(SUMMARY_ROOT)}")
    else:
        print(f"  SKIP (missing): {src.name}")


def write_variant_catalog():
    import csv
    import json

    out = SUMMARY_ROOT / "data" / "prediction" / "variant_catalog.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        variants = json.load(f)["variants"]
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "lineage", "accession", "file", "location"])
        for item in variants:
            w.writerow([item["name"], item["lineage"], item["accession"], item["file"], "data/prediction"])
    print(f"  {out.relative_to(SUMMARY_ROOT)}")


def sync_overleaf():
    src = PROJECT_ROOT / "overleaf"
    dst = SUMMARY_ROOT / "overleaf_final_report"
    zip_path = SUMMARY_ROOT / "overleaf_final_report.zip"

    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"  overleaf_final_report/ (from project)")
        zip_root = src.parent
        zip_base = src
    elif dst.is_dir():
        print(f"  overleaf_final_report/ (existing in summary)")
        zip_root = dst.parent
        zip_base = dst
    else:
        print("  SKIP overleaf (no source found)")
        return

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in zip_base.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(zip_root))
    print(f"  overleaf_final_report.zip")


def main():
    print(f"Syncing submission pack -> {SUMMARY_ROOT}\n")

    print("Docs & data:")
    for src, dst in COPY_PAIRS:
        copy_file(Path(src), dst)

    write_variant_catalog()
    sync_overleaf()

    print("\nDone. Submission pack ready at:")
    print(f"  {SUMMARY_ROOT}")
    print("\nHand in:")
    print("  1. Project code: D:\\covid_website_project")
    print("  2. Summary pack: D:\\covid_website_summary")
    print("  3. Overleaf ZIP:  D:\\covid_website_summary\\overleaf_final_report.zip")


if __name__ == "__main__":
    main()
