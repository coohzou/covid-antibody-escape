# Data Directory Guide

Project data are organised into three folders by purpose. Do not mix them.

## 1. `data/training/` — Machine learning

Used to train Casirivimab / Imdevimab IC50 Ridge models (offline only).

| Path | Description |
|------|-------------|
| `cov_unibind/` | Processed CoV-UniBind IC50 tables (`mutation_ic50.csv`, `wildtype_ic50.csv`) |
| `cov_unibind/raw/` | Archived Arora source CSVs |
| `processed_ml_features.csv` | Full mutation feature matrix (83 rows) |
| `ml_train.csv` | Training split (65 rows) |
| `ml_test.csv` | Held-out ML test split (18 rows; not used for training) |
| `models/` | Trained Ridge models and `feature_columns.json` |

Scripts: `build_ml_features.py`, `split_ml_dataset.py`, `train_neutralization_model.py`.

## 2. `data/prediction/` — Web runtime

Fourteen NCBI reference genomes loaded by the web app for variant matching and spike mutation calling.

| Path | Description |
|------|-------------|
| `manifest.json` | Variant metadata (name, lineage, accession, FASTA filename) |
| `*_complete.fasta` | Full genomes including Wuhan-Hu-1 |

Used by `utils/sequence_comparator.py` and `app.py`. Refresh with `scripts/download_variants.py`.

## 3. `data/evaluation/` — Test configuration and results

Held-out evaluation outputs for the report (separate from training data).

| Path | Description |
|------|-------------|
| `split_config.json` | ML / pipeline test split rules |
| `split_summary.json` | Split statistics |
| `ml_test_results.json` | ML test metrics (MAE, RMSE, r) |
| `pipeline_test_results.json` | Pipeline test results |
| `pipeline_test_summary.csv` | Pipeline test CSV summary |
| `internal/` | 14-strain batch regression (not a primary report metric) |

Run: `python scripts/run_evaluation.py`

## Quick reference

| Task | Folder |
|------|--------|
| Train / retrain models | `data/training/` |
| Upload analysis (web app) | `data/prediction/` |
| Report test metrics | `data/evaluation/` |
| Internal 14-strain regression | `data/evaluation/internal/` |
